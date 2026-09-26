"""Text and attribute multi-view normalization package for Amazon ML Challenge 2026."""

from src.normalization.text import (
    base_normalize,
    case_fold,
    clean_punctuation,
    latinize_text,
    normalize_whitespace,
    remove_diacritics,
    transliterate_to_ascii,
    unicode_normalize,
)
from src.normalization.name import (
    get_name_compact,
    get_name_latinized,
    get_name_legal_stripped,
    get_name_norm,
    get_name_tokens,
    get_name_transliterated,
    normalize_business_name_all_views,
)
from src.normalization.address import (
    extract_numeric_tokens,
    get_address_compact,
    get_address_latinized,
    get_address_norm,
    get_address_tokens,
    get_address_transliterated,
    normalize_business_address_all_views,
)
from src.normalization.country import normalize_country
from src.normalization.pipeline import normalize_dataframe, normalize_record

__all__ = [
    "base_normalize",
    "case_fold",
    "clean_punctuation",
    "normalize_whitespace",
    "remove_diacritics",
    "latinize_text",
    "transliterate_to_ascii",
    "unicode_normalize",
    "get_name_norm",
    "get_name_compact",
    "get_name_tokens",
    "get_name_latinized",
    "get_name_transliterated",
    "get_name_legal_stripped",
    "normalize_business_name_all_views",
    "get_address_norm",
    "get_address_compact",
    "get_address_tokens",
    "get_address_latinized",
    "get_address_transliterated",
    "extract_numeric_tokens",
    "normalize_business_address_all_views",
    "normalize_country",
    "normalize_record",
    "normalize_dataframe",
]
