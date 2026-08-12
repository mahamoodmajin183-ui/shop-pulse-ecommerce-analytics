"""Unit tests for the real data loader module."""
import os
import pandas as pd
from src.data_loader import load_or_download_real_data, DATASET_METADATA

def test_dataset_metadata_completeness():
    assert "dataset_name" in DATASET_METADATA
    assert "source_url" in DATASET_METADATA
    assert DATASET_METADATA["raw_records"] == 9994
    assert DATASET_METADATA["raw_columns"] == 21

def test_load_or_download_real_data():
    df = load_or_download_real_data()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 9994
    assert len(df.columns) >= 20
    assert "Order ID" in df.columns or "order_id" in df.columns
