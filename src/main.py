import json
import random
import time

from generator.invoice import generate_invoice
from generator.logger import logger, metrics_logger
from postgres.loader import load_batch


logger.info(
    "Generator started",
    extra={
        "event": "generator_started",
        "extra_fields": {
            "service": "ecommerce-generator"
        }
    }
)


while True:

    # --------------------------------------
    # تعداد Invoice در Batch
    # --------------------------------------

    number_of_invoices = random.randint(
        1,
        10
    )

    print(
        "\n"
        + "#" * 80
    )

    print(
        f"Generating {number_of_invoices} invoices..."
    )

    print(
        "#" * 80
    )


    # --------------------------------------
    # Generate Batch
    # --------------------------------------

    batch = []

    for invoice_number in range(
        1,
        number_of_invoices + 1
    ):

        invoice = generate_invoice()

        batch.append(invoice)

        # ----------------------------------
        # Invoice Log
        # ----------------------------------

        logger.info(
            "Invoice generated successfully",
            extra={
                "event": "invoice_generated",
                "extra_fields": {
                    "invoice_id": invoice["invoice_id"],
                    "order_id": invoice["order_id"],
                    "customer_id": invoice["customer"]["customer_id"],
                    "items_count": len(invoice["items"]),
                    "total": invoice["pricing"]["total"],
                    "payment_method": invoice["payment"]["method"],
                    "payment_status": invoice["payment"]["status"],
                    "order_status": invoice["order_status"]
                }
            }
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

        print(
            "\n"
            + "-" * 80
        )


        # ----------------------------------
        # فاصله بین فاکتورها
        # ----------------------------------

        time.sleep(
            random.uniform(
                0.2,
                2
            )
        )


    # --------------------------------------
    # Expected PostgreSQL Records
    # --------------------------------------

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


    # --------------------------------------
    # Metrics Log
    # --------------------------------------

    metrics_logger.info(
        "Batch load expected | "
        f"invoices={len(batch)} | "
        f"customers={expected_customers} | "
        f"products={expected_products} | "
        f"orders={expected_orders} | "
        f"order_items={expected_order_items} | "
        f"payments={expected_payments}"
    )


    # --------------------------------------
    # نمایش تعداد مورد انتظار
    # --------------------------------------

    print(
        "\nExpected PostgreSQL records:"
    )

    print(
        f"Customers    : {expected_customers}"
    )

    print(
        f"Products     : {expected_products}"
    )

    print(
        f"Orders       : {expected_orders}"
    )

    print(
        f"Order Items  : {expected_order_items}"
    )

    print(
        f"Payments     : {expected_payments}"
    )


    # --------------------------------------
    # Load Batch → PostgreSQL
    # --------------------------------------

    print(
        "\nLoading batch into PostgreSQL..."
    )

    load_batch(batch)


    # --------------------------------------
    # فاصله تا Batch بعدی
    # --------------------------------------

    wait_time = random.uniform(
        5,
        10
    )

    print(
        f"\nWaiting {wait_time:.2f} seconds..."
    )

    time.sleep(
        wait_time
    )