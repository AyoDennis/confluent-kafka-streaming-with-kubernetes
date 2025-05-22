import json
import time
import os

from data import get_customer_info
from kafka import KafkaProducer
from dotenv import load_dotenv

load_dotenv()


conf = {
'bootstrap_servers': os.getenv("BOOTSTRAP_SERVER"),
'sasl.mechanism': 'PLAIN',
'security_protocol': 'SSL',
'sasl.username': os.getenv("SASL_USERNAME"), # You put API Key here
'sasl.opassword': os.getenv("SASL_PASSWORD") # You put API Secret here
}


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
