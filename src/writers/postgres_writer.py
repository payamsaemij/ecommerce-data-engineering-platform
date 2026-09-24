from postgres.loader import load_batch
from writers.base import BaseWriter


class PostgresWriter(BaseWriter):

    def write(self, event):

        invoice = {
            "invoice_id": event["event_id"],
            "order_id": event["order_id"],
            "created_at": event["occurred_at"],
            "currency": event["data"]["currency"],
            "customer": event["data"]["customer"],
            "items": event["data"]["items"],
            "pricing": event["data"]["pricing"],
            "payment": event["data"]["payment"],
            "order_status": event["data"]["order_status"],
        }

        load_batch([invoice])