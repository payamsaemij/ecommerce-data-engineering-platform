from postgres.connection import get_connection
from logger import get_logger


logger = get_logger(__name__)
logger = get_logger("postgres-loader")

def load_batch(invoices):

    logger.info(
        "Starting PostgreSQL batch load",
        extra={
            "service": "postgres-loader",
            "event": "batch_load_started",
            "batch_size": len(invoices),
        },
    )

    try:

        with get_connection() as conn:

            with conn.transaction():

                with conn.cursor() as cur:

                    for invoice in invoices:

                        event_id = invoice["invoice_id"]
                        order_id = invoice["order_id"]
                        customer = invoice["customer"]
                        customer_id = customer["customer_id"]

                        # --------------------------------
                        # Customer
                        # --------------------------------

                        cur.execute(
                            """
                            INSERT INTO ecommerce.customers (
                                customer_id,
                                first_name,
                                last_name,
                                email,
                                city,
                                postcode,
                                shipping_address,
                                created_at
                            )
                            VALUES (
                                %s, %s, %s, %s,
                                %s, %s, %s, %s
                            )
                            ON CONFLICT (customer_id)
                            DO NOTHING
                            """,
                            (
                                customer_id,
                                customer["first_name"],
                                customer["last_name"],
                                customer["email"],
                                customer["shipping_address"]["city"],
                                customer["shipping_address"]["postcode"],
                                customer["shipping_address"]["country"],
                                invoice["created_at"],
                            ),
                        )

                        if cur.rowcount == 1:

                            logger.info(
                                "Customer inserted",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "customer_inserted",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                },
                            )

                        else:

                            logger.warning(
                                "Customer insert skipped because of conflict",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "customer_insert_conflict",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                },
                            )

                        # --------------------------------
                        # Products
                        # --------------------------------

                        for item in invoice["items"]:

                            product_id = item["product_id"]

                            cur.execute(
                                """
                                INSERT INTO ecommerce.products (
                                    product_id,
                                    name,
                                    category,
                                    price,
                                    created_at
                                )
                                VALUES (
                                    %s, %s, %s, %s, %s
                                )
                                ON CONFLICT (product_id)
                                DO UPDATE SET
                                    name = EXCLUDED.name,
                                    category = EXCLUDED.category,
                                    price = EXCLUDED.price
                                """,
                                (
                                    product_id,
                                    item["product_name"],
                                    item["category"],
                                    item["unit_price"],
                                    invoice["created_at"],
                                ),
                            )

                            logger.info(
                                "Product inserted or updated",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "product_upserted",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                    "product_id": product_id,
                                },
                            )

                        # --------------------------------
                        # Order
                        # --------------------------------

                        pricing = invoice["pricing"]

                        cur.execute(
                            """
                            INSERT INTO ecommerce.orders (
                                order_id,
                                customer_id,
                                created_at,
                                currency,
                                subtotal,
                                item_discount,
                                order_discount,
                                shipping_cost,
                                tax,
                                total,
                                order_status
                            )
                            VALUES (
                                %s, %s, %s, %s,
                                %s, %s, %s, %s,
                                %s, %s, %s
                            )
                            ON CONFLICT (order_id)
                            DO NOTHING
                            """,
                            (
                                order_id,
                                customer_id,
                                invoice["created_at"],
                                invoice["currency"],
                                pricing["subtotal"],
                                sum(
                                    item["discount_amount"]
                                    for item in invoice["items"]
                                ),
                                pricing["order_discount_amount"],
                                pricing["shipping"],
                                pricing["tax"],
                                pricing["total"],
                                invoice["order_status"],
                            ),
                        )

                        if cur.rowcount == 1:

                            logger.info(
                                "Order inserted",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "order_inserted",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                },
                            )

                        else:

                            logger.warning(
                                "Order insert skipped because of conflict",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "order_insert_conflict",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                },
                            )

                        # --------------------------------
                        # Order Items
                        # --------------------------------

                        for item in invoice["items"]:

                            product_id = item["product_id"]

                            gross_price = (
                                item["quantity"]
                                * item["unit_price"]
                            )

                            cur.execute(
                                """
                                INSERT INTO ecommerce.order_items (
                                    order_id,
                                    product_id,
                                    quantity,
                                    unit_price,
                                    discount_percent,
                                    gross_price,
                                    discount_amount,
                                    item_total
                                )
                                VALUES (
                                    %s, %s, %s, %s,
                                    %s, %s, %s, %s
                                )
                                """,
                                (
                                    order_id,
                                    product_id,
                                    item["quantity"],
                                    item["unit_price"],
                                    item["discount_percent"],
                                    gross_price,
                                    item["discount_amount"],
                                    item["total"],
                                ),
                            )

                            logger.info(
                                "Order item inserted",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "order_item_inserted",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                    "product_id": product_id,
                                },
                            )

                        # --------------------------------
                        # Payment
                        # --------------------------------

                        payment = invoice["payment"]

                        paid_at = None

                        if payment["status"] == "completed":
                            paid_at = invoice["created_at"]

                        cur.execute(
                            """
                            INSERT INTO ecommerce.payments (
                                order_id,
                                payment_method,
                                payment_status,
                                paid_at
                            )
                            VALUES (
                                %s, %s, %s, %s
                            )
                            ON CONFLICT (order_id)
                            DO NOTHING
                            """,
                            (
                                order_id,
                                payment["method"],
                                payment["status"],
                                paid_at,
                            ),
                        )

                        if cur.rowcount == 1:

                            logger.info(
                                "Payment inserted",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "payment_inserted",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                },
                            )

                        else:

                            logger.warning(
                                "Payment insert skipped because of conflict",
                                extra={
                                    "service": "postgres-loader",
                                    "event": "payment_insert_conflict",
                                    "event_id": event_id,
                                    "order_id": order_id,
                                    "customer_id": customer_id,
                                },
                            )

        logger.info(
            "PostgreSQL batch load completed",
            extra={
                "service": "postgres-loader",
                "event": "batch_load_completed",
                "batch_size": len(invoices),
            },
        )

        print(
            f"Batch of {len(invoices)} invoices "
            f"inserted successfully."
        )

    except Exception:

        logger.exception(
            "PostgreSQL batch load failed",
            extra={
                "service": "postgres-loader",
                "event": "batch_load_failed",
                "batch_size": len(invoices),
            },
        )

        raise
