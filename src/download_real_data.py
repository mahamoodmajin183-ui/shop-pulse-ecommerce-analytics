"""
Scratch script to download and profile real e-commerce datasets.
"""
import urllib.request
import os
import pandas as pd

os.makedirs("data/raw", exist_ok=True)

# 1. Download Superstore Dataset
superstore_url = "https://raw.githubusercontent.com/yajasarora/Superstore-Sales-Analysis-with-Tableau/master/Superstore%20sales%20dataset.csv"
superstore_path = "data/raw/superstore_dataset.csv"

try:
    print("Downloading Superstore dataset...")
    urllib.request.urlretrieve(superstore_url, superstore_path)
    df_super = pd.read_csv(superstore_path, encoding="latin1")
    print("\n--- Superstore Dataset Profile ---")
    print(f"Rows: {len(df_super):,}")
    print(f"Columns ({len(df_super.columns)}): {list(df_super.columns)}")
    print(f"Unique Orders: {df_super['Order ID'].nunique():,}")
    print(f"Unique Customers: {df_super['Customer ID'].nunique():,}")
    print(f"Unique Products: {df_super['Product ID'].nunique():,}")
    print(f"Categories: {df_super['Category'].unique().tolist()}")
    print(f"Regions: {df_super['Region'].unique().tolist()}")
    print(f"Total Sales: ${df_super['Sales'].sum():,.2f}")
    if 'Profit' in df_super.columns:
        print(f"Total Profit: ${df_super['Profit'].sum():,.2f}")
    print(f"Date Range: {df_super['Order Date'].min()} to {df_super['Order Date'].max()}")
except Exception as e:
    print(f"Failed to download/profile Superstore: {e}")

# 2. Download UCI Online Retail Dataset
uci_url = "https://raw.githubusercontent.com/databricks/Spark-The-Definitive-Guide/master/data/retail-data/all/online-retail-dataset.csv"
uci_path = "data/raw/online_retail_uci.csv"

try:
    print("\nDownloading UCI Online Retail dataset...")
    urllib.request.urlretrieve(uci_url, uci_path)
    df_uci = pd.read_csv(uci_path)
    print("\n--- UCI Online Retail Dataset Profile ---")
    print(f"Rows: {len(df_uci):,}")
    print(f"Columns ({len(df_uci.columns)}): {list(df_uci.columns)}")
    print(f"Unique Invoices: {df_uci['InvoiceNo'].nunique():,}")
    print(f"Unique Customers: {df_uci['CustomerID'].nunique():,}")
    print(f"Unique Products: {df_uci['StockCode'].nunique():,}")
    print(f"Date Range: {df_uci['InvoiceDate'].min()} to {df_uci['InvoiceDate'].max()}")
except Exception as e:
    print(f"Failed to download/profile UCI: {e}")
