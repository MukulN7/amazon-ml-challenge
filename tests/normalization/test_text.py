"""Unit tests for core text transformations (src/normalization/text.py)."""

import pytest
from src.normalization.text import (
    base_normalize,
    case_fold,
    clean_punctuation,
    latinize_text,
    normalize_whitespace,
    remove_diacritics,
    unicode_normalize,
)


def test_unicode_normalize():
    assert unicode_normalize("Café", form="NFKD") == "Cafe\u0301"
    assert unicode_normalize(None) == ""
    assert unicode_normalize("") == ""


def test_case_fold():
    assert case_fold("ACME Corp") == "acme corp"
    assert case_fold(None) == ""


def test_normalize_whitespace():
    assert normalize_whitespace("  Acme   Corporation \t\n Ltd ") == "Acme Corporation Ltd"
    assert normalize_whitespace(None) == ""


def test_remove_diacritics_latin_only():
    # Latin accents stripped
    assert remove_diacritics("Café Lumière München") == "Cafe Lumiere Munchen"
    # Devanagari script matras preserved intact
    assert remove_diacritics("राम मार्केटिंग") == "राम मार्केटिंग"
    assert remove_diacritics(None) == ""


def test_clean_punctuation():
    assert clean_punctuation("Acme, Inc. & Sons!") == "Acme Inc Sons"
    assert clean_punctuation(None) == ""


def test_latinize_text():
    assert latinize_text("Bistro Paris - Café 123") == "Bistro Paris - Cafe 123"
    assert latinize_text(None) == ""


def test_base_normalize_latin_and_non_latin():
    # Latin
    assert base_normalize("  ACME,  Inc. & Sons (Pvt) Ltd.  ") == "acme inc sons pvt ltd"
    # French Latin accent
    assert base_normalize("Société Générale") == "societe generale"
    # Devanagari script preserved in base_normalize!
    assert base_normalize("राम मार्केटिंग") == "राम मार्केटिंग"


def test_deterministic_execution():
    raw = "  Global Tech & Logistics (India) Pvt. Ltd. "
    res1 = base_normalize(raw)
    res2 = base_normalize(raw)
    assert res1 == res2 == "global tech logistics india pvt ltd"
