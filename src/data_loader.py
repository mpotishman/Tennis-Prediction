import os
import pandas as pd
from features import create_two_rows
from features import add_raw_data
from train import training

# ============================================================
# LOAD
# ============================================================
directory_path = "data/raw"
all_data = []
expected_total_rows = 0

for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        df = pd.read_csv(os.path.join(directory_path, filename))
        print(f"{filename}: {len(df)} rows")
        expected_total_rows += len(df)
        all_data.append(df)

all_data = pd.concat(all_data).reset_index(drop=True)

all_data["tourney_date"] = pd.to_datetime(all_data["tourney_date"], format="%Y%m%d")
all_data["match_num"] = pd.to_numeric(all_data["match_num"], errors="coerce")

# ============================================================
# SORT (CRITICAL FOR ALL SEQUENTIAL FEATURES)
# ============================================================
all_data = all_data.sort_values(
    ["tourney_date", "tourney_id", "match_num"]
).reset_index(drop=True)

print(f"\nExpected rows: {expected_total_rows} | Actual: {len(all_data)}")
print(f"Date range: {all_data['tourney_date'].min().date()} to {all_data['tourney_date'].max().date()}")

# ============================================================
# FEATURE ENGINEERING (SEQUENTIAL FEATURES FIRST)
# ============================================================
original_columns = set(all_data.columns)
print(f"\nColumns before: {len(all_data.columns)}")

all_data = add_raw_data.add_raw_data_to_csv(all_data)

after_features = set(all_data.columns)
print(f"Columns after features: {len(all_data.columns)} | New: {sorted(after_features - original_columns)}")


sinner = all_data[(all_data["winner_name"] == "Jannik Sinner") | (all_data["winner_name"] == "Novak Djokovic")]
print(sinner[sinner["loser_name"] == "Novak Djokovic"][["winner_name", "loser_name", "player_h2h", "tourney_date"]].head(10).to_string())

# ============================================================
# TWO ROW TRANSFORMATION (LABEL EXPANSION ONLY)
# ============================================================
all_data = create_two_rows.create_two_rows(all_data)

print(f"Columns after reshape: {len(all_data.columns)}")
print(f"Rows after reshape: {len(all_data)} (expected {expected_total_rows * 2})")

# ============================================================
# FINAL SHUFFLE (ONLY ONCE)
# ============================================================
all_data = all_data.sample(frac=1, random_state=42).reset_index(drop=True)

# ============================================================
# SANITY CHECKS
# ============================================================
print(all_data["surface"].unique())

# ============================================================
# SAVE
# ============================================================
output_path = "data/processed/combined.csv"
all_data.to_csv(output_path, index=False)

print(f"\nSaved to {output_path} — shape: {all_data.shape}")

print(all_data[["player_elo", "opponent_elo"]].describe())
print(all_data.groupby("result")["elo_gap"].mean())


print(training(all_data))