import time


from confluent_kafka import SerializingProducer
from confluent_kafka.serialization import StringSerializer
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.json_schema import JSONSerializer

from data import get_customer_info

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


def delivery_report(err, msg) -> None:
    """Called once for each message produced to indicate delivery result."""
    if err is not None:
        print(f'Message delivery failed: {err}')
    else:
        print(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')

conf = read_config()
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

