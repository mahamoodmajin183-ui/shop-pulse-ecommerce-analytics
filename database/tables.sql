-- ==============================================================================
-- ShopPulse E-Commerce Analytics Platform - Relational & Fact Table Definitions
-- Based on the Verified Sample Superstore E-Commerce Dataset
-- ==============================================================================

-- 1. Dim Customers Table
DROP TABLE IF EXISTS shoppulse.dim_customers CASCADE;
CREATE TABLE shoppulse.dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    country VARCHAR(100) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    postal_code VARCHAR(20),
    region VARCHAR(50) NOT NULL
);

-- 2. Dim Products Table
DROP TABLE IF EXISTS shoppulse.dim_products CASCADE;
CREATE TABLE shoppulse.dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    sub_category VARCHAR(100) NOT NULL
);

-- 3. Fact Orders Table
DROP TABLE IF EXISTS shoppulse.fact_orders CASCADE;
CREATE TABLE shoppulse.fact_orders (
    row_id INTEGER PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    order_date DATE NOT NULL,
    ship_date DATE NOT NULL,
    ship_mode VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL REFERENCES shoppulse.dim_customers(customer_id),
    product_id VARCHAR(50) NOT NULL REFERENCES shoppulse.dim_products(product_id),
    sales NUMERIC(12, 2) NOT NULL CHECK (sales >= 0),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    discount NUMERIC(5, 4) NOT NULL DEFAULT 0.0,
    profit NUMERIC(12, 2) NOT NULL,
    cost NUMERIC(12, 2) NOT NULL,
    profit_margin_pct NUMERIC(8, 2),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL
);

-- Optimization Indexes
CREATE INDEX idx_dim_customers_segment ON shoppulse.dim_customers (customer_segment);
CREATE INDEX idx_dim_customers_region ON shoppulse.dim_customers (region);
CREATE INDEX idx_dim_products_category ON shoppulse.dim_products (category, sub_category);
CREATE INDEX idx_fact_orders_date ON shoppulse.fact_orders (order_date);
CREATE INDEX idx_fact_orders_customer_id ON shoppulse.fact_orders (customer_id);
CREATE INDEX idx_fact_orders_product_id ON shoppulse.fact_orders (product_id);
