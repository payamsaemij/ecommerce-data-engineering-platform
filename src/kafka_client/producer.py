import json

from kafka import KafkaProducer

from logger import get_logger


logger = get_logger(__name__)


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

        logger.info(
            "Kafka producer initialized",
            extra={
                "service": "kafka-producer",
                "event": "producer_initialized",
                "bootstrap_servers": bootstrap_servers,
            },
        )

    def send_order(self, event):

        customer_id = event["customer_id"]

        try:

            future = self.producer.send(
                "orders",
                key=customer_id,
                value=event,
            )

            # Wait for Kafka acknowledgement.
            metadata = future.get(timeout=10)

            logger.info(
                "Order event published to Kafka",
                extra={
                    "service": "kafka-producer",
                    "event": "kafka_publish_success",
                    "event_id": event["event_id"],
                    "order_id": event["order_id"],
                    "customer_id": customer_id,
                    "topic": metadata.topic,
                    "partition": metadata.partition,
                    "offset": metadata.offset,
                },
            )

            return metadata

        except Exception:

            logger.exception(
                "Failed to publish order event to Kafka",
                extra={
                    "service": "kafka-producer",
                    "event": "kafka_publish_failed",
                    "event_id": event.get("event_id"),
                    "order_id": event.get("order_id"),
                    "customer_id": customer_id,
                },
            )

            raise

    def flush(self):

        logger.info(
            "Flushing Kafka producer",
            extra={
                "service": "kafka-producer",
                "event": "producer_flush_started",
            },
        )

        self.producer.flush()

        logger.info(
            "Kafka producer flushed successfully",
            extra={
                "service": "kafka-producer",
                "event": "producer_flush_completed",
            },
        )

    def close(self):

        logger.info(
            "Closing Kafka producer",
            extra={
                "service": "kafka-producer",
                "event": "producer_close_started",
            },
        )

        self.producer.close()

        logger.info(
            "Kafka producer closed",
            extra={
                "service": "kafka-producer",
                "event": "producer_closed",
            },
        )
