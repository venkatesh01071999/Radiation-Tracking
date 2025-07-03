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
    5. `./kafka-configs.sh --bootstrap-server kafka:9092 --alter --entity-type topics --entity-name configuration-topic --add-config max.message.bytes=10485880`
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

## Steps to setup Middleware
1) Move to `app/middleware` in the project directory.
2) pip install -r requirements.txt
3) fastapi run api_socket.py

## Steps to setup UI
1) Move to `app/frontend` in the project directory.
2) npm i
3) Set the environment variables by creating a **.env** file.
4) npm start
5) Once UI is started, start the kafka provider by moving to `app/kafka` directory and run `python kafka_stream.py`

## Hint
1) For the environment variables for each service refer `docker-compose.yml` file.

# Docker Setup
1) Install Docker from [Docker Website](https://www.docker.com/)
2) The docker images for the project is under the namespace **venky01071999**.
3) List of Docker Images
    1. `venky01071999/producer`
    2. `venky01071999/flink-submit-job`
    3. `venky01071999/flink-taskmanager`
    4. `venky01071999/ui`
    5. `venky01071999/flink-jobmanager`
    6. `venky01071999/middleware`
4) Move to the root of the project.
5) Pull the images using the commmand `docker-compose pull`
6) Start the container using `docker-compose up -d`

