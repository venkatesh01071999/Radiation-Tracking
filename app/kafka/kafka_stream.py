from kafka import KafkaProducer
import csv
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()


producer = KafkaProducer(bootstrap_servers=os.environ.get('KAFKA_CLIENT')) # kafka client


csv_file_path = os.environ.get('PROCESSED_FILE')  # Path to reversed CSV file

# Open and stream the CSV
with open(csv_file_path, 'r') as file:
    reader = csv.reader(file)
    header = next(reader)  # skip header if needed
    for index, row in enumerate(reader):
        message = {header[i]: row[i] for i in range(len(header))}            
        producer.send('radiation-topic', value=json.dumps(message).encode('utf-8'))
        print(f"Sent message {index}: {message}")
        time.sleep(0.5) # simulate delay between messages

producer.flush() # sends any remaining messages to the kafka
producer.close() # closes the network connections and allocated resources