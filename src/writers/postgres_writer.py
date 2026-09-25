from postgres.loader import load_batch
from writers.base import BaseWriter
from logger import get_logger


logger = get_logger(__name__)
logger = get_logger("postgres-writer")

class PostgresWriter(BaseWriter):

    def write(self, event):

        event_id = event.get("event_id")
        order_id = event.get("order_id")
        customer_id = event.get("customer_id")

        logger.info(
            "Preparing event for PostgreSQL",
            extra={
                "service": "postgres-writer",
                "event": "postgres_write_started",
                "event_id": event_id,
                "order_id": order_id,
                "customer_id": customer_id,
            },
        )

        try:

            invoice = {
                "invoice_id": event_id,
                "order_id": order_id,
                "created_at": event["occurred_at"],
                "currency": event["data"]["currency"],
                "customer": event["data"]["customer"],
                "items": event["data"]["items"],
                "pricing": event["data"]["pricing"],
                "payment": event["data"]["payment"],
                "order_status": event["data"]["order_status"],
            }

            load_batch([invoice])

            logger.info(
                "Event loaded into PostgreSQL",
                extra={
                    "service": "postgres-writer",
                    "event": "postgres_write_completed",
                    "event_id": event_id,
                    "order_id": order_id,
                    "customer_id": customer_id,
                },
            )

        except Exception:

            logger.exception(
                "Failed to write event to PostgreSQL",
                extra={
                    "service": "postgres-writer",
                    "event": "postgres_write_failed",
                    "event_id": event_id,
                    "order_id": order_id,
                    "customer_id": customer_id,
                },
            )

            raise
