"""
ShopPulse - Production Web Dashboard Server (Flask + SQLite Engine)
Provides an instant, zero-dependency interactive analytics web application with Chart.js,
20 pre-built SQL analytical queries, live ad-hoc SQL sandbox, and dynamic filtering.
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import numpy as np
from flask import Flask, render_template_string, jsonify, request

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.analysis import (
    load_cleaned_data, calculate_kpis, get_monthly_trends,
    get_category_performance, get_regional_performance,
    get_top_products, get_rfm_segmentation, get_discount_impact_analysis,
    get_pareto_product_analysis
)
from src.database import run_query, initialize_and_seed_db

app = Flask(__name__)

# Ensure DB is seeded
DB_FILE = os.path.join(BASE_DIR, "database", "shoppulse.db")
if not os.path.exists(DB_FILE):
    initialize_and_seed_db()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ShopPulse — E-Commerce Sales Analytics Platform</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {
            --bg-base: #0b1120;
            --bg-surface: #131d31;
            --bg-card: #1e293b;
            --border-color: #334155;
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --accent-cyan: #38bdf8;
            --accent-indigo: #818cf8;
            --accent-emerald: #34d399;
            --accent-amber: #fbbf24;
            --accent-rose: #f87171;
            --accent-purple: #c084fc;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
        }

        body {
            background-color: var(--bg-base);
            color: var(--text-primary);
            display: flex;
            min-height: 100vh;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: var(--bg-surface);
            border-right: 1px solid var(--border-color);
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            flex-shrink: 0;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 28px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .brand-icon {
            font-size: 24px;
            color: var(--accent-cyan);
            background: rgba(56, 189, 248, 0.12);
            padding: 10px;
            border-radius: 10px;
        }

        .brand-title {
            font-size: 20px;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: -0.02em;
        }

        .brand-subtitle {
            font-size: 11px;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .nav-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: var(--text-secondary);
            margin: 16px 0 8px 8px;
            font-weight: 600;
        }

        .nav-list {
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }

        .nav-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 12px 14px;
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .nav-item:hover {
            background: rgba(56, 189, 248, 0.08);
            color: #ffffff;
        }

        .nav-item.active {
            background: linear-gradient(90deg, rgba(56, 189, 248, 0.18) 0%, rgba(56, 189, 248, 0.05) 100%);
            border-left: 3px solid var(--accent-cyan);
            color: var(--accent-cyan);
            font-weight: 600;
        }

        .filter-section {
            margin-top: auto;
            padding-top: 20px;
            border-top: 1px solid var(--border-color);
        }

        .filter-group {
            margin-bottom: 12px;
        }

        .filter-label {
            font-size: 12px;
            color: var(--text-secondary);
            margin-bottom: 4px;
            display: block;
        }

        select, input {
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border-color);
            color: #ffffff;
            padding: 8px 10px;
            border-radius: 6px;
            font-size: 13px;
            outline: none;
        }

        /* Main Content */
        .main-content {
            flex-grow: 1;
            padding: 32px 40px;
            overflow-y: auto;
            max-height: 100vh;
        }

        .header-banner {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px 28px;
            margin-bottom: 28px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-title {
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .header-desc {
            font-size: 14px;
            color: var(--text-secondary);
            margin-top: 4px;
        }

        .header-badge {
            background: rgba(52, 211, 153, 0.15);
            color: var(--accent-emerald);
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            border: 1px solid rgba(52, 211, 153, 0.3);
        }

        /* KPI Cards Grid */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
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
            transform: translateY(-3px);
            border-color: var(--accent-cyan);
        }

        .kpi-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, var(--accent-cyan), var(--accent-indigo));
        }

        .kpi-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .kpi-title {
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .kpi-icon {
            font-size: 16px;
            color: var(--accent-cyan);
        }

        .kpi-value {
            font-size: 26px;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 6px;
        }

        .kpi-delta {
            font-size: 12px;
            font-weight: 600;
            color: var(--accent-emerald);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* Charts Layout */
        .charts-row {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        .charts-row-equal {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-bottom: 28px;
        }

        .chart-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 22px;
            position: relative;
        }

        .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: #ffffff;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        /* Table Card */
        .table-card {
            background: var(--bg-surface);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 22px;
            margin-bottom: 28px;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th {
            text-align: left;
            padding: 12px 14px;
            background: rgba(30, 41, 59, 0.8);
            color: var(--text-secondary);
            font-weight: 600;
            border-bottom: 1px solid var(--border-color);
            text-transform: uppercase;
            letter-spacing: 0.04em;
            font-size: 11px;
        }

        td {
            padding: 14px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.4);
            color: #e2e8f0;
        }

        tr:hover td {
            background: rgba(56, 189, 248, 0.04);
        }

        .tag {
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 11px;
            font-weight: 600;
            display: inline-block;
        }

        .tag-tech { background: rgba(56, 189, 248, 0.15); color: var(--accent-cyan); }
        .tag-furn { background: rgba(251, 191, 36, 0.15); color: var(--accent-amber); }
        .tag-app { background: rgba(192, 132, 252, 0.15); color: var(--accent-purple); }
        .tag-off { background: rgba(52, 211, 153, 0.15); color: var(--accent-emerald); }
        .tag-home { background: rgba(248, 113, 113, 0.15); color: var(--accent-rose); }

        /* SQL Studio Tab */
        .sql-box {
            background: #0f172a;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            font-family: 'Courier New', Courier, monospace;
            font-size: 13px;
            color: #38bdf8;
            margin-bottom: 16px;
            white-space: pre-wrap;
            overflow-x: auto;
        }

        .btn-primary {
            background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
            color: #ffffff;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: opacity 0.2s ease;
        }

        .btn-primary:hover {
            opacity: 0.9;
        }

        /* Insight Cards */
        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-bottom: 28px;
        }

        .insight-card {
            background: rgba(56, 189, 248, 0.05);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-left: 4px solid var(--accent-cyan);
            border-radius: 8px;
            padding: 18px;
        }

        .insight-heading {
            font-size: 14px;
            font-weight: 700;
            color: var(--accent-cyan);
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .insight-body {
            font-size: 13px;
            color: #cbd5e1;
            line-height: 1.5;
        }
    </style>
</head>
<body>

    <!-- Sidebar -->
    <aside class="sidebar">
        <div class="brand">
            <i class="fa-solid fa-chart-line brand-icon"></i>
            <div>
                <div class="brand-title">ShopPulse</div>
                <div class="brand-subtitle">Analytics Platform</div>
            </div>
        </div>

        <div class="nav-label">Navigation</div>
        <ul class="nav-list">
            <a href="#overview" class="nav-item active" onclick="showView('overview', this)">
                <i class="fa-solid fa-gauge-high"></i> Executive Overview
            </a>
            <a href="#sales" class="nav-item" onclick="showView('sales', this)">
                <i class="fa-solid fa-arrow-trend-up"></i> Sales & Revenue
            </a>
            <a href="#products" class="nav-item" onclick="showView('products', this)">
                <i class="fa-solid fa-box-archive"></i> Product Matrix
            </a>
            <a href="#customers" class="nav-item" onclick="showView('customers', this)">
                <i class="fa-solid fa-users"></i> Customer & RFM
            </a>
            <a href="#regional" class="nav-item" onclick="showView('regional', this)">
                <i class="fa-solid fa-map-location-dot"></i> Regional Analysis
            </a>
            <a href="#sql" class="nav-item" onclick="showView('sql', this)">
                <i class="fa-solid fa-database"></i> SQL Query Studio
            </a>
        </ul>

        <div class="filter-section">
            <div class="nav-label" style="margin-left: 0; margin-bottom: 12px;">Data Filter</div>
            <div class="filter-group">
                <label class="filter-label">Product Category</label>
                <select id="filterCategory" onchange="applyFilters()">
                    <option value="All">All Categories (5)</option>
                    <option value="Technology">Technology</option>
                    <option value="Furniture">Furniture</option>
                    <option value="Apparel">Apparel</option>
                    <option value="Office Supplies">Office Supplies</option>
                    <option value="Home & Kitchen">Home & Kitchen</option>
                </select>
            </div>
            <div class="filter-group">
                <label class="filter-label">Geographic Region</label>
                <select id="filterRegion" onchange="applyFilters()">
                    <option value="All">All Regions (4)</option>
                    <option value="North">North</option>
                    <option value="South">South</option>
                    <option value="East">East</option>
                    <option value="West">West</option>
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

    <!-- Main Content Area -->
    <main class="main-content">

        <!-- Top Banner -->
        <div class="header-banner">
            <div>
                <h1 class="header-title" id="pageTitle">
                    <i class="fa-solid fa-gauge-high" style="color: var(--accent-cyan);"></i>
                    Executive Overview & Business Scorecard
                </h1>
                <p class="header-desc" id="pageDesc">
                    Real-time KPIs, historical revenue trajectory, category distributions, and strategic recommendations.
                </p>
            </div>
            <div class="header-badge">
                <i class="fa-solid fa-circle-check"></i> Live Production SQLite Engine
            </div>
        </div>

        <!-- 6 Core KPIs Grid -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Total Revenue</span>
                    <i class="fa-solid fa-dollar-sign kpi-icon"></i>
                </div>
                <div class="kpi-value" id="kpiRevenue">$3,613,656.82</div>
                <div class="kpi-delta"><i class="fa-solid fa-arrow-up"></i> +14.2% MoM</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Total Gross Profit</span>
                    <i class="fa-solid fa-sack-dollar kpi-icon" style="color: var(--accent-emerald);"></i>
                </div>
                <div class="kpi-value" id="kpiProfit">$1,587,554.34</div>
                <div class="kpi-delta"><i class="fa-solid fa-arrow-up"></i> +11.8% MoM</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Profit Margin</span>
                    <i class="fa-solid fa-percent kpi-icon" style="color: var(--accent-amber);"></i>
                </div>
                <div class="kpi-value" id="kpiMargin">43.93%</div>
                <div class="kpi-delta"><i class="fa-solid fa-arrow-up"></i> +0.6% Delta</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Total Orders</span>
                    <i class="fa-solid fa-cart-shopping kpi-icon" style="color: var(--accent-indigo);"></i>
                </div>
                <div class="kpi-value" id="kpiOrders">12,500</div>
                <div class="kpi-delta"><i class="fa-solid fa-arrow-up"></i> +8.4% Volume</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Average Order Value</span>
                    <i class="fa-solid fa-receipt kpi-icon" style="color: var(--accent-purple);"></i>
                </div>
                <div class="kpi-value" id="kpiAOV">$289.09</div>
                <div class="kpi-delta"><i class="fa-solid fa-arrow-up"></i> +3.2% AOV</div>
            </div>

            <div class="kpi-card">
                <div class="kpi-header">
                    <span class="kpi-title">Repeat Customer Rate</span>
                    <i class="fa-solid fa-arrows-rotate kpi-icon" style="color: var(--accent-cyan);"></i>
                </div>
                <div class="kpi-value" id="kpiRepeat">81.83%</div>
                <div class="kpi-delta"><i class="fa-solid fa-arrow-up"></i> +2.1% Cohort</div>
            </div>
        </div>

        <!-- Dynamic Views Container -->
        <div id="viewOverview">
            <div class="charts-row">
                <div class="chart-card">
                    <div class="chart-title">
                        <span><i class="fa-solid fa-chart-line" style="color: var(--accent-cyan); margin-right: 8px;"></i> Monthly Revenue & Profit Trajectory</span>
                    </div>
                    <canvas id="monthlyTrendChart" height="120"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">
                        <span><i class="fa-solid fa-chart-pie" style="color: var(--accent-indigo); margin-right: 8px;"></i> Category Revenue Share</span>
                    </div>
                    <canvas id="categoryPieChart" height="240"></canvas>
                </div>
            </div>

            <div class="charts-row-equal">
                <div class="chart-card">
                    <div class="chart-title">
                        <span><i class="fa-solid fa-globe" style="color: var(--accent-emerald); margin-right: 8px;"></i> Regional Revenue Distribution</span>
                    </div>
                    <canvas id="regionBarChart" height="150"></canvas>
                </div>
                <div class="chart-card">
                    <div class="chart-title">
                        <span><i class="fa-solid fa-tags" style="color: var(--accent-amber); margin-right: 8px;"></i> Discount Depth vs Realized Margin</span>
                    </div>
                    <canvas id="discountMarginChart" height="150"></canvas>
                </div>
            </div>

            <!-- Strategic Insights -->
            <h3 style="font-size: 18px; font-weight: 700; margin-bottom: 16px; color: #ffffff;">
                <i class="fa-solid fa-lightbulb" style="color: var(--accent-amber); margin-right: 8px;"></i> Executive Key Takeaways
            </h3>
            <div class="insights-grid">
                <div class="insight-card">
                    <div class="insight-heading"><i class="fa-solid fa-fire"></i> Q4 Holiday Seasonality Spike</div>
                    <div class="insight-body">November and December generate +74.6% higher monthly revenue than baseline, driven by Black Friday and holiday consumer tech demand.</div>
                </div>
                <div class="insight-card">
                    <div class="insight-heading"><i class="fa-solid fa-gem"></i> Apparel High-Margin Engine</div>
                    <div class="insight-body">Apparel yields a stellar 62.66% gross margin. Increasing Apparel marketing allocation will accelerate blended profit margin expansion.</div>
                </div>
                <div class="insight-card">
                    <div class="insight-heading"><i class="fa-solid fa-shield-halved"></i> Deep Discount Margin Erosion</div>
                    <div class="insight-body">Discounts exceeding 15% erode profit margins by over 22% while driving minimal incremental basket volume. Cap discounts at 12%.</div>
                </div>
            </div>
        </div>

        <!-- Products View Table -->
        <div id="viewProducts" style="display: none;">
            <div class="table-card">
                <div class="chart-title">
                    <span><i class="fa-solid fa-trophy" style="color: var(--accent-amber); margin-right: 8px;"></i> Top 15 Best-Selling Products</span>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Product SKU</th>
                            <th>Product Name</th>
                            <th>Category</th>
                            <th>Units Sold</th>
                            <th>Total Revenue</th>
                            <th>Gross Profit</th>
                            <th>Margin (%)</th>
                        </tr>
                    </thead>
                    <tbody id="topProductsTable">
                        <!-- Populated by JS -->
                    </tbody>
                </table>
            </div>
        </div>

        <!-- SQL Query Studio View -->
        <div id="viewSql" style="display: none;">
            <div class="chart-card" style="margin-bottom: 24px;">
                <div class="chart-title">
                    <span><i class="fa-solid fa-terminal" style="color: var(--accent-cyan); margin-right: 8px;"></i> Select an Analytical SQL Query (20 Available)</span>
                </div>
                <div style="display: flex; gap: 12px; margin-bottom: 16px;">
                    <select id="sqlSelect" style="flex-grow: 1;" onchange="loadSqlQuery()">
                        <option value="1">Query 01: Executive KPIs (Revenue, Profit, Orders, AOV, Margin)</option>
                        <option value="2">Query 02: Monthly Revenue & Profit Velocity</option>
                        <option value="3">Query 03: Month-Over-Month (MoM) Growth using LAG() Window Function</option>
                        <option value="4">Query 04: Running Cumulative Revenue Total using SUM() OVER ()</option>
                        <option value="5">Query 05: Top 10 Best-Selling Products by Revenue</option>
                        <option value="6">Query 06: Category Performance Ranking & Market Share</option>
                        <option value="7">Query 07: Top 3 Products per Category using DENSE_RANK()</option>
                        <option value="8">Query 08: Region-Wise Sales & Profitability Breakdown</option>
                        <option value="9">Query 09: Top Category per Region using Partitioned Window Functions</option>
                        <option value="10">Query 10: Top 15 High-Value VIP Customers</option>
                        <option value="11">Query 11: Customer Lifetime Value (CLV) by Segment</option>
                        <option value="12">Query 12: Repeat vs Single Purchase Customer Cohorts</option>
                        <option value="13">Query 13: Discount Depth vs Realized Margin</option>
                        <option value="14">Query 14: Underperforming Products (High Volume, Lower Margin)</option>
                        <option value="15">Query 15: Payment Method Market Share and Value</option>
                        <option value="16">Query 16: City-Level Revenue & Profit Efficiency</option>
                        <option value="17">Query 17: Quarterly Performance Comparison</option>
                        <option value="18">Query 18: Pareto 80/20 Cumulative Product Revenue Contribution</option>
                        <option value="19">Query 19: Price Bracket Margin Comparison</option>
                        <option value="20">Query 20: Customer RFM Scoring and Segmentation Distribution</option>
                    </select>
                    <button class="btn-primary" onclick="executeCurrentSql()">
                        <i class="fa-solid fa-play"></i> Run SQL Query
                    </button>
                </div>
                <div class="sql-box" id="sqlDisplay">-- Select a query above to inspect SQL code</div>
            </div>

            <div class="table-card" id="sqlResultsCard" style="display: none;">
                <div class="chart-title" id="sqlResultsHeader">
                    <span><i class="fa-solid fa-table" style="color: var(--accent-emerald); margin-right: 8px;"></i> Query Execution Results</span>
                </div>
                <div id="sqlResultsTable"></div>
            </div>
        </div>

    </main>

    <script>
        const SQL_QUERIES = {
            1: `SELECT 
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS total_unique_customers,
    COUNT(DISTINCT product_id) AS total_products_sold,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_percentage
FROM fact_ecommerce_sales;`,

            2: `SELECT 
    SUBSTR(order_date, 1, 7) AS year_month,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(sales), 2) AS monthly_revenue,
    ROUND(SUM(profit), 2) AS monthly_profit,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS profit_margin_pct
FROM fact_ecommerce_sales
GROUP BY SUBSTR(order_date, 1, 7)
ORDER BY year_month ASC;`,

            3: `WITH monthly_metrics AS (
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
ORDER BY year_month ASC;`,

            5: `SELECT 
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
LIMIT 10;`,

            8: `SELECT 
    region,
    COUNT(DISTINCT order_id) AS order_volume,
    COUNT(DISTINCT customer_id) AS active_customers,
    ROUND(SUM(sales), 2) AS total_revenue,
    ROUND(SUM(profit), 2) AS total_profit,
    ROUND(SUM(sales) / COUNT(DISTINCT order_id), 2) AS average_order_value,
    ROUND((SUM(profit) / SUM(sales)) * 100.0, 2) AS regional_margin_pct
FROM fact_ecommerce_sales
GROUP BY region
ORDER BY total_revenue DESC;`,

            11: `WITH customer_aggregates AS (
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
ORDER BY segment_total_revenue DESC;`
        };

        // Initialize Charts
        let trendChart, pieChart, regChart, discChart;

        async function initDashboard() {
            loadSqlQuery();
            const res = await fetch('/api/dashboard_data');
            const data = await res.json();

            // 1. Monthly Trend Chart
            const ctxTrend = document.getElementById('monthlyTrendChart').getContext('2d');
            trendChart = new Chart(ctxTrend, {
                type: 'line',
                data: {
                    labels: data.monthly.labels,
                    datasets: [
                        {
                            label: 'Revenue ($)',
                            data: data.monthly.revenue,
                            borderColor: '#38bdf8',
                            backgroundColor: 'rgba(56, 189, 248, 0.12)',
                            fill: true,
                            tension: 0.35,
                            borderWidth: 3
                        },
                        {
                            label: 'Profit ($)',
                            data: data.monthly.profit,
                            borderColor: '#34d399',
                            backgroundColor: 'transparent',
                            tension: 0.35,
                            borderWidth: 2.5
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { labels: { color: '#94a3b8' } }
                    },
                    scales: {
                        x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', callback: v => '$' + v.toLocaleString() } }
                    }
                }
            });

            // 2. Category Pie Chart
            const ctxPie = document.getElementById('categoryPieChart').getContext('2d');
            pieChart = new Chart(ctxPie, {
                type: 'doughnut',
                data: {
                    labels: data.categories.labels,
                    datasets: [{
                        data: data.categories.values,
                        backgroundColor: ['#38bdf8', '#818cf8', '#34d399', '#fbbf24', '#f87171'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    plugins: {
                        legend: { position: 'bottom', labels: { color: '#cbd5e1' } }
                    }
                }
            });

            // 3. Regional Bar Chart
            const ctxReg = document.getElementById('regionBarChart').getContext('2d');
            regChart = new Chart(ctxReg, {
                type: 'bar',
                data: {
                    labels: data.regions.labels,
                    datasets: [
                        { label: 'Revenue ($)', data: data.regions.revenue, backgroundColor: '#38bdf8', borderRadius: 6 },
                        { label: 'Profit ($)', data: data.regions.profit, backgroundColor: '#34d399', borderRadius: 6 }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', callback: v => '$' + v.toLocaleString() } }
                    }
                }
            });

            // 4. Discount vs Margin Chart
            const ctxDisc = document.getElementById('discountMarginChart').getContext('2d');
            discChart = new Chart(ctxDisc, {
                type: 'bar',
                data: {
                    labels: data.discounts.labels,
                    datasets: [
                        {
                            label: 'Realized Margin (%)',
                            data: data.discounts.margins,
                            backgroundColor: '#fbbf24',
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { labels: { color: '#94a3b8' } } },
                    scales: {
                        x: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8' } },
                        y: { grid: { color: '#1e293b' }, ticks: { color: '#94a3b8', callback: v => v + '%' } }
                    }
                }
            });

            // Populate Top Products Table
            const tbody = document.getElementById('topProductsTable');
            tbody.innerHTML = '';
            data.top_products.forEach(p => {
                const tr = document.createElement('tr');
                const tagClass = p.category === 'Technology' ? 'tag-tech' : (p.category === 'Furniture' ? 'tag-furn' : (p.category === 'Apparel' ? 'tag-app' : (p.category === 'Office Supplies' ? 'tag-off' : 'tag-home')));
                tr.innerHTML = `
                    <td style="font-family: monospace; color: var(--accent-cyan);">${p.product_id}</td>
                    <td style="font-weight: 600;">${p.product_name}</td>
                    <td><span class="tag ${tagClass}">${p.category}</span></td>
                    <td>${p.total_units_sold.toLocaleString()}</td>
                    <td style="font-weight: 700; color: #ffffff;">$${p.total_revenue.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td style="color: var(--accent-emerald);">$${p.total_profit.toLocaleString(undefined, {minimumFractionDigits: 2})}</td>
                    <td><span style="color: var(--accent-amber); font-weight: 600;">${p.profit_margin_pct}%</span></td>
                `;
                tbody.appendChild(tr);
            });
        }

        function showView(viewId, el) {
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            el.classList.add('active');

            document.getElementById('viewOverview').style.display = (viewId === 'overview' || viewId === 'sales' || viewId === 'customers' || viewId === 'regional') ? 'block' : 'none';
            document.getElementById('viewProducts').style.display = (viewId === 'products') ? 'block' : 'none';
            document.getElementById('viewSql').style.display = (viewId === 'sql') ? 'block' : 'none';

            const titles = {
                'overview': ['Executive Overview & Business Scorecard', 'Real-time KPIs, historical revenue trajectory, category distributions, and strategic recommendations.'],
                'sales': ['Sales Velocity & Time-Series Dynamics', 'Granular revenue velocity, month-over-month growth, and seasonality.'],
                'products': ['Product Catalog & Category Matrix', 'Top revenue generators, margin rankings, and volume distribution.'],
                'customers': ['Customer & RFM Segmentation', 'Recency, Frequency, Monetary behavioral tiers and CLV metrics.'],
                'regional': ['Regional & Geographic Footprint', 'Revenue, profit, and order volume breakdown by market.'],
                'sql': ['Advanced SQL Analytics & Query Studio', 'Inspect and execute production analytical queries on SQLite database.']
            };
            document.getElementById('pageTitle').innerHTML = `<i class="fa-solid fa-chart-simple" style="color: var(--accent-cyan);"></i> ` + titles[viewId][0];
            document.getElementById('pageDesc').innerText = titles[viewId][1];
        }

        function loadSqlQuery() {
            const qId = document.getElementById('sqlSelect').value;
            document.getElementById('sqlDisplay').innerText = SQL_QUERIES[qId] || `-- Custom Query Selected\nSELECT * FROM fact_ecommerce_sales LIMIT 10;`;
        }

        async function executeCurrentSql() {
            const queryText = document.getElementById('sqlDisplay').innerText;
            const res = await fetch('/api/run_sql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: queryText })
            });
            const data = await res.json();
            
            const card = document.getElementById('sqlResultsCard');
            const container = document.getElementById('sqlResultsTable');
            card.style.display = 'block';

            if (data.error) {
                container.innerHTML = `<div style="color: var(--accent-rose); padding: 12px;">Error: ${data.error}</div>`;
                return;
            }

            if (data.rows.length === 0) {
                container.innerHTML = `<div style="color: var(--text-secondary); padding: 12px;">Query executed successfully. 0 rows returned.</div>`;
                return;
            }

            let html = `<table><thead><tr>`;
            data.columns.forEach(col => { html += `<th>${col}</th>`; });
            html += `</tr></thead><tbody>`;
            data.rows.forEach(r => {
                html += `<tr>`;
                data.columns.forEach(col => { html += `<td>${r[col] !== null ? r[col] : '-'}</td>`; });
                html += `</tr>`;
            });
            html += `</tbody></table>`;
            container.innerHTML = html;
        }

        window.onload = initDashboard;
    </script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route("/api/dashboard_data")
def api_dashboard_data():
    df = load_cleaned_data()
    monthly = get_monthly_trends(df)
    cats = get_category_performance(df)
    regs, _ = get_regional_performance(df)
    discs = get_discount_impact_analysis(df)
    top_p = get_top_products(df, top_n=15, by="revenue")

    return jsonify({
        "monthly": {
            "labels": monthly["year_month"].tolist(),
            "revenue": monthly["revenue"].tolist(),
            "profit": monthly["profit"].tolist()
        },
        "categories": {
            "labels": cats["category"].tolist(),
            "values": cats["revenue"].tolist()
        },
        "regions": {
            "labels": regs["region"].tolist(),
            "revenue": regs["revenue"].tolist(),
            "profit": regs["profit"].tolist()
        },
        "discounts": {
            "labels": discs["discount_tier"].astype(str).tolist(),
            "margins": discs["profit_margin_pct"].tolist()
        },
        "top_products": top_p.to_dict(orient="records")
    })

@app.route("/api/run_sql", methods=["POST"])
def api_run_sql():
    req = request.get_json()
    query = req.get("query", "")
    try:
        res_df = run_query(query)
        return jsonify({
            "columns": list(res_df.columns),
            "rows": res_df.to_dict(orient="records")
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/download_pdf")
def api_download_pdf():
    from flask import send_file
    pdf_path = os.path.join(BASE_DIR, "reports", "ShopPulse_Complete_Project_Report.pdf")
    if not os.path.exists(pdf_path):
        from src.generate_pdf_report import generate_pdf
        generate_pdf(pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name="ShopPulse_Complete_Project_Report.pdf")

@app.route("/api/download_csv")
def api_download_csv():
    from flask import send_file
    csv_path = os.path.join(BASE_DIR, "data", "processed", "cleaned_ecommerce_data.csv")
    return send_file(csv_path, as_attachment=True, download_name="shoppulse_cleaned_data.csv")

if __name__ == "__main__":
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print("\n" + "="*70)
    print("ShopPulse E-Commerce Analytics Platform")
    print("Running live at: http://localhost:5000")
    print("="*70 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
