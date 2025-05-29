import json
import os

from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

conf = {
    'bootstrap.servers': '<ccloud bootstrap servers>',
    'sasl.mechanism': 'PLAIN',
    'security.protocol': 'SASL_SSL',
    'sasl.username': '<ccloud key>',
    'sasl.password': '<ccloud secret>',
    'group.id': 'id',
    'auto.offset.reset': 'earliest',
    'error_cb': error_cb,
}


def consume_messages():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        auto_offset_reset='earliest',
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )

    print("kafka consumer started. Waiting for messages...\n")

    try:
        for msg in consumer:
            user = msg.value
            print(f"Customer info: {user}")
    except KeyboardInterrupt:
        print("\nstopping consumer...")
    finally:
        consumer.close()
        print("consume completed.")


if __name__ == "__main__":
    consume_messages()
