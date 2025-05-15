from confluent_kafka import Producer
from dotenv import load_dotenv
import os
import json
import logging

load_dotenv()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)

producer = Producer({'bootstrap.servers': os.environ.get('KAFKA_CLIENT')}) # kafka client
topic = os.environ.get('CONFIG_TOPIC')

with open(os.environ.get('CONFIG_FILE'), 'r') as file:
    config = json.load(file)
    producer.produce(
        topic, 
        value=json.dumps(config).encode('utf-8'),
    )
    producer.flush()
    logger.info(f"Config: {config} sent to Kafka topic: {topic}")