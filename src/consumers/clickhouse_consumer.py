from kafka_client.consumer import BaseKafkaConsumer
from writers.clickhouse_writer import ClickHouseWriter
from logger import get_logger


logger = get_logger("clickhouse-consumer")


class ClickHouseConsumer:

    def __init__(
        self,
        topic="orders",
        group_id="clickhouse-writer",
        bootstrap_servers="localhost:9092",
    ):
        self.consumer = BaseKafkaConsumer(
            topic=topic,
            group_id=group_id,
            bootstrap_servers=bootstrap_servers,
        )

        self.writer = ClickHouseWriter()

    def run(self):

        logger.info(
            "ClickHouse consumer started",
            extra={
                "service": "clickhouse-consumer",
                "event": "consumer_started",
                "topic": "orders",
                "group_id": "clickhouse-writer",
            },
        )

        try:

            for message in self.consumer.consume():

                event = message.value

                event_id = event.get("event_id")
                order_id = event.get("order_id")
                customer_id = event.get("customer_id")

                logger.info(
                    "Kafka event received",
                    extra={
                        "service": "clickhouse-consumer",
                        "event": "kafka_event_received",
                        "event_id": event_id,
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "partition": message.partition,
                        "offset": message.offset,
                    },
                )

                try:

                    self.writer.write(event)

                    self.consumer.commit()

                    logger.info(
                        "Kafka event committed",
                        extra={
                            "service": "clickhouse-consumer",
                            "event": "kafka_offset_committed",
                            "event_id": event_id,
                            "order_id": order_id,
                            "partition": message.partition,
                            "offset": message.offset,
                        },
                    )

                except Exception:

                    logger.exception(
                        "Failed to process Kafka event",
                        extra={
                            "service": "clickhouse-consumer",
                            "event": "kafka_event_processing_failed",
                            "event_id": event_id,
                            "order_id": order_id,
                            "customer_id": customer_id,
                            "partition": message.partition,
                            "offset": message.offset,
                        },
                    )

                    # Offset is intentionally NOT committed.
                    # Kafka will redeliver the event.

        except KeyboardInterrupt:

            logger.info(
                "ClickHouse consumer stopped",
                extra={
                    "service": "clickhouse-consumer",
                    "event": "consumer_stopped",
                },
            )

        finally:
            self.consumer.close()

            logger.info(
                "ClickHouse consumer closed",
                extra={
                    "service": "clickhouse-consumer",
                    "event": "consumer_closed",
                },
            )