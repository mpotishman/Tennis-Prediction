import contextlib
import io
import json
import sys
import pandas as pd
from predict import DATA_PATH
from simulate import get_match_probability
from train import training

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

    df = pd.read_csv(DATA_PATH)

    with contextlib.redirect_stdout(io.StringIO()):
        model, scaler, features = training(df, features_selected, model_type)

    prob = get_match_probability(
        player1, player2, 4, model, scaler, df, features, None, {})
    win_pct = round(prob * 100, 1)
    
    if win_pct > 50:
        winner, loser = player1, player2
    else:
        winner, loser = player2, player1
        win_pct = round(100 - win_pct, 1)

    print(json.dumps(
        {"winner": winner, "loser": loser, "winPct": win_pct, "modelLabel": MODEL_LABELS.get(model_type, model_type),
         "features": features}))


if __name__ == "__main__":
    main()
