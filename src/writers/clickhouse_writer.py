from clickhouse.loader import load_invoice
from writers.base import BaseWriter
from logger import get_logger


logger = get_logger("clickhouse-writer")


class ClickHouseWriter(BaseWriter):

    def write(self, event):
        event_id = event.get("event_id")
        order_id = event.get("order_id")
        customer_id = event.get("customer_id")

        logger.info(
            "Preparing event for ClickHouse",
            extra={
                "service": "clickhouse-writer",
                "event": "clickhouse_write_started",
                "event_id": event_id,
                "order_id": order_id,
                "customer_id": customer_id,
            },
        )

        try:
            invoice = {
                "invoice_id": event_id,
                "order_id": event["order_id"],
                "created_at": event["occurred_at"],
                "currency": event["data"]["currency"],
                "customer": event["data"]["customer"],
                "items": event["data"]["items"],
                "pricing": event["data"]["pricing"],
                "payment": event["data"]["payment"],
                "order_status": event["data"]["order_status"],
            }

            load_invoice(invoice)

            logger.info(
                "Event loaded into ClickHouse",
                extra={
                    "service": "clickhouse-writer",
                    "event": "clickhouse_write_completed",
                    "event_id": event_id,
                    "order_id": order_id,
                    "customer_id": customer_id,
                },
            )

        except Exception:
            logger.exception(
                "Failed to write event to ClickHouse",
                extra={
                    "service": "clickhouse-writer",
                    "event": "clickhouse_write_failed",
                    "event_id": event_id,
                    "order_id": order_id,
                    "customer_id": customer_id,
                },
            )

            raise