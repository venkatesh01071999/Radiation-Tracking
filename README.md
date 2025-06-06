# BD25_Project_M2_C

# Local Setup
## Steps to setup Kafka

1) Download Kafka Docker Image [Apache/Kafka](https://hub.docker.com/r/apache/kafka)
2) Run the Docker Image in Docker Desktop.
3) Create topics in Kafka by switching into the directory "**cd opt/kafka/bin**" of the container environment and execute the command 
    1. `./kafka-topics.sh --create --topic radiation-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`
    2. `./kafka-topics.sh --create --topic configuration-topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1`
    3. `./kafka-topics.sh --create --topic processed-topic --bootstrap-server localhost:9092 --partitions 64 --replication-factor 1`
    4. `./kafka-topics.sh --create --topic aggregate-topic --bootstrap-server localhost:9092 --partitions 64 --replication-factor 1`
4) Move to `app/kafka` in the project directory.
5) pip install -r requirements.txt
6) Set the environment variables by creating a **.env** file.
7) `python chunk_csv.py` to create a large chunk of the original dataset.
8) `python reverse_dataset.py` to reverse the dataset to stream the old data first.


## Steps to setup Flink
1) Install JDK 11
2) Set `JAVA_HOME` environment variable and add the **bin/** folder to the `PATH`
3) Move to `app/flink` in the project directory.
4) pip install -r requirements.txt
5) Set the environment variables by creating a **.env** file. Especially JAR files path in the format `file:///`
6) `python kafka_consumer.py` to start processing.
7) Once Flink app is started, start the kafka provider by moving to `app/kafka` directory and run `python kafka_stream.py`

