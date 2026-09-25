CREATE DATABASE IF NOT EXISTS ecommerce;

USE ecommerce;


-- ============================================================
-- Dimension: Date
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_date
(
    date_key UInt32,
    full_date Date,

    year UInt16,
    quarter UInt8,
    month UInt8,
    month_name String,

    week UInt8,
    day UInt8,
    day_of_week UInt8,

    is_weekend UInt8
)
ENGINE = MergeTree
ORDER BY date_key;


-- ============================================================
-- Dimension: Customer
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_customer
(
    customer_key UInt64,
    customer_id String,

    first_name String,
    last_name String,
    email String,

    city String,
    postcode String,
    country String,

    created_at DateTime64(3, 'UTC')
)
ENGINE = MergeTree
ORDER BY customer_id;


-- ============================================================
-- Dimension: Product
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_product
(
    product_key UInt64,
    product_id String,

    product_name String,
    category String,
    brand String
)
ENGINE = MergeTree
ORDER BY product_id;


-- ============================================================
-- Dimension: Payment
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_payment
(
    payment_key UInt64,

    payment_method String,
    payment_status String
)
ENGINE = MergeTree
ORDER BY payment_key;


-- ============================================================
-- Fact: Order Items
--
-- Grain:
-- One row = one order item
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_order_items
(
    order_item_key UInt64,

    order_item_id UUID,
    order_id String,

    date_key UInt32,
    customer_key UInt64,
    product_key UInt64,
    payment_key UInt64,

    quantity UInt32,

    unit_price Decimal(12, 2),
    gross_price Decimal(12, 2),

    discount_percent Decimal(5, 2),
    discount_amount Decimal(12, 2),

    item_total Decimal(12, 2),

    order_discount_amount Decimal(12, 2),
    shipping_cost Decimal(12, 2),
    tax Decimal(12, 2),

    currency LowCardinality(String),

    order_status LowCardinality(String),

    created_at DateTime64(3, 'UTC')
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(created_at)
ORDER BY
(
    date_key,
    product_key,
    customer_key,
    order_id
);