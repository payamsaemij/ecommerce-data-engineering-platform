from kafka_client.consumer import BaseKafkaConsumer
from writers.postgres_writer import PostgresWriter
from logger import get_logger


logger = get_logger(__name__)
logger = get_logger("postgres-consumer")

class PostgresConsumer:

    def __init__(self):

        self.consumer = BaseKafkaConsumer(
            topic="orders",
            group_id="postgres-writer-v2",
        )

        self.writer = PostgresWriter()

        logger.info(
            "PostgreSQL consumer initialized",
            extra={
                "service": "postgres-consumer",
                "event": "consumer_initialized",
                "topic": "orders",
                "group_id": "postgres-writer-v2",
            },
        )

    def run(self):

        logger.info(
            "PostgreSQL consumer started",
            extra={
                "service": "postgres-consumer",
                "event": "consumer_started",
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
                        "service": "postgres-consumer",
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

                    logger.info(
                        "Event written to PostgreSQL",
                        extra={
                            "service": "postgres-consumer",
                            "event": "postgres_write_success",
                            "event_id": event_id,
                            "order_id": order_id,
                            "customer_id": customer_id,
                            "partition": message.partition,
                            "offset": message.offset,
                        },
                    )

                    self.consumer.commit()

                    logger.info(
                        "Kafka event processed successfully",
                        extra={
                            "service": "postgres-consumer",
                            "event": "event_processed",
                            "event_id": event_id,
                            "order_id": order_id,
                            "customer_id": customer_id,
                            "partition": message.partition,
                            "offset": message.offset,
                        },
                    )

                except Exception:

                    logger.exception(
                        "Failed to process Kafka event",
                        extra={
                            "service": "postgres-consumer",
                            "event": "event_processing_failed",
                            "event_id": event_id,
                            "order_id": order_id,
                            "customer_id": customer_id,
                            "partition": message.partition,
                            "offset": message.offset,
                        },
                    )

        except KeyboardInterrupt:

            logger.info(
                "PostgreSQL consumer stopped by user",
                extra={
                    "service": "postgres-consumer",
                    "event": "consumer_stopped",
                },
            )

        except Exception:

            logger.exception(
                "PostgreSQL consumer crashed",
                extra={
                    "service": "postgres-consumer",
                    "event": "consumer_crashed",
                },
            )

            raise

        finally:

            self.consumer.close()

            logger.info(
                "PostgreSQL consumer closed",
                extra={
                    "service": "postgres-consumer",
                    "event": "consumer_closed",
                },
            )
