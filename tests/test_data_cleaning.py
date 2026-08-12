"""
Unit tests for data_cleaning module and data validation rules.
"""

import pytest
import pandas as pd
import numpy as np
from src.data_cleaning import DataCleaner

@pytest.fixture
def dirty_sample_df():
    """Create a controlled sample dataset with intentional edge cases."""
    return pd.DataFrame([
        {
            "order_id": "ORD-001",
            "order_date": "2024-01-15 10:30:00",
            "customer_id": "CUST-1",
            "customer_name": "Alice Smith",
            "product_id": "PROD-1",
            "product_name": "ProBook Laptop",
            "category": "  Technology  ",
            "quantity": 2,
            "unit_price": 1000.0,
            "discount": 0.10,
            "sales": 1800.0,
            "cost": 1200.0,
            "profit": 600.0,
            "region": " north ",
            "city": "New York",
            "payment_method": "Credit Card",
            "customer_segment": "consumer"
        },
        {
            # Exact duplicate of ORD-001
            "order_id": "ORD-001",
            "order_date": "2024-01-15 10:30:00",
            "customer_id": "CUST-1",
            "customer_name": "Alice Smith",
            "product_id": "PROD-1",
            "product_name": "ProBook Laptop",
            "category": "Technology",
            "quantity": 2,
            "unit_price": 1000.0,
            "discount": 0.10,
            "sales": 1800.0,
            "cost": 1200.0,
            "profit": 600.0,
            "region": "North",
            "city": "New York",
            "payment_method": "Credit Card",
            "customer_segment": "Consumer"
        },
        {
            # Missing customer name (should be mapped from CUST-1), mixed date format
            "order_id": "ORD-002",
            "order_date": "25/02/2024",
            "customer_id": "CUST-1",
            "customer_name": np.nan,
            "product_id": "PROD-2",
            "product_name": "Desk Chair",
            "category": "Furniture",
            "quantity": 1,
            "unit_price": 300.0,
            "discount": 0.0,
            "sales": 999.0, # Discrepant sales value to be corrected
            "cost": 180.0,
            "profit": 120.0,
            "region": "South",
            "city": "Austin",
            "payment_method": None,
            "customer_segment": "Consumer"
        }
    ])

def test_deduplication(dirty_sample_df):
    """Test that duplicate rows are cleanly removed."""
    cleaner = DataCleaner()
    df_deduped = cleaner.remove_duplicates(dirty_sample_df)
    assert len(df_deduped) == 2
    assert df_deduped["order_id"].tolist() == ["ORD-001", "ORD-002"]

def test_string_standardization(dirty_sample_df):
    """Test whitespace trimming and title casing."""
    cleaner = DataCleaner()
    df_std = cleaner.standardize_strings(dirty_sample_df)
    assert df_std.loc[0, "category"] == "Technology"
    assert df_std.loc[0, "region"] == "North"
    assert df_std.loc[0, "customer_segment"] == "Consumer"

def test_missing_value_imputation(dirty_sample_df):
    """Test relational imputation for missing customer names and payment methods."""
    cleaner = DataCleaner()
    df_std = cleaner.standardize_strings(dirty_sample_df)
    df_imputed = cleaner.handle_missing_values(df_std)
    
    # Customer name for ORD-002 should resolve to Alice Smith (via CUST-1 mapping)
    assert df_imputed.loc[2, "customer_name"] == "Alice Smith"
    assert df_imputed["payment_method"].isnull().sum() == 0

def test_financial_correction(dirty_sample_df):
    """Test automated correction of mathematical discrepancies in sales and profit."""
    cleaner = DataCleaner()
    df_cleaned = cleaner.validate_and_correct_financials(dirty_sample_df)
    
    # ORD-002 had sales = 999.0, should be corrected to 1 * 300.0 * (1 - 0.0) = 300.0
    assert df_cleaned.loc[2, "sales"] == 300.0
    assert df_cleaned.loc[2, "profit"] == 120.0 # 300.0 - 180.0
    assert df_cleaned.loc[2, "profit_margin_pct"] == 40.0
