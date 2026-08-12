-- ==============================================================================
-- ShopPulse E-Commerce Analytics Platform - PostgreSQL Schema & Optimization
-- ==============================================================================

-- Create database schema namespace
CREATE SCHEMA IF NOT EXISTS shoppulse;

-- Set search path
SET search_path TO shoppulse, public;

-- Enable UUID extension if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================================================
-- Performance Indexes & Constraints Strategy
-- ==============================================================================

-- Drop existing indexes if recreating
DROP INDEX IF EXISTS idx_orders_order_date;
DROP INDEX IF EXISTS idx_orders_customer_id;
DROP INDEX IF EXISTS idx_order_items_product_id;
DROP INDEX IF EXISTS idx_order_items_order_id;
DROP INDEX IF EXISTS idx_fact_sales_date_cat;
DROP INDEX IF EXISTS idx_fact_sales_region;

-- Create optimization indexes on normalized entities
-- (Created after tables are defined in tables.sql)
