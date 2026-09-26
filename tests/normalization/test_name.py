"""Unit tests for business name multi-view normalization (src/normalization/name.py)."""

import pytest
from src.normalization.name import (
    get_name_compact,
    get_name_latinized,
    get_name_legal_stripped,
    get_name_norm,
    get_name_tokens,
    normalize_business_name_all_views,
)


def test_name_norm_latin_and_devanagari():
    raw_latin = "  Acme Corporation, Pvt. Ltd. "
    assert get_name_norm(raw_latin) == "acme corporation pvt ltd"
    
    raw_devanagari = "राम मार्केटिंग प्राइवेट लिमिटेड"
    assert get_name_norm(raw_devanagari) == "राम मार्केटिंग प्राइवेट लिमिटेड"


def test_name_compact():
    raw = " Acme - Corp (US) 123! "
    assert get_name_compact(raw) == "acmecorpus123"
    
    raw_devanagari = "राम मार्केटिंग"
    assert get_name_compact(raw_devanagari) == "राममार्केटिंग"


def test_name_tokens():
    raw = "Global Tech Logistics"
    assert get_name_tokens(raw) == ["global", "tech", "logistics"]


def test_name_latinized():
    raw = "Société Générale (France)"
    assert get_name_latinized(raw) == "societe generale france"


def test_name_legal_stripped():
    raw = "Acme Corporation Private Limited"
    # Legal terms stripped from secondary view
    assert get_name_legal_stripped(raw) == "acme"
    # Primary view retains legal suffixes intact!
    assert get_name_norm(raw) == "acme corporation private limited"


def test_name_all_views_dictionary():
    raw = "Bistro Paris S.A.R.L."
    views = normalize_business_name_all_views(raw)
    assert views["name_norm"] == "bistro paris s a r l"
    assert views["name_compact"] == "bistroparissarl"
    assert "bistro" in views["name_tokens"]
    assert views["name_latinized"] == "bistro paris s a r l"
    assert views["name_legal_stripped"] == "bistro paris s a r l"


def test_empty_and_null_names():
    assert get_name_norm(None) == ""
    assert get_name_compact("") == ""
    assert get_name_tokens(None) == []
    assert get_name_legal_stripped(None) == ""
