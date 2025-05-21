import json
import time

from data import get_customer_info
from kafka import KafkaProducer

KAFKA_TOPIC = 'customer_information'
KAFKA_BOOTSTRAP = 'localhost:9092'


def json_serializer(data):
    return json.dumps(data).encode("utf-8")


def produce_messages():
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP,
                             value_serializer=json_serializer)
    customer_information = get_customer_info()
    # print(customer_information)
    producer.send(KAFKA_TOPIC, customer_information)


if __name__ == "__main__":
    while True:
        produce_messages()
        time.sleep(5)
