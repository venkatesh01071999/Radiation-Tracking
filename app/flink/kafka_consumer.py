from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaSink, KafkaRecordSerializationSchema, KafkaOffsetsInitializer
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common import WatermarkStrategy
from pyflink.datastream.state import MapStateDescriptor
from pyflink.datastream.functions import KeyedBroadcastProcessFunction, WindowFunction
from pyflink.datastream.window import TumblingProcessingTimeWindows
from pyflink.common.time import Time
from pyflink.common.typeinfo import Types
from dotenv import load_dotenv
import json
import os
from datetime import datetime
import logging

load_dotenv()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# KeyedBroadcastProcessFunction must be inherited if we are connecting a broadcast stream with a keyed stream
class DynamicFilterFunction(KeyedBroadcastProcessFunction):
    global TIME_FORMAT
    def __init__(self, config_descriptor):
        self.config_descriptor = config_descriptor

    def process_broadcast_element(self, value, ctx): # broadcast stream
        config = json.loads(value)
        logger.info(f"Received config: {config}")
        bc_state = ctx.get_broadcast_state(self.config_descriptor) # Get the latest broadcast state
        user_id = config.pop("user")
        bc_state.put(user_id, json.dumps(config)) # Store the config in the broadcast state

    def _operators(self, event, config):
        default_return = True

        # OPERATOR 1 - Non Null Radiation Value
        radiation_value = event.get("Value")
        if radiation_value is None or radiation_value == "":
            default_return = False

        # OPERATOR 2 - Time Based Filtering
        if "timeframe" in config:
            start_time, end_time = datetime.strptime(config["timeframe"].get("start"), TIME_FORMAT), \
                    datetime.strptime(config["timeframe"].get("end", datetime.now().strftime("%Y-%m-%d %H:%M:%S")), TIME_FORMAT)

            captured_time = datetime.strptime(event['Captured Time'], TIME_FORMAT) 

            if captured_time < start_time or captured_time > end_time:
                default_return = False
        
        #OPERATOR 3 - Location Based Filtering
        # This is a bounding box filter
        # bounds[0] = lat_min, bounds[1] = lat_max, bounds[2] = lon_min, bounds[3] = lon_max
        if "boundingbox" in config:
            bounds = config["boundingbox"]
            lat, lon = float(event['Latitude']), float(event['Longitude'])
            if not ((bounds[0] <= lat <= bounds[1]) and
                    (bounds[2] <= lon <= bounds[3])):
                default_return = False
        
        return default_return

    def process_element(self, value, ctx): # main data stream
        event = json.loads(value)
        logger.info(f"Received event: {event}")
        records = event.get("Records", [])
        bc_state = ctx.get_broadcast_state(self.config_descriptor)

        for user in bc_state.keys():
            config = json.loads(bc_state.get(user))
            for record in records:
                if self._operators(record, config):
                    record_copy = record.copy()
                    record_copy["user"] = user
                    record_copy["country"] = config.get("country", "")
                    yield json.dumps(record_copy)

class Aggregate(WindowFunction):
    def apply(self, key, window, inputs):
        radiations = []
        for data in inputs:
            data = json.loads(data)
            radiations.append(float(data.get("Value")))

        if len(radiations) != 0:
            # Aggregation 1
            avg_val = sum(radiations) / len(radiations)
            # Aggregation 2
            max_val = max(radiations)
            yield json.dumps({
                "user_id": key,
                "avg_radiation": avg_val,
                "max_radiation": max_val,
            })
    

def kafka_to_kafka_json():
    env = StreamExecutionEnvironment.get_execution_environment()
    env.add_jars(
        os.environ.get('KAFKA_CLIENT_JAR'),
        os.environ.get('KAFKA_CONNECTOR'),
    )

    # Set the parallelism to 1 later overriding it in the sink
    env.set_parallelism(1)

    kafka_brokers = os.environ.get('KAFKA_CLIENT')

    input_topic = os.environ.get('KAFKA_TOPIC')

    config_topic = os.environ.get('CONFIG_TOPIC')
    
    output_topic = os.environ.get('PROCESSED_TOPIC')

    agg_topic = os.environ.get('AGGREGATE_TOPIC')

    # Kafka Data Source
    kafka_source = KafkaSource.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_topics(input_topic) \
        .set_group_id("flink-group") \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest())  \
        .build()
    
    # Kafka Config Source
    kafka_source_config = KafkaSource.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_topics(config_topic) \
        .set_group_id("flink-config-group") \
        .set_value_only_deserializer(SimpleStringSchema()) \
        .set_starting_offsets(KafkaOffsetsInitializer.latest())  \
        .build()
    
    # Kafka Processed Sink
    kafka_sink = KafkaSink.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
            .set_topic(output_topic)
            .set_key_serialization_schema(SimpleStringSchema())
            .set_value_serialization_schema(SimpleStringSchema())
            .build()
        )  \
        .build()
    
    # Kafka Agg Sink
    kafka_sink_agg = KafkaSink.builder() \
        .set_bootstrap_servers(kafka_brokers) \
        .set_record_serializer(
            KafkaRecordSerializationSchema.builder()
                .set_topic(agg_topic)
                .set_key_serialization_schema(SimpleStringSchema())
                .set_value_serialization_schema(SimpleStringSchema())
                .build()
        ) \
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

    # Key By - creates a keyed stream based on the user id.Which is a row data
    # Map - maps the row data into a stringified data to pass it to sink
    # set parallelism - match ouput topic partitioning. Tells flink to run 64 instances in parallel. Each instance is like a subtask.
    # Each subtask can write data into one partition of the topic.
    keyed_stream = processed.key_by(lambda x: json.loads(x).get("user"), key_type=Types.STRING())\
    
    keyed_stream.map(lambda x: x, output_type=Types.STRING()) \
        .sink_to(kafka_sink).set_parallelism(64)
    
    # Aggregating for 10 seconds
    agg_data = keyed_stream \
        .window(TumblingProcessingTimeWindows.of(Time.seconds(10))) \
        .apply(Aggregate(), output_type=Types.STRING()) \
    
    agg_data.print()
    agg_data.sink_to(kafka_sink_agg).set_parallelism(64)
    
    env.execute("Flink Processing Job")

if __name__ == '__main__':
    kafka_to_kafka_json()