import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from confluent_kafka import Consumer, TopicPartition
import os
from dotenv import load_dotenv
import logging
import json
from murmurhash2 import murmurhash2


load_dotenv()

app = FastAPI()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


processed_topic = os.environ.get('PROCESSED_TOPIC')


def get_partition_for_user(username: str) -> int:
    return murmurhash2(username.encode('utf-8'), 0x9747b28c) % 64


def create_consumer(topic: str, partition: int):
    consumer = Consumer({
        'bootstrap.servers': os.environ.get('KAFKA_CLIENT'),
        'group.id': "middleware-group",
        'auto.offset.reset': 'latest',
        'enable.partition.eof': False, # consumer will not send end-of-file messages
    })
    consumer.assign([TopicPartition(topic, partition)]) # Assign the consumer to a specific partition
    return consumer


@app.websocket("/data-stream")
async def ws_data_stream(websocket: WebSocket):
    await websocket.accept()

    logger.info(f"Client connected: {websocket.client}")

    req_body = await websocket.receive_json()
    username = req_body.get("user")
    partition = get_partition_for_user(username)
    consumer = create_consumer(processed_topic, partition)
    logger.info(f"Consumer created for user {username} on partition {partition}")


    try:
        while True:
            msg = consumer.poll(5.0)  # Poll for messages with a timeout of 5 seconds
            if msg is None:
                await asyncio.sleep(0.1) # Sleep to avoid waiting for data indefinitely
                continue
            if msg.error():
                logger.error(f"Consumer error: {msg.error()}")
                continue

            key = msg.key().decode() if msg.key() else ""
            if key == username:
                value = msg.value().decode()
                await websocket.send_json(json.loads(value))
    except WebSocketDisconnect:
        logger.info(f"Client {username} disconnected")
    finally:
        consumer.close()
