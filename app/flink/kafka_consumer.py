import os
import json
from pyflink.common import Configuration, WatermarkStrategy
from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import FlinkKafkaConsumer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream import CheckpointingMode

def main():
    # Set up Flink config to include Kafka connector JAR if needed
    config = Configuration()
    config.set_string(
        "pipeline.jars",
        "file:///Users/kunalchavan/Desktop/bd/bd25_project_m2_c/app/flink/flink-connector-kafka-3.0.1-1.18.jar"
    )

    env = StreamExecutionEnvironment.get_execution_environment(config)
    env.set_parallelism(1)

    # Enable checkpointing
    env.enable_checkpointing(10000, CheckpointingMode.EXACTLY_ONCE)

    kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    kafka_topic = os.environ.get("KAFKA_TOPIC", "radiation-topic")

    # Configure Kafka Consumer with SimpleStringSchema
    kafka_consumer = FlinkKafkaConsumer(
        topics=kafka_topic,
        deserialization_schema=SimpleStringSchema(),
        properties={
            'bootstrap.servers': kafka_bootstrap_servers,
            'group.id': os.environ.get("KAFKA_GROUP_ID", "flink-consumer-group"),
            'auto.offset.reset': 'earliest'
        }
    )

    # Add source and parse JSON manually
    ds = env.add_source(kafka_consumer).name("Kafka Source")
    parsed = ds.map(lambda x: json.loads(x)).name("Parse JSON")

    # Log the parsed output
    parsed.map(lambda x: f"Received record: {x}").print()

    env.execute("Kafka to Flink Pipeline")

if __name__ == "__main__":
    main()
