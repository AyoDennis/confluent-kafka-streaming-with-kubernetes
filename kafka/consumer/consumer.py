from confluent_kafka import Consumer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
import json
import time
import awswrangler as wr
import boto3


TOPIC = "customer-information"


def read_config() -> dict:
  # reads the client configuration from client.properties
  # and returns it as a key-value map
  config = {}
  # Ensure you run the script from the kafka directory
  # where the config.properties file is located
  with open("config.properties") as fh:
    for line in fh:
      line = line.strip()
      if len(line) != 0 and line[0] != "#":
        parameter, value = line.strip().split('=', 1)
        config[parameter] = value.strip()
  return config


def fetch_schema(topic, conf):
    schema_registry_conf = {
        'url': conf.get("schema_url"),
        'basic.auth.user.info': f'{conf.get("schema_key")}:{conf.get("schema_secret")}'
    }

    # create a Schema Registry client
    schema_registry_client = SchemaRegistryClient(schema_registry_conf)

    # retrieve the json schema string
    schema_response = schema_registry_client.get_latest_version(f'{topic}-value')
    return schema_response.schema.schema_str


def consume(topic, config):
    # sets the consumer group ID and offset
    config["group.id"] = "DLA-1"
    config["auto.offset.reset"] = "earliest"


    # fetch schema first
    schema = fetch_schema(topic, config)
    keys_to_remove = ['schema_url', 'schema_key', 'schema_secret']
    for key in keys_to_remove:
        config.pop(key, None)


    # creates a new consumer instance
    consumer = Consumer(config)
    consumer = DeserializingConsumer({
        **config,
        'key.deserializer': lambda k, c: k.decode("utf-8") if k else None,
        'value.deserializer': JSONDeserializer(schema),
        'enable.auto.commit': False
    })

    # subscribes to the specified topic
    consumer.subscribe([topic])
    batch = []
    BATCH_SIZE = 1000
    FLUSH_INTERVAL = 60  # seconds
    last_flush = time.time()

    try:
        while True:
        # consumer polls the topic and prints any incoming messages
            msg = consumer.poll(1.0)
            if msg is not None and msg.error() is None:
                batch.append(msg.value)
                if len(batch) >= BATCH_SIZE or (time.time() - last_flush) >= FLUSH_INTERVAL:
                    print(f"Batch of {len(batch)} messages received.")
                    filename = f"batch_{int(time.time())}.jsonl"
                    path = f"/tmp/{filename}"
                    with open(path, 'w') as f:
                        for record in batch:
                            f.write(json.dumps(record) + "\n")
                        print(f"Batch written to {filename}")
                
                    try:
                        wr.s3.upload(local_file=path, path=f's3://kafka-kubernetes-project/kafka-consumption/{filename}')
                        consumer.commit()
                        batch.clear()
                        last_flush = time.time()
                    except Exception as e:
                        print(f"Error uploading to S3: {e}")
                elif msg is not None:
                    print(f"Error: {msg.error()}")
            else:
                print("No new messages received.")
    except KeyboardInterrupt:
        pass
    finally:
        # closes the consumer connection
        consumer.close()

if __name__ == "__main__":
    # reads the client configuration
    config = read_config()
    # consumes messages from the specified topic
    consume(TOPIC, config)