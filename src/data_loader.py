import os
import pandas as pd

directory_path = "data/raw"

all_data = []
expected_total_rows = 0
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):

        dataframe = pd.read_csv(directory_path + "/" + filename)
        print(f"{filename} has {len(dataframe)} rows")
        expected_total_rows += len(dataframe)
        
        all_data.append(dataframe)
        

    
all_data = pd.concat(all_data)
all_data = all_data.sort_values("tourney_date")
all_data.to_csv("data/processed/combined.csv", index=False)


print(f'Total rows expected for combined csv is {expected_total_rows}, actual number of rows is {len(all_data)}')