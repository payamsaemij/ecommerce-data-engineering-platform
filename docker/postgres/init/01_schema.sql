-- ============================================================
-- E-Commerce Data Engineering Platform
-- PostgreSQL Schema
-- ============================================================

-- ------------------------------------------------------------
-- Extensions
-- ------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS pgcrypto;


-- ------------------------------------------------------------
-- Schema
-- ------------------------------------------------------------

CREATE SCHEMA IF NOT EXISTS ecommerce;


-- ------------------------------------------------------------
-- Customers
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ecommerce.customers (
    customer_id VARCHAR(50) PRIMARY KEY,

    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,

    email VARCHAR(255) NOT NULL,

    city VARCHAR(100),
    postcode VARCHAR(20),
    shipping_address TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_customers_email
ON ecommerce.customers (email);


-- ------------------------------------------------------------
-- Products
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ecommerce.products (
    product_id VARCHAR(50) PRIMARY KEY,

    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    brand VARCHAR(100),

    -- Current product price
    price NUMERIC(12,2) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_products_category
ON ecommerce.products (category);


-- ------------------------------------------------------------
-- Orders
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ecommerce.orders (
    order_id VARCHAR(50) PRIMARY KEY,

    customer_id VARCHAR(50) NOT NULL,

    created_at TIMESTAMPTZ NOT NULL,

    currency VARCHAR(10) NOT NULL,

    subtotal NUMERIC(12,2) NOT NULL,

    -- Total discount applied to order items
    item_discount NUMERIC(12,2) NOT NULL DEFAULT 0,

    -- Order-level discount
    order_discount NUMERIC(12,2) NOT NULL DEFAULT 0,

    shipping_cost NUMERIC(12,2) NOT NULL DEFAULT 0,

    tax NUMERIC(12,2) NOT NULL DEFAULT 0,

    total NUMERIC(12,2) NOT NULL,

    order_status VARCHAR(50) NOT NULL,

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (customer_id)
        REFERENCES ecommerce.customers(customer_id)
);

CREATE INDEX IF NOT EXISTS idx_orders_created_at
ON ecommerce.orders (created_at);

CREATE INDEX IF NOT EXISTS idx_orders_customer_created
ON ecommerce.orders (customer_id, created_at);


-- ------------------------------------------------------------
-- Order Items
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ecommerce.order_items (
    order_item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,

    quantity INTEGER NOT NULL,

    -- Price at the time of purchase
    unit_price NUMERIC(12,2) NOT NULL,

    discount_percent NUMERIC(5,2) NOT NULL DEFAULT 0,

    -- quantity * unit_price
    gross_price NUMERIC(12,2) NOT NULL,

    discount_amount NUMERIC(12,2) NOT NULL DEFAULT 0,

    -- Final item amount after discount
    item_total NUMERIC(12,2) NOT NULL,

    CONSTRAINT fk_order_items_order
        FOREIGN KEY (order_id)
        REFERENCES ecommerce.orders(order_id),

    CONSTRAINT fk_order_items_product
        FOREIGN KEY (product_id)
        REFERENCES ecommerce.products(product_id),

    CONSTRAINT chk_order_items_quantity
        CHECK (quantity > 0)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id
ON ecommerce.order_items (order_id);

CREATE INDEX IF NOT EXISTS idx_order_items_product_id
ON ecommerce.order_items (product_id);


-- ------------------------------------------------------------
-- Payments
-- ------------------------------------------------------------

CREATE TABLE IF NOT EXISTS ecommerce.payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    order_id VARCHAR(50) NOT NULL UNIQUE,

    payment_method VARCHAR(50) NOT NULL,

    payment_status VARCHAR(50) NOT NULL,

    paid_at TIMESTAMPTZ,

    CONSTRAINT fk_payments_order
        FOREIGN KEY (order_id)
        REFERENCES ecommerce.orders(order_id)
);


-- ------------------------------------------------------------
-- Comments / Documentation
-- ------------------------------------------------------------

COMMENT ON TABLE ecommerce.customers IS
'Customer master data.';

COMMENT ON TABLE ecommerce.products IS
'Current product master data. Product ID can appear in multiple orders.';

COMMENT ON COLUMN ecommerce.products.price IS
'Current product price, not historical purchase price.';

COMMENT ON TABLE ecommerce.orders IS
'Order-level information.';

COMMENT ON TABLE ecommerce.order_items IS
'Products purchased within each order.';

COMMENT ON COLUMN ecommerce.order_items.unit_price IS
'Product price at the time of purchase.';

COMMENT ON TABLE ecommerce.payments IS
'Payment information for orders.';


-- ------------------------------------------------------------
-- End of schema
-- ------------------------------------------------------------