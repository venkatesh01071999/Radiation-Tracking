from confluent_kafka import Producer
import csv
from dotenv import load_dotenv
import os
import json
import time
from datetime import datetime, timedelta
import logging
import threading

load_dotenv()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)


producer = Producer({'bootstrap.servers': os.environ.get('KAFKA_CLIENT')}) # kafka client
BUFFER = []
FLUSH_INTERVAL = timedelta(seconds=int(os.environ.get('FLUSH_INTERVAL')))
stop_event = threading.Event()  # event to signal the thread to stop


def failure_report(err, msg):
    if err is not None:
        logger.error(f"Message delivery failed for the message: {msg} with {err}")

def flush_to_kafka():
    global BUFFER

    if BUFFER:
        logger.info(f"Flushing begins at time: {datetime.now()}")
        BUFFER.sort(key=lambda x: x['Captured Time'])  # Sort by Captured Time

        # Group records by 'Captured Time'
        grouped_records = {}
        for record in BUFFER:
            captured_time = record['Captured Time']
            if captured_time not in grouped_records:
                grouped_records[captured_time] = []
            grouped_records[captured_time].append(record)
        
        logger.info(f"Flushing grouped records to Kafka: {len(grouped_records)} groups")
        for captured_time, record in grouped_records.items():
            producer.produce(
                os.environ.get('KAFKA_TOPIC'), 
                key=captured_time, 
                value=json.dumps({
                    'Captured Time': captured_time,
                    'Records': record
                }).encode('utf-8'),
                callback=failure_report
            )
            time.sleep(float(os.environ.get('SUBMISSION_INTERVAL')))  # simulate delay between messages
        producer.flush()  # Ensure all messages are sent
        BUFFER = [] # clear the buffer after sending
        logger.info(f"Flushing ends at time: {datetime.now()}")


def periodic_flush():
    while True:
        logger.info(f"Periodic flush called at time: {datetime.now()}")
        flush_to_kafka()
        stop_event.wait(float(os.environ.get('FLUSH_INTERVAL')))  # Wait for the flush interval     

def kafka_submission(csv_file_path):
    # Open and stream the CSV
    global BUFFER
    logger.info("Starting reading CSV file")
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)  # skip header if needed
        for index, row in enumerate(reader):
            logger.info(f"Processing row {index + 1}")
            if row[0] is None or row[0] == '': # skip null or empty rows
                continue
            BUFFER.append({header[i]: row[i] for i in range(len(header))})            
            
            time.sleep(float(os.environ.get('MESSAGE_DELAY'))) # simulate delay between messages

    stop_event.set() # signal the thread to stop after processing the CSV
    producer.flush()  # Ensure all messages are sent
    producer.close() # closes the network connections and allocated resources

if __name__ == "__main__":
    csv_file_path = os.environ.get('PROCESSED_FILE')
    if os.path.exists(csv_file_path):
        thread = threading.Thread(target=periodic_flush, daemon=True)
        thread.start()
        kafka_submission(csv_file_path)
        thread.join() # wait for the thread to finish