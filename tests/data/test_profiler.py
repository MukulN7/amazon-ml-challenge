"""Unit tests for dataset profiler (src/data/profiler.py).

Tests metric aggregation and profiling behavior on synthetic TSV fixtures.
"""

from pathlib import Path
import pytest
from src.data.profiler import DatasetProfiler, profiling_normalize_text


@pytest.fixture
def synthetic_source_tsv(tmp_path: Path) -> Path:
    fpath = tmp_path / "test_source1.tsv"
    content = (
        "entity_id\tbusiness_name\tbusiness_address\tcountry\n"
        "S1-001\tAcme Corporation\t100 Main Street, Suite 5\tUS\n"
        "S1-002\tAcme Corp.\t100 Main Street\tUS\n"
        "S1-003\tGlobal Logistics\t500 Industrial Pkwy\tIndia\n"
        "S1-004\tBistro De Paris\t15 Rue de Lyon\tFrance\n"
    )
    fpath.write_text(content, encoding="utf-8")
    return fpath


@pytest.fixture
def synthetic_ground_truth_tsv(tmp_path: Path) -> Path:
    fpath = tmp_path / "train_ground_truth.tsv"
    content = (
        "source1_entity_id\tmatched_entity_ids\n"
        "S1-001\tS2-101,S3-201\n"
        "S1-002\tS2-102\n"
        "S1-003\t\n"
        "S1-004\tS3-205,S3-206,S3-207\n"
    )
    fpath.write_text(content, encoding="utf-8")
    return fpath


def test_profiling_normalize_text():
    raw = " Acme,   Corporation!!!  "
    assert profiling_normalize_text(raw) == "acme corporation"


def test_profile_source_file(synthetic_source_tsv: Path):
    profiler = DatasetProfiler(chunksize=10)
    prof = profiler.profile_source_file(synthetic_source_tsv)

    assert prof["total_rows"] == 4
    assert prof["column_count"] == 4
    assert prof["id_stats"]["unique_ids"] == 4
    assert prof["id_stats"]["duplicate_ids"] == 0

    # Countries check
    cdist = prof["country_distribution"]
    assert "US" in cdist
    assert cdist["US"]["count"] == 2
    assert "France" in cdist
    assert cdist["France"]["count"] == 1

    # Name frequency check
    name_freq = prof["business_name_stats"]["frequency_analysis"]
    assert name_freq["unique_raw_names"] == 4


def test_profile_ground_truth(synthetic_ground_truth_tsv: Path):
    profiler = DatasetProfiler(chunksize=10)
    gt_prof = profiler.profile_ground_truth(synthetic_ground_truth_tsv)

    assert gt_prof["total_s1_entities"] == 4
    card = gt_prof["cardinality_distribution"]
    assert card["singleton_count_0_matches"] == 1
    assert card["exactly_1_match_count"] == 1
    assert card["exactly_2_matches_count"] == 1
    assert card["3_plus_matches_count"] == 1
    assert card["max_matches_for_single_s1"] == 3

    target = gt_prof["target_source_breakdown"]
    assert target["total_s2_references"] == 2
    assert target["total_s3_references"] == 4
