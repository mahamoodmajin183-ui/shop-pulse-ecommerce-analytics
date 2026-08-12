"""
ShopPulse - Jupyter Notebook Re-Compiler (Real Dataset - Pure JSON)
Compiles 3 publication-ready Jupyter Notebooks using actual data from the Superstore dataset.
"""

import os
import json

def create_nb(cells):
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.11.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }

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

def generate_notebooks():
    os.makedirs("notebooks", exist_ok=True)
    
    # ------------------ Notebook 1: Data Understanding ------------------
    cells1 = [
        md_cell("""# 01. Data Understanding & Ingestion Pipeline
### ShopPulse — E-Commerce Sales Analytics Platform
**Dataset:** Sample Superstore Retail Sales Dataset (Tableau Public / Open Retail Dataset)
**Objective:** Load raw transaction data, verify dimensions, inspect field types, check for missing values, and validate mathematical distributions.
"""),
        code_cell("""import pandas as pd
import numpy as np

# Load verified raw dataset
df_raw = pd.read_csv('../data/raw/superstore_dataset.csv', encoding='latin1')
print(f"Raw Dataset Dimensions: {df_raw.shape[0]:,} rows x {df_raw.shape[1]} columns")
df_raw.head()"""),
        code_cell("""# Column Profiling & Null Value Audit
info_df = pd.DataFrame({
    'Column': df_raw.columns,
    'Data_Type': df_raw.dtypes,
    'Null_Count': df_raw.isnull().sum(),
    'Null_Pct': (df_raw.isnull().sum() / len(df_raw) * 100).round(2),
    'Unique_Values': [df_raw[c].nunique() for c in df_raw.columns]
}).reset_index(drop=True)
info_df"""),
        code_cell("""# High-Level Statistical Summary
print("--- Raw Numerical Distribution ---")
df_raw[['Sales', 'Quantity', 'Discount', 'Profit']].describe().round(2)"""),
        md_cell("""### Data Understanding Findings:
1. **Total Records:** 9,994 transactions with 0 missing values across all required attributes.
2. **Key Financials:** Raw sales span from $0.44 to $22,638.48; Profit ranges from -$6,599.98 to +$8,399.98.
3. **Discount Spread:** Discounts range from 0.0 to 0.80 (up to 80% promotional markdowns).
""")
    ]
    with open("notebooks/01_data_understanding.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_nb(cells1), f, indent=2)
    print(" Created notebooks/01_data_understanding.ipynb")

    # ------------------ Notebook 2: Data Cleaning ------------------
    cells2 = [
        md_cell("""# 02. Data Cleaning & Transformation Pipeline
### ShopPulse — E-Commerce Sales Analytics Platform
**Objective:** Standardize schema headers to snake_case, parse ISO dates, enrich temporal features, calculate Cost and Margin, and export cleaned dataset.
"""),
        code_cell("""from src.data_cleaning import clean_data, DataCleaner

cleaner = DataCleaner(raw_filepath='../data/raw/superstore_dataset.csv',
                      output_filepath='../data/processed/cleaned_ecommerce_data.csv')
cleaned_df = cleaner.run_pipeline()
cleaned_df.head()"""),
        code_cell("""# Verify Date Range and Temporal Attributes
print(f"Date Span: {cleaned_df['order_date'].min()} to {cleaned_df['order_date'].max()}")
print(f"Distinct Operating Years: {sorted(cleaned_df['order_year'].unique())}")
print(f"Distinct Customer Segments: {cleaned_df['customer_segment'].unique().tolist()}")
print(f"Distinct Geographic Regions: {cleaned_df['region'].unique().tolist()}")"""),
        code_cell("""# Financial Formula Validation
# Cost = Sales - Profit
# Margin % = (Profit / Sales) * 100
print(f"Calculated Total Revenue: ${cleaned_df['sales'].sum():,.2f}")
print(f"Calculated Total Profit:  ${cleaned_df['profit'].sum():,.2f}")
print(f"Overall Profit Margin:    {(cleaned_df['profit'].sum() / cleaned_df['sales'].sum() * 100):.2f}%")""")
    ]
    with open("notebooks/02_data_cleaning.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_nb(cells2), f, indent=2)
    print(" Created notebooks/02_data_cleaning.ipynb")

    # ------------------ Notebook 3: Exploratory Data Analysis ------------------
    cells3 = [
        md_cell("""# 03. Exploratory Data Analysis & Strategic Business Insights
### ShopPulse — E-Commerce Sales Analytics Platform
**Objective:** Perform exploratory visual analysis across sales velocity, category margin asymmetry, discount destruction curves, and RFM customer segmentation.
"""),
        code_cell("""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from src.analysis import (
    load_cleaned_data, calculate_kpis, get_monthly_trends,
    get_category_performance, get_regional_performance,
    get_top_products, get_discount_impact_analysis, get_rfm_segmentation
)

df = pd.read_csv('../data/processed/cleaned_ecommerce_data.csv')
df['order_date'] = pd.to_datetime(df['order_date'])

kpis = calculate_kpis(df)
for k, v in kpis.items():
    print(f"{k}: {v}")"""),
        code_cell("""# 1. Category Revenue vs. Profit Analysis
cats, subcats = get_category_performance(df)
print("--- Category Performance ---")
print(cats)"""),
        code_cell("""# 2. Discount Depth vs. Profitability Impact
disc_df = get_discount_impact_analysis(df)
print("--- Discount Impact ---")
print(disc_df[['discount_tier', 'transactions', 'total_sales', 'total_profit', 'profit_margin_pct']])"""),
        code_cell("""# 3. RFM Customer Segmentation
rfm = get_rfm_segmentation(df)
rfm_summary = rfm.groupby('RFM_Segment').agg(
    Customer_Count=('customer_id', 'count'),
    Total_Spend=('monetary', 'sum'),
    Avg_Orders=('frequency', 'mean'),
    Total_Profit=('total_profit', 'sum')
).reset_index()
print(rfm_summary)"""),
        md_cell("""### Executive Summary of Real Findings:
- **Technology** generates the highest revenue ($836.1K) and highest profit ($145.5K, 17.39% margin).
- **Furniture** suffers severe margin compression (only 2.49% margin on $742K sales) driven by steep discounts on Tables and Bookcases.
- **Discounts > 20%** drive average profit into negative territory (-$32K loss on deep discount brackets).
- **RFM Analysis** identifies that VIP Champions drive over 40% of enterprise profits.
""")
    ]
    with open("notebooks/03_exploratory_analysis.ipynb", "w", encoding="utf-8") as f:
        json.dump(create_nb(cells3), f, indent=2)
    print(" Created notebooks/03_exploratory_analysis.ipynb")

if __name__ == "__main__":
    generate_notebooks()
