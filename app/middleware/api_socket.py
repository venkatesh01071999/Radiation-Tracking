import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from aiokafka import AIOKafkaConsumer, TopicPartition, AIOKafkaProducer
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel, Field, model_validator
import os
from dotenv import load_dotenv
import logging
import json
from murmurhash2 import murmurhash2
from fastapi.middleware.cors import CORSMiddleware

# Loading  environment variables here
load_dotenv()


logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


processed_topic = os.environ.get('PROCESSED_TOPIC')
aggregate_topic = os.environ.get('AGGREGATE_TOPIC')
config_topic = os.environ.get('CONFIG_TOPIC')

BASE_DELAY = 1  # second
PING_INTERVAL = 10.0  # seconds
MAX_MESSAGES_PER_BATCH = 20 # 20 Messages per batch



# Pydantic models for our  config.json structure
class Timeframe(BaseModel):
    start: str = Field(..., description="Start time in 'YYYY-MM-DD HH:MM:SS' format")
    end: Optional[str] = Field(None, description="Optional end time in 'YYYY-MM-DD HH:MM:SS' format")

    @model_validator(mode='after')
    def ensure_end_is_valid(self):
        if self.end is None or self.end == 'null':
            self.end = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self
class Config(BaseModel):
    user: str
    boundingbox: list[float] = Field(..., min_items=4, max_items=4)
    country: str
    threshold: int
    threshold_type: str = Field(alias='threshold-type')  
    timeframe: Timeframe

def get_sleep_time(speed):
    actual_speed = max(1.0, min(10.0, speed))
    delay = BASE_DELAY / actual_speed
    logger.info(f"Actual delay for user: {delay}")
    return delay



def get_partition_for_user(username: str) -> int:
    return murmurhash2(username.encode('utf-8'), 0x9747b28c) % 64 # default partitionining strategy of kafka


async def create_consumer(topic: str, partition: int):
    consumer = AIOKafkaConsumer(
        bootstrap_servers= os.environ.get('KAFKA_CLIENT'),
        group_id =  "middleware-group",
        auto_offset_reset = 'latest',
        enable_auto_commit=False,
        max_poll_records=MAX_MESSAGES_PER_BATCH
    )
    await consumer.start()
    consumer.assign([TopicPartition(topic, partition)]) # Assign the consumer to a specific partition
    return consumer

# Global Kafka producer variable
producer: AIOKafkaProducer | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=os.environ.get('KAFKA_CLIENT')
    )
    await producer.start()
    logger.info("Kafka Producer started")
    try:
        yield
    finally:
        if producer:
            await producer.stop()
            logger.info("Kafka Producer stopped")

app = FastAPI(lifespan=lifespan)

# CORS Middleware setup
origins = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#  WebSocket Routes 
@app.websocket("/data-stream")
async def ws_data_stream(websocket: WebSocket):
    await websocket.accept()

    logger.info(f"Client connected: {websocket.client}")

    qp = websocket.query_params
    username = qp.get("user")
    speed = float(qp.get("speed"))
    partition = get_partition_for_user(username)
    consumer = await create_consumer(processed_topic, partition)
    logger.info(f"Consumer created for user {username} on partition {partition} on topic {processed_topic}")

    last_message = asyncio.get_event_loop().time()
    try:
        while True:
            try:
                client_data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=0.01 # 10ms
                )
                if "speed" in client_data:
                    speed = float(client_data["speed"])
                    logger.info(f"Updated speed:{speed}")
            except asyncio.TimeoutError:
                pass  # No client message, proceed to Kafka

            msg = await consumer.getmany(timeout_ms=2000, max_records=MAX_MESSAGES_PER_BATCH) # poll for 2 second to retrieve
            now = asyncio.get_event_loop().time()
            if not msg:
                if now - last_message > PING_INTERVAL:
                    await websocket.send_json({"type": "ping"}) # Send a ping message to keep the connection alive
                    last_message = now
                await asyncio.sleep(0.1) # Sleep to avoid waiting for data indefinitely
                continue
            
            for tp, messages in msg.items():
                for message in messages:
                    if message.key.decode() == username:
                        value = json.loads(message.value.decode())
                        radiation_data = json.loads(value['radiation_data'])
                        lat_lon = radiation_data['Latitude'] + '_' + radiation_data['Longitude']
                        await websocket.send_json({
                            str(lat_lon): radiation_data
                        })
                        last_message = now
                        await asyncio.sleep(get_sleep_time(speed))
                
    except WebSocketDisconnect:
        logger.info(f"Client {username} disconnected")
    finally:
        await consumer.stop()

@app.websocket("/aggregate-stream")
async def ws_aggregate_stream(websocket: WebSocket):
    await websocket.accept()

    logger.info(f"Client connected: {websocket.client}")

    qp = websocket.query_params
    username = qp.get("user")
    partition = get_partition_for_user(username)
    consumer = await create_consumer(aggregate_topic, partition)
    logger.info(f"Consumer created for user {username} on partition {partition} on topic {aggregate_topic}")

    last_message = asyncio.get_event_loop().time()
    try:
        while True:
            try:
                msg = await asyncio.wait_for(
                    consumer.getone(),
                    timeout=1.0
                ) # wait for a second to retrieve message

                key = msg.key.decode()
                if key == username:
                    value = json.loads(msg.value.decode())
                    value['agg_data'] = json.loads(value['agg_data'])
                    await websocket.send_json(value)
                    last_message = asyncio.get_event_loop().time()
            except asyncio.TimeoutError:
                now = asyncio.get_event_loop().time()
                if now - last_message > PING_INTERVAL:
                    await websocket.send_json({"type": "ping"}) # Send a ping message to keep the connection alive
                    last_message = now

    except WebSocketDisconnect:
        logger.info(f"Client {username} disconnected")
    finally:
        await consumer.stop()

# POST API to the configuration
@app.post("/set-config")
async def set_config(config: Config):
    global producer
    if not producer:
        return {"error": "Kafka producer not initialized"}

    config_json = json.dumps(config.model_dump(by_alias=True)).encode('utf-8')
    await producer.send_and_wait(
        topic=config_topic,
        value=config_json
    )
    logger.info(f"Configuration sent to topic {config_topic}: {config_json.decode()}")
    return {"message": "Configuration set successfully"}