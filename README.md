# Amazon ML Challenge 2026 - Business Entity Resolution

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

High-precision, high-recall entity resolution system for the **Amazon ML Challenge 2026**, resolving Source 1 business entities against Source 2 and Source 3 records.

---

## 🎯 Project Objective

The goal is to accurately identify matching business entities across three distinct data sources (Source 1, Source 2, and Source 3) under strict $F_{0.5}$ metric constraints (where precision is weighted 4x more than recall).

To ensure scalability across large datasets, the system avoids brute-force $O(N \times M)$ comparisons. Instead, it follows a three-tier architecture:

$$\text{RETRIEVE} \longrightarrow \text{SCORE} \longrightarrow \text{ASSEMBLE}$$

---

## 🏗️ Core Architecture

```
    +-------------------------------------------------------+
    |                    RAW TSV DATA                       |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |              DATA VALIDATION & SCHEMA                 |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |           DETERMINISTIC NORMALIZATION                 |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |      CANDIDATE GENERATION & HYBRID RETRIEVAL          |
    |  (Exact, Token, TF-IDF, N-Gram, Structured Keys)      |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |            PAIRWISE FEATURE EXTRACTION                |
    |      (String similarities, TF-IDF, Meta-features)     |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |          MATCHING MODEL (LightGBM / XGBoost)          |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |          ENTITY-LEVEL MATCH ASSEMBLY                  |
    |        (Zero, 1-to-1, or 1-to-N resolution)            |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |              F0.5 DECISION OPTIMIZATION               |
    +-------------------------------------------------------+
                                |
                                v
    +-------------------------------------------------------+
    |                   SUBMISSION TSV                      |
    +-------------------------------------------------------+
```

### Key Stages

1. **Normalization**: Case folding, Unicode normalization, punctuation/whitespace normalization, conservative abbreviation handling without altering raw files.
2. **Candidate Generation / Retrieval**: Combining multi-view blocking rules (exact match, token overlap, TF-IDF, character n-grams) to maximize candidate recall while keeping candidate counts small.
3. **Pairwise Feature Engineering**: Computing string distance, token overlap, TF-IDF similarity, and retrieval meta-features for candidate pairs.
4. **Matching Model**: Gradient boosted decision trees (LightGBM/XGBoost) trained on candidate distribution with entity-level cross-validation.
5. **Entity-Level Assembly**: Aggregating pairwise scores to handle 0-match, 1-match, and multi-match entities per Source 1 record.
6. **F0.5 Optimization**: Calibrating decision thresholds specifically to optimize precision-heavy $F_{0.5}$.

---

## 📂 Project Directory Structure

```
D:\amazon_hackathon\
├── PROJECT_CONTEXT.md   # Complete project specification & source of truth
├── README.md            # Overview, architecture, and usage guide
├── requirements.txt     # Dependency declarations
├── .gitignore          # Excludes raw data, interim outputs, caches
├── data/
│   ├── raw/            # IMMUTABLE challenge datasets (train/test TSVs)
│   ├── interim/        # Interim normalized data and extracted features
│   └── processed/      # Processed dataset artifacts
├── src/
│   ├── __init__.py
│   ├── config/         # System configuration & parameter definitions
│   ├── data/           # Dataset loaders and schema validation
│   ├── normalization/  # Attribute normalization algorithms
│   ├── blocking/       # Blocking rules and key generators
│   ├── retrieval/      # Indexing and candidate retrieval engines
│   ├── features/       # Pairwise feature extraction functions
│   ├── models/         # Pairwise classification & ranking models
│   ├── assembly/       # Entity resolution decision & assembly logic
│   ├── evaluation/     # Metrics: F0.5, Precision, Recall, Candidate Recall
│   └── inference/      # Pipeline runner & submission generation
├── outputs/
│   ├── candidates/     # Candidate pair files
│   ├── predictions/    # Raw model predictions
│   ├── submissions/    # Verified submission files
│   └── reports/        # Evaluation summaries and experiment reports
├── experiments/        # Experiment logs and research notebooks
├── scripts/            # CLI utilities and workflow entrypoints
└── tests/              # Unit and integration test suite
```

---

## 🧪 Experimentation Philosophy

Every component is evaluated empirically. We avoid arbitrary parameters and unvalidated complexity.

### Benchmark Progressions
- **Blocking Strategies ($B_0 \dots B_8$)**: Evaluated on Candidate Recall, Average Candidates per S1, and Reduction Ratio.
- **Matching Models ($M_0 \dots M_4$)**: Evaluated on Precision, Recall, and $F_{0.5}$ using Source 1 entity-grouped cross-validation.

---

## ⚙️ Development Workflow

1. **Rule Compliance**: Only use allowed offline algorithms and libraries. No external databases, geocoding APIs, or hosted LLM endpoints.
2. **Raw Data Safety**: Files under `data/raw/` are strictly read-only.
3. **Validation**: Always use Source 1 entity-level splits to avoid validation leakage.
4. **Git Commits**: Canonical repo at `https://github.com/MukulN7/amazon-ml-challenge`. Commit frequently with standard conventional commit prefixes (`feat:`, `experiment:`, `chore:`, `fix:`).

---

## 📌 Current Project Status

- [x] **Stage 1: Project Foundation** (Directory structure, package initialization, specifications, git setup)
- [ ] **Stage 2: Dataset & Schema Inspection**
- [ ] **Stage 3: Data Validation Pipeline**
- [ ] **Stage 4: Dataset Profiling & EDA**
- [ ] **Stage 5: Normalization Pipeline**
- [ ] **Stage 6: Blocking & Retrieval Experiments**
- [ ] **Stage 7: Pairwise Feature Engineering**
- [ ] **Stage 8: Matching Model Development**
- [ ] **Stage 9: Entity-Level Assembly**
- [ ] **Stage 10: F0.5 Optimization**
- [ ] **Stage 11: End-to-End Test Inference**
- [ ] **Stage 12: Submission Validation & Generation**

---

## 🚀 How to Run (Once Implementation Begins)

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest tests/
```

### 3. Pipeline Execution (Future)
```bash
# Example command structure for pipeline runner once implemented
python -m src.inference.run_pipeline --config src/config/default.yaml
```
