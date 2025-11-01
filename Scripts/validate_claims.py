# scripts/validate_claims.py
import re
import pandas as pd
from pathlib import Path

GT = Path("analysis") / "ground_truth_full.csv"
LOG = Path("results") / "llm_outputs_structured.csv"
OUT = Path("analysis") / "claims_validation.csv"

NUMERIC_COLS = [
    "Overall","Potential","Age",
    "Finishing","ShotPower","LongShots","Dribbling","BallControl",
    "ShortPassing","LongPassing","Vision","Composure",
    "Acceleration","SprintSpeed","Stamina","Strength","Aggression",
    "Interceptions","StandingTackle","SlidingTackle",
    "GKDiving","GKHandling","GKKicking","GKPositioning","GKReflexes"
]

def extract_numbers(text: str):
    return [float(x) for x in re.findall(r"\b\d+(?:\.\d+)?\b", str(text))]

def r2(x):
    try:
        v = round(float(x), 2)
        return v
    except:
        return None

def main():
    if not GT.exists(): raise FileNotFoundError(GT)
    if not LOG.exists(): raise FileNotFoundError(LOG)

    gt = pd.read_csv(GT)
    log = pd.read_csv(LOG)

    # round ground truth numbers for matching
    for c in NUMERIC_COLS:
        if c in gt.columns:
            gt[c] = pd.to_numeric(gt[c], errors="coerce").apply(r2)

    # build player -> set(numeric facts)
    players = gt["player"].astype(str).tolist()
    facts = {}
    for _, r in gt.iterrows():
        vals = set()
        for c in NUMERIC_COLS:
            if c in gt.columns and pd.notna(r.get(c)):
                vals.add(r2(r[c]))
        facts[str(r["player"])] = vals

    rows = []
    for _, r in log.iterrows():
        txt = str(r["response_text"])
        nums = {r2(n) for n in extract_numbers(txt) if n is not None}
        mentioned = [p for p in players if p in txt]
        per_hits = {p: len(facts[p].intersection(nums)) for p in mentioned}
        rows.append({
            "prompt_id": r["prompt_id"],
            "condition": r["condition"],
            "model": r["model"],
            "run": r["run"],
            "mentioned_players": ", ".join(mentioned),
            "mentioned_players_count": len(mentioned),
            "total_ground_truth_numeric_hits": int(sum(per_hits.values())),
            "any_player_supported_by_numbers": bool(any(h > 0 for h in per_hits.values()))
        })

    out = pd.DataFrame(rows)
    OUT.parent.mkdir(exist_ok=True, parents=True)
    out.to_csv(OUT, index=False)
    print(f"✅ Wrote {OUT} ({len(out)} rows)")

if __name__ == "__main__":
    main()
