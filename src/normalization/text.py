"""Core string transformation functions for Amazon ML Challenge 2026.

Provides deterministic, thread-safe, memory-efficient text transformations:
- Unicode NFC/NFKD normalization
- Lowercase / case folding
- Whitespace normalization
- Script-safe Punctuation handling (preserves Unicode Marks/Mn/Mc)
- Selective Latin combining diacritic stripping
- ASCII Latinization representation
"""

import re
import unicodedata
from typing import List, Optional

# Pre-compiled regex patterns for performance
RE_WHITESPACE = re.compile(r"\s+")
RE_NON_ALPHANUMERIC = re.compile(r"[^\w]")


def unicode_normalize(text: Optional[str], form: str = "NFC") -> str:
    """Applies standard Unicode normalization (NFC default for script safety)."""
    if not text or not isinstance(text, str):
        return ""
    return unicodedata.normalize(form, text)


def case_fold(text: Optional[str]) -> str:
    """Converts string to lowercase."""
    if not text or not isinstance(text, str):
        return ""
    return text.lower()


def normalize_whitespace(text: Optional[str]) -> str:
    """Strips leading/trailing whitespace and collapses inner spaces."""
    if not text or not isinstance(text, str):
        return ""
    return RE_WHITESPACE.sub(" ", text).strip()


def remove_diacritics(text: Optional[str]) -> str:
    """Selectively strips Latin combining accents and diacritics (e.g. 'é' -> 'e', 'münchen' -> 'munchen').
    
    Preserves non-Latin script combining marks (such as Devanagari vowel matras U+093E-U+094C)
    so non-Latin text is not corrupted.
    """
    if not text or not isinstance(text, str):
        return ""
    nfkd_form = unicodedata.normalize("NFKD", text)
    result = []
    for c in nfkd_form:
        if unicodedata.category(c) == "Mn":
            # Strip standard Latin combining diacritical marks (U+0300 to U+036F)
            if 0x0300 <= ord(c) <= 0x036F:
                continue
        result.append(c)
    return "".join(result)


def clean_punctuation(text: Optional[str], replace_with_space: bool = True) -> str:
    """Replaces Unicode punctuation ('P') and symbol ('S') characters with space or removes them.
    
    Preserves all letters ('L'), numbers ('N'), and marks ('M' like Devanagari matras).
    """
    if not text or not isinstance(text, str):
        return ""
    replacement = " " if replace_with_space else ""
    cleaned = []
    for c in text:
        cat = unicodedata.category(c)
        if cat.startswith("P") or cat.startswith("S"):
            cleaned.append(replacement)
        else:
            cleaned.append(c)
    return normalize_whitespace("".join(cleaned))


def latinize_text(text: Optional[str]) -> str:
    """Converts Latin accented characters to their closest ASCII equivalent.
    
    NOTE: This is a Latinization / diacritic-stripping transformation, NOT a full non-Latin transliterator.
    Non-Latin characters (e.g. Devanagari, Cyrillic) will be dropped if unconvertible to ASCII.
    Use for Latin-script text diacritic normalization.
    """
    if not text or not isinstance(text, str):
        return ""
    stripped = remove_diacritics(text)
    return stripped.encode("ascii", "ignore").decode("ascii")


def transliterate_to_ascii(text: Optional[str]) -> str:
    """Alias for latinize_text for backwards compatibility."""
    return latinize_text(text)


def base_normalize(text: Optional[str]) -> str:
    """Primary conservative base normalization.
    
    Operations:
    1. Unicode NFC normalization (preserving composite non-Latin script characters)
    2. Latin diacritic / accent stripping (e.g., 'é' -> 'e') while preserving non-Latin marks
    3. Case folding (lowercasing)
    4. Script-safe punctuation cleaning (replacing 'P' and 'S' Unicode categories with space)
    5. Whitespace collapsed and stripped
    
    Preserves original tokens, digits, non-Latin words (Devanagari, etc.), and legal terms.
    """
    if not text or not isinstance(text, str):
        return ""
    u_norm = unicode_normalize(text, form="NFC")
    no_diacritics = remove_diacritics(u_norm)
    c_fold = case_fold(no_diacritics)
    p_clean = clean_punctuation(c_fold, replace_with_space=True)
    return normalize_whitespace(p_clean)
