import clickhouse_connect

from logger import get_logger


logger = get_logger("clickhouse-loader")


CLICKHOUSE_HOST = "localhost"
CLICKHOUSE_PORT = 8123
CLICKHOUSE_USERNAME = "ecommerce_user"
CLICKHOUSE_PASSWORD = "123456"
CLICKHOUSE_DATABASE = "ecommerce"


def get_client():

    try:
        client = clickhouse_connect.get_client(
            host=CLICKHOUSE_HOST,
            port=CLICKHOUSE_PORT,
            username=CLICKHOUSE_USERNAME,
            password=CLICKHOUSE_PASSWORD,
            database=CLICKHOUSE_DATABASE,
        )

        logger.info(
            "ClickHouse connection established",
            extra={
                "service": "clickhouse-loader",
                "event": "database_connection_established",
                "database": CLICKHOUSE_DATABASE,
                "host": CLICKHOUSE_HOST,
                "port": CLICKHOUSE_PORT,
            },
        )

        return client

    except Exception:

        logger.exception(
            "Failed to establish ClickHouse connection",
            extra={
                "service": "clickhouse-loader",
                "event": "database_connection_failed",
                "database": CLICKHOUSE_DATABASE,
                "host": CLICKHOUSE_HOST,
                "port": CLICKHOUSE_PORT,
            },
        )

        raise