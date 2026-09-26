"""Unit tests for business address multi-view normalization (src/normalization/address.py)."""

import pytest
from src.normalization.address import (
    extract_numeric_tokens,
    get_address_compact,
    get_address_latinized,
    get_address_norm,
    get_address_tokens,
    normalize_business_address_all_views,
)


def test_address_norm():
    raw = " 100 Main St., Suite #5, New York, NY 10001 "
    assert get_address_norm(raw) == "100 main st suite 5 new york ny 10001"


def test_address_compact():
    raw = "100 Main St, Suite #5"
    assert get_address_compact(raw) == "100mainstsuite5"


def test_extract_numeric_tokens_preserves_leading_zeros():
    raw = "78 Rue de Rivoli, Apt 004B, PIN 01234"
    nums = extract_numeric_tokens(raw)
    assert nums == ["78", "004", "01234"]  # Leading zeros in PIN and apt numbers 100% preserved as strings!


def test_address_latinized():
    raw = "175 Boulevard du Président Franklin Roosevelt"
    assert get_address_latinized(raw) == "175 boulevard du president franklin roosevelt"


def test_address_all_views():
    raw = "456 Park Avenue, Floor 12, Mumbai 400001"
    views = normalize_business_address_all_views(raw)
    assert views["address_norm"] == "456 park avenue floor 12 mumbai 400001"
    assert views["has_digits"] is True
    assert views["numeric_tokens"] == ["456", "12", "400001"]
    assert views["token_count"] == 7
    assert views["char_length"] > 0


def test_address_without_digits():
    raw = "Main Street Corner, High Road"
    views = normalize_business_address_all_views(raw)
    assert views["has_digits"] is False
    assert views["numeric_tokens"] == []


def test_empty_and_null_address():
    assert get_address_norm(None) == ""
    assert get_address_compact("") == ""
    assert extract_numeric_tokens(None) == []
