from kafka import KafkaConsumer
import json


class BaseKafkaConsumer:

    def __init__(
        self,
        topic,
        group_id,
        bootstrap_servers="localhost:9092",
    ):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="latest",
            enable_auto_commit=False,
            key_deserializer=lambda key: (
                key.decode("utf-8") if key else None
            ),
            value_deserializer=lambda value: json.loads(
                value.decode("utf-8")
            ),
        )

    def consume(self):
        return self.consumer

    def commit(self):
        self.consumer.commit()

    def close(self):
        self.consumer.close()