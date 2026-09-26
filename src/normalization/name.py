"""Business name multi-view normalization module.

Generates multiple derived representations for business names:
- name_norm: Conservative primary representation (lowercase, NFKD, cleaned punctuation).
- name_compact: Compact representation without spaces/punctuation.
- name_tokens: List of normalized word tokens.
- name_latinized: Latinized ASCII-only representation (diacritics stripped).
- name_legal_stripped: Derived representation with common legal business suffixes removed.
"""

import re
import unicodedata
from typing import Dict, List, Optional, Set

from src.normalization.text import (
    base_normalize,
    latinize_text,
    normalize_whitespace,
)

# Recognized legal business suffix tokens
LEGAL_SUFFIX_TOKENS: Set[str] = {
    "ltd",
    "limited",
    "inc",
    "incorporated",
    "llc",
    "corp",
    "corporation",
    "pvt",
    "private",
    "co",
    "company",
    "gmbh",
    "sa",
    "sarl",
    "nv",
    "plc",
    "holdings",
    "enterprises",
    "group",
    "services",
    "technologies",
    "solutions",
    "international",
    "global",
}


def _strip_spaces_and_punct(text: str) -> str:
    """Strips whitespace and punctuation while preserving all Unicode letters, marks, and numbers."""
    if not text:
        return ""
    result = []
    for c in text:
        cat = unicodedata.category(c)
        if not (cat.startswith("P") or cat.startswith("S") or c.isspace()):
            result.append(c)
    return "".join(result)


def get_name_norm(name: Optional[str]) -> str:
    """Returns primary conservative normalized name."""
    return base_normalize(name)


def get_name_compact(name: Optional[str]) -> str:
    """Returns compact representation without spaces or punctuation."""
    if not name or not isinstance(name, str):
        return ""
    norm = base_normalize(name)
    return _strip_spaces_and_punct(norm)


def get_name_tokens(name: Optional[str]) -> List[str]:
    """Returns list of tokens in normalized name."""
    norm = get_name_norm(name)
    return [t for t in norm.split() if t]


def get_name_latinized(name: Optional[str]) -> str:
    """Returns Latinized ASCII-only representation (diacritics/accents stripped)."""
    if not name or not isinstance(name, str):
        return ""
    norm = get_name_norm(name)
    return latinize_text(norm)


def get_name_transliterated(name: Optional[str]) -> str:
    """Alias for get_name_latinized for backwards compatibility."""
    return get_name_latinized(name)


def get_name_legal_stripped(name: Optional[str]) -> str:
    """Returns derived representation with legal business suffixes removed.
    
    NOTE: This is a secondary derived representation. Primary name_norm retains legal suffixes.
    """
    tokens = get_name_tokens(name)
    if not tokens:
        return ""
    
    filtered = [t for t in tokens if t not in LEGAL_SUFFIX_TOKENS]
    if not filtered:
        return get_name_norm(name)
        
    return " ".join(filtered)


def normalize_business_name_all_views(name: Optional[str]) -> Dict[str, str]:
    """Computes all name normalization views for a given business name string."""
    norm = get_name_norm(name)
    tokens = [t for t in norm.split() if t] if norm else []
    compact = _strip_spaces_and_punct(norm)
    
    return {
        "name_norm": norm,
        "name_compact": compact,
        "name_tokens": tokens,
        "name_latinized": latinize_text(norm) if norm else "",
        "name_transliterated": latinize_text(norm) if norm else "",  # Alias field
        "name_legal_stripped": get_name_legal_stripped(name),
    }
