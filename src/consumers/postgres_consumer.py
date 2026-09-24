from kafka_client.consumer import BaseKafkaConsumer
from writers.postgres_writer import PostgresWriter


class PostgresConsumer:

    def __init__(self):

        self.consumer = BaseKafkaConsumer(
            topic="orders",
            group_id="postgres-writer-v2",
        )

        self.writer = PostgresWriter()

    def run(self):

        print("PostgreSQL Consumer started...")

        try:

            for message in self.consumer.consume():

                event = message.value

                try:

                    self.writer.write(event)

                    self.consumer.commit()

                    print(
                        f"Processed order "
                        f"{event['order_id']} "
                        f"| partition={message.partition} "
                        f"| offset={message.offset}"
                    )

                except Exception as error:

                    print(
                        f"Failed to process "
                        f"{event.get('order_id')}: {error}"
                    )

        except KeyboardInterrupt:

            print("\nPostgreSQL Consumer stopped.")

        finally:

            self.consumer.close()