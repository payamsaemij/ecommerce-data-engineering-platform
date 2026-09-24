import json

from kafka import KafkaProducer


class OrderProducer:

    def __init__(self, bootstrap_servers="localhost:9092"):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            key_serializer=lambda key: key.encode("utf-8"),
            value_serializer=lambda value: json.dumps(
                value,
                ensure_ascii=False
            ).encode("utf-8"),
        )

    def send_order(self, event):
        customer_id = event["customer_id"]

        future = self.producer.send(
            "orders",
            key=customer_id,
            value=event,
        )

        return future

    def flush(self):
        self.producer.flush()

    def close(self):
        self.producer.close()