import json

from kafka import KafkaConsumer

KAFKA_TOPIC = 'customer_information'
KAFKA_BOOTSTRAP = 'localhost:9092'
KAFKA_GROUP_ID = 'customer-info'


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
