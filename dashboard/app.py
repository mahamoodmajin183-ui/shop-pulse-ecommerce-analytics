"""
ShopPulse — Production Streamlit E-Commerce Analytics Dashboard
Dynamically queries and visualizes the verified real Sample Superstore dataset.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import text

from src.database import get_engine
from src.analysis import (
    load_cleaned_data, calculate_kpis, get_monthly_trends,
    get_category_performance, get_regional_performance,
    get_top_products, get_discount_impact_analysis, get_rfm_segmentation
)

st.set_page_config(
    page_title="ShopPulse — E-Commerce Sales Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Dark Modern Aesthetics
st.markdown("""
<style>
    .main { background-color: #090d16; }
    .stMetric {
        background-color: #0f172a;
        padding: 16px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 3px solid #0284c7;
    }
    h1, h2, h3 { font-family: 'Plus Jakarta Sans', sans-serif; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def get_data():
    return load_cleaned_data()

df_all = get_data()

# Sidebar
st.sidebar.image("https://img.icons8.com/fluency/96/shopping-bag.png", width=64)
st.sidebar.title("ShopPulse Analytics")
st.sidebar.caption("Verified Real E-Commerce Dataset")

st.sidebar.header("Global Filters")
selected_year = st.sidebar.selectbox("Operating Year", ["All Years"] + sorted(df_all["order_year"].unique().tolist(), reverse=True))
selected_region = st.sidebar.selectbox("Region", ["All Regions"] + sorted(df_all["region"].unique().tolist()))
selected_category = st.sidebar.selectbox("Category", ["All Categories"] + sorted(df_all["category"].unique().tolist()))
selected_segment = st.sidebar.selectbox("Customer Segment", ["All Segments"] + sorted(df_all["customer_segment"].unique().tolist()))

# Filter Dataframe
df = df_all.copy()
if selected_year != "All Years":
    df = df[df["order_year"] == selected_year]
if selected_region != "All Regions":
    df = df[df["region"] == selected_region]
if selected_category != "All Categories":
    df = df[df["category"] == selected_category]
if selected_segment != "All Segments":
    df = df[df["customer_segment"] == selected_segment]

# Top Title
st.title("🛍️ ShopPulse — E-Commerce Analytics Platform")
st.caption(f"Analyzing {len(df):,} transactions ({df['order_date'].min().strftime('%Y-%m-%d')} to {df['order_date'].max().strftime('%Y-%m-%d')})")

# KPI Metrics
kpis = calculate_kpis(df)
col1, col2, col3, col4, col5, col6 = st.columns(6)

col1.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}")
col2.metric("Total Profit", f"${kpis['total_profit']:,.2f}")
col3.metric("Profit Margin", f"{kpis['profit_margin_pct']}%")
col4.metric("Total Orders", f"{kpis['total_orders']:,}")
col5.metric("Avg Order Value", f"${kpis['average_order_value']:,.2f}")
col6.metric("Repeat Buyers", f"{kpis['repeat_customer_rate']}%")

st.markdown("---")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Sales & Profit Trends",
    "📦 Category & Products",
    "👥 Customer & RFM",
    "🌍 Regional Dynamics",
    "⚡ SQL Query Studio"
])

with tab1:
    st.subheader("Monthly Sales Velocity & Profit Trajectory")
    monthly = get_monthly_trends(df)
    
    fig_monthly = go.Figure()
    fig_monthly.add_trace(go.Bar(
        x=monthly["year_month"], y=monthly["revenue"],
        name="Revenue ($)", marker_color="#0284c7"
    ))
    fig_monthly.add_trace(go.Scatter(
        x=monthly["year_month"], y=monthly["profit"],
        name="Profit ($)", line=dict(color="#10b981", width=3)
    ))
    fig_monthly.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=400,
        margin=dict(l=20, r=20, t=30, b=20)
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

    st.subheader("Discount Depth vs. Profitability Impact")
    disc = get_discount_impact_analysis(df)
    fig_disc = px.line(
        disc, x="discount_tier", y="profit_margin_pct",
        markers=True, title="Realized Profit Margin (%) Across Discount Depth",
        template="plotly_dark"
    )
    fig_disc.update_traces(line_color="#f43f5e", line_width=3)
    fig_disc.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=320)
    st.plotly_chart(fig_disc, use_container_width=True)

with tab2:
    col_c1, col_c2 = st.columns([1, 1])
    cats, subcats = get_category_performance(df)
    
    with col_c1:
        st.subheader("Category Revenue Share")
        fig_cat = px.pie(
            cats, names="category", values="revenue",
            hole=0.5, color_discrete_sequence=["#0284c7", "#f59e0b", "#10b981"],
            template="plotly_dark"
        )
        fig_cat.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with col_c2:
        st.subheader("Sub-Category Profitability Breakdown")
        fig_sub = px.bar(
            subcats, x="revenue", y="sub_category", orientation="h",
            color="profit", color_continuous_scale="Viridis",
            template="plotly_dark", title="Sub-Category Revenue colored by Profit"
        )
        fig_sub.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_sub, use_container_width=True)

    st.subheader("Top 10 High-Revenue Product SKUs")
    top_p = get_top_products(df, top_n=10)
    st.dataframe(top_p, use_container_width=True)

with tab3:
    st.subheader("Customer RFM Value Segmentation")
    rfm = get_rfm_segmentation(df)
    rfm_sum = rfm.groupby("RFM_Segment").agg(
        Customer_Count=("customer_id", "count"),
        Total_Spend=("monetary", "sum"),
        Avg_Orders=("frequency", "mean"),
        Total_Profit=("total_profit", "sum")
    ).reset_index()
    
    fig_rfm = px.bar(
        rfm_sum, x="RFM_Segment", y="Total_Spend",
        color="Total_Profit", color_continuous_scale="Blues",
        template="plotly_dark"
    )
    fig_rfm.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_rfm, use_container_width=True)
    st.dataframe(rfm_sum, use_container_width=True)

with tab4:
    st.subheader("Regional Performance & Margins")
    regions, states = get_regional_performance(df)
    fig_reg = px.bar(
        regions, x="region", y=["revenue", "profit"],
        barmode="group", color_discrete_sequence=["#0284c7", "#10b981"],
        template="plotly_dark"
    )
    fig_reg.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_reg, use_container_width=True)
    
    st.subheader("State-Level Profit Efficiency")
    st.dataframe(states.head(20), use_container_width=True)

with tab5:
    st.subheader("⚡ Live SQL Query Studio")
    query_text = st.text_area(
        "SQL Query",
        "SELECT category, sub_category, ROUND(SUM(sales), 2) AS total_sales, ROUND(SUM(profit), 2) AS total_profit FROM fact_ecommerce_sales GROUP BY category, sub_category ORDER BY total_sales DESC LIMIT 10;",
        height=120
    )
    if st.button("Execute Query"):
        engine = get_engine()
        with engine.connect() as conn:
            result_df = pd.read_sql_query(text(query_text), conn)
        st.dataframe(result_df, use_container_width=True)
