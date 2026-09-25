import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from logging.handlers import RotatingFileHandler


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class JsonFormatter(logging.Formatter):

    STANDARD_FIELDS = {
        "name",
        "msg",
        "args",
        "levelname",
        "levelno",
        "pathname",
        "filename",
        "module",
        "exc_info",
        "exc_text",
        "stack_info",
        "lineno",
        "funcName",
        "created",
        "msecs",
        "relativeCreated",
        "thread",
        "threadName",
        "processName",
        "process",
        "message",
    }

    def format(self, record):

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add structured fields from `extra`
        for key, value in record.__dict__.items():

            if key not in self.STANDARD_FIELDS:
                log_data[key] = value

        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_data,
            ensure_ascii=False
        )


def get_logger(service):

    logger = logging.getLogger(service)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    logger.propagate = False

    formatter = JsonFormatter()

    # -------------------------
    # Console
    # -------------------------

    console_handler = logging.StreamHandler(sys.stdout)

    console_handler.setFormatter(formatter)

    # -------------------------
    # File
    # -------------------------

    file_path = LOG_DIR / f"{service}.log"

    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )

    file_handler.setFormatter(formatter)

    # -------------------------
    # Handlers
    # -------------------------

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger