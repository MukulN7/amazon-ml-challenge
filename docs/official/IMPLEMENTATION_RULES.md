# Official Implementation Rules

> **AUTHORITATIVE COMPLIANCE SPECIFICATION**  
> Compiled from official Amazon ML Challenge 2026 guidelines, email communications, and Q&A form responses.

---

## 1. Challenge Objective

- **Source 1 Representation**: Source 1 is the deduplicated reference entity source containing clean/canonical business entity records.
- **Source 2 & Source 3 Representation**: Source 2 and Source 3 represent secondary and tertiary data sources containing noisy, incomplete, or variations of business entity records (with inconsistent business names, missing address components, typos, abbreviations, and landmark references).
- **Match Definition**: A match occurs when a record in Source 2 or Source 3 refers to the exact same real-world business entity as a record in Source 1.
- **Match Multiplicity**: A Source 1 entity may match:
  - **Zero matches** (singleton entity)
  - **One match** (1-to-1 matching: e.g. S1-A $\rightarrow$ S2-101)
  - **Multiple matches** (1-to-N matching: e.g. S1-B $\rightarrow$ S2-101, S2-102, S3-505)
- **Target Output**: For every Source 1 entity in the test set, output a mapping to all matching entity IDs from Source 2 and/or Source 3.

*Source: `6ab674645103d_emails_comms_amazon_ml_challenge_2026.pdf` (Page 1 & 2)*

---

## 2. Dataset Format

### File Schemas
- **Source Records** (`train_source1.tsv`, `train_source2.tsv`, `train_source3.tsv`, `test_source1.tsv`, `test_source2.tsv`, `test_source3.tsv`):
  - File Format: Tab-Separated Values (`.tsv`), explicitly read with `sep="\t"`.
  - Column 1: `entity_id` — Unique record ID. Prefix indicates source (`S1-`, `S2-`, `S3-`).
  - Column 2: `business_name` — Entity name (contains abbreviations, legal suffixes, typos, transliterations).
  - Column 3: `business_address` — Address (partial addresses, missing PIN codes, landmark references, component reordering).
  - Column 4: `country` — Country label.
- **Ground Truth** (`train_ground_truth.tsv`):
  - Column 1: `source1_entity_id` — Entity ID of Source 1 record.
  - Column 2: `matched_entity_ids` — Comma-separated list of matching entity IDs from Source 2 and/or Source 3 (empty string for singletons with no match).

### Critical Data Rules
- **Open Set Country Rule**: Training data contains `{US, India}`. The test set additionally contains `{France}`. Country fields MUST be treated as an open set of string labels. Hard-coding, filtering out non-training countries, or one-hot encoding strictly to `{US, India}` is prohibited. Every test entity (including `France`) must appear in the final submission.
- **Source Identification**: Entity sources are explicitly identified by the `entity_id` prefix (`S1-`, `S2-`, `S3-`) and the file in which they appear.

*Source: `6ab674645103d_emails_comms_amazon_ml_challenge_2026.pdf` (Page 2)*

---

## 3. Submission Format

### Dual Submission Package
Teams must generate two TSV files placed in the `output/` directory of the final submission package:
1. `matching_results.tsv`: Final entity matches scored on the leaderboard.
2. `candidate_pairs.tsv`: Final candidate set produced by the blocking/candidate-generation stage before matching model scoring.

### Submission File Specifications

| Attribute | `matching_results.tsv` | `candidate_pairs.tsv` |
| :--- | :--- | :--- |
| **Header** | `source1_entity_id\tmatched_entity_ids` | `source1_entity_id\tcandidate_entity_ids` |
| **Row Count** | Exactly 1 row per test Source 1 entity | Exactly 1 row per test Source 1 entity |
| **ID Separator** | Commas `,` with no spaces or quotes | Commas `,` with no spaces or quotes |
| **Empty Values** | Empty string when no matches exist | Empty string when blocking finds no candidates |
| **Allowed Prefixes**| `S2-` and `S3-` entity IDs only | `S2-` and `S3-` entity IDs only |
| **Forbidden IDs** | `S1-` IDs (self-matches cause rejection) | `S1-` IDs (self-matches cause rejection) |
| **Duplicate IDs** | Duplicate IDs within list cause rejection | Duplicate IDs within list cause rejection |

### Validation Utility (`utils/validate_submission.py`)
A standard-library validation script is provided to verify submission files locally prior to portal upload:
```bash
python3 utils/validate_submission.py \
  --matching output/matching_results.tsv \
  --candidate output/candidate_pairs.tsv \
  --test-dir dataset/test
```
- **Validation Checks**: Header exact match, exact test Source 1 coverage, absence of duplicate rows, absence of self-matches (`S1-`), validity of test S2/S3 IDs, absence of internal duplicate IDs, and subset enforcement (`matched_entity_ids` $\subseteq$ `candidate_entity_ids`).

### Final Submission Zip Archive Structure (`<team_name>_submission.zip`)
```
<team_name>_submission.zip
├── output/
│   ├── matching_results.tsv      # Final entity matches (leaderboard scored)
│   └── candidate_pairs.tsv       # Candidate set from candidate generation
├── code/
│   └── business_entity_resolution/
│       ├── src/                 # All pipeline source code
│       ├── README.md            # Exact end-to-end reproduction instructions
│       └── requirements.txt     # Pinned environment dependencies
└── Documentation_template.md    # Methodology write-up document
```

*Source: `6ab674645103d_emails_comms_amazon_ml_challenge_2026.pdf` (Page 3-5)*

---

## 4. Evaluation

### Metric: Macro-Averaged $F_{0.5}$ Score
Submissions are evaluated using the $F_\beta$ score with $\beta = 0.5$:
$$F_{0.5} = \frac{(1 + 0.5^2) \cdot \text{Precision} \cdot \text{Recall}}{(0.5^2 \cdot \text{Precision}) + \text{Recall}} = \frac{1.25 \cdot \text{Precision} \cdot \text{Recall}}{0.25 \cdot \text{Precision} + \text{Recall}}$$

### Key Metric Properties
- **Precision-Heavy**: Precision is weighted $2\times$ over recall (false positive merges are penalized $4\times$ more heavily than missed matches).
- **Macro-Averaged**: $F_{0.5}$ is calculated independently per Source 1 entity and then averaged across all Source 1 entities in the evaluation set.
- **Singleton Handling**: Entities with no true matches (singletons) are included in the macro-average:
  - Correctly predicting an empty list for a singleton $\rightarrow$ Scores **1.0** for that entity.
  - Incorrectly predicting any match for a singleton $\rightarrow$ Scores **0.0** for that entity.

*Source: `6ab674645103d_emails_comms_amazon_ml_challenge_2026.pdf` (Page 6)*

---

## 5. Candidate Generation Requirements

1. **Scalability Requirement**: Brute-force comparison is strictly forbidden. The blocking stage must reduce the search space to a small candidate set per Source 1 entity.
2. **Subset Constraint**: `candidate_pairs.tsv` represents the exact candidate set fed into the matching model for inference. Every ID in `matching_results.tsv` MUST appear in `candidate_pairs.tsv` for that Source 1 entity:
   $$\text{matched\_entity\_ids} \subseteq \text{candidate\_entity\_ids}$$
3. **Efficiency Ranking Tie-Breaker**: In addition to leaderboard $F_{0.5}$ performance, Amazon reviews `candidate_pairs.tsv` during final ranking. **Approaches generating a smaller average candidate set per Source 1 entity will be ranked higher in final evaluation.**

*Source: `6ab674645103d_emails_comms_amazon_ml_challenge_2026.pdf` (Page 1 & 4)*

---

## 6. Allowed Techniques

| Technique Category | Status | Details & Conditions |
| :--- | :--- | :--- |
| **Deterministic Normalization** | **ALLOWED** | Case folding, punctuation, diacritics, whitespace, conservative abbreviation handling. |
| **Fuzzy Matching / Similarity** | **ALLOWED** | Levenshtein, Jaro-Winkler, Jaccard, token overlap, character n-grams. |
| **TF-IDF & Sparse Retrieval** | **ALLOWED** | Character & word TF-IDF indices computed on provided data. |
| **Unsupervised Test Statistics**| **ALLOWED** | Computing TF-IDF dictionaries, token frequencies, and blocking indices on test files. |
| **Self-Training & Synthetic Data**| **ALLOWED** | Generating synthetic pairs or pseudo-labels strictly from provided records. |
| **Open-Weight ML/LLM Models** | **CONDITIONALLY ALLOWED**| Allowed IF MIT/Apache 2.0 licensed, $\le$ 8B params, run 100% offline, fine-tuned only on provided data. |
| **Classic ML Models** | **ALLOWED** | LightGBM, XGBoost, CatBoost, Logistic Regression, Scikit-Learn algorithms. |
| **AI Coding Assistance** | **ALLOWED** | AI tools used during development for code generation/pair programming. |

*Source: `Amazon ML Challenge 2026 - Query Form (Responses).xlsx` & PDF (Page 7-8)*

---

## 7. Prohibited / Restricted Techniques

| Prohibited Category | Enforcement Status | Official Rationale |
| :--- | :--- | :--- |
| **External Databases** | **STRICTLY PROHIBITED** | No commercial entity resolution APIs, government business registries, or postal lookups. |
| **Geocoding APIs** | **STRICTLY PROHIBITED** | No external geocoding services (Google Maps, Nominatim, OSM) to normalize addresses. |
| **Internet Data Augmentation** | **STRICTLY PROHIBITED** | No web scraping or internet-sourced entity enrichment. |
| **Hosted LLM APIs** | **STRICTLY PROHIBITED** | No calls to commercial cloud APIs (Claude, Gemini, ChatGPT, OpenAI API, etc.). |
| **Restricted Model Licenses** | **STRICTLY PROHIBITED** | No models with non-MIT/Apache 2.0 licenses (e.g., LLaMA license, GPL, non-commercial licenses). |
| **Models > 8B Parameters** | **STRICTLY PROHIBITED** | No models exceeding 8 Billion parameters. |

*Source: `6ab674645103d_emails_comms_amazon_ml_challenge_2026.pdf` (Page 7)*

---

## 8. Pretrained Model Restrictions

If any pretrained model is incorporated into any pipeline stage, it must satisfy all 5 mandatory conditions:
1. **License**: Must be released under **MIT** or **Apache 2.0** license only.
2. **Parameter Count**: Maximum **8 Billion (8B)** parameters per model.
3. **Independent Scope**: The limit applies **per model independently**. Every component (embedder, reranker, matcher, text preprocessor) must individually satisfy the 8B and license rules.
4. **Offline Execution**: Must run completely offline on local/instance hardware without any internet/third-party API calls.
5. **Training Data**: Must be fine-tuned ONLY on the provided challenge dataset.

*Source: `Amazon ML Challenge 2026 - Query Form (Responses).xlsx` (Leader Q&A Response #5)*

---

## 9. Training and Validation Rules

1. **Validation Setup**: No test ground truth is provided. Local validation splits must be created from `dataset/train/`.
2. **Leakage Prevention**: Validation splits MUST be performed at the **Source 1 entity level** (grouping all candidates of a given S1 entity together) rather than splitting candidate pairs randomly.
3. **Metric Alignment**: Local validation evaluation must compute macro-averaged $F_{0.5}$ including singletons to align with leaderboard evaluation.

---

## 10. Important Competition Constraints

1. **Submission Limits**: Maximum 5 submissions per day on the portal.
2. **Dual Output File Mandate**: Both `matching_results.tsv` and `candidate_pairs.tsv` are mandatory in the final zip archive.
3. **Candidate Efficiency Ranking**: Final rankings evaluate candidate set size—smaller candidate sets per Source 1 entity are favored.
4. **Code Reproducibility**: Winning solutions will be audited for exact end-to-end reproducibility from raw TSVs.

---

## 11. Items Not Specified

1. **Exact Hardware Hardware Specs**: Specific RAM/VRAM constraints for local execution (beyond offline execution requirement).
2. **Public vs. Private Leaderboard Split Percentage**: Exact proportion of test entities assigned to public vs. private leaderboard.
