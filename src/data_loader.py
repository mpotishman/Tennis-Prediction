import os
import pandas as pd
from features import create_two_rows, add_elo_to_csv


directory_path = "data/raw"

all_data = []
expected_total_rows = 0
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):

        dataframe = pd.read_csv(directory_path + "/" + filename)
        print(f"{filename} has {len(dataframe)} rows")
        expected_total_rows += len(dataframe)

        all_data.append(dataframe)


all_data = pd.concat(all_data).reset_index(drop=True)
all_data = all_data.sort_values("tourney_date")
print(all_data.iloc[0])

print(
    f'Total rows expected for combined csv is {expected_total_rows}, actual number of rows is {len(all_data)}')

all_data["tourney_date"] = pd.to_datetime(
    all_data["tourney_date"], format="%Y%m%d")
print(f"the current number of headers is {len(all_data.columns)}")
all_data = add_elo_to_csv(all_data)
print(
    f"After adding elos and probabilities, the current number of headers is {len(all_data.columns)}")
print(all_data[all_data["winner_name"] == "Nicolas Jarry"].iloc[0]["player_elo"])
all_data = create_two_rows(all_data)
print(
    f"After adding 2 rows per match , the current number of headers is {len(all_data.columns)}")
all_data.to_csv("data/processed/combined.csv", index=False)


print(all_data["tourney_level"].unique())
