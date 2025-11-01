# scripts/run_experiment.py
import time
import pandas as pd
from pathlib import Path

PROMPTS_CSV = Path("prompts") / "prompt_variations.csv"
RESULTS = Path("results"); RESULTS.mkdir(exist_ok=True)
RAW = RESULTS / "raw"
OUT = RESULTS / "llm_outputs_structured.csv"

def parse_filename(stem: str):
    # model_condition_runX
    parts = stem.split("_")
    if len(parts) < 3:
        raise ValueError("Expected filename like model_condition_run1.txt")
    model, condition, run = parts[0], parts[1], parts[2].replace("run","")
    return model, condition, run

def main():
    if not PROMPTS_CSV.exists():
        raise FileNotFoundError("prompts/prompt_variations.csv not found.")
    prompts = pd.read_csv(PROMPTS_CSV)
    by_cond = {r["condition"]: r for _, r in prompts.iterrows()}

    files = []
    if RAW.exists():
        files += list(RAW.glob("*.txt")) + list(RAW.glob("*.md"))
    if not files:
        print(f"No raw files in {RAW.resolve()}")
        return

    rows = []
    for p in sorted(files):
        try:
            model, condition, run = parse_filename(p.stem)
        except Exception as e:
            print(f"Skipping {p.name}: {e}")
            continue
        if condition not in by_cond:
            print(f"Skipping {p.name}: unknown condition '{condition}'")
            continue

        rows.append({
            "prompt_id": by_cond[condition]["prompt_id"],
            "hypothesis": by_cond[condition]["hypothesis"],
            "condition": condition,
            "model": model,
            "run": run,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "prompt_text": by_cond[condition]["prompt_text"],
            "response_text": p.read_text(encoding="utf-8", errors="ignore")
        })

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"✅ Wrote {OUT} ({len(rows)} rows)")

if __name__ == "__main__":
    main()
