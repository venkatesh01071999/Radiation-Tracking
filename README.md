# BD25_Project_M2_C


## Steps to setup Kafka

1) Download Kafka Docker Image [Apache/Kafka](https://hub.docker.com/r/apache/kafka)
2) Run the Docker Image in Docker Desktop.
3) Create a topic in Kafka by switching into the directory "**cd opt/kafka/bin**" of the container environment and execute the command "**./kafka-topics.sh --create --topic topic-name --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1**".
4) Move to "app/kafka" in the project directory.
5) pip install -r requirements.txt
6) Set the environment variables by creating a **.env** file.
7) python chunk_csv.py to create a large chunk of the original dataset.
8) python reverse_dataset.py to reverse the dataset to stream the old data first.
9) python kafka_stream.py
10) View the grouped data streaming in Kafka console using the command "**./kafka-console-consumer.sh --from-beginning --bootstrap-server localhost:9092 --topic topic-name**"
