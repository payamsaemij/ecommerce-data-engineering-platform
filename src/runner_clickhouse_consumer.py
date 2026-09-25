from consumers.clickhouse_consumer import ClickHouseConsumer
from logger import get_logger


logger = get_logger("clickhouse-consumer-runner")


def main():
    logger.info(
        "Starting ClickHouse consumer runner",
        extra={
            "service": "clickhouse-consumer-runner",
            "event": "runner_started",
        },
    )

    consumer = ClickHouseConsumer(
        topic="orders",
        group_id="clickhouse-writer",
        bootstrap_servers="localhost:9092",
    )

    try:
        consumer.run()

    except Exception:
        logger.exception(
            "ClickHouse consumer runner failed",
            extra={
                "service": "clickhouse-consumer-runner",
                "event": "runner_failed",
            },
        )
        raise

    finally:
        logger.info(
            "ClickHouse consumer runner stopped",
            extra={
                "service": "clickhouse-consumer-runner",
                "event": "runner_stopped",
            },
        )


if __name__ == "__main__":
    main()