from confluent_kafka import Consumer
from confluent_kafka.schema_registry.json_schema import JSONDeserializer
from confluent_kafka import DeserializingConsumer
from confluent_kafka.schema_registry import SchemaRegistryClient
import json
import time
import os
import awswrangler as wr
import boto3


TOPIC = "customer-information"


conf = {
     'bootstrap.servers':os.environ.get("BOOTSTRAP_SERVER"),
     'security.protocol':"SASL_SSL",
     'sasl.mechanisms':"PLAIN",
     'sasl.username':os.environ.get("CONSUMER_SASL_USERNAME"),
     'sasl.password':os.environ.get("CONSUMER_SASL_PASSWORD"),
     'client.id':os.environ.get("CONSUMER_CLIENT_ID"),
     'schema_url':os.environ.get("SCHEMA_URL"),
     'schema_key':os.environ.get("SCHEMA_KEY"),
     'schema_secret':os.environ.get("SCHEMA_SECRET"),
     'session.timeout.ms':45000
  }


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


def aws_session():
    """
    Instantiates aws session"""
    session = boto3.Session(
        aws_access_key_id=os.environ.get('AWS_ACCESS_KEY'),
        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
        region_name=os.environ.get("REGION"))
    return session



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
                batch.append(msg.value())
                if len(batch) >= BATCH_SIZE or (time.time() - last_flush) >= FLUSH_INTERVAL:
                    print(f"Batch of {len(batch)} messages received.")
                    filename = f"batch_{int(time.time())}.jsonl"
                    path = f"/tmp/{filename}"
                    with open(path, 'w') as f:
                        for record in batch:
                            f.write(json.dumps(record) + "\n")
                        print(f"Batch written to {filename}")
                
                    try:
                        wr.s3.upload(local_file=path, boto3_session=aws_session(), path=f's3://kafka-kubernetes-project/kafka-consumption/{filename}')
                        consumer.commit()
                        batch.clear()
                        last_flush = time.time()
                    except Exception as e:
                        print(f"Error uploading to S3: {e}")
                elif msg is not None:
                     print("Message consumed.")
            else:
                print("No new messages received.")
    except KeyboardInterrupt:
        pass
    finally:
        # closes the consumer connection
        consumer.close()

if __name__ == "__main__":
    # reads the client configuration
    config = conf
    # consumes messages from the specified topic
    consume(TOPIC, config)