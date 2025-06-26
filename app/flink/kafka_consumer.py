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
from pyflink.table import StreamTableEnvironment, EnvironmentSettings, Schema, DataTypes
import json
import os
from datetime import datetime
import logging
from shapely.geometry import Point, shape
from shapely.prepared import prep

load_dotenv()
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger(__name__)
TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

geometry_cache = {}
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
        geometry_cache[user_id] = shape(config['geojson'])
        del config['geojson']  # Remove geojson from the config to avoid storing large data in broadcast state 
        bc_state.put(user_id, json.dumps(config)) # Store the config in the broadcast state

    def _operators(self, event, config, user):
        try:
            captured_time = datetime.strptime(event['Captured Time'], TIME_FORMAT)
        except ValueError:
            captured_time =  datetime.strptime(event['Captured Time'], "%Y-%m-%d %H:%M:%S.%f") 
        event['timestamp'] = captured_time.timestamp()  # Add timestamp for easier processing

        # OPERATOR 1 - Non Null Radiation Value
        radiation_value = event.get("Value")
        if radiation_value is None or radiation_value == "":
            return False

        # OPERATOR 2 - Time Based Filtering
        if "timeframe" in config:
            timeframe = config["timeframe"]
            if "start" in timeframe:
                start_time = datetime.strptime(timeframe.get("start"), TIME_FORMAT)
                if captured_time < start_time:
                   return False
            if "end" in timeframe:
                end_time = datetime.strptime(timeframe.get("end"), TIME_FORMAT)
                if captured_time > end_time:
                    return False
        
        #OPERATOR 3 - Location Based Filtering
        # This is a bounding box filter
        # bounds[0] = lat_min, bounds[1] = lat_max, bounds[2] = lon_min, bounds[3] = lon_max
        if user in geometry_cache:
            bounds = geometry_cache[user]
            point = Point(float(event['Longitude']), float(event['Latitude']))
            contains = bounds.contains(point)
            print(f"contains point {point} in geojson: {contains}")
            if not contains:
                return False
            
                
        #OPERATOR 4 - THRESHOLDTYPE-BASED COLOR TAGGING AND FILTERING
        threshold = config.get("threshold")
        threshold_type = config.get("threshold-type", "both")

        if threshold is not None:
            try:
                threshold = float(threshold)
            except ValueError:
                event["status"] = "invalid"
                return False

            if threshold_type == "both":
            # No filtering, just tagging
                if float(radiation_value) > threshold:
                    event["status"] = "red"
                else:
                    event["status"] = "green"

            elif threshold_type == "above":
                if float(radiation_value) > threshold:
                    event["status"] = "red"
                else:
                    return False

            elif threshold_type == "below":
                if float(radiation_value) < threshold:
                    event["status"] = "green"
                else:
                    return False


        return True

    
    def process_element(self, value, ctx): # main data stream
        event = json.loads(value)
        logger.info(f"Received event: {event}")
        records = event.get("Records", [])
        bc_state = ctx.get_broadcast_state(self.config_descriptor)

        for user in bc_state.keys():
            config = json.loads(bc_state.get(user))
            for record in records:
                if self._operators(record, config, user):
                    record_copy = record.copy()
                    record_copy["user"] = user
                    record_copy["country"] = config.get("country", "")
                    yield json.dumps(record_copy)

class Aggregate(WindowFunction):
    def apply(self, key, window, inputs):
        min_val, min_data = float("inf"), None
        max_val, max_data = float("-inf"), None
        sum_val, count = 0, 0
        values = [] 
        for data in inputs:
            data = json.loads(data)
            radiation_value = float(data.get("Value"))
            values.append(radiation_value)
            # AGGREGATION - Logic for Average radiation value
            sum_val += radiation_value
            count += 1
            # AGGREGATION - Find the minimum radiation value
            if radiation_value < min_val:
                min_val = radiation_value
                min_data = {
                    "lat": data.get("Latitude"),
                    "lon": data.get("Longitude"),
                    "time": data.get("Captured Time"),
                    "value": min_val
                }
            # AGGREGATION - Find the maximum radiation value
            if radiation_value > max_val:
                max_val = radiation_value
                max_data = {
                    "lat": data.get("Latitude"),
                    "lon": data.get("Longitude"),
                    "time": data.get("Captured Time"),
                    "value": max_val
                }
                
        # AGGREGATION - FIND THE Standard deviation - to find variability of radidation values
        mean = sum_val / count if count > 0 else 0
        variance = sum((x - mean) ** 2 for x in values) / count if count > 0 else 0
        stddev = variance ** 0.5
            
        yield json.dumps({
            "user_id": key,
            "min_radiation": min_data,
            "max_radiation": max_data,
            "Average":{
                "value": sum_val / count if count > 0 else 0, # Avoid division by zero
                "count": count,
                "sum": sum_val
            },
            "stddev": stddev 
        })

def kafka_to_kafka_json():
    env = StreamExecutionEnvironment.get_execution_environment()
    settings = EnvironmentSettings.in_streaming_mode() # Use streaming mode for continuous data processing
    table_env = StreamTableEnvironment.create(env, environment_settings=settings) # Create a Table Environment
    if os.environ.get('KAFKA_CLIENT_JAR') and os.environ.get('KAFKA_CONNECTOR'):
        env.add_jars(
            os.environ.get('KAFKA_CLIENT_JAR'),
            os.environ.get('KAFKA_CONNECTOR')
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
    
    mapped_stream = keyed_stream.map(lambda x: (
        json.loads(x).get("user"),
        x
    ), output_type=Types.TUPLE([Types.STRING(), Types.STRING()])) \
         
    result_table = table_env.from_data_stream(
        mapped_stream,
        Schema.new_builder()
            .column_by_expression("user", "f0")
            .column_by_expression("radiation_data", "f1")
            .build()
    )

    result_table = result_table.select(result_table.user, result_table.radiation_data)

    table_env.execute_sql(f"""
        CREATE TABLE processed_sink (
            `user` STRING,
            radiation_data STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{os.environ.get("PROCESSED_TOPIC")}',
            'properties.bootstrap.servers' = '{os.environ.get("KAFKA_CLIENT")}',
            'key.format' = 'raw',
            'key.fields' = 'user',
            'value.format' = 'json',
            'sink.parallelism' = '64'
        )
    """)

    result_table.execute_insert("processed_sink")
    
    # Aggregating for 10 seconds
    agg_data = keyed_stream \
        .window(TumblingProcessingTimeWindows.of(Time.seconds(10))) \
        .apply(Aggregate(), output_type=Types.STRING()) \
    
    agg_stream = agg_data.map(lambda x: (json.loads(x).get('user_id'),x), 
                        output_type=Types.TUPLE([Types.STRING(), Types.STRING()])
                    )

    agg_table = table_env.from_data_stream(
        agg_stream,
        Schema.new_builder()
            .column_by_expression("user", "f0")
            .column_by_expression("agg_data", "f1")
            .build()
    )
    agg_table = agg_table.select(agg_table.user, agg_table.agg_data)

    table_env.execute_sql(f"""
        CREATE TABLE aggregate_sink (
            user_id STRING,
            agg_data STRING
        ) WITH (
            'connector' = 'kafka',
            'topic' = '{os.environ.get("AGGREGATE_TOPIC")}',
            'properties.bootstrap.servers' = '{os.environ.get("KAFKA_CLIENT")}',
            'key.format' = 'raw',
            'key.fields' = 'user_id',
            'value.format' = 'json',
            'sink.parallelism' = '64'
        )
    """)  
    agg_table.execute_insert("aggregate_sink")  
    env.execute("Flink Processing Job")

if __name__ == '__main__':
    kafka_to_kafka_json()