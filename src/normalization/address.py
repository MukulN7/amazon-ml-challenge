"""Business address multi-view normalization module.

Generates multiple derived representations for business addresses:
- address_norm: Conservative primary representation (lowercase, NFKD, cleaned punctuation).
- address_compact: Compact representation without spaces/punctuation.
- address_tokens: List of normalized word tokens.
- address_latinized: Latinized ASCII-only representation.
- Address structural information:
  - has_digits: Boolean flag indicating presence of numeric characters.
  - numeric_tokens: Extracted list of contiguous numeric digit sequences (preserves leading zeros).
  - token_count: Number of tokens in normalized address.
  - char_length: Character length of normalized address.
"""

import re
import unicodedata
from typing import Any, Dict, List, Optional

from src.normalization.text import (
    base_normalize,
    latinize_text,
)

RE_DIGITS = re.compile(r"\d+")


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


def get_address_norm(address: Optional[str]) -> str:
    """Returns primary conservative normalized address."""
    return base_normalize(address)


def get_address_compact(address: Optional[str]) -> str:
    """Returns compact alphanumeric-only address representation."""
    if not address or not isinstance(address, str):
        return ""
    norm = base_normalize(address)
    return _strip_spaces_and_punct(norm)


def get_address_tokens(address: Optional[str]) -> List[str]:
    """Returns list of tokens in normalized address."""
    norm = get_address_norm(address)
    return [t for t in norm.split() if t]


def get_address_latinized(address: Optional[str]) -> str:
    """Returns Latinized ASCII-only normalized address."""
    if not address or not isinstance(address, str):
        return ""
    norm = get_address_norm(address)
    return latinize_text(norm)


def get_address_transliterated(address: Optional[str]) -> str:
    """Alias for get_address_latinized for backwards compatibility."""
    return get_address_latinized(address)


def extract_numeric_tokens(address: Optional[str]) -> List[str]:
    """Extracts all contiguous numeric sequences from the address (preserves leading zeros)."""
    if not address or not isinstance(address, str):
        return []
    norm = base_normalize(address)
    return RE_DIGITS.findall(norm)


def normalize_business_address_all_views(address: Optional[str]) -> Dict[str, Any]:
    """Computes all address normalization views and structural features."""
    norm = get_address_norm(address)
    tokens = [t for t in norm.split() if t] if norm else []
    num_tokens = extract_numeric_tokens(address)
    compact = _strip_spaces_and_punct(norm)
    
    return {
        "address_norm": norm,
        "address_compact": compact,
        "address_tokens": tokens,
        "address_latinized": latinize_text(norm) if norm else "",
        "address_transliterated": latinize_text(norm) if norm else "",  # Alias field
        "has_digits": len(num_tokens) > 0,
        "numeric_tokens": num_tokens,
        "token_count": len(tokens),
        "char_length": len(norm),
    }
