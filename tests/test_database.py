"""Integration tests for database initialization, schema, and queries."""
from src.database import get_engine, initialize_and_seed_db, run_query

def test_database_initialization_and_seeding():
    initialize_and_seed_db()
    res = run_query("SELECT COUNT(*) AS total_rows, SUM(sales) AS total_sales, SUM(profit) AS total_profit FROM fact_ecommerce_sales")
    assert res.iloc[0]["total_rows"] == 9994
    assert abs(res.iloc[0]["total_sales"] - 2297200.65) < 1.0
    assert abs(res.iloc[0]["total_profit"] - 286396.54) < 1.0

def test_star_schema_tables():
    cust_res = run_query("SELECT COUNT(*) AS total_customers FROM dim_customers")
    prod_res = run_query("SELECT COUNT(*) AS total_products FROM dim_products")
    orders_res = run_query("SELECT COUNT(*) AS total_orders FROM fact_orders")
    
    assert cust_res.iloc[0]["total_customers"] == 793
    assert prod_res.iloc[0]["total_products"] == 1862
    assert orders_res.iloc[0]["total_orders"] == 9994
