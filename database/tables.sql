-- ==============================================================================
-- ShopPulse E-Commerce Analytics Platform - Relational & Fact Table Definitions
-- ==============================================================================

-- 1. Dim Customers Table
DROP TABLE IF EXISTS shoppulse.dim_customers CASCADE;
CREATE TABLE shoppulse.dim_customers (
    customer_id VARCHAR(50) PRIMARY KEY,
    customer_name VARCHAR(150) NOT NULL,
    customer_segment VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Dim Products Table
DROP TABLE IF EXISTS shoppulse.dim_products CASCADE;
CREATE TABLE shoppulse.dim_products (
    product_id VARCHAR(50) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    unit_price NUMERIC(12, 2) NOT NULL CHECK (unit_price >= 0),
    cost NUMERIC(12, 2) NOT NULL CHECK (cost >= 0)
);

-- 3. Fact Orders Table
DROP TABLE IF EXISTS shoppulse.fact_orders CASCADE;
CREATE TABLE shoppulse.fact_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    order_date TIMESTAMP NOT NULL,
    customer_id VARCHAR(50) NOT NULL REFERENCES shoppulse.dim_customers(customer_id),
    product_id VARCHAR(50) NOT NULL REFERENCES shoppulse.dim_products(product_id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price NUMERIC(12, 2) NOT NULL,
    discount NUMERIC(5, 4) NOT NULL DEFAULT 0.0 CHECK (discount >= 0.0 AND discount <= 1.0),
    sales NUMERIC(12, 2) NOT NULL CHECK (sales >= 0),
    cost NUMERIC(12, 2) NOT NULL CHECK (cost >= 0),
    profit NUMERIC(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    region VARCHAR(50) NOT NULL,
    city VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- Optimized Indexes for High-Velocity Analytical Queries
-- ==============================================================================

CREATE INDEX idx_dim_customers_segment ON shoppulse.dim_customers (customer_segment);
CREATE INDEX idx_dim_customers_region ON shoppulse.dim_customers (region);

CREATE INDEX idx_dim_products_category ON shoppulse.dim_products (category);

CREATE INDEX idx_fact_orders_date ON shoppulse.fact_orders (order_date);
CREATE INDEX idx_fact_orders_customer_id ON shoppulse.fact_orders (customer_id);
CREATE INDEX idx_fact_orders_product_id ON shoppulse.fact_orders (product_id);
CREATE INDEX idx_fact_orders_category_date ON shoppulse.fact_orders (region, order_date);
