import json
import random
import time

from generator.invoice import generate_invoice
from kafka_client.events import create_order_event
from kafka_client.producer import OrderProducer
from logger import get_logger


MAX_ORDERS = 200
total_orders = 0

logger = get_logger(__name__)
logger = get_logger("generator")


logger.info(
    "Generator started",
    extra={
        "service": "ecommerce-generator",
        "event": "generator_started",
    },
)

producer = OrderProducer()

try:

    while total_orders < MAX_ORDERS:

        remaining_orders = MAX_ORDERS - total_orders

        number_of_invoices = min(
            random.randint(1, 10),
            remaining_orders
        )

        logger.info(
            "Generating order batch",
            extra={
                "service": "ecommerce-generator",
                "event": "batch_generation_started",
                "batch_size": number_of_invoices,
                "total_orders": total_orders,
                "remaining_orders": remaining_orders,
            },
        )

        print("\n" + "#" * 80)
        print(f"Generating {number_of_invoices} invoices...")
        print(f"Progress: {total_orders}/{MAX_ORDERS}")
        print("#" * 80)

        batch = []

        for invoice_number in range(1, number_of_invoices + 1):

            invoice = generate_invoice()
            batch.append(invoice)

            event = create_order_event(invoice)

            logger.info(
                "Invoice generated successfully",
                extra={
                    "service": "ecommerce-generator",
                    "event": "invoice_generated",
                    "event_id": event["event_id"],
                    "order_id": invoice["order_id"],
                    "customer_id": invoice["customer"]["customer_id"],
                },
            )

            print(
                f"\nInvoice {invoice_number}/{number_of_invoices}"
            )

            print(
                json.dumps(
                    invoice,
                    indent=2,
                    ensure_ascii=False
                )
            )

            print("\n" + "-" * 80)

            producer.send_order(event)

            

        total_orders += len(batch)

        expected_customers = len(batch)
        expected_orders = len(batch)
        expected_payments = len(batch)

        expected_order_items = sum(
            len(invoice["items"])
            for invoice in batch
        )

        expected_products = len({
            item["product_id"]
            for invoice in batch
            for item in invoice["items"]
        })

        logger.info(
            "Batch published to Kafka",
            extra={
                "service": "ecommerce-generator",
                "event": "batch_published",
                "orders": expected_orders,
                "customers": expected_customers,
                "products": expected_products,
                "order_items": expected_order_items,
                "payments": expected_payments,
                "total_orders": total_orders,
                "max_orders": MAX_ORDERS,
            },
        )

        print("\nExpected Kafka events:")
        print(f"Customers    : {expected_customers}")
        print(f"Products     : {expected_products}")
        print(f"Orders       : {expected_orders}")
        print(f"Order Items  : {expected_order_items}")
        print(f"Payments     : {expected_payments}")

        producer.flush()

        print(
            f"\nBatch of {len(batch)} invoices "
            "published to Kafka successfully."
        )

        print(
            f"Total orders published: "
            f"{total_orders}/{MAX_ORDERS}"
        )

        if total_orders >= MAX_ORDERS:
            break


finally:

    producer.close()

    logger.info(
        "Generator stopped",
        extra={
            "service": "ecommerce-generator",
            "event": "generator_stopped",
            "total_orders": total_orders,
            "max_orders": MAX_ORDERS,
        },
    )

    print(
        f"\nGenerator stopped. "
        f"Total orders generated: {total_orders}"
    )

