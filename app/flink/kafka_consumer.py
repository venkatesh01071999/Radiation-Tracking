from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy
from pyflink.common.typeinfo import Types
from dotenv import load_dotenv
import os

load_dotenv()

def kafka_to_kafka_json():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars(
        os.environ.get('KAFKA_CLIENT_JAR'),
        os.environ.get('KAFKA_CONNECTOR'),
    )
    env.set_parallelism(1)

    kafka_brokers = os.environ.get('KAFKA_CLIENT')

    input_topic = os.environ.get('KAFKA_TOPIC')
    
    output_topic = os.environ.get('PROCESSED_TOPIC')

    # Kafka Consumer
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_topics(input_topic) \
        .set_group_id("flink-group") \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest())  \
        .build()
    # Kafka Producer
    kafka_sink = KafkaSink.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(output_topic)
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )  \
        .build()

    def custom_map(json_data):
        print("Processing JSON data: ", json_data)
        return json_data

    # Create the data stream
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="KafkaSource"
    )

    stream.map(custom_map, output_type=Types.STRING()).sink_to(kafka_sink)

    env.execute("Kafka to Kafka JSON Streaming Job")

if _name_ == '_main_':
    kafka_to_kafka_json()
