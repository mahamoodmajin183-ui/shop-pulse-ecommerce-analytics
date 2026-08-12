"""
Unit tests for data_loader module and synthetic dataset generator.
"""

import pytest
import pandas as pd
from src.data_loader import generate_synthetic_dataset, inject_raw_data_anomalies, PRODUCT_CATALOG

def test_generate_synthetic_dataset_shape():
    """Verify synthetic dataset generates expected record volume and columns."""
    df = generate_synthetic_dataset(target_records=1000)
    
    assert len(df) == 1000
    expected_cols = [
        "order_id", "order_date", "customer_id", "customer_name",
        "product_id", "product_name", "category", "quantity",
        "unit_price", "discount", "sales", "cost", "profit",
        "region", "city", "payment_method", "customer_segment"
    ]
    for col in expected_cols:
        assert col in df.columns, f"Missing required column: {col}"

def test_dataset_financial_consistency():
    """Verify generated base records satisfy basic mathematical bounds."""
    df = generate_synthetic_dataset(target_records=500)
    
    assert (df["quantity"] > 0).all()
    assert (df["unit_price"] > 0).all()
    assert (df["discount"] >= 0.0).all() and (df["discount"] <= 1.0).all()
    assert (df["sales"] >= 0.0).all()
    assert (df["cost"] >= 0.0).all()

def test_raw_data_anomaly_injection():
    """Verify anomaly injection properly introduces realistic duplicates and missing fields."""
    base_df = generate_synthetic_dataset(target_records=500)
    raw_df = inject_raw_data_anomalies(base_df)
    
    # Anomaly checks
    assert len(raw_df) > len(base_df) # Duplicates added
    assert raw_df["customer_name"].isnull().sum() > 0 # Null customer names injected
    assert raw_df["payment_method"].isnull().sum() > 0 # Null payment methods injected
