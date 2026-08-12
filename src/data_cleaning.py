"""
ShopPulse - Production Data Cleaning and Validation Pipeline
Performs deduplication, missing value resolution, data type normalization,
business rule validations, and produces clean analytics-ready datasets.
"""

import os
import logging
import pandas as pd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("ShopPulseCleaner")

class DataCleaner:
    """Enterprise Data Cleaning and Transformation Engine for E-Commerce Data."""

    def __init__(self, raw_filepath: str = "data/raw/raw_ecommerce_data.csv",
                 output_filepath: str = "data/processed/cleaned_ecommerce_data.csv"):
        self.raw_filepath = raw_filepath
        self.output_filepath = output_filepath
        self.audit_log = {}

    def load_data(self) -> pd.DataFrame:
        """Load raw dataset from disk."""
        if not os.path.exists(self.raw_filepath):
            raise FileNotFoundError(f"Raw data file not found at: {self.raw_filepath}")
        
        df = pd.read_csv(self.raw_filepath)
        self.audit_log["initial_record_count"] = len(df)
        self.audit_log["initial_column_count"] = len(df.columns)
        logger.info(f"Loaded raw dataset with {len(df):,} records and {len(df.columns)} columns.")
        return df

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Identify and remove exact and order-id duplicate records."""
        # Exact row duplicates
        exact_dupes = df.duplicated().sum()
        df = df.drop_duplicates().reset_index(drop=True)
        
        # Order ID duplicates if any
        order_dupes = df.duplicated(subset=["order_id"]).sum()
        if order_dupes > 0:
            df = df.drop_duplicates(subset=["order_id"], keep="first").reset_index(drop=True)
            
        total_removed = exact_dupes + order_dupes
        self.audit_log["duplicates_removed"] = int(total_removed)
        logger.info(f"Deduplication complete: Removed {total_removed:,} duplicate rows.")
        return df

    def standardize_strings(self, df: pd.DataFrame) -> pd.DataFrame:
        """Strip whitespace and normalize casing for all categorical columns."""
        string_cols = ["customer_id", "customer_name", "product_id", "product_name",
                       "category", "region", "city", "payment_method", "customer_segment"]
        
        for col in string_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                # Replace 'nan' string with actual np.nan
                df[col] = df[col].replace({"nan": np.nan, "None": np.nan, "": np.nan})
                
        # Title case for regions and segments
        if "region" in df.columns:
            df["region"] = df["region"].str.title()
        if "category" in df.columns:
            df["category"] = df["category"].str.title()
        if "customer_segment" in df.columns:
            df["customer_segment"] = df["customer_segment"].str.title()

        logger.info("Categorical strings trimmed and standardized.")
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Impute missing values using entity mappings and business defaults."""
        null_counts_before = df.isnull().sum().to_dict()
        self.audit_log["nulls_before_imputation"] = {k: int(v) for k, v in null_counts_before.items() if v > 0}
        
        # 1. Customer Name mapping: if known from other transactions with same customer_id
        known_names = df.dropna(subset=["customer_name"]).drop_duplicates(subset=["customer_id"]).set_index("customer_id")["customer_name"].to_dict()
        df["customer_name"] = df.apply(
            lambda r: known_names.get(r["customer_id"], f"Customer {r['customer_id']}") if pd.isna(r["customer_name"]) else r["customer_name"],
            axis=1
        )
        
        # 2. Payment Method imputation: use customer's most frequent method or overall mode
        default_payment = df["payment_method"].mode()[0] if not df["payment_method"].empty else "Credit Card"
        df["payment_method"] = df["payment_method"].fillna(default_payment)
        
        # 3. Numeric null checks (fallback to 0)
        numeric_defaults = {
            "quantity": 1,
            "unit_price": 0.0,
            "discount": 0.0,
            "sales": 0.0,
            "cost": 0.0,
            "profit": 0.0
        }
        for col, default_val in numeric_defaults.items():
            if col in df.columns and df[col].isnull().sum() > 0:
                df[col] = df[col].fillna(default_val)
                
        null_counts_after = df.isnull().sum().to_dict()
        self.audit_log["nulls_after_imputation"] = {k: int(v) for k, v in null_counts_after.items() if v > 0}
        logger.info(f"Missing values handled successfully. Remaining nulls: {sum(null_counts_after.values())}")
        return df

    def parse_dates_and_enrich(self, df: pd.DataFrame) -> pd.DataFrame:
        """Parse mixed date formats and enrich with calendar temporal features."""
        # Convert date column with robust parsing
        df["order_date"] = pd.to_datetime(df["order_date"], format='mixed', errors='coerce')
        
        # Drop rows where date parsing completely failed (if any)
        invalid_dates = df["order_date"].isnull().sum()
        if invalid_dates > 0:
            df = df.dropna(subset=["order_date"]).reset_index(drop=True)
            logger.warning(f"Dropped {invalid_dates} rows with unparseable dates.")
            
        # Enrich with analytical date attributes
        df["order_date"] = pd.to_datetime(df["order_date"], format='mixed', errors='coerce').dt.round('s')
        df["order_year"] = df["order_date"].dt.year
        df["order_month"] = df["order_date"].dt.month
        df["order_year_month"] = df["order_date"].dt.to_period("M").astype(str)
        df["order_quarter"] = df["order_date"].dt.to_period("Q").astype(str)
        df["order_day_name"] = df["order_date"].dt.day_name()
        df["order_hour"] = df["order_date"].dt.hour
        df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
        
        logger.info("Date columns normalized and enriched with calendar features.")
        return df

    def validate_and_correct_financials(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Validate and ensure mathematical integrity across quantities, unit prices,
        discounts, sales, costs, and profits.
        """
        # Ensure correct datatypes
        df["quantity"] = df["quantity"].astype(int)
        df["unit_price"] = df["unit_price"].astype(float).round(2)
        df["discount"] = df["discount"].astype(float).clip(lower=0.0, upper=0.70).round(2)
        
        # Enforce business rules:
        # Sales = Quantity * Unit_Price * (1 - Discount)
        expected_sales = (df["quantity"] * df["unit_price"] * (1.0 - df["discount"])).round(2)
        discrepant_sales = (df["sales"] - expected_sales).abs() > 0.05
        df.loc[discrepant_sales, "sales"] = expected_sales[discrepant_sales]
        
        # Cost validation
        df["cost"] = df["cost"].astype(float).round(2)
        
        # Profit = Sales - Cost
        expected_profit = (df["sales"] - df["cost"]).round(2)
        discrepant_profit = (df["profit"] - expected_profit).abs() > 0.05
        df.loc[discrepant_profit, "profit"] = expected_profit[discrepant_profit]
        
        # Add Profit Margin ratio (%)
        df["profit_margin_pct"] = np.where(
            df["sales"] > 0,
            (df["profit"] / df["sales"] * 100.0).round(2),
            0.0
        )
        
        # Sanity checks: Quantity > 0, Unit Price > 0
        valid_mask = (df["quantity"] > 0) & (df["unit_price"] > 0)
        invalid_count = (~valid_mask).sum()
        if invalid_count > 0:
            df = df[valid_mask].reset_index(drop=True)
            logger.warning(f"Filtered out {invalid_count} records with non-positive price/quantity.")

        logger.info("Financial integrity verified: Sales, Discounts, Costs, and Profit Margins validated.")
        return df

    def run_pipeline(self) -> pd.DataFrame:
        """Execute full cleaning and validation pipeline."""
        logger.info("--- Starting ShopPulse Data Cleaning Pipeline ---")
        df = self.load_data()
        df = self.remove_duplicates(df)
        df = self.standardize_strings(df)
        df = self.handle_missing_values(df)
        df = self.parse_dates_and_enrich(df)
        df = self.validate_and_correct_financials(df)
        
        # Sort chronologically
        df = df.sort_values(by="order_date").reset_index(drop=True)
        
        self.audit_log["final_record_count"] = len(df)
        self.audit_log["final_column_count"] = len(df.columns)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(self.output_filepath), exist_ok=True)
        df.to_csv(self.output_filepath, index=False)
        logger.info(f"Cleaned dataset saved successfully to: {self.output_filepath}")
        logger.info(f"Final dataset shape: {df.shape[0]:,} rows x {df.shape[1]} columns.")
        logger.info("--- Pipeline Completed Successfully ---")
        return df

def clean_data(raw_path: str = "data/raw/raw_ecommerce_data.csv",
               output_path: str = "data/processed/cleaned_ecommerce_data.csv") -> pd.DataFrame:
    """Convenience function to run cleaning pipeline."""
    cleaner = DataCleaner(raw_filepath=raw_path, output_filepath=output_path)
    return cleaner.run_pipeline()

if __name__ == "__main__":
    cleaned_df = clean_data()
    print("\n--- Data Cleaning Audit Summary ---")
    print(f"Total Rows: {len(cleaned_df):,}")
    print(f"Total Revenue: ${cleaned_df['sales'].sum():,.2f}")
    print(f"Total Profit: ${cleaned_df['profit'].sum():,.2f}")
    print(f"Overall Profit Margin: {(cleaned_df['profit'].sum() / cleaned_df['sales'].sum() * 100):.2f}%")
    print(f"Unique Customers: {cleaned_df['customer_id'].nunique():,}")
    print(f"Unique Products: {cleaned_df['product_id'].nunique():,}")
    print(f"Date Span: {cleaned_df['order_date'].min()} to {cleaned_df['order_date'].max()}")
