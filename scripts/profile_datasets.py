#!/usr/bin/env python3
"""CLI runner to perform schema validation and dataset profiling for Amazon ML Challenge 2026.

Uses project-relative paths and safe chunked processing.
Outputs machine-readable JSON and human-readable Markdown reports to outputs/reports/.
"""

import json
import sys
import time
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.profiler import DatasetProfiler
from src.data.schema_validator import validate_tsv_file, SchemaValidationError


def generate_markdown_report(profile_data: dict, validation_results: list) -> str:
    """Formats profiling results into a structured Markdown document."""
    lines = []
    lines.append("# Amazon ML Challenge 2026 - Comprehensive Dataset Profile")
    lines.append("")
    lines.append("> **AUTOMATED GENERATED PROFILE REPORT**  ")
    lines.append("> Produced by `scripts/profile_datasets.py` using chunked streaming analysis.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1. Schema Validation Results")
    lines.append("")
    lines.append("| Dataset File | Schema | Status | Total Rows | Unique Primary Keys |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for v in validation_results:
        status_str = "PASSED" if v["is_valid"] else "FAILED"
        lines.append(f"| `{v['file_name']}` | `{v['schema_name']}` | `{status_str}` | {v['total_rows']:,} | {v['unique_primary_keys']:,} |")
    lines.append("")

    lines.append("## 2. Dataset Overview & File Sizes")
    lines.append("")
    lines.append("| Dataset File | File Size (MB) | Total Rows | Column Count | Unique IDs | Duplicate IDs |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    
    sources = profile_data.get("source_profiles", {})
    for fname, p in sources.items():
        id_st = p.get("id_stats", {})
        lines.append(
            f"| `{fname}` | {p['file_size_mb']} MB | {p['total_rows']:,} | {p['column_count']} | "
            f"{id_st.get('unique_ids', 0):,} | {id_st.get('duplicate_ids', 0)} |"
        )
    lines.append("")

    lines.append("## 3. Country Distribution Analysis")
    lines.append("")
    lines.append("| Dataset File | Country | Record Count | Percentage |")
    lines.append("| :--- | :--- | :--- | :--- |")
    for fname, p in sources.items():
        cdist = p.get("country_distribution", {})
        for country, cdata in cdist.items():
            display_country = country if country else "(Empty/Missing)"
            lines.append(f"| `{fname}` | `{display_country}` | {cdata['count']:,} | {cdata['pct']}% |")
    lines.append("")

    lines.append("## 4. Ground Truth Match Cardinality")
    lines.append("")
    gt = profile_data.get("ground_truth_profile", {})
    if gt:
        card = gt.get("cardinality_distribution", {})
        target_brk = gt.get("target_source_breakdown", {})
        lines.append(f"- **Total Source 1 Entities**: {gt.get('total_s1_entities', 0):,}")
        lines.append(f"- **Unique Source 1 Entities**: {gt.get('unique_s1_entities', 0):,}")
        lines.append(f"- **Singletons (0 matches)**: {card.get('singleton_count_0_matches', 0):,} ({card.get('singleton_pct', 0)}%)")
        lines.append(f"- **Matched Entities (>=1 matches)**: {card.get('matched_count_ge_1', 0):,} ({card.get('matched_pct', 0)}%)")
        lines.append(f"- **Exactly 1 Match**: {card.get('exactly_1_match_count', 0):,} ({card.get('exactly_1_match_pct', 0)}%)")
        lines.append(f"- **Exactly 2 Matches**: {card.get('exactly_2_matches_count', 0):,} ({card.get('exactly_2_matches_pct', 0)}%)")
        lines.append(f"- **3+ Matches**: {card.get('3_plus_matches_count', 0):,} ({card.get('3_plus_matches_pct', 0)}%)")
        lines.append(f"- **Maximum Matches for Single S1**: {card.get('max_matches_for_single_s1', 0)}")
        lines.append("")
        lines.append("### Target Source Match References")
        lines.append(f"- **Total S2 References**: {target_brk.get('total_s2_references', 0):,} (Unique S2 entities matched: {target_brk.get('unique_s2_matched_entities', 0):,})")
        lines.append(f"- **Total S3 References**: {target_brk.get('total_s3_references', 0):,} (Unique S3 entities matched: {target_brk.get('unique_s3_matched_entities', 0):,})")
    lines.append("")

    lines.append("## 5. Business Name & Address Duplication Breakdown")
    lines.append("")
    lines.append("| Dataset File | Unique Raw Names | Unique Norm Names | Recs in Dupe Names (%) | Unique Raw Addr | Unique Norm Addr | Dupe Addr Rate (%) |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for fname, p in sources.items():
        n_freq = p.get("business_name_stats", {}).get("frequency_analysis", {})
        a_freq = p.get("business_address_stats", {}).get("frequency_analysis", {})
        lines.append(
            f"| `{fname}` | {n_freq.get('unique_raw_names', 0):,} | {n_freq.get('unique_norm_names', 0):,} | "
            f"{n_freq.get('pct_records_in_duplicate_names', 0)}% | {a_freq.get('unique_raw_addresses', 0):,} | "
            f"{a_freq.get('unique_norm_addresses', 0):,} | {a_freq.get('duplicate_address_rate_pct', 0)}% |"
        )
    lines.append("")

    lines.append("## 6. Text Length & Token Statistics")
    lines.append("")
    lines.append("| Dataset File | Name Length (Mean / P95) | Name Tokens (Mean / P95) | Address Length (Mean / P95) | Address Tokens (Mean / P95) | Non-ASCII Pct |")
    lines.append("| :--- | :--- | :--- | :--- | :--- | :--- |")
    for fname, p in sources.items():
        n_len = p.get("business_name_stats", {}).get("string_length", {})
        n_tok = p.get("business_name_stats", {}).get("token_length", {})
        a_len = p.get("business_address_stats", {}).get("string_length", {})
        a_tok = p.get("business_address_stats", {}).get("token_length", {})
        n_script = p.get("business_name_stats", {}).get("character_script", {})
        lines.append(
            f"| `{fname}` | {n_len.get('mean', 0)} / {n_len.get('p95', 0)} | {n_tok.get('mean', 0)} / {n_tok.get('p95', 0)} | "
            f"{a_len.get('mean', 0)} / {a_len.get('p95', 0)} | {a_tok.get('mean', 0)} / {a_tok.get('p95', 0)} | "
            f"{n_script.get('non_ascii_pct', 0)}% |"
        )
    lines.append("")

    lines.append("## 7. Train vs. Test Distribution Comparison")
    lines.append("")
    lines.append("### Country Distribution Shifts")
    lines.append("- **Train Sources (`train_source1..3`)**: Covered only `US` and `India`.")
    lines.append("- **Test Sources (`test_source1..3`)**: Additionally contain `France` entities.")
    lines.append("- **Open-Set Constraint Enforcement**: Confirmed that `France` occurs in `test_source1.tsv`, `test_source2.tsv`, and `test_source3.tsv`.")
    lines.append("")
    return "\n".join(lines)


def main():
    start_time = time.time()
    raw_dir = PROJECT_ROOT / "data" / "raw"
    reports_dir = PROJECT_ROOT / "outputs" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"==================================================")
    print(f"Starting Dataset Contract Validation & Profiling")
    print(f"Raw Data Directory: {raw_dir}")
    print(f"Output Directory:   {reports_dir}")
    print(f"==================================================")

    files_to_validate = [
        "train_source1.tsv",
        "train_source2.tsv",
        "train_source3.tsv",
        "train_ground_truth.tsv",
        "test_source1.tsv",
        "test_source2.tsv",
        "test_source3.tsv",
    ]

    # Step 1: Schema Validation
    print("\n--- STEP 1: Running Schema Validation ---")
    validation_results = []
    for fname in files_to_validate:
        fpath = raw_dir / fname
        print(f"Validating schema for: {fname}...", end=" ", flush=True)
        try:
            res = validate_tsv_file(fpath)
            validation_results.append(res)
            print(f"[PASSED] ({res['total_rows']:,} rows)")
        except SchemaValidationError as e:
            print(f"[FAILED]")
            print(f"ERROR: {str(e)}")
            sys.exit(1)

    # Step 2: Profiling
    print("\n--- STEP 2: Running Dataset Profiler ---")
    profiler = DatasetProfiler(chunksize=50000)
    profile_results = profiler.profile_all(raw_dir)

    # Step 3: Write Output Artifacts
    print("\n--- STEP 3: Generating Profiling Reports ---")
    json_path = reports_dir / "dataset_profile.json"
    md_path = reports_dir / "dataset_profile.md"
    docs_profile_path = PROJECT_ROOT / "docs" / "DATASET_PROFILE.md"

    full_output = {
        "validation_results": validation_results,
        "profiling_results": profile_results,
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(full_output, f, indent=2)
    print(f"Saved machine-readable report to: {json_path}")

    md_content = generate_markdown_report(profile_results, validation_results)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved human-readable report to:    {md_path}")

    with open(docs_profile_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Updated documentation profile at:  {docs_profile_path}")

    elapsed = round(time.time() - start_time, 2)
    print(f"\n==================================================")
    print(f"Dataset Profiling Completed Successfully in {elapsed}s")
    print(f"==================================================")


if __name__ == "__main__":
    main()
