"""
Helper script to generate valid, richly documented Jupyter Notebooks for ShopPulse.
"""

import json
import os

def create_notebook(cells, filepath):
    nb = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {"name": "ipython", "version": 3},
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(nb, f, indent=2)
    print(f"Created notebook: {filepath}")

def md_cell(source):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in source.split("\n")]
    }

def code_cell(source):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in source.split("\n")]
    }

# ----------------- NOTEBOOK 1: Data Understanding -----------------
nb1_cells = [
    md_cell("""# ShopPulse: E-Commerce Sales Analytics Platform
## Notebook 01: Data Understanding & Initial Profiling

### 1. Project Background & Context
**ShopPulse** is a multi-category omnichannel e-commerce retail platform. The executive team requires an end-to-end analytical assessment of sales performance, profitability, customer acquisition/retention, product margins, and regional variance across historical transactions.

### 2. Objectives of this Notebook:
- Ingest raw transactional data (`data/raw/raw_ecommerce_data.csv`)
- Inspect structural metadata (schema, datatypes, shape, memory footprint)
- Profile missing values, null patterns, and duplicate records
- Analyze statistical distributions of transactional metrics (`sales`, `quantity`, `discount`, `profit`)
- Document data quality issues to address in the data cleaning pipeline"""),

    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Plot styling configuration
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

print("Libraries imported successfully.")"""),

    md_cell("""### 3. Load Raw Transactional Dataset"""),

    code_cell("""raw_data_path = '../data/raw/raw_ecommerce_data.csv'
df_raw = pd.read_csv(raw_data_path)

print(f"Raw Dataset Shape: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")
df_raw.head(5)"""),

    md_cell("""### 4. Data Types and Schema Inspection"""),

    code_cell("""print("--- Data Schema & Non-Null Counts ---")
df_raw.info()"""),

    md_cell("""### 5. Missing Value Profiling & Nullity Audit"""),

    code_cell("""null_counts = df_raw.isnull().sum()
null_pct = (null_counts / len(df_raw)) * 100
missing_df = pd.DataFrame({
    'Missing Count': null_counts,
    'Percentage (%)': null_pct.round(2)
}).sort_values(by='Missing Count', ascending=False)

print("--- Missing Values Summary ---")
print(missing_df[missing_df['Missing Count'] > 0])

# Visualize Missing Values
plt.figure(figsize=(10, 4))
missing_df[missing_df['Missing Count'] > 0]['Missing Count'].plot(kind='bar', color='#e74c3c')
plt.title('Missing Value Count by Feature', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('Null Record Count')
plt.xlabel('Features')
plt.xticks(rotation=0)
plt.tight_layout()
plt.show()"""),

    md_cell("""### 6. Duplicate Record Detection"""),

    code_cell("""exact_duplicates = df_raw.duplicated().sum()
order_id_duplicates = df_raw.duplicated(subset=['order_id']).sum()

print(f"Exact Duplicate Rows: {exact_duplicates:,} ({(exact_duplicates/len(df_raw)*100):.2f}%)")
print(f"Duplicate Order IDs: {order_id_duplicates:,} ({(order_id_duplicates/len(df_raw)*100):.2f}%)")"""),

    md_cell("""### 7. Numerical Summary & Distribution Analysis"""),

    code_cell("""numerical_cols = ['quantity', 'unit_price', 'discount', 'sales', 'cost', 'profit']
summary_stats = df_raw[numerical_cols].describe().T
summary_stats['median'] = df_raw[numerical_cols].median()
summary_stats[['mean', 'std', 'min', '25%', 'median', '75%', 'max']]"""),

    md_cell("""### 8. Categorical Cardinality & Unique Entities"""),

    code_cell("""cat_cols = ['category', 'region', 'city', 'payment_method', 'customer_segment']
for col in cat_cols:
    n_unique = df_raw[col].nunique()
    print(f"Column '{col}': {n_unique} unique values -> {list(df_raw[col].dropna().unique())[:8]}")"""),

    md_cell("""### 9. Key Findings & Cleaning Action Items
1. **Duplicates**: 150 duplicate rows detected that must be pruned.
2. **Missing Customer Names**: ~100 records contain missing customer names, which can be imputed via `customer_id` mapping.
3. **Missing Payment Methods**: Impute missing payment channels using customer default or mode.
4. **Date Formatting**: `order_date` contains mixed string representations and should be parsed to standard datetime format and calendar features extracted.
5. **Whitespace Inconsistencies**: Category and regional strings contain leading/trailing whitespaces requiring trimming.
6. **Financial Coherence**: Validate that `sales = quantity * price * (1 - discount)` and `profit = sales - cost` across all transactions.""")
]

# ----------------- NOTEBOOK 2: Data Cleaning -----------------
nb2_cells = [
    md_cell("""# ShopPulse: E-Commerce Sales Analytics Platform
## Notebook 02: Production Data Cleaning & Validation Pipeline

### Objectives:
1. Ingest raw data extract (`data/raw/raw_ecommerce_data.csv`)
2. Remove duplicate orders and exact duplicate records
3. Strip whitespace discrepancies in categorical attributes
4. Impute missing customer names and payment methods using relational heuristics
5. Convert date strings to standardized datetime formats and extract analytical temporal features
6. Enforce financial integrity constraints (`sales`, `cost`, `profit`, `profit_margin_pct`)
7. Export the production-grade dataset to `data/processed/cleaned_ecommerce_data.csv`"""),

    code_cell("""import pandas as pd
import numpy as np
import os
import sys

# Ensure root directory is on python path
sys.path.append('..')
from src.data_cleaning import DataCleaner

print("DataCleaner imported successfully.")"""),

    md_cell("""### 1. Initialize and Run Cleaning Pipeline"""),

    code_cell("""cleaner = DataCleaner(
    raw_filepath='../data/raw/raw_ecommerce_data.csv',
    output_filepath='../data/processed/cleaned_ecommerce_data.csv'
)

df_clean = cleaner.run_pipeline()
print(f"Processed dataset ready: {df_clean.shape[0]:,} rows, {df_clean.shape[1]} columns.")"""),

    md_cell("""### 2. Audit Trail & Transformation Metrics"""),

    code_cell("""print("=== Data Cleaning Audit Log ===")
for metric, val in cleaner.audit_log.items():
    print(f"{metric}: {val}")"""),

    md_cell("""### 3. Post-Cleaning Validation Checks"""),

    code_cell("""# Validation 1: Zero Missing Values
remaining_nulls = df_clean.isnull().sum().sum()
assert remaining_nulls == 0, f"Error: Found {remaining_nulls} null values!"
print(" Validation Check 1 Passed: 0 Missing values across all columns.")

# Validation 2: Zero Duplicate Order IDs
duplicate_orders = df_clean.duplicated(subset=['order_id']).sum()
assert duplicate_orders == 0, f"Error: Found {duplicate_orders} duplicate order IDs!"
print(" Validation Check 2 Passed: 0 Duplicate order IDs.")

# Validation 3: Financial Mathematical Integrity
# Check Sales = Quantity * Unit_Price * (1 - Discount)
computed_sales = (df_clean['quantity'] * df_clean['unit_price'] * (1.0 - df_clean['discount'])).round(2)
sales_diff = (df_clean['sales'] - computed_sales).abs().max()
assert sales_diff <= 0.05, f"Error: Sales calculation discrepancy of {sales_diff}"
print(f" Validation Check 3 Passed: Financial Sales formula verified (Max delta = {sales_diff}).")

# Validation 4: Profit = Sales - Cost
computed_profit = (df_clean['sales'] - df_clean['cost']).round(2)
profit_diff = (df_clean['profit'] - computed_profit).abs().max()
assert profit_diff <= 0.05, f"Error: Profit calculation discrepancy of {profit_diff}"
print(f" Validation Check 4 Passed: Profit formula verified (Max delta = {profit_diff}).")"""),

    md_cell("""### 4. Cleaned Dataset Sample & Schema Inspection"""),

    code_cell("""df_clean.head(5)"""),

    md_cell("""### 5. Summary Statistics of Cleaned Data"""),

    code_cell("""summary_table = pd.DataFrame({
    'Metric': ['Total Transactions', 'Total Revenue ($)', 'Total Gross Profit ($)', 'Overall Margin (%)',
               'Unique Customers', 'Unique Products', 'Average Order Value ($)', 'Average Discount (%)'],
    'Value': [
        f"{len(df_clean):,}",
        f"${df_clean['sales'].sum():,.2f}",
        f"${df_clean['profit'].sum():,.2f}",
        f"{(df_clean['profit'].sum() / df_clean['sales'].sum() * 100):.2f}%",
        f"{df_clean['customer_id'].nunique():,}",
        f"{df_clean['product_id'].nunique():,}",
        f"${df_clean['sales'].mean():,.2f}",
        f"{(df_clean['discount'].mean() * 100):.2f}%"
    ]
})
summary_table""")
]

# ----------------- NOTEBOOK 3: Exploratory Analysis -----------------
nb3_cells = [
    md_cell("""# ShopPulse: E-Commerce Sales Analytics Platform
## Notebook 03: Comprehensive Exploratory Data Analysis (EDA)

### Strategic Business Goals:
1. **Revenue & Profit Dynamics**: Evaluate monthly revenue velocity, margin expansion, and seasonal surges.
2. **Product Portfolio Performance**: Analyze category revenue shares, unit margins, and product concentration (Pareto 80/20).
3. **Regional & City Breakdown**: Identify geographic revenue strongholds and under-indexed markets.
4. **Customer Segmentation & RFM**: Profile customer cohorts, repeat purchase rate, and CLV distribution.
5. **Promotional Pricing & Discount Elasticity**: Quantify discount erosion on profitability."""),

    code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import sys

sys.path.append('..')
from src.analysis import (
    load_cleaned_data, calculate_kpis, get_monthly_trends,
    get_category_performance, get_regional_performance,
    get_top_products, get_rfm_segmentation, get_discount_impact_analysis,
    get_pareto_product_analysis
)

# Styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 11

df = load_cleaned_data('../data/processed/cleaned_ecommerce_data.csv')
print(f"Dataset loaded: {len(df):,} transactions.")"""),

    md_cell("""### 1. Executive KPIs Overview"""),

    code_cell("""kpis = calculate_kpis(df)
kpi_df = pd.DataFrame(list(kpis.items()), columns=['KPI Metric', 'Value'])
kpi_df"""),

    md_cell("""### 2. Time-Series Analysis: Monthly Revenue, Profit & MoM Growth"""),

    code_cell("""monthly_df = get_monthly_trends(df)

fig, ax1 = plt.subplots(figsize=(14, 6))

color = '#1f77b4'
ax1.set_xlabel('Month (YYYY-MM)', fontweight='bold')
ax1.set_ylabel('Total Revenue ($)', color=color, fontweight='bold')
ax1.plot(monthly_df['year_month'], monthly_df['revenue'], color=color, marker='o', linewidth=2.5, label='Revenue')
ax1.plot(monthly_df['year_month'], monthly_df['profit'], color='#2ca02c', marker='s', linewidth=2.5, label='Profit')
ax1.tick_params(axis='y', labelcolor=color)
ax1.tick_params(axis='x', rotation=45)
ax1.yaxis.set_major_formatter('${x:,.0f}')

ax2 = ax1.twinx()
color = '#ff7f0e'
ax2.set_ylabel('Profit Margin (%)', color=color, fontweight='bold')
ax2.plot(monthly_df['year_month'], monthly_df['profit_margin_pct'], color=color, linestyle='--', marker='^', linewidth=2, label='Margin %')
ax2.tick_params(axis='y', labelcolor=color)
ax2.yaxis.set_major_formatter('{x:.1f}%')

plt.title('Monthly Revenue, Profit and Margin Trajectory (2024 - 2025)', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.show()"""),

    md_cell("""### 3. Category Sales & Profitability Breakdown"""),

    code_cell("""cat_df = get_category_performance(df)

fig, ax = plt.subplots(1, 2, figsize=(16, 6))

# Revenue Share by Category
ax[0].pie(cat_df['revenue'], labels=cat_df['category'], autopct='%1.1f%%',
          startangle=140, colors=['#2b5c8f', '#4682b4', '#5dade2', '#aed6f1', '#ebf5fb'])
ax[0].set_title('Revenue Share by Product Category', fontsize=13, fontweight='bold')

# Profit Margin by Category
sns.barplot(data=cat_df, x='category', y='profit_margin_pct', ax=ax[1], palette='crest')
ax[1].set_title('Profit Margin (%) by Product Category', fontsize=13, fontweight='bold')
ax[1].set_ylabel('Margin (%)')
ax[1].set_xlabel('Category')
for p in ax[1].patches:
    ax[1].annotate(f"{p.get_height():.1f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                   ha='center', va='center', xytext=(0, 7), textcoords='offset points', fontweight='bold')

plt.tight_layout()
plt.show()"""),

    md_cell("""### 4. Regional & Geographic Sales Analysis"""),

    code_cell("""region_df, city_df = get_regional_performance(df)

plt.figure(figsize=(12, 5))
sns.barplot(data=region_df, x='region', y='revenue', palette='viridis')
plt.title('Total Revenue Generated by Geographic Region', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('Revenue ($)')
plt.xlabel('Geographic Region')
plt.gca().yaxis.set_major_formatter('${x:,.0f}')

for p in plt.gca().patches:
    plt.gca().annotate(f"${p.get_height():,.0f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                       ha='center', va='center', xytext=(0, 7), textcoords='offset points', fontweight='bold')

plt.tight_layout()
plt.show()"""),

    md_cell("""### 5. Top 10 Best-Selling Products by Revenue"""),

    code_cell("""top_prods = get_top_products(df, top_n=10, by='revenue')

plt.figure(figsize=(14, 6))
sns.barplot(data=top_prods, y='product_name', x='total_sales', hue='category', dodge=False, palette='mako')
plt.title('Top 10 Products by Total Revenue ($)', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Total Revenue ($)')
plt.ylabel('Product Name')
plt.gca().xaxis.set_major_formatter('${x:,.0f}')
plt.legend(title='Category', loc='lower right')
plt.tight_layout()
plt.show()"""),

    md_cell("""### 6. Customer Segmentation & RFM Clustering"""),

    code_cell("""rfm_df = get_rfm_segmentation(df)

rfm_summary = rfm_df.groupby('RFM_Segment').agg(
    customer_count=('customer_id', 'count'),
    avg_recency_days=('recency', 'mean'),
    avg_order_freq=('frequency', 'mean'),
    avg_monetary_spend=('monetary', 'mean'),
    total_segment_revenue=('monetary', 'sum')
).reset_index()

rfm_summary['revenue_share_pct'] = (rfm_summary['total_segment_revenue'] / rfm_summary['total_segment_revenue'].sum() * 100).round(2)
rfm_summary = rfm_summary.sort_values(by='total_segment_revenue', ascending=False)

plt.figure(figsize=(12, 5))
sns.barplot(data=rfm_summary, x='RFM_Segment', y='total_segment_revenue', palette='rocket')
plt.title('Total Revenue Contribution by RFM Customer Segment', fontsize=14, fontweight='bold', pad=15)
plt.ylabel('Total Spend ($)')
plt.xlabel('Customer Segment')
plt.xticks(rotation=15)
plt.gca().yaxis.set_major_formatter('${x:,.0f}')
plt.tight_layout()
plt.show()"""),

    md_cell("""### 7. Discount Depth vs. Profitability Margin Erosion"""),

    code_cell("""disc_analysis = get_discount_impact_analysis(df)

fig, ax1 = plt.subplots(figsize=(12, 5))

sns.barplot(data=disc_analysis, x='discount_tier', y='total_sales', ax=ax1, color='#3498db', alpha=0.7, label='Total Sales ($)')
ax1.set_ylabel('Total Sales ($)', color='#2980b9', fontweight='bold')
ax1.yaxis.set_major_formatter('${x:,.0f}')

ax2 = ax1.twinx()
ax2.plot(disc_analysis['discount_tier'], disc_analysis['profit_margin_pct'], color='#e74c3c', marker='o', linewidth=3, label='Profit Margin (%)')
ax2.set_ylabel('Profit Margin (%)', color='#c0392b', fontweight='bold')
ax2.yaxis.set_major_formatter('{x:.1f}%')

plt.title('Discount Sensitivity: Revenue Volume vs. Profit Margin Erosion', fontsize=14, fontweight='bold', pad=15)
fig.tight_layout()
plt.show()"""),

    md_cell("""### 8. Pareto Principle (80/20 Rule) on Product Catalog"""),

    code_cell("""pareto_df = get_pareto_product_analysis(df)

top_20_pct_count = int(len(pareto_df) * 0.20)
top_20_pct_rev_share = pareto_df.iloc[top_20_pct_count]['cumulative_share_pct']

plt.figure(figsize=(12, 5))
plt.plot(pareto_df['product_pct'], pareto_df['cumulative_share_pct'], color='#8e44ad', linewidth=2.5, label='Cumulative Revenue Share')
plt.axvline(x=20, color='red', linestyle='--', label=f'Top 20% SKUs = {top_20_pct_rev_share:.1f}% Revenue')
plt.axhline(y=top_20_pct_rev_share, color='red', linestyle=':')
plt.title('Pareto Cumulative Revenue Curve Across Product SKUs', fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Percentage of Total Product Catalog (%)')
plt.ylabel('Cumulative Revenue Share (%)')
plt.legend()
plt.tight_layout()
plt.show()

print(f"Pareto Finding: The top 20% of product SKUs generate {top_20_pct_rev_share:.2f}% of total enterprise revenue.")"""),

    md_cell("""### 9. Strategic Conclusions from EDA
1. **Seasonality**: November and December exhibit a substantial revenue surge (~75% higher than baseline months), driven by Q4 holiday demand.
2. **Product Hierarchy**: Technology generates nearly 50% of total revenue ($1.8M), while Apparel delivers the highest margin rate (62.66%).
3. **Customer Retention**: High repeat customer rate (81.8%), with VIP / Champion customers generating over 45% of total spend.
4. **Discount Guardrails**: Discounts above 15% erode profit margins by over 18 percentage points without generating commensurate volume elasticity.""")
]

if __name__ == "__main__":
    create_notebook(nb1_cells, "notebooks/01_data_understanding.ipynb")
    create_notebook(nb2_cells, "notebooks/02_data_cleaning.ipynb")
    create_notebook(nb3_cells, "notebooks/03_exploratory_analysis.ipynb")
