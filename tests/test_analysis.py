"""
Unit tests for analysis module and business KPI calculations.
"""

import pytest
import pandas as pd
from src.analysis import (
    calculate_kpis, get_monthly_trends, get_category_performance,
    get_regional_performance, get_top_products, get_rfm_segmentation,
    load_cleaned_data
)

@pytest.fixture
def clean_dataset():
    """Load cleaned transaction data for test validations."""
    return load_cleaned_data("data/processed/cleaned_ecommerce_data.csv")

def test_calculate_kpis(clean_dataset):
    """Verify KPI calculations produce accurate and reasonable metrics."""
    kpis = calculate_kpis(clean_dataset)
    
    assert kpis["total_revenue"] > 1000000
    assert kpis["total_profit"] > 500000
    assert kpis["total_orders"] >= 10000
    assert kpis["total_customers"] >= 2000
    assert kpis["average_order_value"] > 0
    assert 0 < kpis["profit_margin_pct"] < 100
    assert 0 < kpis["repeat_customer_rate"] < 100

def test_monthly_trends(clean_dataset):
    """Verify monthly aggregation structure and MoM growth metrics."""
    monthly = get_monthly_trends(clean_dataset)
    
    assert not monthly.empty
    assert "year_month" in monthly.columns
    assert "revenue" in monthly.columns
    assert "profit" in monthly.columns
    assert "revenue_mom_growth_pct" in monthly.columns
    assert "cumulative_revenue" in monthly.columns
    
    # Cumulative revenue should be monotonically increasing
    assert (monthly["cumulative_revenue"].diff().dropna() >= 0).all()

def test_category_performance(clean_dataset):
    """Verify category totals match total enterprise revenue."""
    cats = get_category_performance(clean_dataset)
    
    assert len(cats) >= 5
    total_cat_rev = cats["revenue"].sum()
    total_sales = clean_dataset["sales"].sum()
    assert abs(total_cat_rev - total_sales) < 1.0

def test_rfm_segmentation(clean_dataset):
    """Verify RFM customer segmentation assigns all customers to valid segments."""
    rfm = get_rfm_segmentation(clean_dataset)
    
    assert len(rfm) == clean_dataset["customer_id"].nunique()
    assert rfm["RFM_Segment"].isnull().sum() == 0
    valid_segments = [
        "Champions / VIP", "Loyal Customers", "Promising / New",
        "Needs Attention", "At Risk / High Value", "Hibernating / Dormant"
    ]
    assert rfm["RFM_Segment"].isin(valid_segments).all()
