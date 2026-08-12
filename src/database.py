"""
ShopPulse - Database Interface and Connection Layer
Supports both SQLite (local embedded zero-config) and PostgreSQL (production server).
Provides automated schema migration, table seeding, and query execution.
"""

import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_ENGINE_TYPE = os.getenv("DB_ENGINE", "sqlite").lower()
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "database/shoppulse.db")

POSTGRES_HOST = os.getenv("DB_HOST", "localhost")
POSTGRES_PORT = os.getenv("DB_PORT", "5432")
POSTGRES_DB = os.getenv("DB_NAME", "shoppulse_db")
POSTGRES_USER = os.getenv("DB_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("DB_PASSWORD", "")

def get_db_connection_url() -> str:
    """Generate SQLAlchemy connection URL based on configuration."""
    if DB_ENGINE_TYPE == "postgresql":
        return f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        # SQLite
        os.makedirs(os.path.dirname(SQLITE_DB_PATH), exist_ok=True)
        return f"sqlite:///{SQLITE_DB_PATH}"

def get_engine():
    """Create and return SQLAlchemy engine with connection fallback."""
    try:
        url = get_db_connection_url()
        engine = create_engine(url, echo=False)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception as e:
        print(f"Warning: Primary database connection failed ({e}). Falling back to local SQLite.")
        os.makedirs("database", exist_ok=True)
        return create_engine("sqlite:///database/shoppulse.db", echo=False)

def initialize_and_seed_db(csv_path: str = "data/processed/cleaned_ecommerce_data.csv") -> None:
    """
    Populate database tables (normalized star schema and flat table)
    from the cleaned e-commerce dataset.
    """
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Cleaned dataset not found at: {csv_path}")

    df = pd.read_csv(csv_path)
    engine = get_engine()

    print(f"Seeding database from: {csv_path} ({len(df):,} records)...")

    # 1. Populate Flat Analytics Fact Table
    df.to_sql("fact_ecommerce_sales", con=engine, if_exists="replace", index=False)

    # 2. Populate Normalized Dim Customers
    dim_customers = df[[
        "customer_id", "customer_name", "customer_segment", "region", "city"
    ]].drop_duplicates(subset=["customer_id"]).reset_index(drop=True)
    dim_customers.to_sql("dim_customers", con=engine, if_exists="replace", index=False)

    # 3. Populate Normalized Dim Products
    dim_products = df[[
        "product_id", "product_name", "category", "unit_price", "cost"
    ]].drop_duplicates(subset=["product_id"]).reset_index(drop=True)
    dim_products.to_sql("dim_products", con=engine, if_exists="replace", index=False)

    # 4. Populate Normalized Fact Orders
    fact_orders = df[[
        "order_id", "order_date", "customer_id", "product_id", "quantity",
        "unit_price", "discount", "sales", "cost", "profit",
        "payment_method", "region", "city"
    ]].reset_index(drop=True)
    fact_orders.to_sql("fact_orders", con=engine, if_exists="replace", index=False)

    print(f" Database successfully initialized and seeded:")
    print(f"  - `fact_ecommerce_sales`: {len(df):,} rows")
    print(f"  - `dim_customers`: {len(dim_customers):,} rows")
    print(f"  - `dim_products`: {len(dim_products):,} rows")
    print(f"  - `fact_orders`: {len(fact_orders):,} rows")

def run_query(sql_query: str) -> pd.DataFrame:
    """Execute a SQL query against the active database and return a Pandas DataFrame."""
    engine = get_engine()
    with engine.connect() as conn:
        result = pd.read_sql_query(text(sql_query), conn)
    return result

if __name__ == "__main__":
    initialize_and_seed_db()
    test_df = run_query("SELECT COUNT(*) AS total_records, SUM(sales) AS total_revenue FROM fact_ecommerce_sales")
    print("\nTest Query Verification:")
    print(test_df)
