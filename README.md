# Radiation Tracking

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
2) Move to the root of the project.
3) Start the container using `docker-compose up -d`

# Cloud Details
1) The project is deployed in **Azure Cloud Environment**.
2) Services used for the Project - **Azure Kubernetes Service(AKS)**, **Azure Container Registry(ACR)**
3) **ACR** is used for storing the docker images to be used by the AKS.
4) **AKS** is used to deploy the application in a scalable fashion.
5) Compute node used for AKS **Standard_B2ms** which comrises of 2VCPU and 8GB memory.
6) Node count = 2.
8) Totally 3 Deployments and 9 Pods where each services have 1 replica except Task Manager of Flink which will have 2 replica to process real-time data.
9) Two of these Pods are Load Balancers to expose to the real world. (Ui, Middleware)
10) Static IP's or domain names are not purchased, so the IP's used in the `docker-compose-cloud.yml` file is subjected to change.

## High Level Cloud Setup instruction
1) Enable Insights, OperationalInsights, ContainerService, ContainerRegistry to setup ACR, AKS.
2) Setup ACR.
3) Setup AKS.
4) Setup a connection between AKS and ACR to allow AKS to pull images from ACR.
5) Push all the built and tagged docker files to ACR.
6) **kubectl apply** all the deployment and service files.


