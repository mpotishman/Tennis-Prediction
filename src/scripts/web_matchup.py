# Entry point called by the Next.js /api/matchup route.
# Receives two player names, model type, selected features, and year ranges as CLI args,
# trains the model on all available data, then prints the head-to-head win probability
# as a JSON result to stdout.

import contextlib
import io
import json
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import DATA_PATH
from modeling.train import training
from simulation.simulate import get_match_probability

MODEL_LABELS = {
    "xgboost": "XGBoost",
    "random_forest": "Random Forest",
    "logistic": "Logistic Regression",
}


def main():
    player1 = sys.argv[1]
    player2 = sys.argv[2]
    model_type = sys.argv[3] if len(sys.argv) > 3 else "xgboost"
    features_selected = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
    p1year_end = sys.argv[5] if len(sys.argv) > 5 else 2026
    p2year_end = sys.argv[6] if len(sys.argv) > 6 else 2026

    df = pd.read_csv(DATA_PATH)

    with contextlib.redirect_stdout(io.StringIO()):
        model, scaler, features = training(df, None, model_type, features_selected)

    prob = get_match_probability(
        player1, player2, 4, model, scaler, df, features, None, {},
        p1year_end, p2year_end,
    )
    win_pct = round(prob * 100, 1)

    print(json.dumps({
        "player_1":      player1,
        "player_2":      player2,
        "player_1_year": p1year_end,
        "player_2_year": p2year_end,
        "player_1_prob": win_pct,
        "player_2_prob": round(100 - win_pct, 1),
        "modelLabel":    MODEL_LABELS.get(model_type, model_type),
        "features":      features,
    }))


if __name__ == "__main__":
    main()
