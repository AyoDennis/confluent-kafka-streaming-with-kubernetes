import time
import os


from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

from data import get_customer_info

TOPIC = "customer-information"

conf = {
     'bootstrap.servers':os.environ.get("BOOTSTRAP_SERVER"),
     'security.protocol':"SASL_SSL",
     'sasl.mechanisms':"PLAIN",
     'sasl.username':os.environ.get("PRODUCER_SASL_USERNAME"),
     'sasl.password':os.environ.get("PRODUCER_SASL_PASSWORD"),
     'client.id':os.environ.get("CLIENT_ID"),
     'schema_url':os.environ.get("SCHEMA_URL"),
     'schema_key':os.environ.get("SCHEMA_KEY"),
     'schema_secret':os.environ.get("SCHEMA_SECRET"),
     'session.timeout.ms':45000
  }


def delivery_report(err, msg) -> None:
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

# conf = read_config()

schema_registry_conf = {
    'url': conf.get("schema_url"),
    'basic.auth.user.info': f'{conf.get("schema_key")}:{conf.get("schema_secret")}'
}

keys_to_remove = ['schema_url', 'schema_key', 'schema_secret']
for key in keys_to_remove:
    conf.pop(key, None)


print(conf.keys())

# create a Schema Registry client
schema_registry_client = SchemaRegistryClient(schema_registry_conf)

# retrieve the json schema string
schema_response = schema_registry_client.get_latest_version(f'{TOPIC}-value')
schema_str = schema_response.schema.schema_str

# create a JSON serializer using the schema
json_serializer = JSONSerializer(
    schema_str,
    schema_registry_client
)

producer = SerializingProducer({
    **conf,
    'key.serializer': StringSerializer('utf_8'),
    'value.serializer': json_serializer
})



def produce_messages():
    try:
       while True:
            customer_information = get_customer_info()
            # print(customer_information)
            producer.produce(
                topic=TOPIC,
                key=str(customer_information['customer_id']),
                value=customer_information,
                on_delivery=delivery_report
            )
            producer.poll(0)
            time.sleep(5)
    except KeyboardInterrupt:
        print("Producer interrupted by user.")
    finally:
        producer.flush()


if __name__ == "__main__":
    produce_messages()

