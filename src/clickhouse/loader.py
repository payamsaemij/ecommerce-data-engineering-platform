from datetime import datetime
from uuid import uuid4

from clickhouse.connection import get_client
from logger import get_logger


logger = get_logger("clickhouse-loader")


def load_invoice(invoice):

    client = get_client()

    try:
        customer = invoice["customer"]
        pricing = invoice["pricing"]
        payment = invoice["payment"]

        created_at = datetime.fromisoformat(
            invoice["created_at"].replace("Z", "+00:00")
        ).replace(tzinfo=None)

        customer_id = customer["customer_id"]
        order_id = invoice["order_id"]

        # --------------------------------------------------
        # 0. Idempotency Check
        # --------------------------------------------------

        existing_order = client.query(
            """
            SELECT 1
            FROM fact_orders
            WHERE order_id = {order_id:String}
            LIMIT 1
            """,
            parameters={
                "order_id": order_id,
            },
        ).result_rows

        if existing_order:

            logger.info(
                "Order already exists in ClickHouse",
                extra={
                    "service": "clickhouse-loader",
                    "event": "clickhouse_load_skipped",
                    "invoice_id": invoice["invoice_id"],
                    "order_id": order_id,
                    "customer_id": customer_id,
                },
            )

            return

        # --------------------------------------------------
        # Load Started
        # --------------------------------------------------

        logger.info(
            "Loading invoice into ClickHouse",
            extra={
                "service": "clickhouse-loader",
                "event": "clickhouse_load_started",
                "invoice_id": invoice["invoice_id"],
                "order_id": order_id,
                "customer_id": customer_id,
            },
        )

        # --------------------------------------------------
        # 1. Customer Dimension
        # --------------------------------------------------

        existing_customer = client.query(
            """
            SELECT customer_key
            FROM dim_customer
            WHERE customer_id = {customer_id:String}
            LIMIT 1
            """,
            parameters={
                "customer_id": customer_id,
            },
        ).result_rows

        if existing_customer:

            customer_key = existing_customer[0][0]

        else:

            customer_key = client.query(
                """
                SELECT coalesce(max(customer_key), 0) + 1
                FROM dim_customer
                """
            ).result_rows[0][0]

            client.insert(
                "dim_customer",
                [[
                    customer_key,
                    customer["customer_id"],
                    customer["first_name"],
                    customer["last_name"],
                    customer["email"],
                    customer["shipping_address"]["city"],
                    customer["shipping_address"]["postcode"],
                    customer["shipping_address"]["country"],
                    created_at,
                ]],
                column_names=[
                    "customer_key",
                    "customer_id",
                    "first_name",
                    "last_name",
                    "email",
                    "city",
                    "postcode",
                    "country",
                    "created_at",
                ],
            )

        # --------------------------------------------------
        # 2. Payment Dimension
        # --------------------------------------------------

        existing_payment = client.query(
            """
            SELECT payment_key
            FROM dim_payment
            WHERE payment_method = {method:String}
              AND payment_status = {status:String}
            LIMIT 1
            """,
            parameters={
                "method": payment["method"],
                "status": payment["status"],
            },
        ).result_rows

        if existing_payment:

            payment_key = existing_payment[0][0]

        else:

            payment_key = client.query(
                """
                SELECT coalesce(max(payment_key), 0) + 1
                FROM dim_payment
                """
            ).result_rows[0][0]

            client.insert(
                "dim_payment",
                [[
                    payment_key,
                    payment["method"],
                    payment["status"],
                ]],
                column_names=[
                    "payment_key",
                    "payment_method",
                    "payment_status",
                ],
            )

        # --------------------------------------------------
        # 3. Date Dimension
        # --------------------------------------------------

        existing_date = client.query(
            """
            SELECT date_key
            FROM dim_date
            WHERE full_date = toDate({created_at:DateTime64(3)})
            LIMIT 1
            """,
            parameters={
                "created_at": created_at,
            },
        ).result_rows

        if existing_date:

            date_key = existing_date[0][0]

        else:

            date_key = client.query(
                """
                SELECT toYYYYMMDD(
                    toDate({created_at:DateTime64(3)})
                )
                """,
                parameters={
                    "created_at": created_at,
                },
            ).result_rows[0][0]

            client.insert(
                "dim_date",
                [[
                    date_key,
                    created_at.date(),
                    created_at.year,
                    ((created_at.month - 1) // 3) + 1,
                    created_at.month,
                    created_at.strftime("%B"),
                    created_at.isocalendar().week,
                    created_at.day,
                    created_at.isoweekday(),
                    int(created_at.weekday() >= 5),
                ]],
                column_names=[
                    "date_key",
                    "full_date",
                    "year",
                    "quarter",
                    "month",
                    "month_name",
                    "week",
                    "day",
                    "day_of_week",
                    "is_weekend",
                ],
            )

        # --------------------------------------------------
        # 4. Product Dimension
        # --------------------------------------------------

        product_keys = {}

        for item in invoice["items"]:

            product_id = item["product_id"]

            existing_product = client.query(
                """
                SELECT product_key
                FROM dim_product
                WHERE product_id = {product_id:String}
                LIMIT 1
                """,
                parameters={
                    "product_id": product_id,
                },
            ).result_rows

            if existing_product:

                product_key = existing_product[0][0]

            else:

                product_key = client.query(
                    """
                    SELECT coalesce(max(product_key), 0) + 1
                    FROM dim_product
                    """
                ).result_rows[0][0]

                client.insert(
                    "dim_product",
                    [[
                        product_key,
                        product_id,
                        item["product_name"],
                        item["category"],
                        item.get("brand", ""),
                    ]],
                    column_names=[
                        "product_key",
                        "product_id",
                        "product_name",
                        "category",
                        "brand",
                    ],
                )

            product_keys[product_id] = product_key

        # --------------------------------------------------
        # 5. Order Fact
        # --------------------------------------------------

        order_key = client.query(
            """
            SELECT coalesce(max(order_key), 0) + 1
            FROM fact_orders
            """
        ).result_rows[0][0]

        client.insert(
            "fact_orders",
            [[
                order_key,
                order_id,
                date_key,
                customer_key,
                payment_key,
                pricing["subtotal"],
                pricing["order_discount_amount"],
                pricing["shipping"],
                pricing["tax"],
                pricing["total"],
                invoice["currency"],
                invoice["order_status"],
                created_at,
            ]],
            column_names=[
                "order_key",
                "order_id",
                "date_key",
                "customer_key",
                "payment_key",
                "subtotal",
                "order_discount_amount",
                "shipping_cost",
                "tax",
                "total",
                "currency",
                "order_status",
                "created_at",
            ],
        )

        # --------------------------------------------------
        # 6. Order Item Fact
        # --------------------------------------------------

        fact_rows = []

        next_order_item_key = client.query(
            """
            SELECT coalesce(max(order_item_key), 0) + 1
            FROM fact_order_items
            """
        ).result_rows[0][0]

        for item in invoice["items"]:

            gross_price = round(
                item["quantity"] * item["unit_price"],
                2,
            )

            fact_rows.append([
                next_order_item_key,
                str(uuid4()),
                order_id,
                date_key,
                customer_key,
                product_keys[item["product_id"]],
                payment_key,
                item["quantity"],
                item["unit_price"],
                gross_price,
                item["discount_percent"],
                item["discount_amount"],
                item["total"],
                invoice["currency"],
                invoice["order_status"],
                created_at,
            ])

            next_order_item_key += 1

        client.insert(
            "fact_order_items",
            fact_rows,
            column_names=[
                "order_item_key",
                "order_item_id",
                "order_id",
                "date_key",
                "customer_key",
                "product_key",
                "payment_key",
                "quantity",
                "unit_price",
                "gross_price",
                "discount_percent",
                "discount_amount",
                "item_total",
                "currency",
                "order_status",
                "created_at",
            ],
        )

        # --------------------------------------------------
        # Load Completed
        # --------------------------------------------------

        logger.info(
            "Invoice loaded into ClickHouse",
            extra={
                "service": "clickhouse-loader",
                "event": "clickhouse_load_completed",
                "invoice_id": invoice["invoice_id"],
                "order_id": order_id,
                "customer_id": customer_id,
                "items_count": len(invoice["items"]),
            },
        )

    except Exception:

        logger.exception(
            "Failed to load invoice into ClickHouse",
            extra={
                "service": "clickhouse-loader",
                "event": "clickhouse_load_failed",
                "invoice_id": invoice.get("invoice_id"),
                "order_id": invoice.get("order_id"),
                "customer_id": invoice.get(
                    "customer",
                    {},
                ).get("customer_id"),
            },
        )

        raise

    finally:
        client.close()