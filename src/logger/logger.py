import json
import logging
import sys
from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):

    def format(self, record):

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "service"):
            log_data["service"] = record.service

        if hasattr(record, "event"):
            log_data["event"] = record.event

        if hasattr(record, "event_id"):
            log_data["event_id"] = record.event_id

        if hasattr(record, "order_id"):
            log_data["order_id"] = record.order_id

        if hasattr(record, "customer_id"):
            log_data["customer_id"] = record.customer_id

        if hasattr(record, "partition"):
            log_data["partition"] = record.partition

        if hasattr(record, "offset"):
            log_data["offset"] = record.offset

        if hasattr(record, "operation"):
            log_data["operation"] = record.operation

        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms

        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_data,
            ensure_ascii=False
        )


def get_logger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler(sys.stdout)

    handler.setFormatter(JsonFormatter())

    logger.addHandler(handler)

    logger.propagate = False

    return logger