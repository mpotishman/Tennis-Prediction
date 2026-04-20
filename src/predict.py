from pathlib import Path

import pandas as pd

from simulate import get_bracket, run_first_round_simulation
from train import training


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "combined.csv"


def main():
    df = pd.read_csv(DATA_PATH)
    bracket = get_bracket(df)
    model, scaler, features = training(df)
    run_first_round_simulation(bracket, model, scaler, df, features, n=10000)


if __name__ == "__main__":
    main()
