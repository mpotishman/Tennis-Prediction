import os
import pandas as pd
from features import create_two_rows, add_elo_to_csv
from train import training

# ============================================================
# LOAD
# ============================================================
directory_path = "data/raw"
all_data = []
expected_total_rows = 0

for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        df = pd.read_csv(directory_path + "/" + filename)
        print(f"{filename}: {len(df)} rows")
        expected_total_rows += len(df)
        all_data.append(df)

all_data = pd.concat(all_data).reset_index(drop=True)
all_data["tourney_date"] = pd.to_datetime(all_data["tourney_date"], format="%Y%m%d")
all_data["match_num"] = pd.to_numeric(all_data["match_num"], errors="coerce")

all_data = all_data.sort_values(
    ["tourney_date", "tourney_id", "match_num"]
).reset_index(drop=True)


print(f"\nExpected rows: {expected_total_rows} | Actual: {len(all_data)}")
print(f"Date range: {all_data['tourney_date'].min().date()} to {all_data['tourney_date'].max().date()}")

# ============================================================
# FEATURE ENGINEERING
# ============================================================
original_columns = set(all_data.columns)
print(f"\nColumns before: {len(all_data.columns)}")

all_data = add_elo_to_csv(all_data)
after_elo = set(all_data.columns)
print(f"Columns after ELO: {len(all_data.columns)} | New: {sorted(after_elo - original_columns)}")

all_data = create_two_rows(all_data)
all_data = all_data.sample(frac=1, random_state=42).reset_index(drop=True)
print(f"Columns after reshape: {len(all_data.columns)}")
print(f"Rows after reshape: {len(all_data)} (expected {expected_total_rows * 2})")

# shuffle the data
all_data = all_data.sample(frac=1, random_state=42).reset_index(drop=True)

# ============================================================
# UNIQUE VALUE CHECKS — uncomment to inspect
# ============================================================
# print(all_data["tourney_level"].unique())
# print(all_data["surface"].unique())
# print(all_data["round"].unique())
# print(all_data["player_hand"].unique())
# print(all_data["opponent_hand"].unique())

# ============================================================
# SPOT CHECKS — uncomment to inspect specific players
# ============================================================
# print(all_data[all_data["player_name"] == "Carlos Alcaraz"].tail(3))
# print(all_data[all_data["player_name"] == "Jannik Sinner"].tail(3))

# ============================================================
# SAVE
# ============================================================
output_path = "data/processed/combined.csv"
all_data.to_csv(output_path, index=False)
print(df[df["tourney_level"] == "G"]["tourney_name"].unique())
print(df[df["tourney_name"] == "US Open"]["tourney_date"].unique())
print(f"\nSaved to {output_path} — shape: {all_data.shape}")


print(training(all_data))