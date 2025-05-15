from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy
from pyflink.datastream.state import MapStateDescriptor
from pyflink.datastream.functions import KeyedBroadcastProcessFunction
from pyflink.common.typeinfo import Types
from dotenv import load_dotenv
import json
import os

load_dotenv()

# KeyedBroadcastProcessFunction must be inherited if we are connecting a broadcast stream with a keyed stream
class DynamicFilterFunction(KeyedBroadcastProcessFunction):
    def __init__(self, config_descriptor):
        self.config_descriptor = config_descriptor

    def process_broadcast_element(self, value, ctx): # broadcast stream
        config = json.loads(value)
        bc_state = ctx.get_broadcast_state(self.config_descriptor) # Get the latest broadcast state
        for key, val in config.items():
            bc_state.put(key, str(val)) # Update the broadcast state with the new configuration

    def process_element(self, value, ctx): # main data stream
        event = json.loads(value)
        bc_state = ctx.get_broadcast_state(self.config_descriptor)
        

def kafka_to_kafka_json():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars(
        os.environ.get('KAFKA_CLIENT_JAR'),
        os.environ.get('KAFKA_CONNECTOR'),
    )
    env.set_parallelism(1)

    kafka_brokers = os.environ.get('KAFKA_CLIENT')

    input_topic = os.environ.get('KAFKA_TOPIC')

    config_topic = os.environ.get('CONFIG_TOPIC')
    
    output_topic = os.environ.get('PROCESSED_TOPIC')

    # Kafka Consumer
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_topics(input_topic) \
        .set_group_id("flink-group") \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest())  \
        .build()
    
    # Kafka Config Consumer
    kafka_source_config = KafkaSource.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_topics(config_topic) \
        .set_group_id("flink-config-group") \
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

    # Create the data stream
    stream = env.from_source(
        source=kafka_source,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="KafkaSource"
    )

    # Create the config stream
    config_stream = env.from_source(
        source=kafka_source_config,
        watermark_strategy=WatermarkStrategy.no_watermarks(),
        source_name="ConfigSource"
    )

    # defines a key-value map for sharing dynamic configuration across different data streams
    config_descriptor = MapStateDescriptor("config", Types.STRING(), Types.STRING()) # "lat": "0.0", "lon": "0.0"

    # Here we key by a static key to ensure that all records are processed by the same instance.
    # connect the config stream to the main stream.
    # process handles the dynamic filtering logic.
    processed = stream.key_by(lambda x: "radiation_data") \
                .connect(config_stream.broadcast(config_descriptor)) \
                .process(DynamicFilterFunction(config_descriptor), output_type=Types.STRING())

    processed.sink_to(kafka_sink)

    env.execute("Flink Processing Job")

if __name__ == '__main__':
    kafka_to_kafka_json()
