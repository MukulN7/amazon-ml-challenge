"""Schema validation module for Amazon ML Challenge 2026 datasets.

Performs strict, memory-safe schema validation on TSV files to ensure data contract compliance.
Fails explicitly if malformed headers, missing columns, duplicate IDs, or unexpected ID formats occur.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Union
import pandas as pd

from src.data.schema import (
    GROUND_TRUTH_SCHEMA,
    SCHEMA_REGISTRY,
    ColumnSchema,
    SchemaValidationError,
    TableSchema,
)


def validate_header(header_cols: List[str], schema: TableSchema) -> None:
    """Validates exact column names and column ordering."""
    if header_cols != schema.column_names:
        raise SchemaValidationError(
            f"Header mismatch for schema '{schema.name}'.\n"
            f"Expected: {schema.column_names}\n"
            f"Actual:   {header_cols}"
        )


def validate_identifier_prefix(id_val: str, expected_prefixes: Set[str], row_num: int, col_name: str) -> None:
    """Validates that an identifier string starts with one of the expected prefixes."""
    if not isinstance(id_val, str) or not id_val.strip():
        raise SchemaValidationError(f"Row {row_num}: Column '{col_name}' contains empty or non-string ID.")
    if not any(id_val.startswith(prefix) for prefix in expected_prefixes):
        raise SchemaValidationError(
            f"Row {row_num}: Column '{col_name}' value '{id_val}' does not start with any expected prefix: {expected_prefixes}"
        )


def validate_ground_truth_matches(matched_str: str, row_num: int) -> None:
    """Validates matched_entity_ids column formatting in ground truth."""
    if pd.isna(matched_str) or not matched_str or not matched_str.strip():
        return  # Empty match list is valid (singleton)
    
    match_ids = [m.strip() for m in matched_str.split(",") if m.strip()]
    for m_id in match_ids:
        if not (m_id.startswith("S2-") or m_id.startswith("S3-")):
            raise SchemaValidationError(
                f"Row {row_num}: Invalid ground truth match ID '{m_id}'. Must start with S2- or S3-."
            )


def validate_tsv_file(
    file_path: Union[str, Path],
    schema: Optional[TableSchema] = None,
    chunksize: int = 100000,
) -> Dict[str, Union[int, str, bool]]:
    """Performs streaming, chunked validation of a TSV dataset file.

    Args:
        file_path: Path to the TSV file.
        schema: Optional TableSchema. If None, resolves from SCHEMA_REGISTRY using filename.
        chunksize: Number of rows to read per chunk for memory safety.

    Returns:
        Dict containing validation metadata (row_count, unique_id_count, status).
    """
    path = Path(file_path)
    if not path.exists():
        raise SchemaValidationError(f"File not found: {path}")

    filename = path.name
    if schema is None:
        if filename in SCHEMA_REGISTRY:
            schema = SCHEMA_REGISTRY[filename]
        else:
            raise SchemaValidationError(f"No registered schema found for file: {filename}")

    # Read first chunk or header to inspect columns
    try:
        reader = pd.read_csv(
            path,
            sep="\t",
            chunksize=chunksize,
            dtype=str,
            keep_default_na=False,  # Treat empty fields as empty strings, not NaN
        )
    except Exception as e:
        raise SchemaValidationError(f"Failed to open TSV file {path}: {str(e)}")

    seen_ids: Set[str] = set()
    total_rows = 0
    is_ground_truth = (schema.name == "ground_truth")
    pk_col = schema.primary_key

    for chunk_idx, chunk in enumerate(reader):
        if chunk_idx == 0:
            validate_header(list(chunk.columns), schema)

        chunk_rows = len(chunk)

        # Validate Primary Key column uniqueness & prefixes
        if pk_col and pk_col in chunk.columns:
            pk_series = chunk[pk_col]
            
            # Check null / empty PKs
            empty_pk_mask = pk_series.isna() | (pk_series == "")
            if empty_pk_mask.any():
                first_bad_idx = total_rows + empty_pk_mask.idxmax() + 1
                raise SchemaValidationError(f"Row {first_bad_idx}: Primary key '{pk_col}' is empty/null.")

            # Validate prefixes
            for local_idx, val in enumerate(pk_series):
                global_row = total_rows + local_idx + 1
                validate_identifier_prefix(val, schema.expected_id_prefixes, global_row, pk_col)
                if val in seen_ids:
                    raise SchemaValidationError(
                        f"Row {global_row}: Duplicate primary key ID detected: '{val}'"
                    )
                seen_ids.add(val)

        # Special validation for ground truth matches
        if is_ground_truth and "matched_entity_ids" in chunk.columns:
            for local_idx, val in enumerate(chunk["matched_entity_ids"]):
                global_row = total_rows + local_idx + 1
                validate_ground_truth_matches(val, global_row)

        total_rows += chunk_rows

    return {
        "file_name": filename,
        "schema_name": schema.name,
        "total_rows": total_rows,
        "unique_primary_keys": len(seen_ids),
        "is_valid": True,
    }
