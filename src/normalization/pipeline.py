"""Multi-view normalization pipeline orchestrator.

Applies deterministic multi-view normalization across single records, pandas Series, or DataFrames.
Preserves all original fields untouched and appends derived multi-view representations.
"""

from typing import Any, Dict, List, Optional
import pandas as pd

from src.normalization.address import (
    extract_numeric_tokens,
    get_address_compact,
    get_address_latinized,
    get_address_norm,
    get_address_tokens,
    normalize_business_address_all_views,
)
from src.normalization.country import normalize_country
from src.normalization.name import (
    get_name_compact,
    get_name_latinized,
    get_name_legal_stripped,
    get_name_norm,
    get_name_tokens,
    normalize_business_name_all_views,
)


def normalize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """Normalizes a single entity record dictionary, returning a new dictionary with all views added.
    
    Original keys are preserved intact.
    """
    out = dict(record)
    
    # Business name views
    b_name = record.get("business_name", "")
    name_views = normalize_business_name_all_views(b_name)
    out.update(name_views)
    
    # Business address views
    b_addr = record.get("business_address", "")
    addr_views = normalize_business_address_all_views(b_addr)
    out.update(addr_views)
    
    # Country view
    country = record.get("country", "")
    out["country_norm"] = normalize_country(country)
    
    return out


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Vectorized/efficient batch multi-view normalization on a pandas DataFrame.
    
    Returns a NEW DataFrame containing all original columns plus derived normalized view columns.
    Original DataFrame columns are never modified.
    """
    out_df = df.copy()
    
    # Process Business Name
    if "business_name" in out_df.columns:
        name_series = out_df["business_name"].fillna("").astype(str)
        out_df["name_norm"] = name_series.apply(get_name_norm)
        out_df["name_compact"] = name_series.apply(get_name_compact)
        out_df["name_latinized"] = name_series.apply(get_name_latinized)
        out_df["name_transliterated"] = out_df["name_latinized"]  # Alias for backwards compatibility
        out_df["name_legal_stripped"] = name_series.apply(get_name_legal_stripped)
        out_df["name_tokens"] = name_series.apply(get_name_tokens)
        
    # Process Business Address
    if "business_address" in out_df.columns:
        addr_series = out_df["business_address"].fillna("").astype(str)
        out_df["address_norm"] = addr_series.apply(get_address_norm)
        out_df["address_compact"] = addr_series.apply(get_address_compact)
        out_df["address_latinized"] = addr_series.apply(get_address_latinized)
        out_df["address_transliterated"] = out_df["address_latinized"]  # Alias for backwards compatibility
        out_df["address_tokens"] = addr_series.apply(get_address_tokens)
        out_df["address_numeric_tokens"] = addr_series.apply(extract_numeric_tokens)
        out_df["address_has_digits"] = out_df["address_numeric_tokens"].apply(lambda x: len(x) > 0)
        out_df["address_token_count"] = out_df["address_tokens"].apply(len)
        out_df["address_char_length"] = out_df["address_norm"].apply(len)
        
    # Process Country
    if "country" in out_df.columns:
        country_series = out_df["country"].fillna("").astype(str)
        out_df["country_norm"] = country_series.apply(normalize_country)
        
    return out_df
