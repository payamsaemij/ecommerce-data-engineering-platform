from datetime import datetime, timezone

from postgres.connection import get_connection


def load_batch(invoices):

    with get_connection() as conn:

        with conn.transaction():

            with conn.cursor() as cur:

                for invoice in invoices:


                    customer = invoice["customer"]

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
                            customer["customer_id"],
                            customer["first_name"],
                            customer["last_name"],
                            customer["email"],
                            customer["shipping_address"]["city"],
                            customer["shipping_address"]["postcode"],
                            customer["shipping_address"]["country"],
                            invoice["created_at"],
                        )
                    )

                    # --------------------------------
                    # Products
                    # --------------------------------

                    for item in invoice["items"]:

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
                                item["product_id"],
                                item["product_name"],
                                item["category"],
                                item["unit_price"],
                                invoice["created_at"],
                            )
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
                            invoice["order_id"],
                            customer["customer_id"],
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
                        )
                    )

                    # --------------------------------
                    # Order Items
                    # --------------------------------

                    for item in invoice["items"]:

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
                                invoice["order_id"],
                                item["product_id"],
                                item["quantity"],
                                item["unit_price"],
                                item["discount_percent"],
                                gross_price,
                                item["discount_amount"],
                                item["total"],
                            )
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
                            invoice["order_id"],
                            payment["method"],
                            payment["status"],
                            paid_at,
                        )
                    )

        print(
            f"Batch of {len(invoices)} invoices "
            f"inserted successfully."
        )