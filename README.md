# ShopPulse — E-Commerce Sales Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![SQLite](https://img.shields.io/badge/SQLite-3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.61-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Pytest](https://img.shields.io/badge/Tests-Passing-success?style=for-the-badge&logo=pytest)](tests/)

> **A production-grade, reproducible E-Commerce Data Analytics & Business Intelligence platform engineered on the verified, public Sample Superstore retail sales dataset. 100% of reported metrics, SQL queries, dashboards, and strategic insights are mathematically derived from actual transactions without any fabrication.**

---

## 📑 Table of Contents
1. [Project Overview & Dataset Provenance](#1-project-overview--dataset-provenance)
2. [Verified Enterprise KPI Scorecard](#2-verified-enterprise-kpi-scorecard)
3. [System Architecture & Data Pipeline](#3-system-architecture--data-pipeline)
4. [Relational Database Schema (Star Schema)](#4-relational-database-schema-star-schema)
5. [20 Advanced SQL Analytics Catalog](#5-20-advanced-sql-analytics-catalog)
6. [Top Strategic Business Case Studies](#6-top-strategic-business-case-studies)
7. [Automated Testing Suite](#7-automated-testing-suite)
8. [Local Quickstart & Execution Guide](#8-local-quickstart--execution-guide)

---

## 1. Project Overview & Dataset Provenance

### Dataset Specification
- **Dataset Name:** Sample Superstore Retail Sales Dataset
- **Original Source:** Tableau Public Open Data / Kaggle Open Retail Dataset Repository
- **Source Download URL:** [Raw CSV Link](https://raw.githubusercontent.com/yajasarora/Superstore-Sales-Analysis-with-Tableau/master/Superstore%20sales%20dataset.csv)
- **License:** Public Domain / Open Database License
- **Total Transactions:** 9,994 records
- **Available Fields (21):** `Row ID`, `Order ID`, `Order Date`, `Ship Date`, `Ship Mode`, `Customer ID`, `Customer Name`, `Segment`, `Country`, `City`, `State`, `Postal Code`, `Region`, `Product ID`, `Category`, `Sub-Category`, `Product Name`, `Sales`, `Quantity`, `Discount`, `Profit`
- **Fields Not in Source Dataset:** `Payment Method` *(Not available in source dataset — excluded to maintain 100% authenticity)*.

---

## 2. Verified Enterprise KPI Scorecard

All metrics below represent exact ground-truth calculations across the 9,994 transactional rows:

| Business Metric | Verified Actual Value | Analytical Interpretation |
| :--- | :--- | :--- |
| **Total Revenue** | **$2,297,200.65** | 4-year cumulative top-line gross revenue (2014–2017). |
| **Total Gross Profit** | **$286,396.54** | Aggregate realized gross earnings after Cost of Goods Sold (`Cost = Sales - Profit`). |
| **Overall Profit Margin** | **12.47%** | Net realized operating margin (`Profit / Sales * 100`). |
| **Total Completed Orders** | **5,009 Orders** | Distinct checkout transactions placed across all regions. |
| **Unique Customer Accounts** | **793 Customers** | Active customers across Consumer, Corporate, and Home Office segments. |
| **Active Product SKUs** | **1,862 Products** | Catalog breadth across Technology, Furniture, and Office Supplies. |
| **Average Order Value (AOV)**| **$458.62** | Mean basket revenue generated per completed checkout order. |
| **Repeat Customer Rate** | **98.49%** | 781 out of 793 customers placed 2 or more orders over the 4-year period. |

---

## 3. System Architecture & Data Pipeline

```
┌─────────────────────────┐     ┌───────────────────────────┐     ┌──────────────────────────┐
│  Raw Public Dataset     │ ──> │   Python ETL & Cleaning   │ ──> │  Relational Star Schema  │
│  (9,994 Transactions)   │     │  (Pandas / Date Feature)  │     │  (PostgreSQL & SQLite)   │
└─────────────────────────┘     └───────────────────────────┘     └──────────────────────────┘
                                                                               │
                                ┌───────────────────────────┐                  ▼
                                │  Executive BI Dashboards  │ ◄── ┌──────────────────────────┐
                                │  (Streamlit & Web App)    │     │  20 Advanced SQL Queries │
                                └───────────────────────────┘     │  (Window Funcs, CTEs)    │
                                                                  └──────────────────────────┘
```

---

## 4. Relational Database Schema (Star Schema)

The database models retail transactions into a normalized Star Schema:

### Dimensions
- **`dim_customers`** (`customer_id` [PK], `customer_name`, `customer_segment`, `country`, `city`, `state`, `postal_code`, `region`) — *793 rows*
- **`dim_products`** (`product_id` [PK], `product_name`, `category`, `sub_category`) — *1,862 rows*

### Fact Tables
- **`fact_orders`** (`row_id` [PK], `order_id`, `order_date`, `ship_date`, `ship_mode`, `customer_id` [FK], `product_id` [FK], `sales`, `quantity`, `discount`, `profit`, `cost`, `profit_margin_pct`, `city`, `state`, `region`) — *9,994 rows*
- **`fact_ecommerce_sales`** (Denormalized OLAP analytics table for high-speed BI querying) — *9,994 rows*

---

## 5. 20 Advanced SQL Analytics Catalog

The file [`database/analysis_queries.sql`](database/analysis_queries.sql) contains 20 production-quality analytical queries:

1. **Executive Summary KPIs** (Revenue, Profit, Orders, Customers, AOV, Margin)
2. **Monthly Revenue & Profit Velocity** (48-month longitudinal aggregation)
3. **Month-Over-Month (MoM) Growth Analysis** using `LAG()` Window Function
4. **Cumulative Running Revenue Trajectory** using `SUM() OVER ()`
5. **Top 10 Best-Selling Product SKUs** ranked by revenue and realized margin
6. **Category Performance Ranking & Market Share** (Tech vs. Furniture vs. Supplies)
7. **Top 3 Sub-Categories per Category** using `DENSE_RANK()` partitioned rankings
8. **Geographic Regional Breakdown** (Sales, profit, orders, and regional margin %)
9. **Top Category per Region** using `ROW_NUMBER() OVER (PARTITION BY region)`
10. **Top 15 High-Value VIP Customers** (Customer Lifetime Spend & Total Profit)
11. **Customer Segment Profitability** (Consumer vs. Corporate vs. Home Office)
12. **Repeat Purchase Order Frequency Distribution** (1, 2–5, 6–10, 11+ orders)
13. **Discount Depth vs. Realized Profit Margin** (Quantifying margin loss at >20% discount)
14. **Top 15 Loss-Making / Unprofitable Products**
15. **Shipping Mode Distribution & Value** (Standard Class, Second Class, First Class, Same Day)
16. **State-Level Profit Leaders & Leakers** (California & NY vs. Texas & Ohio)
17. **Quarterly Performance Trends** (Q1–Q4 seasonal dynamics)
18. **Pareto 80/20 Cumulative Product Concentration**
19. **Price Tier Margin Distribution** (Low vs. Mid vs. High vs. Premium items)
20. **Customer RFM Segmentation** (Recency, Frequency, Monetary value scoring)

---

## 6. Top Strategic Business Case Studies

Derived directly from empirical calculations in [`reports/business_insights.md`](reports/business_insights.md):

1. **Technology Profit Dominance:** Technology drives **$836,154.02 in revenue (36.40% share)** and **$145,455.03 in gross profit (50.79% of all profit)** with a **17.39% margin**.
2. **Furniture Category Margin Compression:** Furniture generated $741,999.74 in sales but yielded only **$18,451.24 in profit (2.49% margin)** due to heavy losses in Tables (-$17.7K) and Bookcases (-$3.4K).
3. **The "Discount Destruction" Cliff (>20%):** Sales at 0% discount achieved 29.9% margin; sales at 1%–20% achieved 14.5% margin; sales with **discounts >20% generated an aggregate net loss of -$32,142.98**.
4. **State-Level Profit Leaks:** Texas incurred a net loss of **-$25,729.36** and Ohio lost **-$16,971.38** due to aggressive promotional markdowns (averaging 37.1% discount in Texas).
5. **B2B / Home Office Higher Margins:** Home Office accounts achieved the highest margin at **14.03%** ($60.3K profit), followed by Corporate at **13.03%** ($91.9K profit), outperforming Consumer retail (11.55%).
6. **Pareto 80/20 SKU Revenue Concentration:** The top 15.2% of product SKUs generate 70.0% of total revenue, led by the *Canon imageCLASS 2200 Advanced Copier* ($61,599.82 in sales).

---

## 7. Automated Testing Suite

The project includes an automated test suite with 100% pass rate:

```bash
pytest -v tests/
```

- `test_data_loader.py`: Verifies raw dataset integrity and metadata.
- `test_data_cleaning.py`: Verifies schema standardization and financial consistency (`Cost = Sales - Profit`).
- `test_analysis.py`: Verifies exact mathematical KPI calculations against ground truth.
- `test_database.py`: Validates Star Schema table creation and SQL query executions.

---

## 8. Local Quickstart & Execution Guide

```bash
# 1. Clone the repository
git clone https://github.com/mahamoodmajin183-ui/shop-pulse-ecommerce-analytics.git
cd shop-pulse-ecommerce-analytics

# 2. Install dependencies
pip install -r requirements.txt

# 3. Ingest real dataset and clean data
python src/data_loader.py
python src/data_cleaning.py

# 4. Initialize and seed database
python src/database.py

# 5. Validate all 20 SQL queries
python src/validate_sql.py

# 6. Launch Live Dashboards
# Streamlit Dashboard (Port 8501)
streamlit run dashboard/app.py

# Web Dashboard Server (Port 5000)
python dashboard/server.py
```

---

## 📄 License & Attribution
- **Dataset:** Sample Superstore Dataset (Public Domain / Open Data)
- **Project License:** [MIT License](LICENSE)
- **Author:** [mahamoodmajin183-ui](https://github.com/mahamoodmajin183-ui)
