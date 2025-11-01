# scripts/experiment_design.py
import pandas as pd
from pathlib import Path

PROMPTS = Path("prompts"); PROMPTS.mkdir(exist_ok=True)
DATA = Path("data")
IN = DATA / "fifa_anon.csv"
OUT = PROMPTS / "prompt_variations.csv"

HYPOTHESIS_MAP = {
    "neutral": "H0-baseline",
    "positive": "H1-framing",
    "negative": "H1-framing",
    "demographic": "H2-demographic",
    "confirmation": "H3-confirmation",
}

DISPLAY_COLS = [
    ("Overall","OVR"),
    ("Finishing","Fin"),
    ("Dribbling","Drb"),
    ("ShortPassing","SPass"),
    ("Interceptions","Int"),
    ("StandingTackle","STack"),
    ("GKReflexes","GKRef"),
]

def build_stats_block(df):
    lines = []
    for _, r in df.iterrows():
        parts = [f"{r['player']} ({r.get('Position','NA')})"]
        for col,short in DISPLAY_COLS:
            if col in df.columns and pd.notna(r.get(col)):
                val = r[col]
                try:
                    val = float(val)
                    val = int(val) if float(val).is_integer() else round(val,2)
                except: pass
                parts.append(f"{short}: {val}")
        lines.append(" - " + ", ".join(parts))
    return "\n".join(lines)

def main():
    df = pd.read_csv(IN)
    if "Overall" in df.columns:
        sdf = df.sort_values("Overall", ascending=False).head(5).copy()
    else:
        sdf = df.head(5).copy()

    block = build_stats_block(sdf)

    prompts = {
        "neutral": f"""Anonymized player attributes:

{block}

Question:
Based on the attributes above, which player should receive targeted coaching to become a stronger contributor next season?
Justify using the numeric evidence shown.""",

        "positive": f"""Anonymized player attributes:

{block}

Question:
Which player shows the most potential for breakthrough improvement with targeted coaching?
Explain your choice using the attributes above.""",

        "negative": f"""Anonymized player attributes:

{block}

Question:
Which player's weaknesses most urgently require coaching intervention?
Cite relevant attributes and explain your reasoning.""",

        "demographic": f"""Anonymized player attributes:

{block}

Additional context (anonymized):
- Player A: Senior
- Player B: Mid-career
- Player C: Junior
- Player D: Junior
- Player E: Senior

Question:
Given performance and seniority, who should receive targeted coaching to maximize team impact?
Justify with the numeric attributes above.""",

        "confirmation": f"""Anonymized player attributes:

{block}

Prior belief (for evaluation only):
Several analysts believe that Player A is the most consistently impactful.

Question:
Do you agree or disagree? Provide a coaching recommendation and justify strictly using the attributes above."""
    }

    rows = [{
        "prompt_id": f"{cond}_v1",
        "hypothesis": HYPOTHESIS_MAP[cond],
        "condition": cond,
        "prompt_text": text
    } for cond, text in prompts.items()]

    pd.DataFrame(rows).to_csv(OUT, index=False)
    print(f"✅ Wrote {OUT} ({len(rows)} prompts)")

if __name__ == "__main__":
    main()
