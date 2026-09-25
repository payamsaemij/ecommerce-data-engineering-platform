import json

from kafka import KafkaConsumer

from logger import get_logger


logger = get_logger(__name__)
logger = get_logger("kafka-consumer")

class BaseKafkaConsumer:

    def __init__(
        self,
        topic,
        group_id,
        bootstrap_servers="localhost:9092",
    ):

        self.topic = topic
        self.group_id = group_id

        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            auto_offset_reset="earliest",
            enable_auto_commit=False,
            key_deserializer=lambda key: (
                key.decode("utf-8") if key else None
            ),
            value_deserializer=lambda value: json.loads(
                value.decode("utf-8")
            ),
        )

        logger.info(
            "Kafka consumer initialized",
            extra={
                "service": "kafka-consumer",
                "event": "consumer_initialized",
                "topic": topic,
                "group_id": group_id,
                "bootstrap_servers": bootstrap_servers,
            },
        )

    def consume(self):

        logger.info(
            "Kafka consumer started consuming",
            extra={
                "service": "kafka-consumer",
                "event": "consume_started",
                "topic": self.topic,
                "group_id": self.group_id,
            },
        )

        return self.consumer

    def commit(self):

        try:

            self.consumer.commit()

            logger.info(
                "Kafka offset committed",
                extra={
                    "service": "kafka-consumer",
                    "event": "offset_committed",
                    "topic": self.topic,
                    "group_id": self.group_id,
                },
            )

        except Exception:

            logger.exception(
                "Failed to commit Kafka offset",
                extra={
                    "service": "kafka-consumer",
                    "event": "offset_commit_failed",
                    "topic": self.topic,
                    "group_id": self.group_id,
                },
            )

            raise

    def close(self):

        logger.info(
            "Closing Kafka consumer",
            extra={
                "service": "kafka-consumer",
                "event": "consumer_close_started",
                "topic": self.topic,
                "group_id": self.group_id,
            },
        )

        self.consumer.close()

        logger.info(
            "Kafka consumer closed",
            extra={
                "service": "kafka-consumer",
                "event": "consumer_closed",
                "topic": self.topic,
                "group_id": self.group_id,
            },
        )

