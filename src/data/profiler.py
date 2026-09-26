"""Memory-safe Dataset Profiler for Amazon ML Challenge 2026 datasets.

Computes comprehensive streaming statistics across TSV files using chunked processing.
Generates machine-readable (JSON) and human-readable (Markdown) profiling reports.
"""

from collections import Counter
import json
import math
import re
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd


def profiling_normalize_text(text: str) -> str:
    """Isolated, profiling-only text normalization.
    
    Used strictly for profiling duplicate counts and token frequencies.
    DO NOT use as production normalization.
    """
    if not text or not isinstance(text, str):
        return ""
    # Unicode NFKD normalization, lowercase, strip non-alphanumeric except space
    normalized = unicodedata.normalize("NFKD", text).lower()
    normalized = re.sub(r"[^\w\s]", " ", normalized)
    return re.sub(r"\s+", " ", normalized).strip()


def detect_unicode_scripts(text: str) -> Counter:
    """Counts Unicode script categories present in a text string."""
    scripts = Counter()
    for char in text:
        if char.isspace() or char.isdigit() or ord(char) < 128:
            continue
        try:
            name = unicodedata.name(char, "UNKNOWN")
            script = name.split()[0]
            scripts[script] += 1
        except ValueError:
            scripts["UNKNOWN"] += 1
    return scripts


class DatasetProfiler:
    """Streaming, chunked dataset profiler."""

    def __init__(self, chunksize: int = 50000):
        self.chunksize = chunksize

    def profile_source_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Profiles a single source TSV file (Source 1, Source 2, or Source 3)."""
        path = Path(file_path)
        file_size_bytes = path.stat().st_size
        file_size_mb = round(file_size_bytes / (1024 * 1024), 2)

        # Streaming aggregators
        total_rows = 0
        col_null_counts = Counter()
        col_empty_counts = Counter()
        col_whitespace_counts = Counter()

        entity_ids_counter = Counter()
        countries_counter = Counter()

        # Name metrics
        raw_names_counter = Counter()
        norm_names_counter = Counter()
        name_lengths = []
        name_token_counts = []
        name_token_df = Counter()
        name_script_counts = Counter()
        non_ascii_name_count = 0

        # Address metrics
        raw_addresses_counter = Counter()
        norm_addresses_counter = Counter()
        address_lengths = []
        address_token_counts = []
        address_token_df = Counter()
        address_has_digits_count = 0

        reader = pd.read_csv(
            path,
            sep="\t",
            chunksize=self.chunksize,
            dtype=str,
            keep_default_na=False,
        )

        columns = []

        for chunk_idx, chunk in enumerate(reader):
            if chunk_idx == 0:
                columns = list(chunk.columns)

            chunk_len = len(chunk)
            total_rows += chunk_len

            # Missingness checks
            for col in columns:
                series = chunk[col]
                is_null = series.isna()
                is_empty = series == ""
                is_ws = series.str.strip() == ""
                
                col_null_counts[col] += int(is_null.sum())
                col_empty_counts[col] += int(is_empty.sum())
                col_whitespace_counts[col] += int(is_ws.sum())

            # ID stats
            if "entity_id" in chunk.columns:
                entity_ids_counter.update(chunk["entity_id"])

            # Country stats
            if "country" in chunk.columns:
                countries_counter.update(chunk["country"])

            # Business Name stats
            if "business_name" in chunk.columns:
                for val in chunk["business_name"]:
                    if not val:
                        continue
                    raw_names_counter[val] += 1
                    norm_val = profiling_normalize_text(val)
                    if norm_val:
                        norm_names_counter[norm_val] += 1

                    val_len = len(val)
                    name_lengths.append(val_len)

                    tokens = [t for t in norm_val.split() if t]
                    name_token_counts.append(len(tokens))
                    name_token_df.update(set(tokens))

                    if not val.isascii():
                        non_ascii_name_count += 1
                        name_script_counts.update(detect_unicode_scripts(val))

            # Business Address stats
            if "business_address" in chunk.columns:
                for val in chunk["business_address"]:
                    if not val:
                        continue
                    raw_addresses_counter[val] += 1
                    norm_val = profiling_normalize_text(val)
                    if norm_val:
                        norm_addresses_counter[norm_val] += 1

                    val_len = len(val)
                    address_lengths.append(val_len)

                    tokens = [t for t in norm_val.split() if t]
                    address_token_counts.append(len(tokens))
                    address_token_df.update(set(tokens))

                    if any(c.isdigit() for c in val):
                        address_has_digits_count += 1

        # Calculate summary statistics
        def _get_length_stats(lengths_list: List[int]) -> Dict[str, Any]:
            if not lengths_list:
                return {"min": 0, "max": 0, "mean": 0.0, "median": 0.0, "p95": 0.0}
            arr = np.array(lengths_list)
            return {
                "min": int(np.min(arr)),
                "max": int(np.max(arr)),
                "mean": round(float(np.mean(arr)), 2),
                "median": round(float(np.median(arr)), 2),
                "p95": round(float(np.percentile(arr, 95)), 2),
            }

        # ID summary
        unique_ids = len(entity_ids_counter)
        duplicate_ids = total_rows - unique_ids
        id_lengths = [len(k) for k in entity_ids_counter.keys()] if entity_ids_counter else [0]

        # Name Frequency Distribution Breakdown
        name_freq_counts = list(raw_names_counter.values())
        norm_name_freq_counts = list(norm_names_counter.values())

        name_freq_breakdown = {
            "unique_raw_names": len(raw_names_counter),
            "unique_norm_names": len(norm_names_counter),
            "records_in_duplicate_names": sum(c for c in name_freq_counts if c > 1),
            "pct_records_in_duplicate_names": round(sum(c for c in name_freq_counts if c > 1) / max(1, total_rows) * 100, 2),
            "count_appearing_ge_2": sum(1 for c in name_freq_counts if c >= 2),
            "count_appearing_ge_5": sum(1 for c in name_freq_counts if c >= 5),
            "count_appearing_ge_10": sum(1 for c in name_freq_counts if c >= 10),
            "count_appearing_ge_50": sum(1 for c in name_freq_counts if c >= 50),
            "count_appearing_ge_100": sum(1 for c in name_freq_counts if c >= 100),
            "top_10_raw_names": raw_names_counter.most_common(10),
            "top_10_norm_names": norm_names_counter.most_common(10),
        }

        # Address Frequency Breakdown
        address_freq_counts = list(raw_addresses_counter.values())
        address_freq_breakdown = {
            "unique_raw_addresses": len(raw_addresses_counter),
            "unique_norm_addresses": len(norm_addresses_counter),
            "duplicate_address_rate_pct": round((1 - len(raw_addresses_counter) / max(1, total_rows)) * 100, 2),
            "digit_presence_pct": round(address_has_digits_count / max(1, total_rows) * 100, 2),
            "top_10_raw_addresses": raw_addresses_counter.most_common(10),
        }

        # Token Distributions
        def _get_token_dist(token_df_counter: Counter) -> Dict[str, Any]:
            total_unique_tokens = len(token_df_counter)
            counts = list(token_df_counter.values())
            return {
                "unique_tokens": total_unique_tokens,
                "top_20_tokens": token_df_counter.most_common(20),
                "rare_tokens_df_1": sum(1 for c in counts if c == 1),
                "rare_tokens_df_le_5": sum(1 for c in counts if c <= 5),
                "high_freq_tokens_df_gt_100": sum(1 for c in counts if c > 100),
                "high_freq_tokens_df_gt_1000": sum(1 for c in counts if c > 1000),
            }

        # Missingness per column
        col_missingness = {}
        for col in columns:
            null_c = col_null_counts[col]
            empty_c = col_empty_counts[col]
            ws_c = col_whitespace_counts[col]
            col_missingness[col] = {
                "null_count": null_c,
                "null_pct": round(null_c / max(1, total_rows) * 100, 2),
                "empty_string_count": empty_c,
                "whitespace_only_count": ws_c,
            }

        # Country distribution
        country_dist = {
            c: {"count": cnt, "pct": round(cnt / max(1, total_rows) * 100, 2)}
            for c, cnt in countries_counter.most_common()
        }

        return {
            "file_name": path.name,
            "file_size_mb": file_size_mb,
            "total_rows": total_rows,
            "column_count": len(columns),
            "column_names": columns,
            "missingness": col_missingness,
            "id_stats": {
                "unique_ids": unique_ids,
                "duplicate_ids": duplicate_ids,
                "min_id_len": int(min(id_lengths)) if id_lengths else 0,
                "max_id_len": int(max(id_lengths)) if id_lengths else 0,
            },
            "country_distribution": country_dist,
            "business_name_stats": {
                "string_length": _get_length_stats(name_lengths),
                "token_length": _get_length_stats(name_token_counts),
                "frequency_analysis": name_freq_breakdown,
                "token_distribution": _get_token_dist(name_token_df),
                "character_script": {
                    "non_ascii_count": non_ascii_name_count,
                    "non_ascii_pct": round(non_ascii_name_count / max(1, total_rows) * 100, 2),
                    "script_distribution": dict(name_script_counts.most_common(10)),
                },
            },
            "business_address_stats": {
                "string_length": _get_length_stats(address_lengths),
                "token_length": _get_length_stats(address_token_counts),
                "frequency_analysis": address_freq_breakdown,
                "token_distribution": _get_token_dist(address_token_df),
            },
        }

    def profile_ground_truth(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Profiles train_ground_truth.tsv match cardinality and distribution."""
        path = Path(file_path)
        file_size_mb = round(path.stat().st_size / (1024 * 1024), 2)

        total_rows = 0
        s1_ids_seen = set()
        duplicate_s1_ids = 0

        singleton_count = 0
        single_match_count = 0
        two_match_count = 0
        three_plus_match_count = 0
        max_matches_single_s1 = 0

        total_matched_s2 = 0
        total_matched_s3 = 0
        matched_s2_ids = Counter()
        matched_s3_ids = Counter()

        reader = pd.read_csv(
            path,
            sep="\t",
            chunksize=self.chunksize,
            dtype=str,
            keep_default_na=False,
        )

        for chunk in reader:
            total_rows += len(chunk)

            for s1_id, matched_str in zip(chunk["source1_entity_id"], chunk["matched_entity_ids"]):
                if s1_id in s1_ids_seen:
                    duplicate_s1_ids += 1
                s1_ids_seen.add(s1_id)

                if not matched_str or not matched_str.strip():
                    singleton_count += 1
                    continue

                m_ids = [m.strip() for m in matched_str.split(",") if m.strip()]
                num_matches = len(m_ids)

                if num_matches == 1:
                    single_match_count += 1
                elif num_matches == 2:
                    two_match_count += 1
                elif num_matches >= 3:
                    three_plus_match_count += 1

                if num_matches > max_matches_single_s1:
                    max_matches_single_s1 = num_matches

                for m_id in m_ids:
                    if m_id.startswith("S2-"):
                        total_matched_s2 += 1
                        matched_s2_ids[m_id] += 1
                    elif m_id.startswith("S3-"):
                        total_matched_s3 += 1
                        matched_s3_ids[m_id] += 1

        total_matched_entities = total_rows - singleton_count

        return {
            "file_name": path.name,
            "file_size_mb": file_size_mb,
            "total_s1_entities": total_rows,
            "unique_s1_entities": len(s1_ids_seen),
            "duplicate_s1_entities": duplicate_s1_ids,
            "cardinality_distribution": {
                "singleton_count_0_matches": singleton_count,
                "singleton_pct": round(singleton_count / max(1, total_rows) * 100, 2),
                "matched_count_ge_1": total_matched_entities,
                "matched_pct": round(total_matched_entities / max(1, total_rows) * 100, 2),
                "exactly_1_match_count": single_match_count,
                "exactly_1_match_pct": round(single_match_count / max(1, total_rows) * 100, 2),
                "exactly_2_matches_count": two_match_count,
                "exactly_2_matches_pct": round(two_match_count / max(1, total_rows) * 100, 2),
                "3_plus_matches_count": three_plus_match_count,
                "3_plus_matches_pct": round(three_plus_match_count / max(1, total_rows) * 100, 2),
                "max_matches_for_single_s1": max_matches_single_s1,
            },
            "target_source_breakdown": {
                "total_s2_references": total_matched_s2,
                "unique_s2_matched_entities": len(matched_s2_ids),
                "s2_duplicate_matches": sum(c - 1 for c in matched_s2_ids.values() if c > 1),
                "total_s3_references": total_matched_s3,
                "unique_s3_matched_entities": len(matched_s3_ids),
                "s3_duplicate_matches": sum(c - 1 for c in matched_s3_ids.values() if c > 1),
            },
        }

    def profile_all(self, raw_data_dir: Union[str, Path]) -> Dict[str, Any]:
        """Profiles all train and test dataset files under data/raw/."""
        raw_path = Path(raw_data_dir)

        files_to_profile = [
            "train_source1.tsv",
            "train_source2.tsv",
            "train_source3.tsv",
            "test_source1.tsv",
            "test_source2.tsv",
            "test_source3.tsv",
        ]

        profiles = {}
        for fname in files_to_profile:
            fpath = raw_path / fname
            if fpath.exists():
                profiles[fname] = self.profile_source_file(fpath)

        gt_path = raw_path / "train_ground_truth.tsv"
        gt_profile = {}
        if gt_path.exists():
            gt_profile = self.profile_ground_truth(gt_path)

        return {
            "source_profiles": profiles,
            "ground_truth_profile": gt_profile,
        }
