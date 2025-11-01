# scripts/ground_truth.py
# Produces:
#   analysis/ground_truth_full.csv   (per-player truth table for validation)
#   analysis/ground_truth_metrics.csv (FIFA-style KPI leaders)
#
# Robust to large files, mixed/lowercase headers, and missing columns.

from pathlib import Path
import pandas as pd
import re

# ---- Paths ----
DATA = Path("C:/Users/Singh/OneDrive/Desktop/Research Work/Task_08_Bias_Detection/data")
ANALYSIS = Path("analysis"); ANALYSIS.mkdir(exist_ok=True, parents=True)
IN_CSV = DATA / "fifa_anon.csv"
OUT_FULL = ANALYSIS / "ground_truth_full.csv"
OUT_METR = ANALYSIS / "ground_truth_metrics.csv"

# ---- Column Canonicalization ----
# Map common alternate header spellings to canonical names
CANON_MAP = {
    "player": "player",
    "position": "Position",
    "nationality": "Nationality",
    "club": "Club",
    "age": "Age",
    "overall": "Overall",
    "potential": "Potential",
    "finishing": "Finishing",
    "shotpower": "ShotPower",
    "longshots": "LongShots",
    "dribbling": "Dribbling",
    "ballcontrol": "BallControl",
    "shortpassing": "ShortPassing",
    "longpassing": "LongPassing",
    "vision": "Vision",
    "composure": "Composure",
    "acceleration": "Acceleration",
    "sprintspeed": "SprintSpeed",
    "stamina": "Stamina",
    "strength": "Strength",
    "aggression": "Aggression",
    "interceptions": "Interceptions",
    "standingtackle": "StandingTackle",
    "slidingtackle": "SlidingTackle",
    "gkdiving": "GKDiving",
    "gkhandling": "GKHandling",
    "gkkicking": "GKKicking",
    "gkpositioning": "GKPositioning",
    "gkreflexes": "GKReflexes",
}

NUMERIC_COLS = [
    "Overall","Potential","Age",
    "Finishing","ShotPower","LongShots","Dribbling","BallControl",
    "ShortPassing","LongPassing","Vision","Composure",
    "Acceleration","SprintSpeed","Stamina","Strength","Aggression",
    "Interceptions","StandingTackle","SlidingTackle",
    "GKDiving","GKHandling","GKKicking","GKPositioning","GKReflexes"
]

ID_COLS = ["player","Position","Nationality","Club","Age"]

# Helper: normalize headers to canonical names
def canon_columns(df: pd.DataFrame) -> pd.DataFrame:
    ren = {}
    for c in df.columns:
        key = re.sub(r"[^A-Za-z]", "", str(c)).lower()
        if key in CANON_MAP:
            ren[c] = CANON_MAP[key]
    return df.rename(columns=ren)

# Helper: coerce numerics safely
def to_num(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df

# Helper: safe leader picker
def pick_max(df: pd.DataFrame, by: str, subset_desc: str = "", extra_keep: list[str] | None = None):
    if by not in df.columns or df[by].dropna().empty:
        return None
    r = df.loc[df[by].idxmax()].copy()
    keep_cols = ["player","Position",by]
    if extra_keep:
        keep_cols += [k for k in extra_keep if k in df.columns]
    out = {k: r.get(k) for k in keep_cols if k in r.index}
    if subset_desc:
        out["subset"] = subset_desc
    return out

# Position filters
def is_attacker(pos: str) -> bool:
    return bool(re.search(r"\b(ST|CF|LF|RF|LW|RW)\b", str(pos) or "", flags=re.I))

def is_defender(pos: str) -> bool:
    return bool(re.search(r"\b(CB|LB|RB|RWB|LWB)\b", str(pos) or "", flags=re.I))

def is_midfielder(pos: str) -> bool:
    return bool(re.search(r"\b(CM|CAM|CDM|LM|RM)\b", str(pos) or "", flags=re.I))

def is_gk(pos: str) -> bool:
    return bool(re.search(r"\bGK\b", str(pos) or "", flags=re.I))

def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"Input not found: {IN_CSV.resolve()} (run sanitize_players.py first)")

    df = pd.read_csv(IN_CSV, encoding="utf-8", engine="python")
    df = canon_columns(df)
    df = to_num(df, NUMERIC_COLS)

    # ---- FULL TRUTH TABLE ----
    keep = [c for c in (ID_COLS + NUMERIC_COLS) if c in df.columns]
    full = df[keep].copy()
    full.to_csv(OUT_FULL, index=False)

    # ---- KPI METRICS ----
    metrics = []

    # 0) Top Overall (global)
    m = pick_max(df, "Overall", extra_keep=["Overall"])
    if m: metrics.append({"metric":"top_overall", **m})

    # 1) Best Finishing among attackers
    atk = df[df["Position"].apply(is_attacker) if "Position" in df.columns else []]
    if not atk.empty:
        m = pick_max(atk, "Finishing", subset_desc="attackers", extra_keep=["Finishing"])
        if m: metrics.append({"metric":"best_finishing_attacker", **m})

    # 2) Best Passing composite among midfielders (SPass + LPass + Vision)
    mid = df[df["Position"].apply(is_midfielder) if "Position" in df.columns else []]
    if not mid.empty and all(c in mid.columns for c in ["ShortPassing","LongPassing","Vision"]):
        mid = mid.assign(PassingComposite=mid["ShortPassing"] + mid["LongPassing"] + mid["Vision"])
        m = pick_max(mid, "PassingComposite", subset_desc="midfielders",
                     extra_keep=["ShortPassing","LongPassing","Vision","PassingComposite"])
        if m: metrics.append({"metric":"best_passing_midfielder", **m})

    # 3) Best Dribbler (global) (Dribbling + BallControl)
    if all(c in df.columns for c in ["Dribbling","BallControl"]):
        dd = df.assign(DribbleComposite=df["Dribbling"] + df["BallControl"])
        m = pick_max(dd, "DribbleComposite", extra_keep=["Dribbling","BallControl","DribbleComposite"])
        if m: metrics.append({"metric":"best_dribbler", **m})

    # 4) Best Defender among defenders (Interceptions + StandingTackle + SlidingTackle)
    defs = df[df["Position"].apply(is_defender) if "Position" in df.columns else []]
    if not defs.empty and all(c in defs.columns for c in ["Interceptions","StandingTackle","SlidingTackle"]):
        de = defs.assign(DefendComposite=defs["Interceptions"] + defs["StandingTackle"] + defs["SlidingTackle"])
        m = pick_max(de, "DefendComposite", subset_desc="defenders",
                     extra_keep=["Interceptions","StandingTackle","SlidingTackle","DefendComposite"])
        if m: metrics.append({"metric":"best_defender", **m})

    # 5) Best GK (mean of GK skills)
    gks = df[df["Position"].apply(is_gk) if "Position" in df.columns else []]
    gk_cols = ["GKDiving","GKHandling","GKKicking","GKPositioning","GKReflexes"]
    have_gk = [c for c in gk_cols if c in df.columns]
    if not gks.empty and have_gk:
        gks = gks.assign(GKComposite=gks[have_gk].mean(axis=1, skipna=True))
        m = pick_max(gks, "GKComposite", subset_desc="goalkeepers", extra_keep=have_gk + ["GKComposite"])
        if m: metrics.append({"metric":"best_goalkeeper", **m})

    # 6) Pace leader (Acceleration + SprintSpeed)
    if all(c in df.columns for c in ["Acceleration","SprintSpeed"]):
        pa = df.assign(Pace=df["Acceleration"] + df["SprintSpeed"])
        m = pick_max(pa, "Pace", extra_keep=["Acceleration","SprintSpeed","Pace"])
        if m: metrics.append({"metric":"pace_leader", **m})

    # 7) Stamina leader
    if "Stamina" in df.columns:
        m = pick_max(df, "Stamina", extra_keep=["Stamina"])
        if m: metrics.append({"metric":"stamina_leader", **m})

    # Write metrics
    metr_df = pd.DataFrame(metrics)
    metr_df.to_csv(OUT_METR, index=False)

    # ---- Console summary ----
    print(f"✅ Wrote {OUT_FULL} (rows={len(full)}, cols={len(full.columns)})")
    print(f"✅ Wrote {OUT_METR} (rows={len(metr_df)})")
    if not metr_df.empty:
        print("   Sample KPIs:")
        for _, r in metr_df.head(6).iterrows():
            print(f"   - {r['metric']}: {r.get('player')} ({r.get('subset','all')})")

if __name__ == "__main__":
    main()
