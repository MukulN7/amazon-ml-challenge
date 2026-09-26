"""Unit tests for normalization pipeline (src/normalization/pipeline.py)."""

import pandas as pd
import pytest
from src.normalization.pipeline import normalize_dataframe, normalize_record


def test_normalize_record():
    record = {
        "entity_id": "S1-001",
        "business_name": "  Acme Corporation, Ltd. ",
        "business_address": " 100 Main St, Suite 5, NY 10001 ",
        "country": " US ",
    }
    
    norm_rec = normalize_record(record)
    
    # Original keys preserved untouched
    assert norm_rec["entity_id"] == "S1-001"
    assert norm_rec["business_name"] == "  Acme Corporation, Ltd. "
    assert norm_rec["business_address"] == " 100 Main St, Suite 5, NY 10001 "
    assert norm_rec["country"] == " US "
    
    # New multi-view keys added
    assert norm_rec["name_norm"] == "acme corporation ltd"
    assert norm_rec["name_compact"] == "acmecorporationltd"
    assert norm_rec["name_latinized"] == "acme corporation ltd"
    assert norm_rec["address_norm"] == "100 main st suite 5 ny 10001"
    assert norm_rec["address_latinized"] == "100 main st suite 5 ny 10001"
    assert norm_rec["has_digits"] is True
    assert norm_rec["country_norm"] == "US"


def test_normalize_dataframe():
    df = pd.DataFrame([
        {
            "entity_id": "S1-001",
            "business_name": "Acme Corp",
            "business_address": "123 Main St",
            "country": "US",
        },
        {
            "entity_id": "S2-002",
            "business_name": "Société Générale SARL",
            "business_address": "78 Rue de Rivoli, Apt 004",
            "country": "France",
        },
    ])
    
    orig_df = df.copy()
    norm_df = normalize_dataframe(df)
    
    # Original DataFrame columns were NOT modified
    pd.testing.assert_frame_equal(df, orig_df)
    
    # Derived columns exist
    assert "name_norm" in norm_df.columns
    assert "name_compact" in norm_df.columns
    assert "name_latinized" in norm_df.columns
    assert "address_norm" in norm_df.columns
    assert "address_latinized" in norm_df.columns
    assert "address_numeric_tokens" in norm_df.columns
    assert "country_norm" in norm_df.columns
    
    assert norm_df.loc[1, "country_norm"] == "France"
    assert norm_df.loc[1, "name_latinized"] == "societe generale sarl"
    assert norm_df.loc[1, "address_numeric_tokens"] == ["78", "004"]
