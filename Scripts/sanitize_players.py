# scripts/sanitize_players.py
# Reads the first CSV in your Dataset folder, anonymizes names robustly (A..Z, AA.., AAA..),
# and writes to data/fifa_anon.csv

import pandas as pd
from pathlib import Path
import string

# Absolute path to your raw dataset directory (READ-ONLY)
RAW_DIR = Path(r"C:/Users/Singh/OneDrive/Desktop/Research Work/Task_08_Bias_Detection/Dataset")

# Project-local paths (WRITE here)
DATA = Path("data"); DATA.mkdir(exist_ok=True, parents=True)
OUT_CSV = DATA / "fifa_anon.csv"

# FIFA-style columns to keep if present
KEEP_COLS = [
    "Name","Age","Nationality","Overall","Potential","Club","Position",
    "Finishing","ShotPower","LongShots","Dribbling","BallControl",
    "ShortPassing","LongPassing","Vision","Composure",
    "Acceleration","SprintSpeed","Stamina","Strength","Aggression",
    "Interceptions","StandingTackle","SlidingTackle",
    "GKDiving","GKHandling","GKKicking","GKPositioning","GKReflexes"
]

def find_first_csv(raw_dir: Path) -> Path:
    candidates = sorted(list(raw_dir.glob("*.csv")))
    if not candidates:
        raise FileNotFoundError(f"No CSV found in: {raw_dir}")
    return candidates[0]

def int_to_letters(idx: int) -> str:
    """
    0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA, 27 -> AB, ..., 701 -> ZZ,
    702 -> AAA, etc. Works for arbitrarily large idx.
    """
    letters = string.ascii_uppercase
    s = []
    n = idx
    while True:
        n, rem = divmod(n, 26)
        s.append(letters[rem])
        if n == 0:
            break
        n -= 1  # Excel-style base-26 (no zero digit)
    return "".join(reversed(s))

def main():
    in_csv = find_first_csv(RAW_DIR)
    df = pd.read_csv(in_csv, encoding="utf-8", engine="python")

    # Keep only expected columns that actually exist
    cols = [c for c in KEEP_COLS if c in df.columns]
    if not cols:
        raise RuntimeError(
            f"None of the expected columns were found.\n"
            f"CSV columns: {list(df.columns)[:25]} ..."
        )
    df = df[cols].copy()

    # Sort by Overall (if available) so early labels are top-rated players
    if "Overall" in df.columns:
        df = df.sort_values("Overall", ascending=False, na_position="last").reset_index(drop=True)

    # Robust anonymization for any number of rows
    n = len(df)
    anon_labels = [f"Player {int_to_letters(i)}" for i in range(n)]
    df.insert(0, "player", anon_labels)

    df.to_csv(OUT_CSV, index=False)
    print(f"✅ Anonymized -> {OUT_CSV}  ({n} rows, {len(df.columns)} columns)")
    if "Overall" in df.columns:
        print(f"   Top row preview: {df.iloc[0][['player','Position','Overall']].to_dict()}")

if __name__ == "__main__":
    main()
