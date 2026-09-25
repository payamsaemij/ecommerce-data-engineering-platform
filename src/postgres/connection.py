import psycopg

from logger import get_logger


logger = get_logger(__name__)


DATABASE_URL = (
    "postgresql://ecommerce_user:123456"
    "@localhost:5432/ecommerce_db"
)


def get_connection():

    try:

        conn = psycopg.connect(DATABASE_URL)

        logger.info(
            "PostgreSQL connection established",
            extra={
                "service": "postgres",
                "event": "database_connection_established",
                "database": "ecommerce_db",
                "host": "localhost",
                "port": 5432,
            },
        )

        return conn

    except Exception:

        logger.exception(
            "Failed to establish PostgreSQL connection",
            extra={
                "service": "postgres",
                "event": "database_connection_failed",
                "database": "ecommerce_db",
                "host": "localhost",
                "port": 5432,
            },
        )

        raise
