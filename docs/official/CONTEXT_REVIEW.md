# Project Context & Official Rules Alignment Review

> **COMPARATIVE AUDIT REPORT**  
> Evaluates `PROJECT_CONTEXT.md` against official challenge documents in `docs/official/`.

---

## 1. Correctly Reflected

The following core design elements in `PROJECT_CONTEXT.md` are fully aligned with official challenge rules:

- **Problem Formulation**: Multi-source business entity resolution matching deduplicated **Source 1** reference entities against **Source 2** and **Source 3**.
- **Retrieve $\rightarrow$ Score $\rightarrow$ Assemble Architecture**: Scalable blocking/retrieval followed by pairwise feature scoring and entity assembly, avoiding brute-force $O(N \times M)$ comparisons.
- **Raw Data Immutability**: Strict rule that raw data under `data/raw/` must never be modified or overwritten in-place.
- **Evaluation Metric ($F_{0.5}$)**: Metric choice of $F_{0.5}$ penalizing false positive merges $4\times$ more heavily than missed matches.
- **Strict Data Prohibitions**: Complete prohibition of external databases, government registries, geocoding APIs, internet enrichment, and hosted LLM APIs.
- **Offline ML & License Restrictions**: Allowance of open-weight offline models up to 8B parameters with MIT/Apache 2.0 licenses.
- **Entity-Level Validation Splits**: Preventing validation leakage by splitting folds at the Source 1 entity level.

---

## 2. Missing from `PROJECT_CONTEXT.md`

The official challenge material specifies several critical rules that are not currently captured in `PROJECT_CONTEXT.md`:

1. **`candidate_pairs.tsv` as a Mandatory Final Submission Artifact**:
   - `PROJECT_CONTEXT.md` discusses candidate files in `outputs/candidates/`, but does not state that `candidate_pairs.tsv` is a **mandatory output file** required in the final submission package alongside `matching_results.tsv`.
2. **Candidate Size Efficiency Ranking Rule**:
   - Official communications explicitly state that Amazon will review `candidate_pairs.tsv` during final ranking: **approaches generating a smaller average candidate set per Source 1 entity will be ranked higher** beyond leaderboard scores.
3. **Open-Set Country Requirement & Test Country (`France`)**:
   - Official guidelines reveal that while training data covers `{US, India}`, the test set contains a third country, `France`.
   - `PROJECT_CONTEXT.md` does not mention that country must be treated as an open set of string labels, prohibiting hardcoded one-hot encodings or filters.
4. **Macro-Averaged Evaluation & Singleton Scoring**:
   - Official docs clarify that $F_{0.5}$ is calculated as a **macro-average per Source 1 entity** across the entire evaluation set.
   - Singletons (entities with no match) earn a full **1.0 score** when an empty list is correctly predicted, and **0.0** if any false match is output.
5. **Validator Utility (`validate_submission.py`)**:
   - Official guidelines provide a standard library validation script to test submission formatting locally before upload.
6. **Per-Model Scope for Model Restrictions**:
   - Official Q&A clarifies that the 8B parameter limit and MIT/Apache 2.0 license requirement apply **independently to every individual model component** (embedder, reranker, preprocessor, matcher).

---

## 3. Potential Conflicts

1. **Submission Directory & Naming Structure**:
   - `PROJECT_CONTEXT.md` specifies output locations as `outputs/predictions/` and `outputs/submissions/`.
   - Official requirements mandate exact relative paths inside the final submission zip: `output/matching_results.tsv` and `output/candidate_pairs.tsv`.
2. **Candidate Volume vs. Candidate Size Ranking**:
   - `PROJECT_CONTEXT.md` lists dense retrieval ($B7$) and hybrid retrieval ($B6$) to maximize recall.
   - However, if candidate generation produces overly broad candidate lists, it will incur a severe penalty under the official **Candidate Size Efficiency Ranking Rule**.

---

## 4. Architectural Implications

1. **Candidate Generation Dual-Objective**:
   - Candidate generation algorithms cannot purely maximize Candidate Recall; they must optimize the **Recall vs. Average Candidate Volume** pareto frontier.
2. **Synchronized Candidate & Match Generation**:
   - The inference engine must generate both `candidate_pairs.tsv` and `matching_results.tsv` in a single pass, guaranteeing that $\text{matched\_entity\_ids} \subseteq \text{candidate\_entity\_ids}$.
3. **Robust Open-Set Normalization & Feature Pipeline**:
   - Country and address features must be designed for unseen international contexts (e.g. France) without relying on fixed geographic categories.
4. **Local Evaluation Metric Calibration**:
   - Local validation scripts must implement exact macro-averaged $F_{0.5}$ including singleton scoring to accurately reflect leaderboard evaluation.
