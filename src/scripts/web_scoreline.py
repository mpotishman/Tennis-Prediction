# Entry point called by the Next.js /api/scoreline route.
# Receives two player names, model type, and selected features as CLI args,
# trains the model, derives each player's serve-point win probability,
# calibrates it so the engine's win % matches the model's win %, runs the
# scoreline simulation, and prints a JSON result to stdout.

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
from simulation.score_simulator import (
    calibrate_p_serve,
    run_multiple_score_predictions,
)

DEFAULT_P_SERVE = 0.62  # fallback if a player has no serve history

# The exact features build_player_lookup.build_feature_row can produce for a
# hypothetical matchup. The model must be trained on these so the win-prob call
# doesn't hit a column mismatch.
CALIBRATION_FEATURES = [
    "elo_gap", "tourney_k_value", "best_of", "surface", "tourney_level", "round",
    "winrate_gap", "surface_elo_gap", "rank_gap", "rank_points_gap",
    "h2h_gap", "days_rest_gap", "hold_rate_gap",
    "first_srv_win_rate_gap", "second_srv_win_rate_gap",
]


def latest_p_serve(df, player_name):
    """Return the player's most recent rolling p_serve, or a default if unknown."""
    rows = df[df["player_name"] == player_name].sort_values("tourney_date")
    if len(rows) == 0:
        return DEFAULT_P_SERVE
    value = rows["player_p_serve"].iloc[-1]
    return float(value) if pd.notna(value) else DEFAULT_P_SERVE


def main():
    player1 = sys.argv[1]
    player2 = sys.argv[2]
    model_type = sys.argv[3] if len(sys.argv) > 3 else "xgboost"
    features_selected = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None

    df = pd.read_csv(DATA_PATH)

    # each player's raw serve-point win probability (controls the score shape)
    raw_p1 = latest_p_serve(df, player1)
    raw_p2 = latest_p_serve(df, player2)

    # Try to anchor the engine's win % to the selected model. If the model call
    # fails (e.g. no explicit feature list passed), fall back to raw p_serve.
    target_win_pct = None
    p1_serve, p2_serve = raw_p1, raw_p2
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            model, scaler, features = training(
                df, None, model_type, features_selected or CALIBRATION_FEATURES
            )
        prob = get_match_probability(
            player1, player2, 4, model, scaler, df, features, None, {},
        )
        target_win_pct = prob * 100
        p1_serve, p2_serve = calibrate_p_serve(raw_p1, raw_p2, target_win_pct)
    except Exception as exc:
        print(f"calibration skipped: {exc}", file=sys.stderr)

    # 4. simulate the scoreline distribution
    match = {
        "player_name": player1,
        "opponent_name": player2,
        "player_p_serve": p1_serve,
        "opponent_p_serve": p2_serve,
    }
    result = run_multiple_score_predictions(match)

    result["player_1"] = player1
    result["player_2"] = player2
    result["model_win_pct"] = round(target_win_pct, 1) if target_win_pct is not None else None

    print(json.dumps(result))


if __name__ == "__main__":
    main()
