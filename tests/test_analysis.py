"""Unit tests for the analytics calculation engine."""
import pandas as pd
from src.analysis import (
    load_cleaned_data, calculate_kpis, get_monthly_trends,
    get_category_performance, get_regional_performance,
    get_top_products, get_discount_impact_analysis, get_rfm_segmentation
)

def test_kpi_calculations_ground_truth():
    df = load_cleaned_data()
    kpis = calculate_kpis(df)
    
    # Assert exact ground truth metrics
    assert kpis["total_orders"] == 5009
    assert kpis["total_customers"] == 793
    assert abs(kpis["total_revenue"] - 2297200.65) < 1.0
    assert abs(kpis["total_profit"] - 286396.54) < 1.0
    assert abs(kpis["profit_margin_pct"] - 12.47) < 0.1
    assert kpis["repeat_customer_rate"] > 95.0

def test_category_performance_integrity():
    df = load_cleaned_data()
    cats, subcats = get_category_performance(df)
    assert len(cats) == 3
    assert set(cats["category"]) == {"Technology", "Furniture", "Office Supplies"}
    assert len(subcats) == 17

def test_rfm_segmentation_coverage():
    df = load_cleaned_data()
    rfm = get_rfm_segmentation(df)
    assert len(rfm) == 793  # All 793 unique customers segmented
    assert "RFM_Segment" in rfm.columns
