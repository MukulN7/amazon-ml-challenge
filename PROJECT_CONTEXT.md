# Amazon ML Challenge 2026 - Business Entity Resolution Context & Specification

> **IMMUTABLE SPECIFICATION & SOURCE OF TRUTH**  
> This document defines the exact architecture, requirements, rules, and design patterns for the Amazon ML Challenge 2026 solution. All future development must strictly adhere to the guidelines set forth here.

---

## 1. Project Objective

We are building a high-precision, high-recall business entity resolution system for the Amazon ML Challenge 2026.

The system resolves **Source 1** business entities against **Source 2** and **Source 3**.

### Core Architecture

```
    RAW DATA
        ↓
    DATA VALIDATION
        ↓
    NORMALIZATION
        ↓
    CANDIDATE GENERATION / RETRIEVAL
        ↓
    PAIRWISE FEATURES
        ↓
    MATCHING MODEL
        ↓
    ENTITY-LEVEL ASSEMBLY
        ↓
    F0.5-OPTIMIZED DECISION
        ↓
    SUBMISSION
```

The system must be scalable. We must **NOT** perform brute-force comparison of every Source 1 record against every Source 2/3 record.

The fundamental design paradigm is:
$$\text{RETRIEVE} \longrightarrow \text{SCORE} \longrightarrow \text{ASSEMBLE}$$

---

## 2. Official Competition Constraints

The following rules have been extracted from official Amazon ML Challenge 2026 materials and constitute binding constraints on system design:

1. **`candidate_pairs.tsv` Scope**: `candidate_pairs.tsv` represents the **FINAL candidate set** actually fed into the matching model for inference. If a cascaded architecture is used, `candidate_pairs.tsv` represents the input candidate set to the first scoring model stage.
2. **Candidate-Match Subset Rule**: Every ID appearing in `matching_results.tsv` MUST also appear in `candidate_pairs.tsv` for that Source 1 entity:
   $$\text{matched\_entity\_ids} \subseteq \text{candidate\_entity\_ids}$$
3. **Exact Row Coverage**: Every Source 1 test entity must have exactly **one output row** in both `matching_results.tsv` and `candidate_pairs.tsv`.
4. **Match Multiplicity**: A Source 1 entity may match **zero** (singleton), **one** (1-to-1), or **many** (1-to-N) Source 2 / Source 3 records.
5. **No Duplicate Collapsing**: Identical-looking Source 2 or Source 3 records must NOT automatically be collapsed into a single ID. Multiple correct entity IDs must be preserved and returned when present.
6. **Macro-Averaged Evaluation**: Competition $F_{0.5}$ metric is computed per Source 1 entity and macro-averaged across all Source 1 entities in the test set.
7. **Critical Singleton Behavior**:
   - True singleton + empty prediction (`matched_entity_ids` = "") $\rightarrow$ Scores **1.0**
   - True singleton + any predicted match $\rightarrow$ Scores **0.0**
8. **Candidate Generation Final Ranking Metric**: Candidate generation quality is explicitly reviewed in final ranking. Amazon favors approaches producing **smaller candidate sets per Source 1 entity**. Candidate generation must optimize the recall vs. candidate-volume tradeoff.
9. **Open-Set Country Constraint**: `France` appears in the test dataset, whereas training data covers `US` and `India`. Country attributes must be treated as an open set of string labels. The pipeline must NEVER be hardcoded to `US` or `India`.
10. **Test-Set Unsupervised Statistics**: Computing unsupervised statistics on test data (such as TF-IDF matrices, token frequencies, and blocking indices) is **allowed**.
11. **Self-Training & Synthetic Data**: Self-training, pseudo-labeling, and synthetic pairs generated strictly from provided records are **allowed**.
12. **Data Enrichment Prohibitions**: External data enrichment is **STRICTLY PROHIBITED**. This includes external business databases, geocoding/entity lookups, internet data augmentation, postal/gazetteer databases, and commercial hosted LLM APIs (Claude, Gemini, ChatGPT).
13. **Pure Algorithmic Open-Source Libraries**: Standard algorithmic open-source Python libraries (`pandas`, `numpy`, `scikit-learn`, `rapidfuzz`, etc.) are **allowed**.
14. **Pretrained Model Restrictions**:
    - License must be **MIT** or **Apache 2.0**.
    - Maximum **8 Billion (8B)** parameters.
    - Must run **100% offline** without network calls.
    - Fine-tuned **only on provided challenge data**.
    - The restriction applies **independently to every individual model component** (embedder, reranker, preprocessor, matcher).
15. **Blocking Evaluation Suite**: Candidate generation must be evaluated using:
    - Candidate recall
    - Entity-complete candidate recall
    - Mean candidates per Source 1 entity
    - P95 / P99 candidates per Source 1 entity
    - Reduction ratio
    - Runtime & memory footprint
    - Downstream $F_{0.5}$ impact
16. **No Fixed Assumptions**: Do NOT assume a fixed candidate limit $K$, frequency cutoff, or score threshold without experimental validation.

---

## 3. Data Guidelines & Directory Rules

### Raw Data Location
Raw challenge data is located at:
`D:\amazon_hackathon\data\raw`

Expected raw files:
- `train_source1.tsv`
- `train_source2.tsv`
- `train_source3.tsv`
- `train_ground_truth.tsv`
- `test_source1.tsv`
- `test_source2.tsv`
- `test_source3.tsv`

### Immutability Constraint
**The raw files are strictly immutable.**
- Never overwrite, edit, normalize in-place, rename columns in-place, or otherwise modify files under `data/raw/`.
- Derived data must be saved to:
  - `data/interim/`
  - `data/processed/`
- Generated candidate sets must be stored under `outputs/candidates/`.
- Predictions must be stored under `outputs/predictions/`.
- Final submissions must be stored under `outputs/submissions/`.
- Experiment artifacts and logs belong in `experiments/` and `outputs/reports/`.

---

## 4. Normalization

Normalization will create derived representations while preserving original values.

### Fields of Interest
- `business_name`
- `business_address`
- `country`

### Normalization Techniques
- Unicode normalization (e.g. NFKD / NFKC)
- Case folding / lowercase conversion
- Punctuation normalization
- Whitespace normalization
- Unicode/diacritic handling
- Conservative abbreviation handling
- Script/transliteration representations where justified

### Requirements
- Normalization must be deterministic and testable.
- **Do not destroy original fields.**
- **Do not use external business/geographic databases.**

---

## 5. Open-Set Country Handling

Official documentation confirms that while the training dataset contains entities from `US` and `India`, the test dataset contains a third country: `France`.

### Implementation Rules for Country
- Country attributes must be processed as an **open set of arbitrary string labels**.
- Do NOT build pipelines, features, or models that rely on hard-coded country lists (e.g. `if country == 'US'`).
- Do NOT perform one-hot encoding restricted only to `{US, India}`.
- Country equality, cross-country indexing, and country-agnostic attribute normalizations must handle `France` and any other potential country strings gracefully without fallback errors or zero-vector crashes.

---

## 6. Candidate Generation Objective & Retrieval (Blocking)

Candidate generation is a critical subsystem of entity resolution.

### Dual Candidate Generation Objective
Candidate generation has **TWO co-equal objectives**:
1. **Retain True Matches**: Maximize candidate recall and entity-complete recall (maximizing the recall ceiling for the matching model).
2. **Minimize Unnecessary Candidates**: Keep total candidate volume per Source 1 entity as small and lean as possible.

> **CRITICAL**: The candidate generation objective is **NOT** simply maximum recall at any volume. Because Amazon evaluates `candidate_pairs.tsv` during final ranking and explicitly rewards smaller average candidate sets per Source 1 entity, the candidate generation subsystem must optimize the **Recall vs. Candidate Volume Pareto curve**.

### Potential Retrieval Mechanisms
1. Exact normalized name
2. Exact normalized address
3. Exact compact representations
4. Rare name-token blocking
5. Rare address-token blocking
6. Frequency-aware/high-DF token blocking
7. Character n-gram retrieval
8. Character TF-IDF retrieval
9. Structured numeric/address keys
10. Name + address composite keys
11. Optional dense embedding retrieval as a recall backstop
12. Reverse retrieval / reciprocal retrieval
13. Learned aliases and cross-script mappings derived ONLY from allowed challenge data

### Blocking Principles
- Candidate sets should generally be **UNIONED** across independent retrieval methods and deduplicated.
- Do not assume one blocking rule is sufficient.
- Do not choose arbitrary candidate $K$ values or frequency thresholds without validation.
- Candidate generation performance must be evaluated experimentally using candidate recall, entity-complete recall, mean candidates per S1, P95/P99 candidates per S1, reduction ratio, runtime/memory, and downstream $F_{0.5}$.

---

## 7. Pairwise Feature Engineering

After retrieval, rich pairwise features are computed on the candidate pairs.

### Feature Families

#### Name Features
- Exact equality
- Normalized equality
- Character similarity (Jaro-Winkler, Levenshtein, Indel, etc. via RapidFuzz)
- Token overlap (Jaccard, Dice, overlap coefficient)
- TF-IDF cosine similarity
- Rare-token overlap
- Token frequency statistics
- Length difference & ratio features
- Edit-distance features

#### Address Features
- Exact equality
- Character similarity
- Token overlap
- TF-IDF similarity
- Numeric agreement
- House/building number agreement
- Postal-code-like numeric patterns when available from the records themselves
- Address length/structure features

#### Country Features
- Open-set exact country agreement
- Generic string similarity and open-set handling

#### Retrieval Meta-Features
- Retrieval method(s) that produced the candidate
- Rank from each retrieval method
- Similarity score from each retrieval method
- Number of independent retrieval methods agreeing
- Reciprocal rank where applicable

#### Entity-Level Features
- Top candidate score
- Second-best candidate score
- Score margin ($\Delta = s_1 - s_2$)
- Candidate density
- Evidence from related/high-confidence matches

*All features must be derived strictly from allowed challenge data or allowed offline algorithms.*

---

## 8. Pairwise Matching Model

The initial matcher should be a strong tree-based gradient boosting model evaluated experimentally:
- LightGBM (`LightGBMClassifier`)
- XGBoost (`XGBClassifier`)
- HistGradientBoosting (`HistGradientBoostingClassifier`)

### Training & Validation Principles
- Compare binary classification and learning-to-rank formulations where useful.
- Training data must reflect the real candidate-generation distribution.
- Hard negatives from actual blocking/retrieval candidates are mandatory (random negatives alone are insufficient).
- **Validation Leakage Prevention**: Split training/validation folds at the **Source 1 entity level** rather than randomly splitting candidate pairs.

---

## 9. Entity-Level Assembly

Entity resolution is **not** strictly a 1-to-1 nearest-neighbor matching problem.

An S1 entity may have:
- **Zero matches** (S1-A $\rightarrow$ no match)
- **One match** (S1-B $\rightarrow$ S2-123)
- **Multiple matches** (S1-C $\rightarrow$ S2-456, S3-789, S3-790)

### Decision Factors
Final decision rules must consider:
- Calibrated model probability / score
- Decision threshold
- Score margin between top candidates
- Candidate density
- Match existence evidence
- Entity-level global evidence
- Precision vs. Recall tradeoff ($F_{0.5}$)

Do not automatically force exactly one match per S1 entity. Do not collapse distinct S2/S3 entity records that have identical names/addresses.

---

## 10. Evaluation & Competition Metric

The primary competition metric is **$F_{0.5}$ score**:
$$F_{0.5} = (1 + 0.5^2) \cdot \frac{\text{Precision} \cdot \text{Recall}}{(0.5^2 \cdot \text{Precision}) + \text{Recall}} = 1.25 \cdot \frac{\text{Precision} \cdot \text{Recall}}{0.25 \cdot \text{Precision} + \text{Recall}}$$

Precision is weighted **4 times more heavily** than recall. False positives (false merges) are heavily penalized.

### Macro-Averaging & Singleton Rules
- Computed as a **macro-average per Source 1 entity** across all entities in the test set.
- **Singletons**: True singletons with no matches earn **1.0** when an empty list is predicted, and **0.0** when any match is predicted.

### Subsystem Evaluation Metrics

#### Blocking Quality Evaluation Suite
- Candidate recall
- Entity-complete candidate recall
- Mean candidates per Source 1 entity
- P95 / P99 candidate count
- Reduction ratio
- Runtime & memory footprint
- Downstream $F_{0.5}$ impact

#### Matching Quality
- Precision
- Recall
- Macro-averaged $F_{0.5}$
- False Positives (FP) count & breakdown
- False Negatives (FN) count & breakdown

*Do not optimize accuracy alone. Do not tune directly on test labels (test labels are unavailable). Use local validation splits.*

---

## 11. Allowed vs. Prohibited Data Sources & Models

Strict compliance with official challenge rules is mandatory.

### Prohibited
- External business databases
- External entity databases
- Geocoding APIs
- Postal / gazetteer databases
- External geographic lookup tables
- Internet-sourced business information / data enrichment
- External APIs that enrich records
- Python packages that silently inject external geographic/business data
- Hosted LLM APIs (Claude, Gemini, ChatGPT)

### Allowed
- `pandas`, `numpy`, `scikit-learn`, `rapidfuzz`
- Standard string algorithms
- Offline deterministic text normalization
- Allowed offline transliteration
- TF-IDF & sparse retrieval
- Unsupervised test statistics (TF-IDF matrices, token frequencies, blocking indices)
- Self-training and synthetic pair generation strictly from provided records
- Allowed pretrained open-weight models satisfying challenge license (MIT/Apache 2.0), size ($\le 8\text{B}$ params per component), and offline restrictions

Before adding any new dependency or model, verify compliance with official rules.

---

## 12. Experimentation Principles

We do not add complexity without empirical proof. Every major component must be evaluated systematically against baselines.

### Progressive Experiment Progression

#### Blocking Progression:
- `B0` $\rightarrow$ Exact name
- `B1` $\rightarrow$ Exact address
- `B2` $\rightarrow$ Token blocking
- `B3` $\rightarrow$ Character TF-IDF
- `B4` $\rightarrow$ Address retrieval
- `B5` $\rightarrow$ Structured keys
- `B6` $\rightarrow$ Hybrid retrieval
- `B7` $\rightarrow$ Hybrid + dense retrieval
- `B8` $\rightarrow$ Hybrid + reverse retrieval

#### Model Progression:
- `M0` $\rightarrow$ Logistic Regression baseline
- `M1` $\rightarrow$ LightGBM
- `M2` $\rightarrow$ XGBoost
- `M3` $\rightarrow$ Learning-to-Rank
- `M4` $\rightarrow$ Matching model + entity-level features

*All parameters ($K$, frequency cutoffs, thresholds) must be driven by experimental data stored in `experiments/` and `outputs/reports/`.*

---

## 13. Project Directory Structure

```
D:\amazon_hackathon\
├── PROJECT_CONTEXT.md   # Complete project specification & source of truth
├── README.md            # Overview, architecture, and usage guide
├── requirements.txt     # Dependency declarations
├── .gitignore          # Excludes raw data, interim outputs, caches
├── data/
│   ├── raw/            # IMMUTABLE raw TSV datasets
│   ├── interim/        # Intermediary normalized data & features
│   └── processed/      # Clean processed dataset artifacts
├── src/
│   ├── __init__.py
│   ├── config/         # System configuration & parameters
│   ├── data/           # Loaders, validation, schema definitions
│   ├── normalization/  # Text & attribute normalization
│   ├── blocking/       # Candidate generation & blocking rules
│   ├── retrieval/      # TF-IDF, n-gram, index retrieval engines
│   ├── features/       # Pairwise feature extractors
│   ├── models/         # ML matchers (LightGBM, XGBoost, etc.)
│   ├── assembly/       # Entity-level match assembly & thresholding
│   ├── evaluation/     # F0.5, recall, precision, blocking metrics
│   └── inference/      # Pipeline orchestration & submission writer
├── outputs/
│   ├── candidates/     # Candidate pair files
│   ├── predictions/    # Raw model predictions
│   ├── submissions/    # Verified final submission TSV/CSV files
│   └── reports/        # Evaluation summaries & metrics
├── experiments/        # Experiment tracking logs & notebooks
├── scripts/            # Helper scripts & CLI runners
└── tests/              # Pytest unit & integration tests
```

---

## 14. Version Control & Git Workflow

- Canonical repository: `https://github.com/MukulN7/amazon-ml-challenge`
- Never commit raw datasets, interim files, or candidate dumps.
- Commit messages must be structured and descriptive:
  - `chore: initialize project structure`
  - `feat: add dataset schema validation`
  - `feat: add normalization pipeline`
  - `feat: add exact blocking`
  - `feat: add tfidf retrieval`
  - `feat: add pairwise features`
  - `feat: add baseline matcher`
  - `experiment: compare blocking strategies`
  - `feat: add entity-level assembly`
- Run test suite (`pytest`) before major commits.
