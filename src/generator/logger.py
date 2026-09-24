import json
import logging
import os
from datetime import datetime, timezone


class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "service": "ecommerce-generator",
            "event": getattr(record, "event", "application_event"),
            "message": record.getMessage(),
        }

        # اضافه کردن اطلاعاتی که همراه log ارسال شده
        extra_fields = getattr(record, "extra_fields", {})

        if extra_fields:
            log_data.update(extra_fields)

        return json.dumps(log_data, ensure_ascii=False)


def setup_logger():
    os.makedirs("logs", exist_ok=True)

    logger = logging.getLogger("ecommerce-generator")
    logger.setLevel(logging.INFO)

    # جلوگیری از اضافه شدن Handler در صورت چند بار اجرا شدن setup
    if logger.handlers:
        return logger

    file_handler = logging.FileHandler(
        "logs/generator.log",
        encoding="utf-8"
    )

    file_handler.setFormatter(JSONFormatter())

    logger.addHandler(file_handler)

    return logger


logger = setup_logger()