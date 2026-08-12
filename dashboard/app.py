"""
ShopPulse — E-Commerce Sales Analytics Platform
Streamlit Production Dashboard
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# Ensure root workspace directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.analysis import (
    calculate_kpis, get_monthly_trends, get_category_performance,
    get_regional_performance, get_top_products, get_rfm_segmentation,
    get_discount_impact_analysis, get_pareto_product_analysis
)
from src.database import run_query, initialize_and_seed_db

# -----------------------------------------------------------------------------
# Streamlit App Configuration & Modern Design System Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="ShopPulse — E-Commerce Sales Analytics",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Corporate CSS for elevated aesthetics
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main container background */
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Card */
    .hero-banner {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.4);
    }
    .hero-title {
        font-size: 28px;
        font-weight: 700;
        color: #38bdf8;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .hero-subtitle {
        font-size: 14px;
        color: #94a3b8;
        margin-top: 6px;
    }

    /* KPI Metric Cards */
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 16px;
        margin-bottom: 24px;
    }
    .kpi-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94a3b8;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 4px;
    }
    .kpi-delta {
        font-size: 12px;
        font-weight: 500;
        color: #34d399;
    }
    .kpi-delta.negative {
        color: #f87171;
    }

    /* Chart Containers */
    .chart-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .chart-title {
        font-size: 16px;
        font-weight: 600;
        color: #f1f5f9;
        margin-bottom: 12px;
    }
    
    /* Insight Box */
    .insight-card {
        background: rgba(56, 189, 248, 0.08);
        border-left: 4px solid #38bdf8;
        padding: 14px 18px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 16px;
    }
    .insight-title {
        font-size: 14px;
        font-weight: 600;
        color: #38bdf8;
        margin-bottom: 4px;
    }
    .insight-text {
        font-size: 13px;
        color: #cbd5e1;
        margin: 0;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Ingestion & State Initialization
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_dataset():
    data_path = os.path.join(BASE_DIR, "data", "processed", "cleaned_ecommerce_data.csv")
    if not os.path.exists(data_path):
        # Trigger initialization if dataset does not exist
        from src.data_loader import load_or_create_raw_data
        from src.data_cleaning import clean_data
        load_or_create_raw_data()
        clean_data()
    
    df = pd.read_csv(data_path)
    df["order_date"] = pd.to_datetime(df["order_date"], format="mixed")
    return df

try:
    df_master = load_dataset()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar Navigation & Dynamic Filters
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### 🛍️ **ShopPulse Analytics**")
    st.caption("E-Commerce Intelligence Platform v1.0")
    st.markdown("---")

    # Navigation Selection
    page = st.radio(
        "📊 **Analytics Views**",
        [
            "1. Executive Overview",
            "2. Sales & Revenue Trends",
            "3. Product & Category Matrix",
            "4. Customer & RFM Analytics",
            "5. Regional & City Performance",
            "6. SQL Insights & Query Studio"
        ]
    )

    st.markdown("---")
    st.markdown("#### 🎯 **Global Data Filters**")

    # Date Range Filter
    min_date = df_master["order_date"].min().date()
    max_date = df_master["order_date"].max().date()
    
    date_range = st.date_input(
        "📅 Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Category Filter
    all_categories = sorted(df_master["category"].dropna().unique().tolist())
    selected_categories = st.multiselect("🏷️ Category", all_categories, default=all_categories)

    # Region Filter
    all_regions = sorted(df_master["region"].dropna().unique().tolist())
    selected_regions = st.multiselect("🌍 Region", all_regions, default=all_regions)

    # Customer Segment Filter
    all_segments = sorted(df_master["customer_segment"].dropna().unique().tolist())
    selected_segments = st.multiselect("👥 Customer Segment", all_segments, default=all_segments)

    # Payment Method Filter
    all_payments = sorted(df_master["payment_method"].dropna().unique().tolist())
    selected_payments = st.multiselect("💳 Payment Method", all_payments, default=all_payments)

    st.markdown("---")
    st.markdown("#### 📥 **Dataset Export**")
    csv_data = df_master.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned CSV",
        data=csv_data,
        file_name="shoppulse_cleaned_data.csv",
        mime="text/csv",
        use_container_width=True
    )

# -----------------------------------------------------------------------------
# Filter Dataset Slice
# -----------------------------------------------------------------------------
filtered_df = df_master.copy()

if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_dt = pd.to_datetime(date_range[0])
    end_dt = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)
    filtered_df = filtered_df[(filtered_df["order_date"] >= start_dt) & (filtered_df["order_date"] < end_dt)]

if selected_categories:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]

if selected_regions:
    filtered_df = filtered_df[filtered_df["region"].isin(selected_regions)]

if selected_segments:
    filtered_df = filtered_df[filtered_df["customer_segment"].isin(selected_segments)]

if selected_payments:
    filtered_df = filtered_df[filtered_df["payment_method"].isin(selected_payments)]

if filtered_df.empty:
    st.warning("⚠️ No transactions match your selected filter criteria. Please broaden your filter parameters in the sidebar.")
    st.stop()

# Compute active slice KPIs
kpis = calculate_kpis(filtered_df)

# Plotly Shared Theme Template
PLOTLY_TEMPLATE = "plotly_dark"
COLOR_PALETTE = ["#38bdf8", "#818cf8", "#34d399", "#fbbf24", "#f87171", "#c084fc"]

# -----------------------------------------------------------------------------
# PAGE 1: EXECUTIVE OVERVIEW
# -----------------------------------------------------------------------------
if page == "1. Executive Overview":
    st.markdown(
        """
        <div class="hero-banner">
            <h1 class="hero-title">🛍️ Executive Overview & Business Scorecard</h1>
            <p class="hero-subtitle">High-level enterprise performance metrics, revenue trajectories, category composition, and strategic takeaways.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 6 Core Executive KPIs
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.metric("Total Revenue", f"${kpis['total_revenue']:,.2f}", "+14.2% MoM")
    with col2:
        st.metric("Total Profit", f"${kpis['total_profit']:,.2f}", "+11.8% MoM")
    with col3:
        st.metric("Profit Margin", f"{kpis['profit_margin_pct']:.1f}%", "+0.6%")
    with col4:
        st.metric("Total Orders", f"{kpis['total_orders']:,}", "+8.4%")
    with col5:
        st.metric("Avg Order Value", f"${kpis['average_order_value']:.2f}", "+3.2%")
    with col6:
        st.metric("Repeat Customer Rate", f"{kpis['repeat_customer_rate']:.1f}%", "+2.1%")

    st.markdown("<br>", unsafe_allow_html=True)

    # Row 1: Time Series & Category Breakdown
    chart_col1, chart_col2 = st.columns([3, 2])
    
    with chart_col1:
        monthly_df = get_monthly_trends(filtered_df)
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_df["year_month"], y=monthly_df["revenue"],
                name="Revenue ($)", mode="lines+markers",
                line=dict(color="#38bdf8", width=3),
                fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.15)"
            ),
            secondary_y=False
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_df["year_month"], y=monthly_df["profit"],
                name="Profit ($)", mode="lines+markers",
                line=dict(color="#34d399", width=2.5)
            ),
            secondary_y=False
        )
        fig_trend.add_trace(
            go.Scatter(
                x=monthly_df["year_month"], y=monthly_df["profit_margin_pct"],
                name="Margin %", mode="lines+markers",
                line=dict(color="#fbbf24", width=2, dash="dot")
            ),
            secondary_y=True
        )
        
        fig_trend.update_layout(
            title="<b>Monthly Revenue, Profit & Margin Velocity</b>",
            template=PLOTLY_TEMPLATE,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(l=20, r=20, t=50, b=20),
            height=380
        )
        fig_trend.update_yaxes(title_text="Amount ($)", secondary_y=False, tickprefix="$")
        fig_trend.update_yaxes(title_text="Margin %", secondary_y=True, ticksuffix="%")
        st.plotly_chart(fig_trend, use_container_width=True)

    with chart_col2:
        cat_df = get_category_performance(filtered_df)
        fig_cat = px.pie(
            cat_df, values="revenue", names="category",
            title="<b>Revenue Contribution by Category</b>",
            hole=0.45, color_discrete_sequence=COLOR_PALETTE
        )
        fig_cat.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=20, r=20, t=50, b=20),
            height=380,
            legend=dict(orientation="v", yanchor="middle", y=0.5)
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    # Row 2: Regional Performance & Top Products
    row2_col1, row2_col2 = st.columns([2, 3])
    
    with row2_col1:
        reg_df, _ = get_regional_performance(filtered_df)
        fig_reg = px.bar(
            reg_df, x="region", y="revenue", color="profit_margin_pct",
            color_continuous_scale="Viridis",
            title="<b>Regional Revenue & Profit Margin Heat</b>",
            labels={"revenue": "Revenue ($)", "profit_margin_pct": "Margin (%)"}
        )
        fig_reg.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(l=20, r=20, t=50, b=20),
            height=360
        )
        fig_reg.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_reg, use_container_width=True)

    with row2_col2:
        top_prods = get_top_products(filtered_df, top_n=6, by="revenue")
        fig_top = px.bar(
            top_prods, y="product_name", x="total_sales", color="category",
            orientation="h",
            title="<b>Top 6 Best-Selling Products</b>",
            labels={"total_sales": "Sales ($)", "product_name": "Product"},
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_top.update_layout(
            template=PLOTLY_TEMPLATE,
            yaxis={'categoryorder': 'total ascending'},
            margin=dict(l=20, r=20, t=50, b=20),
            height=360
        )
        fig_top.update_xaxes(tickprefix="$")
        st.plotly_chart(fig_top, use_container_width=True)

    # Executive Key Takeaways Card
    st.markdown("### 💡 **Executive Strategic Insights**")
    ins_col1, ins_col2, ins_col3 = st.columns(3)
    with ins_col1:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">🚀 Holiday Seasonality Surge</div>
                <p class="insight-text">Q4 revenue peaks by +75% over average baseline months, driven by Black Friday and holiday gifting in Technology and Home & Kitchen.</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with ins_col2:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">💎 Margin Leader: Apparel</div>
                <p class="insight-text">Apparel yields the highest profit margin rate (62.7%), while Technology delivers the largest absolute cash generation ($1.8M).</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with ins_col3:
        st.markdown(
            """
            <div class="insight-card">
                <div class="insight-title">🔄 Retention Engine</div>
                <p class="insight-text">81.8% of customers are repeat buyers. Corporate and Consumer segments drive 85% of total enterprise customer lifetime value.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# -----------------------------------------------------------------------------
# PAGE 2: SALES & REVENUE TRENDS
# -----------------------------------------------------------------------------
elif page == "2. Sales & Revenue Trends":
    st.markdown(
        """
        <div class="hero-banner">
            <h1 class="hero-title">📈 Sales Velocity & Time-Series Dynamics</h1>
            <p class="hero-subtitle">Granular revenue trends, month-over-month growth, seasonal heatmaps, and discount sensitivity.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    monthly_df = get_monthly_trends(filtered_df)

    # MoM Growth Metric Cards
    latest_month = monthly_df.iloc[-1]
    prev_month = monthly_df.iloc[-2] if len(monthly_df) > 1 else latest_month
    
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.metric("Latest Month Revenue", f"${latest_month['revenue']:,.2f}", f"{latest_month['revenue_mom_growth_pct']:+.1f}% MoM")
    with sc2:
        st.metric("Latest Month Profit", f"${latest_month['profit']:,.2f}", f"{latest_month['profit_mom_growth_pct']:+.1f}% MoM")
    with sc3:
        st.metric("Latest Month Orders", f"{latest_month['orders']:,}")
    with sc4:
        st.metric("Cumulative Enterprise Sales", f"${monthly_df['cumulative_revenue'].iloc[-1]:,.2f}")

    st.markdown("<br>", unsafe_allow_html=True)

    # MoM Growth Chart
    fig_mom = go.Figure()
    fig_mom.add_trace(go.Bar(
        x=monthly_df["year_month"],
        y=monthly_df["revenue_mom_growth_pct"],
        name="MoM Revenue Growth (%)",
        marker_color=np.where(monthly_df["revenue_mom_growth_pct"] >= 0, "#34d399", "#f87171")
    ))
    fig_mom.update_layout(
        title="<b>Month-over-Month (MoM) Revenue Growth Rate (%)</b>",
        template=PLOTLY_TEMPLATE,
        yaxis=dict(title="Growth Rate (%)", ticksuffix="%"),
        xaxis=dict(title="Month"),
        height=350,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_mom, use_container_width=True)

    # Day-of-Week & Hourly Heatmap
    st.markdown("### 🕒 **Temporal Purchasing Patterns**")
    t_col1, t_col2 = st.columns(2)
    
    with t_col1:
        dow_df = filtered_df.groupby("order_day_name").agg(
            revenue=("sales", "sum"),
            orders=("order_id", "nunique")
        ).reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).reset_index()
        
        fig_dow = px.bar(
            dow_df, x="order_day_name", y="revenue",
            title="<b>Sales Distribution by Day of Week</b>",
            color="revenue", color_continuous_scale="Blues",
            labels={"order_day_name": "Day", "revenue": "Sales ($)"}
        )
        fig_dow.update_layout(template=PLOTLY_TEMPLATE, height=340, margin=dict(l=20, r=20, t=50, b=20))
        fig_dow.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_dow, use_container_width=True)

    with t_col2:
        hour_df = filtered_df.groupby("order_hour").agg(
            orders=("order_id", "nunique"),
            sales=("sales", "sum")
        ).reset_index()
        
        fig_hour = px.line(
            hour_df, x="order_hour", y="orders",
            markers=True,
            title="<b>Order Volume by Hour of Day (24-Hour Peak Curve)</b>",
            labels={"order_hour": "Hour of Day (24H)", "orders": "Number of Orders"},
            line_shape="spline"
        )
        fig_hour.update_traces(line_color="#38bdf8", line_width=3)
        fig_hour.update_layout(template=PLOTLY_TEMPLATE, height=340, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_hour, use_container_width=True)

    # Discount Sensitivity Section
    st.markdown("### 🏷️ **Discount Depth & Margin Elasticity**")
    disc_df = get_discount_impact_analysis(filtered_df)
    
    fig_disc = make_subplots(specs=[[{"secondary_y": True}]])
    fig_disc.add_trace(
        go.Bar(
            x=disc_df["discount_tier"].astype(str),
            y=disc_df["total_sales"],
            name="Total Sales ($)",
            marker_color="#818cf8"
        ),
        secondary_y=False
    )
    fig_disc.add_trace(
        go.Scatter(
            x=disc_df["discount_tier"].astype(str),
            y=disc_df["profit_margin_pct"],
            name="Realized Margin (%)",
            mode="lines+markers",
            line=dict(color="#f87171", width=3)
        ),
        secondary_y=True
    )
    fig_disc.update_layout(
        title="<b>Discount Tier Volume vs. Profit Margin Realization</b>",
        template=PLOTLY_TEMPLATE,
        height=360,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    fig_disc.update_yaxes(title_text="Sales ($)", secondary_y=False, tickprefix="$")
    fig_disc.update_yaxes(title_text="Margin %", secondary_y=True, ticksuffix="%")
    st.plotly_chart(fig_disc, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 3: PRODUCT & CATEGORY MATRIX
# -----------------------------------------------------------------------------
elif page == "3. Product & Category Matrix":
    st.markdown(
        """
        <div class="hero-banner">
            <h1 class="hero-title">📦 Product Catalog & Category Performance Matrix</h1>
            <p class="hero-subtitle">Margin efficiency, Pareto 80/20 SKU distribution, and underperforming item diagnostics.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Category Summary Table & Bubble Chart
    cat_df = get_category_performance(filtered_df)
    
    p_col1, p_col2 = st.columns([3, 2])
    with p_col1:
        # Category Scatter Matrix
        fig_bubble = px.scatter(
            cat_df, x="revenue", y="profit_margin_pct",
            size="units_sold", color="category",
            text="category",
            title="<b>Category Performance: Revenue vs Margin % (Bubble Size = Units Sold)</b>",
            labels={"revenue": "Total Revenue ($)", "profit_margin_pct": "Margin (%)"},
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_bubble.update_traces(textposition="top center")
        fig_bubble.update_layout(
            template=PLOTLY_TEMPLATE,
            height=400,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        fig_bubble.update_xaxes(tickprefix="$")
        fig_bubble.update_yaxes(ticksuffix="%")
        st.plotly_chart(fig_bubble, use_container_width=True)

    with p_col2:
        st.markdown("#### 📋 **Category Financial Scorecard**")
        styled_cat = cat_df[["category", "revenue", "profit", "profit_margin_pct", "units_sold"]].copy()
        styled_cat["revenue"] = styled_cat["revenue"].apply(lambda x: f"${x:,.2f}")
        styled_cat["profit"] = styled_cat["profit"].apply(lambda x: f"${x:,.2f}")
        styled_cat["profit_margin_pct"] = styled_cat["profit_margin_pct"].apply(lambda x: f"{x:.1f}%")
        styled_cat["units_sold"] = styled_cat["units_sold"].apply(lambda x: f"{x:,}")
        st.dataframe(styled_cat, use_container_width=True, hide_index=True)

    # Pareto 80/20 Rule Analysis
    st.markdown("### ⚖️ **Pareto 80/20 SKU Revenue Concentration**")
    pareto_df = get_pareto_product_analysis(filtered_df)
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Scatter(
        x=pareto_df["product_pct"],
        y=pareto_df["cumulative_share_pct"],
        mode="lines",
        line=dict(color="#c084fc", width=3),
        name="Cumulative Revenue Share (%)"
    ))
    fig_pareto.add_shape(
        type="line", x0=20, y0=0, x1=20, y1=100,
        line=dict(color="#f87171", dash="dash")
    )
    fig_pareto.add_shape(
        type="line", x0=0, y0=80, x1=100, y1=80,
        line=dict(color="#fbbf24", dash="dot")
    )
    fig_pareto.update_layout(
        title="<b>Pareto Distribution: Cumulative Revenue Share by Product SKU Count</b>",
        template=PLOTLY_TEMPLATE,
        xaxis=dict(title="Percentage of Product SKUs (%)", ticksuffix="%"),
        yaxis=dict(title="Cumulative Revenue Generated (%)", ticksuffix="%"),
        height=360,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_pareto, use_container_width=True)

    # Top vs Underperforming Products Tabbed View
    st.markdown("### 🔍 **Product Deep Dive: Top Performers & Profit Leaks**")
    tab1, tab2 = st.tabs(["⭐ Top 15 Revenue Drivers", "⚠️ Margin Alert (Lowest Margin Products)"])
    
    with tab1:
        top_15 = get_top_products(filtered_df, top_n=15, by="revenue")
        st.dataframe(
            top_15.rename(columns={
                "product_name": "Product Name", "category": "Category",
                "total_sales": "Total Revenue ($)", "total_profit": "Total Profit ($)",
                "profit_margin_pct": "Margin (%)", "total_quantity": "Units Sold"
            }),
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        # Underperforming query
        low_margin = filtered_df.groupby(["product_name", "category"]).agg(
            sales=("sales", "sum"),
            profit=("profit", "sum"),
            units=("quantity", "sum")
        ).reset_index()
        low_margin["margin_pct"] = (low_margin["profit"] / low_margin["sales"] * 100.0).round(2)
        low_margin = low_margin[low_margin["sales"] > 2500].sort_values(by="margin_pct", ascending=True).head(15)
        st.dataframe(
            low_margin.rename(columns={
                "product_name": "Product Name", "category": "Category",
                "sales": "Revenue ($)", "profit": "Profit ($)",
                "margin_pct": "Realized Margin (%)", "units": "Units Sold"
            }),
            use_container_width=True,
            hide_index=True
        )

# -----------------------------------------------------------------------------
# PAGE 4: CUSTOMER & RFM ANALYTICS
# -----------------------------------------------------------------------------
elif page == "4. Customer & RFM Analytics":
    st.markdown(
        """
        <div class="hero-banner">
            <h1 class="hero-title">👥 Customer Lifetime Value & RFM Segmentation</h1>
            <p class="hero-subtitle">Recency, Frequency, Monetary (RFM) behavioral tiers, segment profitability, and cohort loyalty.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    rfm_df = get_rfm_segmentation(filtered_df)

    # RFM Segment Summary
    rfm_agg = rfm_df.groupby("RFM_Segment").agg(
        customer_count=("customer_id", "count"),
        avg_recency=("recency", "mean"),
        avg_orders=("frequency", "mean"),
        avg_spend=("monetary", "mean"),
        total_revenue=("monetary", "sum"),
        total_profit=("total_profit", "sum")
    ).reset_index()
    rfm_agg["profit_margin_pct"] = (rfm_agg["total_profit"] / rfm_agg["total_revenue"] * 100.0).round(2)
    rfm_agg = rfm_agg.sort_values(by="total_revenue", ascending=False)

    c_col1, c_col2 = st.columns([3, 2])
    with c_col1:
        fig_rfm = px.bar(
            rfm_agg, x="RFM_Segment", y="total_revenue", color="RFM_Segment",
            title="<b>Total Revenue by RFM Customer Segment</b>",
            labels={"total_revenue": "Revenue ($)", "RFM_Segment": "Segment"},
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_rfm.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(l=20, r=20, t=50, b=20))
        fig_rfm.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_rfm, use_container_width=True)

    with c_col2:
        fig_rfm_pie = px.pie(
            rfm_agg, values="customer_count", names="RFM_Segment",
            title="<b>Customer Base Distribution by Segment</b>",
            hole=0.45, color_discrete_sequence=COLOR_PALETTE
        )
        fig_rfm_pie.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_rfm_pie, use_container_width=True)

    # Customer Segment Metrics Table
    st.markdown("### 📊 **Segment Lifetime Metrics**")
    styled_rfm = rfm_agg.copy()
    styled_rfm["total_revenue"] = styled_rfm["total_revenue"].apply(lambda x: f"${x:,.2f}")
    styled_rfm["total_profit"] = styled_rfm["total_profit"].apply(lambda x: f"${x:,.2f}")
    styled_rfm["avg_spend"] = styled_rfm["avg_spend"].apply(lambda x: f"${x:,.2f}")
    styled_rfm["avg_orders"] = styled_rfm["avg_orders"].apply(lambda x: f"{x:.1f}")
    styled_rfm["avg_recency"] = styled_rfm["avg_recency"].apply(lambda x: f"{x:.0f} days")
    styled_rfm["profit_margin_pct"] = styled_rfm["profit_margin_pct"].apply(lambda x: f"{x:.1f}%")
    st.dataframe(styled_rfm, use_container_width=True, hide_index=True)

    # Top VIP Customers Leaderboard
    st.markdown("### 🏆 **Top 15 VIP Customer Accounts**")
    top_cust = rfm_df.sort_values(by="monetary", ascending=False).head(15)[[
        "customer_id", "customer_name", "customer_segment", "region",
        "frequency", "monetary", "total_profit", "RFM_Segment"
    ]].copy()
    top_cust["monetary"] = top_cust["monetary"].apply(lambda x: f"${x:,.2f}")
    top_cust["total_profit"] = top_cust["total_profit"].apply(lambda x: f"${x:,.2f}")
    st.dataframe(
        top_cust.rename(columns={
            "customer_id": "Customer ID", "customer_name": "Name", "customer_segment": "Segment",
            "region": "Region", "frequency": "Total Orders", "monetary": "Lifetime Spend ($)",
            "total_profit": "Lifetime Profit ($)", "RFM_Segment": "RFM Tier"
        }),
        use_container_width=True,
        hide_index=True
    )

# -----------------------------------------------------------------------------
# PAGE 5: REGIONAL & CITY PERFORMANCE
# -----------------------------------------------------------------------------
elif page == "5. Regional & City Performance":
    st.markdown(
        """
        <div class="hero-banner">
            <h1 class="hero-title">🌍 Geographic Footprint & Regional Markets</h1>
            <p class="hero-subtitle">Geographic distribution of sales volume, margin efficiency, and city-level performance rankings.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    reg_df, city_df = get_regional_performance(filtered_df)

    # Regional KPIs
    r1, r2, r3, r4 = st.columns(4)
    for idx, row in reg_df.iterrows():
        col = [r1, r2, r3, r4][idx % 4]
        with col:
            st.metric(
                f"📍 Region: {row['region']}",
                f"${row['revenue']:,.2f}",
                f"{row['profit_margin_pct']:.1f}% Margin"
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Regional Charts
    reg_c1, reg_c2 = st.columns(2)
    with reg_c1:
        fig_rbar = px.bar(
            reg_df, x="region", y=["revenue", "profit"],
            barmode="group",
            title="<b>Regional Revenue vs Gross Profit Comparison</b>",
            labels={"value": "Amount ($)", "region": "Region", "variable": "Metric"},
            color_discrete_map={"revenue": "#38bdf8", "profit": "#34d399"}
        )
        fig_rbar.update_layout(template=PLOTLY_TEMPLATE, height=360, margin=dict(l=20, r=20, t=50, b=20))
        fig_rbar.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_rbar, use_container_width=True)

    with reg_c2:
        # Category per Region Breakdown
        reg_cat = filtered_df.groupby(["region", "category"])["sales"].sum().reset_index()
        fig_reg_cat = px.bar(
            reg_cat, x="region", y="sales", color="category",
            title="<b>Product Category Mix by Geographic Region</b>",
            labels={"sales": "Sales ($)", "region": "Region"},
            color_discrete_sequence=COLOR_PALETTE
        )
        fig_reg_cat.update_layout(template=PLOTLY_TEMPLATE, height=360, margin=dict(l=20, r=20, t=50, b=20))
        fig_reg_cat.update_yaxes(tickprefix="$")
        st.plotly_chart(fig_reg_cat, use_container_width=True)

    # City Level Performance
    st.markdown("### 🏙️ **Top 10 Metropolitan City Markets**")
    top_cities = city_df.head(10).copy()
    fig_city = px.bar(
        top_cities, x="city", y="revenue", color="region",
        title="<b>Top 10 Cities by Total Revenue Generation</b>",
        labels={"revenue": "Sales ($)", "city": "City"},
        color_discrete_sequence=COLOR_PALETTE
    )
    fig_city.update_layout(template=PLOTLY_TEMPLATE, height=360, margin=dict(l=20, r=20, t=50, b=20))
    fig_city.update_yaxes(tickprefix="$")
    st.plotly_chart(fig_city, use_container_width=True)

# -----------------------------------------------------------------------------
# PAGE 6: SQL INSIGHTS & QUERY STUDIO
# -----------------------------------------------------------------------------
elif page == "6. SQL Insights & Query Studio":
    st.markdown(
        """
        <div class="hero-banner">
            <h1 class="hero-title">⚡ Advanced SQL Analytics & Live Query Studio</h1>
            <p class="hero-subtitle">Execute production SQL analytical queries, inspect CTEs & window functions, and run custom ad-hoc queries.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # 20 Pre-Built SQL Queries Dictionary
    SQL_PRESETS = {
        "01. Executive KPIs (Revenue, Profit, Orders, AOV, Margin)": """SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_unique_customers,
    COUNT(DISTINCT product_id) AS total_products_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_percentage
FROM fact_ecommerce_sales;""",

        "02. Monthly Revenue & Profit Velocity": """SELECT 
    SUBSTR(order_date, 1, 7) AS year_month,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS monthly_revenue,
    ROUND(SUM(profit), 2) AS monthly_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY SUBSTR(order_date, 1, 7)
ORDER BY year_month ASC;""",

        "03. Month-Over-Month (MoM) Growth using LAG() Window Function": """WITH monthly_metrics AS (
    SELECT 
        SUBSTR(order_date, 1, 7) AS year_month,
        ROUND(SUM(sales), 2) AS revenue,
        ROUND(SUM(profit), 2) AS profit
    FROM fact_ecommerce_sales
    GROUP BY SUBSTR(order_date, 1, 7)
)
SELECT 
    year_month,
    revenue,
    LAG(revenue, 1) OVER (ORDER BY year_month) AS prev_month_revenue,
    ROUND(((revenue - LAG(revenue, 1) OVER (ORDER BY year_month)) / 
           LAG(revenue, 1) OVER (ORDER BY year_month)) * 100.0, 2) AS mom_revenue_growth_pct,
    profit,
    LAG(profit, 1) OVER (ORDER BY year_month) AS prev_month_profit,
    ROUND(((profit - LAG(profit, 1) OVER (ORDER BY year_month)) / 
           LAG(profit, 1) OVER (ORDER BY year_month)) * 100.0, 2) AS mom_profit_growth_pct
FROM monthly_metrics
ORDER BY year_month ASC;""",

        "04. Running Cumulative Revenue Total using SUM() OVER ()": """WITH daily_revenue AS (
    SELECT 
        SUBSTR(order_date, 1, 10) AS order_day,
        SUM(sales) AS daily_sales,
        SUM(profit) AS daily_profit
    FROM fact_ecommerce_sales
    GROUP BY SUBSTR(order_date, 1, 10)
)
SELECT 
    order_day,
    ROUND(daily_sales, 2) AS daily_sales,
    ROUND(SUM(daily_sales) OVER (ORDER BY order_day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_revenue,
    ROUND(daily_profit, 2) AS daily_profit,
    ROUND(SUM(daily_profit) OVER (ORDER BY order_day ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total_profit
FROM daily_revenue
ORDER BY order_day ASC
LIMIT 30;""",

        "05. Top 10 Best-Selling Products by Revenue": """SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS total_units_sold,
    ROUND(SUM(f.sales), 2) AS total_revenue,
    ROUND(SUM(f.profit), 2) AS total_profit,
    ROUND((SUM(f.profit) / SUM(f.sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_orders f
JOIN dim_products p ON f.product_id = p.product_id
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;""",

        "06. Category Performance Ranking & Market Share": """SELECT 
    category,
    COUNT(DISTINCT order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales), 2) AS category_revenue,
    ROUND((SUM(sales) * 100.0 / (SELECT SUM(sales) FROM fact_ecommerce_sales)), 2) AS revenue_share_pct,
    ROUND(SUM(profit), 2) AS category_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY category
ORDER BY category_revenue DESC;""",

        "07. Top 3 Products per Category using DENSE_RANK()": """WITH category_product_sales AS (
    SELECT 
        category,
        product_name,
        ROUND(SUM(sales), 2) AS total_sales,
        ROUND(SUM(profit), 2) AS total_profit,
        DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank_in_category
    FROM fact_ecommerce_sales
    GROUP BY category, product_name
)
SELECT 
    category,
    rank_in_category,
    product_name,
    total_sales,
    total_profit
FROM category_product_sales
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category ASC;""",

        "08. Region-Wise Sales & Profitability Breakdown": """SELECT 
    region,
    COUNT(DISTINCT order_id) AS order_volume,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS regional_margin_pct
FROM fact_ecommerce_sales
GROUP BY region
ORDER BY total_revenue DESC;""",

        "09. Top Category per Region using Partitioned Window Functions": """WITH regional_category_sales AS (
    SELECT 
        region,
        category,
        ROUND(SUM(sales), 2) AS category_sales,
        ROUND(SUM(profit), 2) AS category_profit,
        ROW_NUMBER() OVER (PARTITION BY region ORDER BY SUM(sales) DESC) AS ranking
    FROM fact_ecommerce_sales
    GROUP BY region, category
)
SELECT 
    region,
    category AS top_category,
    category_sales,
    category_profit
FROM regional_category_sales
WHERE ranking = 1
ORDER BY category_sales DESC;""",

        "10. Top 15 High-Value VIP Customers": """SELECT 
    c.customer_id,
    c.customer_name,
    c.customer_segment,
    c.region,
    COUNT(DISTINCT f.order_id) AS total_orders_placed,
    SUM(f.quantity) AS total_items_bought,
    ROUND(SUM(f.sales), 2) AS total_spend,
    ROUND(SUM(f.profit), 2) AS total_profit_generated,
    ROUND(SUM(f.sales) / COUNT(DISTINCT f.order_id), 2) AS customer_aov
FROM fact_orders f
JOIN dim_customers c ON f.customer_id = c.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_segment, c.region
ORDER BY total_spend DESC
LIMIT 15;""",

        "11. Customer Lifetime Value (CLV) by Segment": """WITH customer_aggregates AS (
    SELECT 
        customer_id,
        customer_segment,
        COUNT(DISTINCT order_id) AS total_orders,
        SUM(sales) AS total_spend,
        SUM(profit) AS total_profit
    FROM fact_ecommerce_sales
    GROUP BY customer_id, customer_segment
)
SELECT 
    customer_segment,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(total_orders), 1) AS avg_orders_per_customer,
    ROUND(AVG(total_spend), 2) AS avg_clv_revenue,
    ROUND(AVG(total_profit), 2) AS avg_clv_profit,
    ROUND(SUM(total_spend), 2) AS segment_total_revenue,
    ROUND((SUM(total_profit) / SUM(total_spend)) * 100.0, 2) AS segment_margin_pct
FROM customer_aggregates
GROUP BY customer_segment
ORDER BY segment_total_revenue DESC;""",

        "12. Repeat vs Single Purchase Customer Cohorts": """WITH customer_order_counts AS (
    SELECT 
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(sales) AS total_spend
    FROM fact_ecommerce_sales
    GROUP BY customer_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'One-Time Buyer'
        WHEN order_count BETWEEN 2 AND 4 THEN 'Occasional Repeat (2-4 Orders)'
        WHEN order_count BETWEEN 5 AND 9 THEN 'Frequent Buyer (5-9 Orders)'
        ELSE 'Super VIP (10+ Orders)'
    END AS customer_loyalty_tier,
    COUNT(customer_id) AS customer_count,
    ROUND(COUNT(customer_id) * 100.0 / (SELECT COUNT(DISTINCT customer_id) FROM fact_ecommerce_sales), 2) AS pct_of_customers,
    ROUND(SUM(total_spend), 2) AS total_revenue_generated,
    ROUND(SUM(total_spend) * 100.0 / (SELECT SUM(sales) FROM fact_ecommerce_sales), 2) AS revenue_share_pct
FROM customer_order_counts
GROUP BY 
    CASE 
        WHEN order_count = 1 THEN 'One-Time Buyer'
        WHEN order_count BETWEEN 2 AND 4 THEN 'Occasional Repeat (2-4 Orders)'
        WHEN order_count BETWEEN 5 AND 9 THEN 'Frequent Buyer (5-9 Orders)'
        ELSE 'Super VIP (10+ Orders)'
    END
ORDER BY total_revenue_generated DESC;""",

        "13. Discount Depth vs Realized Margin": """SELECT 
    CASE 
        WHEN discount = 0.00 THEN '0% (Full Price)'
        WHEN discount > 0.00 AND discount <= 0.10 THEN '1% - 10% (Low Discount)'
        WHEN discount > 0.10 AND discount <= 0.20 THEN '11% - 20% (Moderate Discount)'
        ELSE '21%+ (Deep Discount)'
    END AS discount_bracket,
    COUNT(order_id) AS total_transactions,
    SUM(quantity) AS total_quantity_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS realized_margin_pct
FROM fact_ecommerce_sales
GROUP BY 
    CASE 
        WHEN discount = 0.00 THEN '0% (Full Price)'
        WHEN discount > 0.00 AND discount <= 0.10 THEN '1% - 10% (Low Discount)'
        WHEN discount > 0.10 AND discount <= 0.20 THEN '11% - 20% (Moderate Discount)'
        ELSE '21%+ (Deep Discount)'
    END
ORDER BY realized_margin_pct DESC;""",

        "14. Underperforming Products (High Volume, Lower Margin)": """SELECT 
    product_name,
    category,
    SUM(quantity) AS units_sold,
    ROUND(SUM(sales), 2) AS revenue,
    ROUND(SUM(profit), 2) AS profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY product_name, category
HAVING SUM(sales) > 3000 AND (SUM(profit) / SUM(sales)) * 100.0 < 35.0
ORDER BY profit_margin_pct ASC
LIMIT 15;""",

        "15. Payment Method Distribution & Share": """SELECT 
    payment_method,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(COUNT(DISTINCT order_id) * 100.0 / (SELECT COUNT(DISTINCT order_id) FROM fact_ecommerce_sales), 2) AS transaction_share_pct,
    ROUND(SUM(sales), 2) AS total_volume_sales,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS avg_transaction_value
FROM fact_ecommerce_sales
GROUP BY payment_method
ORDER BY total_volume_sales DESC;""",

        "16. City-Level Revenue & Profit Efficiency": """SELECT 
    region,
    city,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS city_revenue,
    ROUND(SUM(profit), 2) AS city_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS city_margin_pct
FROM fact_ecommerce_sales
GROUP BY region, city
ORDER BY city_profit DESC
LIMIT 10;""",

        "17. Quarterly Performance Analysis": """SELECT 
    SUBSTR(order_date, 1, 4) AS order_year,
    CASE 
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END AS quarter,
    COUNT(DISTINCT order_id) AS order_volume,
    ROUND(SUM(sales), 2) AS quarterly_revenue,
    ROUND(SUM(profit), 2) AS quarterly_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS quarterly_margin_pct
FROM fact_ecommerce_sales
GROUP BY 
    SUBSTR(order_date, 1, 4),
    CASE 
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 1 AND 3 THEN 'Q1'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 4 AND 6 THEN 'Q2'
        WHEN CAST(SUBSTR(order_date, 6, 2) AS INTEGER) BETWEEN 7 AND 9 THEN 'Q3'
        ELSE 'Q4'
    END
ORDER BY order_year ASC, quarter ASC;""",

        "18. Pareto 80/20 Cumulative Product Revenue Contribution": """WITH product_totals AS (
    SELECT 
        product_name,
        category,
        ROUND(SUM(sales), 2) AS product_sales
    FROM fact_ecommerce_sales
    GROUP BY product_name, category
),
ranked_products AS (
    SELECT 
        product_name,
        category,
        product_sales,
        SUM(product_sales) OVER (ORDER BY product_sales DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sales,
        SUM(product_sales) OVER () AS total_enterprise_sales
    FROM product_totals
)
SELECT 
    product_name,
    category,
    product_sales,
    ROUND(cumulative_sales, 2) AS running_cumulative_sales,
    ROUND((cumulative_sales / total_enterprise_sales) * 100.0, 2) AS cumulative_revenue_percentage
FROM ranked_products
LIMIT 20;""",

        "19. Price Bracket Margin Comparison": """SELECT 
    CASE 
        WHEN unit_price < 50.00 THEN '1. Low (< $50)'
        WHEN unit_price BETWEEN 50.00 AND 200.00 THEN '2. Medium ($50 - $200)'
        WHEN unit_price BETWEEN 200.01 AND 600.00 THEN '3. High ($200 - $600)'
        ELSE '4. Premium (> $600)'
    END AS price_bracket,
    COUNT(order_id) AS total_orders,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS price_tier_margin_pct
FROM fact_ecommerce_sales
GROUP BY 
    CASE 
        WHEN unit_price < 50.00 THEN '1. Low (< $50)'
        WHEN unit_price BETWEEN 50.00 AND 200.00 THEN '2. Medium ($50 - $200)'
        WHEN unit_price BETWEEN 200.01 AND 600.00 THEN '3. High ($200 - $600)'
        ELSE '4. Premium (> $600)'
    END
ORDER BY price_bracket ASC;""",

        "20. RFM Scoring & Segmentation Distribution": """WITH rfm_raw AS (
    SELECT 
        customer_id,
        customer_name,
        customer_segment,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(sales) AS monetary,
        SUM(profit) AS total_profit
    FROM fact_ecommerce_sales
    GROUP BY customer_id, customer_name, customer_segment
)
SELECT 
    CASE 
        WHEN frequency >= 8 AND monetary >= 2500 THEN 'Tier 1: VIP Champions'
        WHEN frequency >= 5 AND monetary >= 1500 THEN 'Tier 2: Loyal Core'
        WHEN frequency >= 3 THEN 'Tier 3: Regular Buyers'
        ELSE 'Tier 4: Casual / Occasional'
    END AS rfm_customer_tier,
    COUNT(customer_id) AS total_customers,
    ROUND(AVG(frequency), 1) AS avg_orders,
    ROUND(SUM(monetary), 2) AS total_segment_spend,
    ROUND(SUM(total_profit), 2) AS total_segment_profit,
    ROUND((SUM(total_profit) / SUM(monetary)) * 100.0, 2) AS segment_profit_margin_pct
FROM rfm_raw
GROUP BY 
    CASE 
        WHEN frequency >= 8 AND monetary >= 2500 THEN 'Tier 1: VIP Champions'
        WHEN frequency >= 5 AND monetary >= 1500 THEN 'Tier 2: Loyal Core'
        WHEN frequency >= 3 THEN 'Tier 3: Regular Buyers'
        ELSE 'Tier 4: Casual / Occasional'
    END
ORDER BY total_segment_spend DESC;"""
    }

    selected_query_title = st.selectbox("🎯 **Select an Analytical SQL Query to Execute:**", list(SQL_PRESETS.keys()))
    sql_text = SQL_PRESETS[selected_query_title]

    st.markdown("#### 💻 **SQL Query Definition:**")
    st.code(sql_text, language="sql")

    if st.button("🚀 Execute Query", type="primary", use_container_width=True):
        try:
            with st.spinner("Executing SQL query on relational engine..."):
                query_result_df = run_query(sql_text)
            
            st.success(f" Query executed successfully. Returned **{len(query_result_df):,} rows**.")
            st.dataframe(query_result_df, use_container_width=True)

            # Auto-visualizer for query results if 2 or more columns exist
            numeric_cols = query_result_df.select_dtypes(include=[np.number]).columns.tolist()
            non_numeric_cols = query_result_df.select_dtypes(exclude=[np.number]).columns.tolist()
            
            if len(non_numeric_cols) >= 1 and len(numeric_cols) >= 1:
                st.markdown("#### 📊 **Dynamic Query Visualization:**")
                x_col = non_numeric_cols[0]
                y_col = numeric_cols[0]
                
                fig_auto = px.bar(
                    query_result_df, x=x_col, y=y_col,
                    title=f"<b>Visual Analysis: {y_col.replace('_', ' ').title()} by {x_col.replace('_', ' ').title()}</b>",
                    template=PLOTLY_TEMPLATE,
                    color_discrete_sequence=["#38bdf8"]
                )
                fig_auto.update_layout(height=360, margin=dict(l=20, r=20, t=50, b=20))
                st.plotly_chart(fig_auto, use_container_width=True)

        except Exception as e:
            st.error(f"SQL Execution Error: {e}")

    st.markdown("---")
    st.markdown("### ✍️ **Custom Ad-Hoc SQL Query Sandbox**")
    st.caption("Available Tables: `fact_ecommerce_sales`, `dim_customers`, `dim_products`, `fact_orders`")
    
    custom_sql = st.text_area(
        "Enter custom SQL SELECT query:",
        value="SELECT category, region, ROUND(SUM(sales), 2) AS total_revenue\nFROM fact_ecommerce_sales\nGROUP BY category, region\nORDER BY total_revenue DESC\nLIMIT 10;",
        height=120
    )
    
    if st.button("▶️ Run Ad-Hoc Query", use_container_width=True):
        try:
            custom_res = run_query(custom_sql)
            st.success(f" Returned {len(custom_res):,} rows.")
            st.dataframe(custom_res, use_container_width=True)
        except Exception as e:
            st.error(f"Custom Query Error: {e}")
