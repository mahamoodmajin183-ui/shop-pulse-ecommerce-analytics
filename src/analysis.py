"""
ShopPulse - Advanced E-Commerce Analytics Engine
Provides modular statistical calculations, time-series metrics, RFM segmentation,
cohort metrics, product profitability analysis, and data preparation for reporting.
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, Tuple

def load_cleaned_data(filepath: str = "data/processed/cleaned_ecommerce_data.csv") -> pd.DataFrame:
    """Load cleaned transaction data and format datetime columns."""
    df = pd.read_csv(filepath)
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
    return df

def calculate_kpis(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate executive level KPIs across the active dataset slice."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "total_orders": 0,
            "total_customers": 0,
            "total_items_sold": 0,
            "average_order_value": 0.0,
            "profit_margin_pct": 0.0,
            "avg_discount_pct": 0.0,
            "repeat_customer_rate": 0.0
        }

    total_revenue = float(df["sales"].sum())
    total_profit = float(df["profit"].sum())
    total_orders = int(df["order_id"].nunique())
    total_customers = int(df["customer_id"].nunique())
    total_items_sold = int(df["quantity"].sum())
    
    aov = float(total_revenue / total_orders) if total_orders > 0 else 0.0
    profit_margin = float((total_profit / total_revenue) * 100.0) if total_revenue > 0 else 0.0
    avg_discount = float(df["discount"].mean() * 100.0)
    
    # Repeat customer rate
    order_counts_per_cust = df.groupby("customer_id")["order_id"].nunique()
    repeat_customers = (order_counts_per_cust > 1).sum()
    repeat_rate = float((repeat_customers / total_customers) * 100.0) if total_customers > 0 else 0.0

    return {
        "total_revenue": round(total_revenue, 2),
        "total_profit": round(total_profit, 2),
        "total_orders": total_orders,
        "total_customers": total_customers,
        "total_items_sold": total_items_sold,
        "average_order_value": round(aov, 2),
        "profit_margin_pct": round(profit_margin, 2),
        "avg_discount_pct": round(avg_discount, 2),
        "repeat_customer_rate": round(repeat_rate, 2)
    }

def get_monthly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate monthly revenue, profit, orders, and MoM growth rates."""
    df_copy = df.copy()
    df_copy["year_month"] = df_copy["order_date"].dt.to_period("M").astype(str)
    
    monthly = df_copy.groupby("year_month").agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique"),
        units_sold=("quantity", "sum")
    ).reset_index()

    monthly["profit_margin_pct"] = (monthly["profit"] / monthly["revenue"] * 100.0).round(2)
    monthly["aov"] = (monthly["revenue"] / monthly["orders"]).round(2)
    
    # MoM Growth calculations using LAG simulation
    monthly["revenue_mom_growth_pct"] = monthly["revenue"].pct_change() * 100.0
    monthly["profit_mom_growth_pct"] = monthly["profit"].pct_change() * 100.0
    
    # Cumulative running totals
    monthly["cumulative_revenue"] = monthly["revenue"].cumsum().round(2)
    monthly["cumulative_profit"] = monthly["profit"].cumsum().round(2)
    
    return monthly

def get_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate sales, profit, orders, and margin metrics by Category."""
    cat_summary = df.groupby("category").agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        units_sold=("quantity", "sum"),
        avg_discount=("discount", lambda x: x.mean() * 100.0)
    ).reset_index()

    cat_summary["profit_margin_pct"] = (cat_summary["profit"] / cat_summary["revenue"] * 100.0).round(2)
    cat_summary["revenue_share_pct"] = (cat_summary["revenue"] / cat_summary["revenue"].sum() * 100.0).round(2)
    cat_summary = cat_summary.sort_values(by="revenue", ascending=False).reset_index(drop=True)
    return cat_summary

def get_regional_performance(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Aggregate metrics by Region and Top Performing Cities."""
    region_summary = df.groupby("region").agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique"),
        customers=("customer_id", "nunique")
    ).reset_index()
    
    region_summary["profit_margin_pct"] = (region_summary["profit"] / region_summary["revenue"] * 100.0).round(2)
    region_summary["aov"] = (region_summary["revenue"] / region_summary["orders"]).round(2)
    region_summary = region_summary.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    city_summary = df.groupby(["region", "city"]).agg(
        revenue=("sales", "sum"),
        profit=("profit", "sum"),
        orders=("order_id", "nunique")
    ).reset_index()
    city_summary["profit_margin_pct"] = (city_summary["profit"] / city_summary["revenue"] * 100.0).round(2)
    city_summary = city_summary.sort_values(by="revenue", ascending=False).reset_index(drop=True)

    return region_summary, city_summary

def get_top_products(df: pd.DataFrame, top_n: int = 10, by: str = "revenue") -> pd.DataFrame:
    """Retrieve top N products ranked by revenue or profit."""
    sort_col = "sales" if by == "revenue" else "profit"
    prod_summary = df.groupby(["product_id", "product_name", "category"]).agg(
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        total_quantity=("quantity", "sum"),
        order_count=("order_id", "nunique")
    ).reset_index()

    prod_summary["profit_margin_pct"] = (prod_summary["total_profit"] / prod_summary["total_sales"] * 100.0).round(2)
    prod_summary = prod_summary.sort_values(by=f"total_{sort_col}", ascending=False).head(top_n).reset_index(drop=True)
    return prod_summary

def get_rfm_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform RFM (Recency, Frequency, Monetary) customer segmentation.
    Recency: Days since last order relative to reference snapshot date.
    Frequency: Total unique orders.
    Monetary: Total spend (sales).
    """
    snapshot_date = df["order_date"].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby("customer_id").agg(
        customer_name=("customer_name", "first"),
        customer_segment=("customer_segment", "first"),
        region=("region", "first"),
        recency=("order_date", lambda x: (snapshot_date - x.max()).days),
        frequency=("order_id", "nunique"),
        monetary=("sales", "sum"),
        total_profit=("profit", "sum")
    ).reset_index()

    # Assign quartile scores (1-4)
    # Recency: lower is better (more recent) -> reverse ranking
    rfm["R_Score"] = pd.qcut(rfm["recency"], 4, labels=[4, 3, 2, 1], duplicates="drop").astype(int)
    rfm["F_Score"] = pd.qcut(rfm["frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["M_Score"] = pd.qcut(rfm["monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    
    rfm["RFM_Score"] = rfm["R_Score"].astype(str) + rfm["F_Score"].astype(str) + rfm["M_Score"].astype(str)
    
    # Segment assignment
    def assign_segment(row):
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r >= 4 and f >= 3:
            return "Champions / VIP"
        elif r >= 3 and f >= 2:
            return "Loyal Customers"
        elif r >= 3 and f == 1:
            return "Promising / New"
        elif r == 2 and f >= 2:
            return "Needs Attention"
        elif r == 1 and f >= 3:
            return "At Risk / High Value"
        else:
            return "Hibernating / Dormant"
            
    rfm["RFM_Segment"] = rfm.apply(assign_segment, axis=1)
    return rfm

def get_discount_impact_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Analyze the relationship between discount tiers and profitability."""
    df_copy = df.copy()
    bins = [-0.01, 0.0, 0.10, 0.20, 1.0]
    labels = ["No Discount (0%)", "Low (1-10%)", "Moderate (11-20%)", "High (>20%)"]
    df_copy["discount_tier"] = pd.cut(df_copy["discount"], bins=bins, labels=labels)
    
    disc_summary = df_copy.groupby("discount_tier", observed=False).agg(
        orders=("order_id", "nunique"),
        total_sales=("sales", "sum"),
        total_profit=("profit", "sum"),
        avg_units=("quantity", "mean"),
        avg_order_value=("sales", "mean")
    ).reset_index()
    
    disc_summary["profit_margin_pct"] = (disc_summary["total_profit"] / disc_summary["total_sales"] * 100.0).round(2)
    return disc_summary

def get_pareto_product_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate cumulative revenue distribution across products (Pareto 80/20 rule)."""
    prod_sales = df.groupby("product_id")["sales"].sum().sort_values(ascending=False).reset_index()
    prod_sales["cumulative_sales"] = prod_sales["sales"].cumsum()
    total_sales = prod_sales["sales"].sum()
    prod_sales["cumulative_share_pct"] = (prod_sales["cumulative_sales"] / total_sales * 100.0).round(2)
    prod_sales["product_rank"] = range(1, len(prod_sales) + 1)
    prod_sales["product_pct"] = (prod_sales["product_rank"] / len(prod_sales) * 100.0).round(2)
    return prod_sales

if __name__ == "__main__":
    df = load_cleaned_data()
    kpis = calculate_kpis(df)
    print("--- Core KPIs ---")
    for k, v in kpis.items():
        print(f"  {k}: {v}")
    
    print("\n--- Monthly Trends Sample ---")
    monthly = get_monthly_trends(df)
    print(monthly.head(3))
    
    print("\n--- Category Breakdown ---")
    cats = get_category_performance(df)
    print(cats)
