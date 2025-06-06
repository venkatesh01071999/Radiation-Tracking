from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from confluent_kafka import Producer
import json

# Initialize FastAPI
app = FastAPI()

# Kafka Producer configuration
kafka_config = {
    'bootstrap.servers': 'localhost:9092'  
}
producer = Producer(kafka_config)
CONFIG_TOPIC = "configuration_topic"  # Kafka topic

# Pydantic model for config.json structure (adjust based on your config.json)
class Config(BaseModel):
    threshold_filtering: dict  
    region_filtering: dict    
    non_null_filtering: bool  
    time_filtering: dict     

# Callback to handle Kafka delivery reports
def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

# POST API to accept config and send to Kafka
@app.post("/set-config")
async def set_config(config: Config):
    try:
        # Convert the config to JSON string
        config_data = config.dict()
        config_json = json.dumps(config_data)

        # Publish to Kafka Configuration Topic
        producer.produce(
            topic=CONFIG_TOPIC,
            value=config_json,
            callback=delivery_report
        )
        producer.flush()  # Ensure the message is sent

        return {"message": "Configuration set successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error setting config: {str(e)}")

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
