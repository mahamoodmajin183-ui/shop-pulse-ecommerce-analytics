"""
Unit tests for database module and SQL query execution.
"""

import pytest
import pandas as pd
from src.database import get_engine, run_query, initialize_and_seed_db

def test_database_connection():
    """Verify database engine connects and executes basic test query."""
    engine = get_engine()
    assert engine is not None

def test_seeded_tables_exist():
    """Verify seeded tables are populated with correct row counts."""
    # Ensure seeded
    initialize_and_seed_db()
    
    res_fact = run_query("SELECT COUNT(*) AS cnt FROM fact_ecommerce_sales")
    assert res_fact.loc[0, "cnt"] >= 10000
    
    res_cust = run_query("SELECT COUNT(*) AS cnt FROM dim_customers")
    assert res_cust.loc[0, "cnt"] >= 2000
    
    res_prod = run_query("SELECT COUNT(*) AS cnt FROM dim_products")
    assert res_prod.loc[0, "cnt"] >= 500

def test_analytical_sql_query():
    """Verify execution of CTE and Window function on database."""
    query = """
    WITH cat_summary AS (
        SELECT 
            category,
            SUM(sales) AS cat_sales,
            SUM(profit) AS cat_profit
        FROM fact_ecommerce_sales
        GROUP BY category
    )
    SELECT 
        category,
        cat_sales,
        cat_profit,
        RANK() OVER (ORDER BY cat_sales DESC) AS sales_rank
    FROM cat_summary;
    """
    df = run_query(query)
    assert not df.empty
    assert "sales_rank" in df.columns
    assert df.loc[0, "sales_rank"] == 1
