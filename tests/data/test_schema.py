"""Unit tests for dataset schema validation (src/data/schema_validator.py).

Tests schema contract enforcement on synthetic TSV fixtures.
"""

import pytest
from pathlib import Path
from src.data.schema import SchemaValidationError, SOURCE1_SCHEMA, GROUND_TRUTH_SCHEMA
from src.data.schema_validator import validate_tsv_file


@pytest.fixture
def valid_source1_tsv(tmp_path: Path) -> Path:
    fpath = tmp_path / "train_source1.tsv"
    content = (
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        "S1-00001\tAcme Corp\t123 Main St, New York, NY\tUS\n"
        "S1-00002\tGlobal Tech Ltd\t456 Park Ave, Mumbai\tIndia\n"
        "S1-00003\tBistro Paris\t78 Rue de Rivoli, Paris\tFrance\n"
    )
    fpath.write_text(content, encoding="utf-8")
    return fpath


@pytest.fixture
def valid_ground_truth_tsv(tmp_path: Path) -> Path:
    fpath = tmp_path / "train_ground_truth.tsv"
    content = (
        "source1_entity_id\tmatched_entity_ids\n"
        "S1-00001\tS2-00047,S3-00812\n"
        "S1-00002\tS3-00004\n"
        "S1-00003\t\n"
    )
    fpath.write_text(content, encoding="utf-8")
    return fpath


def test_validate_valid_source1(valid_source1_tsv: Path):
    res = validate_tsv_file(valid_source1_tsv, schema=SOURCE1_SCHEMA)
    assert res["is_valid"] is True
    assert res["total_rows"] == 3
    assert res["unique_primary_keys"] == 3


def test_validate_valid_ground_truth(valid_ground_truth_tsv: Path):
    res = validate_tsv_file(valid_ground_truth_tsv, schema=GROUND_TRUTH_SCHEMA)
    assert res["is_valid"] is True
    assert res["total_rows"] == 3


def test_header_mismatch(tmp_path: Path):
    fpath = tmp_path / "train_source1.tsv"
    # Missing country column
    content = "entity_id\tbusiness_name\tbusiness_address\nS1-00001\tAcme\tAddr\n"
    fpath.write_text(content, encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Header mismatch"):
        validate_tsv_file(fpath, schema=SOURCE1_SCHEMA)


def test_malformed_id_prefix(tmp_path: Path):
    fpath = tmp_path / "train_source1.tsv"
    # X1- prefix instead of S1-
    content = (
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        "X1-00001\tAcme Corp\t123 Main St\tUS\n"
    )
    fpath.write_text(content, encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="does not start with any expected prefix"):
        validate_tsv_file(fpath, schema=SOURCE1_SCHEMA)


def test_duplicate_primary_key(tmp_path: Path):
    fpath = tmp_path / "train_source1.tsv"
    # Duplicate S1-00001
    content = (
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        "S1-00001\tAcme Corp\t123 Main St\tUS\n"
        "S1-00001\tDuplicate Acme\t456 Park Ave\tUS\n"
    )
    fpath.write_text(content, encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Duplicate primary key ID detected"):
        validate_tsv_file(fpath, schema=SOURCE1_SCHEMA)


def test_invalid_ground_truth_match_prefix(tmp_path: Path):
    fpath = tmp_path / "train_ground_truth.tsv"
    # Ground truth containing self-match S1-00002
    content = (
        "source1_entity_id\tmatched_entity_ids\n"
        "S1-00001\tS1-00002,S2-00001\n"
    )
    fpath.write_text(content, encoding="utf-8")

    with pytest.raises(SchemaValidationError, match="Must start with S2- or S3-"):
        validate_tsv_file(fpath, schema=GROUND_TRUTH_SCHEMA)
