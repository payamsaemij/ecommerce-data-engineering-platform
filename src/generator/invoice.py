import random
import uuid
from datetime import datetime, timezone

from data.products import PRODUCTS
from data.customers import FIRST_NAMES, LAST_NAMES
from data.payments import PAYMENT_METHODS
from data.locations import CITIES
from generator.helpers import generate_id, random_customer

def generate_invoice():

    customer = random_customer()

    # تعداد محصولات داخل سفارش
    number_of_products = random.randint(1, 5)

    selected_products = random.sample(
        PRODUCTS,
        number_of_products
    )

    items = []

    subtotal = 0

    # ======================================
    # GENERATE ITEMS
    # ======================================

    for product in selected_products:

        quantity = random.randint(1, 4)

        unit_price = product["price"]

        # تخفیف محصول
        discount_percent = random.choice([
            0,
            0,
            0,
            5,
            10,
            15
        ])

        gross_price = unit_price * quantity

        discount_amount = (
            gross_price
            * discount_percent
            / 100
        )

        item_total = (
            gross_price
            - discount_amount
        )

        item = {

            "product_id":
                product["product_id"],

            "product_name":
                product["name"],

            "category":
                product["category"],

            "quantity":
                quantity,

            "unit_price":
                unit_price,

            "discount_percent":
                discount_percent,

            "discount_amount":
                round(
                    discount_amount,
                    2
                ),

            "total":
                round(
                    item_total,
                    2
                )
        }

        items.append(item)

        subtotal += item_total


    # ======================================
    # ORDER LEVEL CALCULATIONS
    # ======================================

    subtotal = round(
        subtotal,
        2
    )

    # تخفیف کل سفارش
    order_discount = random.choice([
        0,
        0,
        5,
        10,
        20
    ])

    discount_amount = round(
        subtotal
        * order_discount
        / 100,
        2
    )

    after_discount = (
        subtotal
        - discount_amount
    )


    # ======================================
    # SHIPPING
    # ======================================

    if after_discount >= 100:

        shipping_cost = 0

    else:

        shipping_cost = random.choice([
            4.99,
            7.99,
            9.99
        ])


    # ======================================
    # TAX
    # ======================================

    tax_rate = 0.20

    tax = round(
        after_discount
        * tax_rate,
        2
    )


    # ======================================
    # FINAL TOTAL
    # ======================================

    total = round(
        after_discount
        + tax
        + shipping_cost,
        2
    )


    # ======================================
    # PAYMENT
    # ======================================

    payment_method = random.choice(
        PAYMENT_METHODS
    )

    payment_status = random.choices(
        [
            "completed",
            "failed"
        ],
        weights=[
            95,
            5
        ]
    )[0]


    # ======================================
    # ORDER STATUS
    # ======================================

    if payment_status == "failed":

        order_status = "payment_failed"

    else:

        order_status = random.choice([
            "confirmed",
            "processing",
            "shipped"
        ])


    # ======================================
    # FINAL INVOICE
    # ======================================

    invoice = {

        "invoice_id":
            generate_id("INV"),

        "order_id":
            generate_id("ORD"),

        "created_at":
            datetime.now(
                timezone.utc
            ).isoformat(),

        "currency":
            "GBP",


        # ----------------------------------
        # CUSTOMER
        # ----------------------------------

        "customer":
            customer,


        # ----------------------------------
        # PRODUCTS
        # ----------------------------------

        "items":
            items,


        # ----------------------------------
        # PRICING
        # ----------------------------------

        "pricing": {

            "subtotal":
                subtotal,

            "order_discount_percent":
                order_discount,

            "order_discount_amount":
                discount_amount,

            "shipping":
                shipping_cost,

            "tax_rate":
                tax_rate,

            "tax":
                tax,

            "total":
                total
        },


        # ----------------------------------
        # PAYMENT
        # ----------------------------------

        "payment": {

            "method":
                payment_method,

            "status":
                payment_status,

            "transaction_id":

                generate_id("TX")
                if payment_status == "completed"
                else None
        },


        # ----------------------------------
        # ORDER STATUS
        # ----------------------------------

        "order_status":
            order_status
    }


    return invoice
