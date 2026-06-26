# Entry point called by the Next.js /api/simulation route.
# Receives model type, selected features, and tournament name as CLI args,
# trains the model on pre-tournament data, runs the bracket simulation,
# and prints a JSON result to stdout.

import contextlib
import io
import json
import random
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import DATA_PATH
from core.tournament_mapping import TOURNAMENT_MATCHUP_MAPS, TOURNAMENT_METADATA
from modeling.train import training
from simulation.simulate import run_multiple_tournaments

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
    tournament_selected = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None

    metadata = TOURNAMENT_METADATA.get(tournament_selected)
    if metadata is None:
        raise ValueError(f"Unknown tournament: {tournament_selected}")
    if not metadata.get("start_date"):
        raise ValueError(f"{tournament_selected} does not have a playable start date.")

    tournament_start_date = metadata["start_date"]

    with contextlib.redirect_stdout(io.StringIO()):
        model, scaler, features = training(df, tournament_start_date, model_type, features_selected)
        champion_counts, bracket_counts, bad_matchups = run_multiple_tournaments(
            TOURNAMENT_MATCHUP_MAPS[tournament_selected], model, scaler, df, features, SIMULATION_COUNT, tournament_selected
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

    bad_matchups = [
        {
            "tournament": tournament,
            "round": round_num,
            "player": player,
            "opponent": opponent,
            "player_missing": player_missing,
            "opponent_missing": opponent_missing,
            "fallback_probability": round(prob * 100, 1),
        }
        for tournament, round_num, player, opponent, player_missing, opponent_missing, prob
        in sorted(bad_matchups)
    ]

    print(json.dumps({
        "winner":            winner,
        "winPct":            win_pct,
        "modelLabel":        MODEL_LABELS.get(model_type, model_type),
        "features":          features,
        "results":           dict(champion_counts.most_common()),
        "predicted_bracket": predicted_bracket,
        "bad_matchups":      bad_matchups,
        "tournament":        tournament_selected,
    }))


if __name__ == "__main__":
    main()
