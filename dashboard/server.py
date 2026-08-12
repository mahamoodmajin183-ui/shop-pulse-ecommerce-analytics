"""
ShopPulse - Real E-Commerce Analytics Web Application Server
Serves dynamic visual dashboards, KPI scorecards, interactive charts, and Live SQL Query Studio
computed strictly from the verified real dataset.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, jsonify, request, send_file, render_template_string
from sqlalchemy import text

from src.database import get_engine, initialize_and_seed_db
from src.analysis import (
    load_cleaned_data, calculate_kpis, get_monthly_trends,
    get_category_performance, get_regional_performance,
    get_top_products, get_discount_impact_analysis, get_rfm_segmentation
)

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, "data", "processed", "cleaned_ecommerce_data.csv")

# Ensure clean data exists
if not os.path.exists(CSV_PATH):
    from src.data_cleaning import clean_data
    clean_data()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopPulse — E-Commerce Sales Analytics Platform</title>
    <meta name="description" content="Production-quality E-Commerce Sales Analytics Platform built with Python, SQL, and Star Schema modeling on real transaction data.">
    <!-- Google Fonts & Font Awesome -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #090d16;
            --bg-surface: #0f172a;
            --bg-card: #1e293b;
            --bg-hover: #334155;
            --border-color: rgba(255, 255, 255, 0.08);
            --primary: #0284c7;
            --primary-glow: rgba(2, 132, 199, 0.25);
            --teal: #0d9488;
            --emerald: #10b981;
            --rose: #f43f5e;
            --amber: #f59e0b;
            --indigo: #6366f1;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
            --sidebar-width: 260px;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: var(--bg-base);
            color: var(--text-main);
            display: flex;
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* Sidebar Styles */
        .sidebar {
            width: var(--sidebar-width);
            background: var(--bg-surface);
            border-right: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            position: fixed;
            top: 0;
            bottom: 0;
            left: 0;
            z-index: 100;
            padding: 24px 16px;
        }

        .brand-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--border-color);
        }

        .brand-logo {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            color: #fff;
            box-shadow: 0 0 15px var(--primary-glow);
        }

        .brand-title {
            font-size: 19px;
            font-weight: 800;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #fff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-badge {
            font-size: 10px;
            padding: 2px 6px;
            background: rgba(16, 185, 129, 0.15);
            color: var(--emerald);
            border: 1px solid rgba(16, 185, 129, 0.3);
            border-radius: 4px;
            font-weight: 700;
            text-transform: uppercase;
        }

        .nav-section {
            margin-top: 24px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            flex: 1;
        }

        .nav-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            margin: 12px 12px 4px;
            font-weight: 700;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 10px 14px;
            border-radius: 8px;
            color: var(--text-muted);
            text-decoration: none;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s ease;
            cursor: pointer;
        }

        .nav-item:hover, .nav-item.active {
            background: var(--bg-card);
            color: #fff;
            border-left: 3px solid var(--primary);
        }

        .nav-item i {
            font-size: 16px;
            width: 20px;
        }

        /* Filter Panel in Sidebar */
        .filter-box {
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 14px;
            margin-top: 16px;
        }

        .filter-box label {
            font-size: 11px;
            color: var(--text-muted);
            display: block;
            margin-bottom: 6px;
            font-weight: 600;
            text-transform: uppercase;
        }

        .filter-select {
            width: 100%;
            padding: 8px 10px;
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            color: #fff;
            font-size: 13px;
            outline: none;
            margin-bottom: 10px;
            cursor: pointer;
        }

        /* Main Content Layout */
        .main-container {
            margin-left: var(--sidebar-width);
            flex: 1;
            padding: 32px;
            max-width: 1600px;
        }

        .top-navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 28px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .page-header h1 {
            font-size: 24px;
            font-weight: 800;
            letter-spacing: -0.5px;
        }

        .page-header p {
            font-size: 13px;
            color: var(--text-muted);
            margin-top: 2px;
        }

        .action-btns {
            display: flex;
            gap: 12px;
        }

        .btn-primary {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 9px 16px;
            background: linear-gradient(135deg, var(--primary) 0%, #0369a1 100%);
            border: none;
            border-radius: 8px;
            color: #fff;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            box-shadow: 0 4px 12px var(--primary-glow);
            transition: all 0.2s ease;
        }

        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 16px var(--primary-glow);
        }

        /* KPI Cards Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-bottom: 28px;
        }

        .kpi-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            position: relative;
            overflow: hidden;
            transition: transform 0.2s ease, border-color 0.2s ease;
        }

        .kpi-card:hover {
            transform: translateY(-2px);
            border-color: rgba(2, 132, 199, 0.4);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--primary) 0%, var(--teal) 100%);
        }

        .kpi-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .kpi-value {
            font-size: 26px;
            font-weight: 800;
            margin: 10px 0 4px;
            letter-spacing: -0.5px;
        }

        .kpi-subtext {
            font-size: 11.5px;
            color: var(--text-muted);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .text-success { color: var(--emerald); }
        .text-danger { color: var(--rose); }

        /* Charts Layout */
        .chart-grid-2 {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        .chart-grid-half {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        .chart-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
        }

        .chart-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 16px;
        }

        .chart-title {
            font-size: 15px;
            font-weight: 700;
        }

        .chart-subtitle {
            font-size: 12px;
            color: var(--text-muted);
        }

        /* SQL Studio Workspace */
        .sql-workspace {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 28px;
        }

        .sql-editor {
            width: 100%;
            height: 140px;
            background: #060911;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            color: #38bdf8;
            font-family: 'JetBrains Mono', monospace;
            font-size: 13px;
            padding: 14px;
            outline: none;
            resize: vertical;
            line-height: 1.5;
        }

        .table-responsive {
            overflow-x: auto;
            margin-top: 18px;
        }

        .data-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
            text-align: left;
        }

        .data-table th {
            background: var(--bg-card);
            color: var(--text-muted);
            padding: 10px 14px;
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }

        .data-table td {
            padding: 12px 14px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.04);
            color: #cbd5e1;
        }

        .data-table tr:hover td {
            background: rgba(255, 255, 255, 0.02);
            color: #fff;
        }

        .tag-badge {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
        }
        .tag-tech { background: rgba(2, 132, 199, 0.15); color: #38bdf8; }
        .tag-furn { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
        .tag-supp { background: rgba(16, 185, 129, 0.15); color: #34d399; }

        .hidden-tab { display: none; }
    </style>
</head>
<body>

    <!-- Sidebar Navigation -->
    <aside class="sidebar">
        <div class="brand-header">
            <div class="brand-logo"><i class="fa-solid fa-chart-line"></i></div>
            <div>
                <div class="brand-title">ShopPulse</div>
                <span class="brand-badge">Verified Dataset</span>
            </div>
        </div>

        <div class="nav-section">
            <div class="nav-label">Analytics Modules</div>
            <a class="nav-item active" onclick="switchTab('overview')"><i class="fa-solid fa-gauge-high"></i> Executive Overview</a>
            <a class="nav-item" onclick="switchTab('products')"><i class="fa-solid fa-boxes-stacked"></i> Category & Products</a>
            <a class="nav-item" onclick="switchTab('customers')"><i class="fa-solid fa-users"></i> Customer & RFM</a>
            <a class="nav-item" onclick="switchTab('sql-studio')"><i class="fa-solid fa-terminal"></i> SQL Query Studio</a>
            
            <div class="nav-label">Global Filters</div>
            <div class="filter-box">
                <label><i class="fa-solid fa-calendar"></i> Operating Year</label>
                <select id="filter-year" class="filter-select" onchange="refreshDashboard()">
                    <option value="ALL">All Years (2014-2017)</option>
                    <option value="2014">2014</option>
                    <option value="2015">2015</option>
                    <option value="2016">2016</option>
                    <option value="2017">2017</option>
                </select>

                <label><i class="fa-solid fa-layer-group"></i> Category</label>
                <select id="filter-category" class="filter-select" onchange="refreshDashboard()">
                    <option value="ALL">All Categories</option>
                    <option value="Technology">Technology</option>
                    <option value="Furniture">Furniture</option>
                    <option value="Office Supplies">Office Supplies</option>
                </select>

                <label><i class="fa-solid fa-earth-americas"></i> Region</label>
                <select id="filter-region" class="filter-select" onchange="refreshDashboard()">
                    <option value="ALL">All Regions</option>
                    <option value="West">West</option>
                    <option value="East">East</option>
                    <option value="Central">Central</option>
                    <option value="South">South</option>
                </select>
            </div>
            <div style="margin-top: 16px; display: flex; flex-direction: column; gap: 8px;">
                <a href="/api/download_pdf" class="btn-primary" style="width: 100%; justify-content: center; text-decoration: none; background: linear-gradient(135deg, #0d9488 0%, #0f766e 100%);">
                    <i class="fa-solid fa-file-pdf"></i> Download Project PDF
                </a>
                <a href="/api/download_csv" class="btn-primary" style="width: 100%; justify-content: center; text-decoration: none;">
                    <i class="fa-solid fa-download"></i> Export Clean CSV
                </a>
            </div>
        </div>
    </aside>

    <!-- Main Container -->
    <main class="main-container">
        <header class="top-navbar">
            <div class="page-header">
                <h1 id="page-title">Executive Analytics Dashboard</h1>
                <p id="page-sub">Verified against 9,994 actual transaction records | Sample Superstore Dataset</p>
            </div>
            <div class="action-btns">
                <button class="btn-primary" onclick="refreshDashboard()"><i class="fa-solid fa-rotate"></i> Refresh Data</button>
            </div>
        </header>

        <!-- TAB 1: EXECUTIVE OVERVIEW -->
        <section id="tab-overview">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-title">Total Revenue <i class="fa-solid fa-dollar-sign text-success"></i></div>
                    <div class="kpi-value" id="kpi-revenue">$0.00</div>
                    <div class="kpi-subtext"><span class="text-success"><i class="fa-solid fa-arrow-trend-up"></i> Verified</span> total sales</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Total Profit <i class="fa-solid fa-coins text-success"></i></div>
                    <div class="kpi-value" id="kpi-profit">$0.00</div>
                    <div class="kpi-subtext"><span class="text-success"><i class="fa-solid fa-arrow-trend-up"></i> Realized</span> gross margin</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Profit Margin <i class="fa-solid fa-percent text-success"></i></div>
                    <div class="kpi-value" id="kpi-margin">0.0%</div>
                    <div class="kpi-subtext">Net realized margin</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Total Orders <i class="fa-solid fa-bag-shopping" style="color: var(--primary);"></i></div>
                    <div class="kpi-value" id="kpi-orders">0</div>
                    <div class="kpi-subtext">Unique checkouts</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Avg Order Value (AOV) <i class="fa-solid fa-receipt" style="color: var(--amber);"></i></div>
                    <div class="kpi-value" id="kpi-aov">$0.00</div>
                    <div class="kpi-subtext">Mean basket size</div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-title">Repeat Rate <i class="fa-solid fa-rotate-right" style="color: var(--indigo);"></i></div>
                    <div class="kpi-value" id="kpi-repeat">0.0%</div>
                    <div class="kpi-subtext">Multi-order buyers</div>
                </div>
            </div>

            <!-- Charts Row 1 -->
            <div class="chart-grid-2">
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">Revenue & Profit Trajectory</div>
                            <div class="chart-subtitle">Monthly sales velocity across operating years</div>
                        </div>
                    </div>
                    <div style="height: 320px;">
                        <canvas id="monthlyTrendChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">Category Revenue Share</div>
                            <div class="chart-subtitle">Sales contribution by merchandise division</div>
                        </div>
                    </div>
                    <div style="height: 320px; position: relative;">
                        <canvas id="categoryDonutChart"></canvas>
                    </div>
                </div>
            </div>

            <!-- Charts Row 2 -->
            <div class="chart-grid-half">
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">Regional Sales & Profit Breakdown</div>
                            <div class="chart-subtitle">Sales vs. Profit across 4 geographic territories</div>
                        </div>
                    </div>
                    <div style="height: 280px;">
                        <canvas id="regionBarChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <div class="chart-header">
                        <div>
                            <div class="chart-title">Discount Elasticity & Margin Degradation</div>
                            <div class="chart-subtitle">Profit margin impact across promotional discount depth</div>
                        </div>
                    </div>
                    <div style="height: 280px;">
                        <canvas id="discountImpactChart"></canvas>
                    </div>
                </div>
            </div>
        </section>

        <!-- TAB 2: PRODUCTS & CATEGORIES -->
        <section id="tab-products" class="hidden-tab">
            <div class="chart-card" style="margin-bottom: 24px;">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">Top 10 High-Revenue Product SKUs</div>
                        <div class="chart-subtitle">Ranked by aggregate revenue and realized profit</div>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="data-table" id="top-products-table">
                        <thead>
                            <tr>
                                <th>Product SKU</th>
                                <th>Product Name</th>
                                <th>Category</th>
                                <th>Sub-Category</th>
                                <th>Units Sold</th>
                                <th>Total Revenue</th>
                                <th>Total Profit</th>
                                <th>Margin %</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 3: CUSTOMERS & RFM -->
        <section id="tab-customers" class="hidden-tab">
            <div class="chart-card" style="margin-bottom: 24px;">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">Customer RFM Value Segmentation</div>
                        <div class="chart-subtitle">Behavioral segmentation based on Recency, Frequency & Monetary Value</div>
                    </div>
                </div>
                <div class="table-responsive">
                    <table class="data-table" id="rfm-table">
                        <thead>
                            <tr>
                                <th>RFM Segment Tier</th>
                                <th>Customer Count</th>
                                <th>Avg Orders</th>
                                <th>Total Segment Spend</th>
                                <th>Total Profit Generated</th>
                            </tr>
                        </thead>
                        <tbody></tbody>
                    </table>
                </div>
            </div>
        </section>

        <!-- TAB 4: SQL QUERY STUDIO -->
        <section id="tab-sql-studio" class="hidden-tab">
            <div class="sql-workspace">
                <div class="chart-header">
                    <div>
                        <div class="chart-title"><i class="fa-solid fa-terminal" style="color: var(--primary);"></i> Live SQL Query Studio</div>
                        <div class="chart-subtitle">Execute production analytical queries directly against the SQLite/PostgreSQL database</div>
                    </div>
                    <div style="display: flex; gap: 10px;">
                        <select id="preset-queries" class="filter-select" style="width: 380px; margin-bottom: 0;" onchange="loadPresetQuery()">
                            <option value="1">Query 01: Executive Summary KPIs</option>
                            <option value="2">Query 02: Monthly Revenue & Profit Velocity</option>
                            <option value="3">Query 03: Month-Over-Month (MoM) Growth (LAG)</option>
                            <option value="4">Query 04: Cumulative Running Revenue (SUM OVER)</option>
                            <option value="5">Query 05: Top 10 Best-Selling Products</option>
                            <option value="6">Query 06: Category Performance Ranking</option>
                            <option value="7">Query 07: Top 3 Sub-Cats per Category (DENSE_RANK)</option>
                            <option value="8">Query 08: Region-wise Sales & Margin Breakdown</option>
                            <option value="9">Query 09: Top Category per Region</option>
                            <option value="10">Query 10: Top 15 High-Value VIP Customers</option>
                            <option value="11">Query 11: Customer Segment Profitability</option>
                            <option value="12">Query 12: Repeat Purchase Order Distribution</option>
                            <option value="13">Query 13: Discount Depth vs Profit Margin</option>
                            <option value="14">Query 14: Top 15 Loss-Making Products</option>
                            <option value="15">Query 15: Shipping Mode Distribution</option>
                            <option value="16">Query 16: State-Level Profit Leaders & Leakers</option>
                            <option value="17">Query 17: Quarterly Performance Comparison</option>
                            <option value="18">Query 18: Pareto 80/20 Product Share</option>
                            <option value="19">Query 19: Price Tier Margin Distribution</option>
                            <option value="20">Query 20: Customer RFM Scoring</option>
                        </select>
                        <button class="btn-primary" onclick="executeCustomSQL()"><i class="fa-solid fa-play"></i> Run Query</button>
                    </div>
                </div>
                <textarea id="sql-editor" class="sql-editor">SELECT * FROM fact_ecommerce_sales LIMIT 10;</textarea>
                <div class="table-responsive">
                    <table class="data-table" id="sql-results-table">
                        <thead id="sql-results-head"></thead>
                        <tbody id="sql-results-body"></tbody>
                    </table>
                </div>
            </div>
        </section>
    </main>

    <script>
        let charts = {};
        const PRESET_SQL_QUERIES = {
            "1": "SELECT COUNT(DISTINCT order_id) AS total_orders, COUNT(DISTINCT customer_id) AS total_customers, ROUND(SUM(sales), 2) AS total_revenue, ROUND(SUM(profit), 2) AS total_profit, ROUND(SUM(sales)/COUNT(DISTINCT order_id), 2) AS aov, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales;",
            "2": "SELECT SUBSTR(order_date, 1, 7) AS year_month, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales GROUP BY SUBSTR(order_date, 1, 7) ORDER BY year_month ASC;",
            "3": "WITH monthly AS (SELECT SUBSTR(order_date, 1, 7) AS ym, ROUND(SUM(sales), 2) AS rev FROM fact_ecommerce_sales GROUP BY SUBSTR(order_date, 1, 7)) SELECT ym, rev, LAG(rev, 1) OVER (ORDER BY ym) AS prev_rev, ROUND(((rev - LAG(rev, 1) OVER (ORDER BY ym))/LAG(rev, 1) OVER (ORDER BY ym))*100, 2) AS mom_growth_pct FROM monthly;",
            "4": "WITH daily AS (SELECT order_date, SUM(sales) AS sales FROM fact_ecommerce_sales GROUP BY order_date) SELECT order_date, ROUND(sales, 2) AS daily_sales, ROUND(SUM(sales) OVER (ORDER BY order_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS running_total FROM daily LIMIT 30;",
            "5": "SELECT product_name, category, sub_category, SUM(quantity) AS units_sold, ROUND(SUM(sales), 2) AS total_revenue, ROUND(SUM(profit), 2) AS total_profit FROM fact_ecommerce_sales GROUP BY product_name, category, sub_category ORDER BY total_revenue DESC LIMIT 10;",
            "6": "SELECT category, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales GROUP BY category ORDER BY revenue DESC;",
            "7": "WITH subcat AS (SELECT category, sub_category, ROUND(SUM(sales), 2) AS sales, DENSE_RANK() OVER (PARTITION BY category ORDER BY SUM(sales) DESC) AS rank FROM fact_ecommerce_sales GROUP BY category, sub_category) SELECT * FROM subcat WHERE rank <= 3;",
            "8": "SELECT region, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales GROUP BY region ORDER BY revenue DESC;",
            "9": "WITH regional AS (SELECT region, category, ROUND(SUM(sales), 2) AS sales, ROW_NUMBER() OVER (PARTITION BY region ORDER BY SUM(sales) DESC) AS rn FROM fact_ecommerce_sales GROUP BY region, category) SELECT region, category, sales FROM regional WHERE rn = 1;",
            "10": "SELECT customer_name, customer_segment, region, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales), 2) AS total_spend, ROUND(SUM(profit), 2) AS total_profit FROM fact_ecommerce_sales GROUP BY customer_id, customer_name, customer_segment, region ORDER BY total_spend DESC LIMIT 15;",
            "11": "SELECT customer_segment, COUNT(DISTINCT customer_id) AS customers, ROUND(AVG(sales), 2) AS avg_order_val, ROUND(SUM(sales), 2) AS total_revenue, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales GROUP BY customer_segment ORDER BY total_revenue DESC;",
            "12": "WITH cust_orders AS (SELECT customer_id, COUNT(DISTINCT order_id) AS cnt, SUM(sales) AS spend FROM fact_ecommerce_sales GROUP BY customer_id) SELECT CASE WHEN cnt = 1 THEN '1 Order' WHEN cnt BETWEEN 2 AND 5 THEN '2-5 Orders' WHEN cnt BETWEEN 6 AND 10 THEN '6-10 Orders' ELSE '11+ Orders' END AS tier, COUNT(customer_id) AS customers, ROUND(SUM(spend), 2) AS revenue FROM cust_orders GROUP BY tier ORDER BY revenue DESC;",
            "13": "SELECT CASE WHEN discount = 0 THEN '0% (None)' WHEN discount <= 0.20 THEN '1%-20%' WHEN discount <= 0.50 THEN '21%-50%' ELSE '51%+' END AS discount_tier, COUNT(order_id) AS transactions, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales GROUP BY discount_tier ORDER BY margin_pct DESC;",
            "14": "SELECT product_name, category, sub_category, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS net_loss FROM fact_ecommerce_sales GROUP BY product_name, category, sub_category HAVING SUM(profit) < 0 ORDER BY net_loss ASC LIMIT 15;",
            "15": "SELECT ship_mode, COUNT(DISTINCT order_id) AS orders, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(sales)/COUNT(DISTINCT order_id), 2) AS aov FROM fact_ecommerce_sales GROUP BY ship_mode ORDER BY revenue DESC;",
            "16": "SELECT region, state, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit FROM fact_ecommerce_sales GROUP BY region, state ORDER BY profit DESC LIMIT 15;",
            "17": "SELECT order_year, order_quarter, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit, ROUND((SUM(profit)/SUM(sales))*100, 2) AS margin_pct FROM fact_ecommerce_sales GROUP BY order_year, order_quarter ORDER BY order_year, order_quarter;",
            "18": "WITH totals AS (SELECT product_name, SUM(sales) AS sales FROM fact_ecommerce_sales GROUP BY product_name), ranked AS (SELECT product_name, sales, SUM(sales) OVER (ORDER BY sales DESC) AS cum_sales, SUM(sales) OVER () AS total FROM totals) SELECT product_name, ROUND(sales, 2) AS sales, ROUND((cum_sales/total)*100, 2) AS cum_pct FROM ranked LIMIT 15;",
            "19": "SELECT CASE WHEN sales < 50 THEN '1. Low (< $50)' WHEN sales BETWEEN 50 AND 200 THEN '2. Mid ($50-$200)' WHEN sales BETWEEN 200 AND 1000 THEN '3. High ($200-$1K)' ELSE '4. Premium (> $1K)' END AS tier, COUNT(order_id) AS orders, ROUND(SUM(sales), 2) AS revenue, ROUND(SUM(profit), 2) AS profit FROM fact_ecommerce_sales GROUP BY tier ORDER BY tier;",
            "20": "WITH rfm AS (SELECT customer_id, customer_name, COUNT(DISTINCT order_id) AS freq, SUM(sales) AS mon, SUM(profit) AS prof FROM fact_ecommerce_sales GROUP BY customer_id, customer_name) SELECT CASE WHEN freq >= 10 AND mon >= 4000 THEN 'VIP Champions' WHEN freq >= 6 AND mon >= 2000 THEN 'Loyal Core' WHEN freq >= 3 THEN 'Regular' ELSE 'Occasional' END AS tier, COUNT(customer_id) AS custs, ROUND(SUM(mon), 2) AS spend, ROUND(SUM(prof), 2) AS profit FROM rfm GROUP BY tier ORDER BY spend DESC;"
        };

        function switchTab(tabId) {
            document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('main > section').forEach(el => el.classList.add('hidden-tab'));
            
            event.currentTarget.classList.add('active');
            document.getElementById('tab-' + tabId).classList.remove('hidden-tab');
            
            const titles = {
                'overview': 'Executive Analytics Dashboard',
                'products': 'Product & Category Intelligence Matrix',
                'customers': 'Customer RFM Segmentation & Cohorts',
                'sql-studio': 'Production SQL Query Studio'
            };
            document.getElementById('page-title').innerText = titles[tabId] || 'Analytics Dashboard';
        }

        function loadPresetQuery() {
            const qId = document.getElementById('preset-queries').value;
            if (PRESET_SQL_QUERIES[qId]) {
                document.getElementById('sql-editor').value = PRESET_SQL_QUERIES[qId];
            }
        }

        async function executeCustomSQL() {
            const sql = document.getElementById('sql-editor').value;
            try {
                const res = await fetch('/api/run_custom_sql', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query: sql })
                });
                const data = await res.json();
                
                if (data.error) {
                    alert('SQL Error: ' + data.error);
                    return;
                }
                
                // Render Table Header
                const thead = document.getElementById('sql-results-head');
                thead.innerHTML = '<tr>' + data.columns.map(c => '<th>' + c + '</th>').join('') + '</tr>';
                
                // Render Table Body
                const tbody = document.getElementById('sql-results-body');
                tbody.innerHTML = data.data.map(row => {
                    return '<tr>' + data.columns.map(c => '<td>' + (row[c] !== null ? row[c] : 'NULL') + '</td>').join('') + '</tr>';
                }).join('');
            } catch (err) {
                alert('Execution failed: ' + err);
            }
        }

        async function refreshDashboard() {
            const year = document.getElementById('filter-year').value;
            const category = document.getElementById('filter-category').value;
            const region = document.getElementById('filter-region').value;

            const url = `/api/dashboard_data?year=${year}&category=${category}&region=${region}`;
            const res = await fetch(url);
            const data = await res.json();

            // Update KPIs
            document.getElementById('kpi-revenue').innerText = '$' + data.kpis.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2});
            document.getElementById('kpi-profit').innerText = '$' + data.kpis.total_profit.toLocaleString('en-US', {minimumFractionDigits: 2});
            document.getElementById('kpi-margin').innerText = data.kpis.profit_margin_pct + '%';
            document.getElementById('kpi-orders').innerText = data.kpis.total_orders.toLocaleString();
            document.getElementById('kpi-aov').innerText = '$' + data.kpis.average_order_value.toLocaleString('en-US', {minimumFractionDigits: 2});
            document.getElementById('kpi-repeat').innerText = data.kpis.repeat_customer_rate + '%';

            renderMonthlyTrendChart(data.monthly);
            renderCategoryDonutChart(data.categories);
            renderRegionBarChart(data.regions);
            renderDiscountImpactChart(data.discounts);
            renderTopProductsTable(data.top_products);
            renderRFMTable(data.rfm_summary);
        }

        function renderMonthlyTrendChart(monthlyData) {
            if (charts.monthly) charts.monthly.destroy();
            const ctx = document.getElementById('monthlyTrendChart').getContext('2d');
            charts.monthly = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: monthlyData.map(d => d.year_month),
                    datasets: [
                        {
                            label: 'Revenue ($)',
                            data: monthlyData.map(d => d.revenue),
                            borderColor: '#0284c7',
                            backgroundColor: 'rgba(2, 132, 199, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.3
                        },
                        {
                            label: 'Profit ($)',
                            data: monthlyData.map(d => d.profit),
                            borderColor: '#10b981',
                            borderWidth: 2,
                            tension: 0.3
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { labels: { color: '#94a3b8' } }
                    },
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function renderCategoryDonutChart(categoryData) {
            if (charts.donut) charts.donut.destroy();
            const ctx = document.getElementById('categoryDonutChart').getContext('2d');
            charts.donut = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: categoryData.map(d => d.category),
                    datasets: [{
                        data: categoryData.map(d => d.revenue),
                        backgroundColor: ['#0284c7', '#f59e0b', '#10b981'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#94a3b8' } }
                    },
                    cutout: '70%'
                }
            });
        }

        function renderRegionBarChart(regionData) {
            if (charts.region) charts.region.destroy();
            const ctx = document.getElementById('regionBarChart').getContext('2d');
            charts.region = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: regionData.map(d => d.region),
                    datasets: [
                        {
                            label: 'Revenue ($)',
                            data: regionData.map(d => d.revenue),
                            backgroundColor: '#0284c7'
                        },
                        {
                            label: 'Profit ($)',
                            data: regionData.map(d => d.profit),
                            backgroundColor: '#10b981'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function renderDiscountImpactChart(discData) {
            if (charts.discount) charts.discount.destroy();
            const ctx = document.getElementById('discountImpactChart').getContext('2d');
            charts.discount = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: discData.map(d => d.discount_tier),
                    datasets: [{
                        label: 'Profit Margin (%)',
                        data: discData.map(d => d.profit_margin_pct),
                        borderColor: '#f43f5e',
                        backgroundColor: 'rgba(244, 63, 94, 0.1)',
                        borderWidth: 2.5,
                        fill: true,
                        tension: 0.2,
                        pointRadius: 5
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        x: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#94a3b8' } }
                    }
                }
            });
        }

        function renderTopProductsTable(products) {
            const tbody = document.querySelector('#top-products-table tbody');
            tbody.innerHTML = products.map(p => {
                let badgeClass = p.category === 'Technology' ? 'tag-tech' : (p.category === 'Furniture' ? 'tag-furn' : 'tag-supp');
                return `
                    <tr>
                        <td><code>${p.product_id}</code></td>
                        <td><strong>${p.product_name}</strong></td>
                        <td><span class="tag-badge ${badgeClass}">${p.category}</span></td>
                        <td>${p.sub_category}</td>
                        <td>${p.total_quantity.toLocaleString()}</td>
                        <td>$${p.total_sales.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td class="${p.total_profit >= 0 ? 'text-success' : 'text-danger'}">$${p.total_profit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td><strong>${p.profit_margin_pct}%</strong></td>
                    </tr>
                `;
            }).join('');
        }

        function renderRFMTable(rfmData) {
            const tbody = document.querySelector('#rfm-table tbody');
            tbody.innerHTML = rfmData.map(r => {
                return `
                    <tr>
                        <td><strong>${r.RFM_Segment}</strong></td>
                        <td>${r.Customer_Count.toLocaleString()}</td>
                        <td>${r.Avg_Orders.toFixed(1)} orders</td>
                        <td>$${r.Total_Spend.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                        <td class="${r.Total_Profit >= 0 ? 'text-success' : 'text-danger'}">$${r.Total_Profit.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                    </tr>
                `;
            }).join('');
        }

        // Initialize on page load
        window.addEventListener('DOMContentLoaded', () => {
            refreshDashboard();
            executeCustomSQL();
        });
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/dashboard_data")
def api_dashboard_data():
    df = load_cleaned_data(CSV_PATH)
    
    # Apply Filters
    year = request.args.get("year", "ALL")
    category = request.args.get("category", "ALL")
    region = request.args.get("region", "ALL")

    if year != "ALL":
        df = df[df["order_year"] == int(year)]
    if category != "ALL":
        df = df[df["category"] == category]
    if region != "ALL":
        df = df[df["region"] == region]

    kpis = calculate_kpis(df)
    monthly = get_monthly_trends(df).to_dict(orient="records")
    cats, subcats = get_category_performance(df)
    regions, states = get_regional_performance(df)
    top_products = get_top_products(df, top_n=10).to_dict(orient="records")
    discounts = get_discount_impact_analysis(df).to_dict(orient="records")
    
    # RFM Summary
    rfm = get_rfm_segmentation(df)
    rfm_summary = rfm.groupby("RFM_Segment").agg(
        Customer_Count=("customer_id", "count"),
        Total_Spend=("monetary", "sum"),
        Avg_Orders=("frequency", "mean"),
        Total_Profit=("total_profit", "sum")
    ).reset_index().to_dict(orient="records")

    return jsonify({
        "kpis": kpis,
        "monthly": monthly,
        "categories": cats.to_dict(orient="records"),
        "subcategories": subcats.to_dict(orient="records"),
        "regions": regions.to_dict(orient="records"),
        "top_products": top_products,
        "discounts": discounts,
        "rfm_summary": rfm_summary
    })

@app.route("/api/run_custom_sql", methods=["POST"])
def api_run_custom_sql():
    data = request.get_json() or {}
    sql = data.get("query", "SELECT * FROM fact_ecommerce_sales LIMIT 10;")
    engine = get_engine()
    try:
        with engine.connect() as conn:
            df = pd.read_sql_query(text(sql), conn)
        return jsonify({
            "columns": list(df.columns),
            "data": df.head(100).to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/download_pdf")
def api_download_pdf():
    pdf_path = os.path.join(BASE_DIR, "reports", "ShopPulse_Complete_Project_Report.pdf")
    if not os.path.exists(pdf_path):
        from src.generate_pdf_report import generate_pdf
        generate_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name="ShopPulse_Complete_Project_Report.pdf")

@app.route("/api/download_csv")
def api_download_csv():
    return send_file(CSV_PATH, as_attachment=True, download_name="cleaned_ecommerce_data.csv")

if __name__ == "__main__":
    print("="*70)
    print("ShopPulse E-Commerce Analytics Platform (Verified Dataset)")
    print("Running live at: http://localhost:5000")
    print("="*70)
    app.run(host="0.0.0.0", port=5000, debug=False)
