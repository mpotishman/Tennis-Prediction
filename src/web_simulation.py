import contextlib
import io
import json
import random
import sys

import pandas as pd

from predict import DATA_PATH, ao2026_r1_ordered_full_names
from simulate import run_multiple_tournaments
from train import training

SIMULATION_COUNT = 1000
RANDOM_SEED = 42

MODEL_LABELS = {
    "xgboost": "XGBoost",
    "random_forest": "Random Forest",
    "logistic": "Logistic Regression",
}


def main():
    random.seed(RANDOM_SEED)
    df = pd.read_csv(DATA_PATH)

    model_type = sys.argv[1] if len(sys.argv) > 1 else "xgboost"
    features_selected = json.loads(sys.argv[2]) if len(sys.argv) > 2 else None

    with contextlib.redirect_stdout(io.StringIO()):
        model, scaler, features = training(df, features_selected, model_type)
        champion_counts, bracket_counts = run_multiple_tournaments(
            ao2026_r1_ordered_full_names, model, scaler, df, features, SIMULATION_COUNT,
        )

    winner, count = champion_counts.most_common(1)[0]
    win_pct = round((count / SIMULATION_COUNT) * 100, 1)

    predicted_bracket = {
        round_num: {
            match_pos: {
                player: round(c / SIMULATION_COUNT * 100, 1)
                for player, c in counter.most_common()
            }
            for match_pos, counter in matches.items()
        }
        for round_num, matches in bracket_counts.items()
    }

    print(json.dumps({
        "winner":            winner,
        "winPct":            win_pct,
        "modelLabel":        MODEL_LABELS.get(model_type, model_type),
        "features":          features,
        "results":           dict(champion_counts.most_common()),
        "predicted_bracket": predicted_bracket,
    }))


if __name__ == "__main__":
    main()
