"""Unit tests for the data cleaning pipeline."""
import os
import pandas as pd
from src.data_cleaning import clean_data

def test_data_cleaning_pipeline_integrity():
    df = clean_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 9994
    
    # Verify required schema columns exist
    required_cols = [
        "order_id", "order_date", "customer_id", "customer_name",
        "customer_segment", "region", "category", "sub_category",
        "product_id", "product_name", "sales", "quantity", "discount",
        "profit", "cost", "profit_margin_pct"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column: {col}"

    # Verify no nulls in critical identifiers
    assert df["order_id"].isnull().sum() == 0
    assert df["customer_id"].isnull().sum() == 0
    assert df["product_id"].isnull().sum() == 0

    # Verify financial consistency (Cost = Sales - Profit)
    computed_cost = (df["sales"] - df["profit"]).round(2)
    assert (df["cost"] - computed_cost).abs().max() < 0.05
