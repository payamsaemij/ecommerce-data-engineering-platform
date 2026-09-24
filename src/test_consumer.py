from kafka_client.consumer import OrderConsumer


consumer = OrderConsumer()

print("PostgreSQL Consumer started...")

try:

    for message in consumer.consume():

        event = message.value

        print("\n" + "=" * 80)
        print("Event received")
        print(f"Topic     : {message.topic}")
        print(f"Partition : {message.partition}")
        print(f"Offset    : {message.offset}")
        print(f"Order ID  : {event['order_id']}")
        print(f"Customer  : {event['customer_id']}")
        print("=" * 80)

except KeyboardInterrupt:

    print("\nConsumer stopped.")

finally:

    consumer.close()