# Amazon ML Challenge 2026 - Comprehensive Dataset Profile

> **AUTOMATED GENERATED PROFILE REPORT**  
> Produced by `scripts/profile_datasets.py` using chunked streaming analysis.

---

## 1. Schema Validation Results

| Dataset File | Schema | Status | Total Rows | Unique Primary Keys |
| :--- | :--- | :--- | :--- | :--- |
| `train_source1.tsv` | `source1` | `PASSED` | 2,206,821 | 2,206,821 |
| `train_source2.tsv` | `source2` | `PASSED` | 5,034,616 | 5,034,616 |
| `train_source3.tsv` | `source3` | `PASSED` | 5,285,603 | 5,285,603 |
| `train_ground_truth.tsv` | `ground_truth` | `PASSED` | 2,206,821 | 2,206,821 |
| `test_source1.tsv` | `source1` | `PASSED` | 1,732,544 | 1,732,544 |
| `test_source2.tsv` | `source2` | `PASSED` | 4,887,273 | 4,887,273 |
| `test_source3.tsv` | `source3` | `PASSED` | 5,082,316 | 5,082,316 |

## 2. Dataset Overview & File Sizes

| Dataset File | File Size (MB) | Total Rows | Column Count | Unique IDs | Duplicate IDs |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `train_source1.tsv` | 200.34 MB | 2,206,821 | 4 | 2,206,821 | 0 |
| `train_source2.tsv` | 466.63 MB | 5,034,616 | 4 | 5,034,616 | 0 |
| `train_source3.tsv` | 480.37 MB | 5,285,603 | 4 | 5,285,603 | 0 |
| `test_source1.tsv` | 166.91 MB | 1,732,544 | 4 | 1,732,544 | 0 |
| `test_source2.tsv` | 485.86 MB | 4,887,273 | 4 | 4,887,273 | 0 |
| `test_source3.tsv` | 482.56 MB | 5,082,316 | 4 | 5,082,316 | 0 |

## 3. Country Distribution Analysis

| Dataset File | Country | Record Count | Percentage |
| :--- | :--- | :--- | :--- |
| `train_source1.tsv` | `US` | 1,323,633 | 59.98% |
| `train_source1.tsv` | `India` | 883,188 | 40.02% |
| `train_source2.tsv` | `US` | 3,016,817 | 59.92% |
| `train_source2.tsv` | `India` | 2,017,799 | 40.08% |
| `train_source3.tsv` | `US` | 3,170,056 | 59.98% |
| `train_source3.tsv` | `India` | 2,115,547 | 40.02% |
| `test_source1.tsv` | `India` | 809,986 | 46.75% |
| `test_source1.tsv` | `US` | 663,106 | 38.27% |
| `test_source1.tsv` | `France` | 259,452 | 14.98% |
| `test_source2.tsv` | `India` | 2,312,565 | 47.32% |
| `test_source2.tsv` | `US` | 1,871,330 | 38.29% |
| `test_source2.tsv` | `France` | 703,378 | 14.39% |
| `test_source3.tsv` | `India` | 2,405,000 | 47.32% |
| `test_source3.tsv` | `US` | 1,945,701 | 38.28% |
| `test_source3.tsv` | `France` | 731,615 | 14.4% |

## 4. Ground Truth Match Cardinality

- **Total Source 1 Entities**: 2,206,821
- **Unique Source 1 Entities**: 2,206,821
- **Singletons (0 matches)**: 123,247 (5.58%)
- **Matched Entities (>=1 matches)**: 2,083,574 (94.42%)
- **Exactly 1 Match**: 119,157 (5.4%)
- **Exactly 2 Matches**: 375,212 (17.0%)
- **3+ Matches**: 1,589,205 (72.01%)
- **Maximum Matches for Single S1**: 11

### Target Source Match References
- **Total S2 References**: 3,693,619 (Unique S2 entities matched: 3,693,619)
- **Total S3 References**: 3,944,746 (Unique S3 entities matched: 3,944,746)

## 5. Business Name & Address Duplication Breakdown

| Dataset File | Unique Raw Names | Unique Norm Names | Recs in Dupe Names (%) | Unique Raw Addr | Unique Norm Addr | Dupe Addr Rate (%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `train_source1.tsv` | 1,539,229 | 1,520,684 | 38.31% | 2,130,606 | 2,130,172 | 3.45% |
| `train_source2.tsv` | 4,402,009 | 4,023,650 | 17.33% | 4,337,261 | 4,286,077 | 13.85% |
| `train_source3.tsv` | 4,651,609 | 4,278,929 | 16.88% | 4,632,764 | 4,616,044 | 12.35% |
| `test_source1.tsv` | 1,238,867 | 1,228,068 | 36.0% | 1,677,483 | 1,673,869 | 3.18% |
| `test_source2.tsv` | 4,311,041 | 4,002,462 | 16.36% | 4,224,783 | 4,149,371 | 13.56% |
| `test_source3.tsv` | 4,521,929 | 4,208,836 | 15.71% | 4,456,435 | 4,415,042 | 12.31% |

## 6. Text Length & Token Statistics

| Dataset File | Name Length (Mean / P95) | Name Tokens (Mean / P95) | Address Length (Mean / P95) | Address Tokens (Mean / P95) | Non-ASCII Pct |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `train_source1.tsv` | 24.03 / 37.0 | 3.57 / 5.0 | 52.07 / 103.0 | 8.5 / 17.0 | 0.0% |
| `train_source2.tsv` | 25.1 / 40.0 | 4.55 / 14.0 | 47.83 / 97.0 | 8.34 / 17.0 | 15.19% |
| `train_source3.tsv` | 25.2 / 42.0 | 4.19 / 8.0 | 48.32 / 92.0 | 8.16 / 17.0 | 11.48% |
| `test_source1.tsv` | 23.84 / 36.0 | 3.55 / 5.0 | 57.21 / 105.0 | 9.4 / 17.0 | 2.35% |
| `test_source2.tsv` | 25.7 / 42.0 | 4.84 / 15.0 | 51.78 / 99.0 | 9.07 / 18.0 | 18.99% |
| `test_source3.tsv` | 25.66 / 42.0 | 4.37 / 10.0 | 50.08 / 95.0 | 8.73 / 17.0 | 14.51% |

## 7. Train vs. Test Distribution Comparison

### Country Distribution Shifts
- **Train Sources (`train_source1..3`)**: Covered only `US` and `India`.
- **Test Sources (`test_source1..3`)**: Additionally contain `France` entities.
- **Open-Set Constraint Enforcement**: Confirmed that `France` occurs in `test_source1.tsv`, `test_source2.tsv`, and `test_source3.tsv`.
