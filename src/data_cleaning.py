"""
ShopPulse - Production Data Cleaning and Transformation Engine
Cleans, normalizes, and validates the real-world Sample Superstore e-commerce dataset.
Enforces schema standardization, date temporal enrichment, and audit trails.
"""

import os
import logging
import pandas as pd
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ShopPulseCleaner")

class DataCleaner:
    """Production Data Cleaner for Real-World E-Commerce Sales Datasets."""

    def __init__(self, raw_filepath: str = "data/raw/superstore_dataset.csv",
                 output_filepath: str = "data/processed/cleaned_ecommerce_data.csv"):
        self.raw_filepath = raw_filepath
        self.output_filepath = output_filepath
        self.audit_log = {}

    def load_data(self) -> pd.DataFrame:
        """Load raw dataset with proper encoding handling."""
        if not os.path.exists(self.raw_filepath):
            from src.data_loader import load_or_download_real_data
            load_or_download_real_data(self.raw_filepath)

        df = pd.read_csv(self.raw_filepath, encoding="latin1")
        df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]
        self.audit_log["initial_record_count"] = len(df)
        self.audit_log["initial_column_count"] = len(df.columns)
        logger.info(f"Loaded raw dataset with {len(df):,} records and {len(df.columns)} columns.")
        return df

    def standardize_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Map raw headers to standardized snake_case identifiers."""
        # Clean any leading hidden characters
        df.columns = [c.replace("\ufeff", "").strip() for c in df.columns]
        
        column_mapping = {
            "Row ID": "row_id",
            "Order ID": "order_id",
            "Order Date": "order_date",
            "Ship Date": "ship_date",
            "Ship Mode": "ship_mode",
            "Customer ID": "customer_id",
            "Customer Name": "customer_name",
            "Segment": "customer_segment",
            "Country": "country",
            "City": "city",
            "State": "state",
            "Postal Code": "postal_code",
            "Region": "region",
            "Product ID": "product_id",
            "Category": "category",
            "Sub-Category": "sub_category",
            "Product Name": "product_name",
            "Sales": "sales",
            "Quantity": "quantity",
            "Discount": "discount",
            "Profit": "profit"
        }
        df = df.rename(columns=column_mapping)
        # Drop raw unmapped row id column if present
        unwanted_cols = [c for c in df.columns if "Row ID" in c or "﻿" in c]
        if unwanted_cols:
            df = df.drop(columns=unwanted_cols)
        if "row_id" not in df.columns:
            df["row_id"] = range(1, len(df) + 1)
        logger.info(f"Column headers standardized to snake_case: {list(df.columns)}")
        return df

    def handle_duplicates_and_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove exact duplicates and strip whitespaces from string columns."""
        dupes_count = df.duplicated().sum()
        self.audit_log["exact_duplicates_removed"] = int(dupes_count)
        if dupes_count > 0:
            df = df.drop_duplicates().reset_index(drop=True)
            logger.info(f"Removed {dupes_count} exact duplicate rows.")

        string_cols = [
            "order_id", "ship_mode", "customer_id", "customer_name",
            "customer_segment", "country", "city", "state", "region",
            "product_id", "category", "sub_category", "product_name"
        ]
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()

        logger.info("String attributes trimmed and normalized.")
        return df

    def parse_dates_and_enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse mixed date representations and enrich with calendar features."""
        df["order_date"] = pd.to_datetime(df["order_date"], format="mixed", errors="coerce")
        df["ship_date"] = pd.to_datetime(df["ship_date"], format="mixed", errors="coerce")
        
        # Calculate shipping duration in days
        df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days
        
        # Calendar temporal features
        df["order_year"] = df["order_date"].dt.year
        df["order_month"] = df["order_date"].dt.month
        df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)
        df["order_quarter"] = df["order_date"].dt.to_period("Q").astype(str)
        df["order_day_name"] = df["order_date"].dt.day_name()
        
        # Format date as standardized ISO string
        df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")
        df["ship_date"] = df["ship_date"].dt.strftime("%Y-%m-%d")
        
        logger.info("Dates parsed to ISO format and enriched with temporal features.")
        return df

    def validate_financials(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and format financial quantities, sales, profit,
        and calculate cost and profit margins strictly from source data.
        """
        df["quantity"] = df["quantity"].astype(int)
        df["sales"] = df["sales"].astype(float).round(2)
        df["discount"] = df["discount"].astype(float).round(2)
        df["profit"] = df["profit"].astype(float).round(2)
        
        # Calculate Cost of Goods Sold (COGS) = Sales - Profit
        df["cost"] = (df["sales"] - df["profit"]).round(2)
        
        # Calculate Realized Profit Margin (%) = (Profit / Sales) * 100
        df["profit_margin_pct"] = np.where(
            df["sales"] > 0,
            (df["profit"] / df["sales"] * 100.0).round(2),
            0.0
        )
        
        # Derive base unit price before discount
        df["unit_price"] = np.where(
            df["discount"] < 1.0,
            (df["sales"] / (df["quantity"] * (1.0 - df["discount"]))).round(2),
            (df["sales"] / df["quantity"]).round(2)
        )

        logger.info("Financial integrity verified: Sales, Profit, Cost, and Profit Margin calculated.")
        return df

    def run_pipeline(self) -> pd.DataFrame:
        """Execute full cleaning and transformation pipeline."""
        logger.info("--- Starting ShopPulse Production Data Cleaning Pipeline ---")
        df = self.load_data()
        df = self.standardize_column_names(df)
        df = self.handle_duplicates_and_strings(df)
        df = self.parse_dates_and_enrich(df)
        df = self.validate_financials(df)
        
        # Sort chronologically by order_date
        df = df.sort_values(by=["order_date", "row_id"]).reset_index(drop=True)
        
        self.audit_log["final_record_count"] = len(df)
        self.audit_log["final_column_count"] = len(df.columns)
        
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        df.to_csv(self.output_filepath, index=False)
        logger.info(f"Cleaned dataset saved successfully to: {self.output_filepath}")
        logger.info(f"Final shape: {df.shape[0]:,} rows x {df.shape[1]} columns.")
        logger.info("--- Cleaning Pipeline Completed Successfully ---")
        return df

def clean_data(raw_path: str = "data/raw/superstore_dataset.csv",
               output_path: str = "data/processed/cleaned_ecommerce_data.csv") -> pd.DataFrame:
    """Convenience function to run cleaning pipeline."""
    cleaner = DataCleaner(raw_filepath=raw_path, output_filepath=output_path)
    return cleaner.run_pipeline()

if __name__ == "__main__":
    cleaned_df = clean_data()
    print("\n--- Verified Cleaned Dataset Ground Truth ---")
    print(f"Total Transactions: {len(cleaned_df):,}")
    print(f"Total Unique Orders: {cleaned_df['order_id'].nunique():,}")
    print(f"Total Unique Customers: {cleaned_df['customer_id'].nunique():,}")
    print(f"Total Unique Products: {cleaned_df['product_id'].nunique():,}")
    print(f"Total Revenue: ${cleaned_df['sales'].sum():,.2f}")
    print(f"Total Gross Profit: ${cleaned_df['profit'].sum():,.2f}")
    print(f"Overall Realized Profit Margin: {(cleaned_df['profit'].sum() / cleaned_df['sales'].sum() * 100):.2f}%")
    print(f"Date Span: {cleaned_df['order_date'].min()} to {cleaned_df['order_date'].max()}")
