# One-time data processing script. Reads all raw ATP match CSVs from data/raw/,
# runs the full feature engineering pipeline, and saves the result to data/processed/combined.csv.
# Run this script whenever new raw data is added.

import os
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from features import create_two_rows
from features import add_raw_data

# ============================================================
# LOAD
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parents[2]
directory_path = PROJECT_ROOT / "data" / "raw"
all_data = []
expected_total_rows = 0

for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        df = pd.read_csv(os.path.join(directory_path, filename))
        expected_total_rows += len(df)
        all_data.append(df)

all_data = pd.concat(all_data).reset_index(drop=True)
all_data["tourney_date"] = pd.to_datetime(all_data["tourney_date"], format="%Y%m%d")
all_data["match_num"] = pd.to_numeric(all_data["match_num"], errors="coerce")

serve_stat_columns = [
    "w_svpt", "w_1stIn", "w_1stWon", "w_2ndWon", "w_SvGms", "w_bpSaved", "w_bpFaced",
    "l_svpt", "l_1stIn", "l_1stWon", "l_2ndWon", "l_SvGms", "l_bpSaved", "l_bpFaced",
]
for column in serve_stat_columns:
    all_data[column] = pd.to_numeric(all_data[column], errors="coerce")

# ============================================================
# SORT — order is critical for all sequential features
# ============================================================
all_data = all_data.sort_values(
    ["tourney_date", "tourney_id", "match_num"]
).reset_index(drop=True)

print(f"Loaded {len(all_data)} rows | date range: {all_data['tourney_date'].min().date()} to {all_data['tourney_date'].max().date()}")

# ============================================================
# FEATURE ENGINEERING (sequential features must run in order)
# ============================================================
all_data = add_raw_data.add_raw_data_to_csv(all_data)
print(f"Features added: {len(all_data.columns)} columns")

# ============================================================
# TWO-ROW TRANSFORMATION
# ============================================================
all_data = create_two_rows.create_two_rows(all_data)
print(f"Reshaped to {len(all_data)} rows (expected {expected_total_rows * 2})")

# ============================================================
# SAVE
# ============================================================
output_path = PROJECT_ROOT / "data" / "processed" / "combined.csv"
all_data.to_csv(output_path, index=False)
print(f"Saved to {output_path} — shape: {all_data.shape}")
