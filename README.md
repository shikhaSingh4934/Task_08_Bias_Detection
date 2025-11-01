# ⚽ Research Task 08 – Bias Detection in LLM Narratives (FIFA Dataset)

**Author:** Shikha Singh  
**Course:** SU OPT Research – Task 08  
**Advisor:** Jon Strome ([jrstrome@syr.edu](mailto:jrstrome@syr.edu))  
**Date:** November 2025  

---

## 🧠 Overview

This project investigates whether **Large Language Models (LLMs)** such as ChatGPT, Claude, and Gemini show **biases when interpreting identical data** framed differently.  
It builds on earlier OPT research tasks (Tasks 4–7) and applies controlled testing on an **anonymized FIFA player dataset**.

The experiment tests whether the model’s interpretation changes when:
- The **question framing** (positive vs. negative) changes,
- The **player demographics** are mentioned,
- Or a **prior belief** is stated in the prompt.

---

## 🎯 Objectives

1. **Detect framing, demographic, and confirmation biases** in LLM outputs.  
2. **Quantify narrative differences** using structured prompts and sentiment patterns.  
3. **Validate statements** made by LLMs against real numeric ground truth from the FIFA dataset.  
4. **Document reproducible experiments** that meet Syracuse OPT research standards.

---

## 🧩 Methodology

### 1. Dataset Preparation
- Raw data: `Dataset/fifa_eda_stats.csv`  
- Anonymized with `sanitize_players.py` → output: `data/fifa_anon.csv`  
  - Replaces real names with “Player A”, “Player B”, etc.  
  - Ensures no personally identifiable information is used.

### 2. Ground Truth Creation
- Script: `ground_truth.py`  
- Produces two reference files:
  - `analysis/ground_truth_full.csv` – all numeric stats per player  
  - `analysis/ground_truth_metrics.csv` – top players by key metrics (Finishing, Passing, GK, etc.)

### 3. Prompt Generation
- Script: `experiment_design.py`  
- Creates 5 structured prompt variations for each hypothesis:
  - **neutral**, **positive**, **negative**, **demographic**, **confirmation**  
- Output: `prompts/prompt_variations.csv`

### 4. Experiment Execution
- Each prompt is tested on 2–3 LLMs (ChatGPT, Claude, Gemini).  
- Raw text responses are stored under:
  - `results/raw/model_condition_runX.txt`  
- `run_experiment.py` merges all responses into a single CSV log for analysis.

### 5. Validation
- `validate_claims.py` cross-checks model statements against `ground_truth_metrics.csv`.  
- Flags contradictions, fabrications, or inconsistencies.  
- Output: `analysis/claims_validation.csv`

---

## 🧪 Hypotheses Summary

| ID | Bias Type | Description | Example Prompt |
|----|------------|--------------|----------------|
| H0 | Neutral | Baseline question with stats only | “Which player should get extra training?” |
| H1 | Framing | Positive vs. negative tone | “Most potential for improvement” vs. “Most underperforming” |
| H2 | Demographic | Mentions age/seniority | “Senior vs. Junior players…” |
| H3 | Confirmation | Includes analyst’s opinion | “Analysts believe Player A is best — do you agree?” |

---

## 📂 Directory Structure

```plaintext
Task_08_Bias_Detection/
│
├── Dataset/
│   └── fifa_eda_stats.csv
├── data/
│   └── fifa_anon.csv
├── analysis/
│   ├── ground_truth_full.csv
│   ├── ground_truth_metrics.csv
│   └── claims_validation.csv
├── prompts/
│   └── prompt_variations.csv
├── results/
│   ├── raw/
│   │   ├── gpt4_neutral_run1.txt
│   │   ├── claude_positive_run1.txt
│   │   └── gemini_negative_run1.txt
│   └── combined_llm_responses.csv
├── scripts/
│   ├── sanitize_players.py
│   ├── ground_truth.py
│   ├── experiment_design.py
│   ├── run_experiment.py
│   └── validate_claims.py
├── docs/
│   └── hypotheses.md
└── README.md

---

## 🧾 Deliverables

- ✅ Anonymized FIFA dataset (`fifa_anon.csv`)  
- ✅ Ground truth metrics  
- ✅ Structured LLM prompts  
- ✅ Raw and consolidated model outputs  
- ✅ Validation results comparing LLM claims vs numeric truth  
- ✅ `README.md` and `hypotheses.md` documentation  

---

## 🧭 Learnings

This task refined the following skills:
- **Experimental design** for AI behavior analysis  
- **Data sanitization and bias detection** workflows  
- **Automation scripting** in Python (pandas, pathlib)  
- **Statistical validation and reproducibility**  
- **Ethical documentation and transparency in AI research**

---
