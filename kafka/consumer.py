import json
import os

from kafka import KafkaConsumer
from dotenv import load_dotenv

load_dotenv()

conf = {
'bootstrap_servers': os.getenv("BOOTSTRAP_SERVER"),
'sasl.mechanism': 'PLAIN',
'security_protocol': 'SSL',
'sasl.username': os.getenv("SASL_USERNAME"), # You put API Key here
'sasl.opassword': os.getenv("SASL_PASSWORD") # You put API Secret here
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
