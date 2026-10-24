# Run every simple baseline against the same future matches used by the full model.

import sys
from pathlib import Path

import pandas as pd

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.config import DATA_PATH, PROJECT_ROOT
from evaluation.baselines import (
    coin_flip_probabilities,
    elo_probabilities,
    fit_ranking_logistic,
    higher_ranked_probabilities,
    ranking_logistic_probabilities,
)
from evaluation.backtest_runner import (
    add_match_ids,
    load_backtest_data,
    predict_matches_for_split,
    train_model_for_split,
)
from evaluation.metrics import calculate_classification_metrics
from evaluation.splits import validate_time_split, walk_forward_year_splits


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "backtests" / "baselines"

METHOD_LABELS = {
    "coin_flip": "50/50",
    "higher_ranked": "Higher-ranked player",
    "ranking_logistic": "Ranking logistic regression",
    "standard_elo": "Standard Elo",
    "surface_elo": "Surface Elo",
    "full_xgboost": "Full XGBoost",
}

PREDICTION_COLUMNS = [
    "method",
    "test_year",
    "date",
    "tournament",
    "player_1",
    "player_2",
    "predicted_win_probability",
    "predicted_winner",
    "actual_winner",
    "actual_result",
    "correct",
]


def predictions_from_row_probabilities(split, row_probabilities, method):
    # Reuse the match grouping logic so every method is judged on one row per match.
    class IdentityScaler:
        def transform(self, values):
            return values.to_numpy()

    class SuppliedProbabilityModel:
        def predict_proba(self, values):
            probabilities = values[:, 0]
            return pd.DataFrame({
                0: 1 - probabilities,
                1: probabilities,
            }).to_numpy()

    probability_frame = split["test_df"].copy()
    probability_frame["_baseline_probability"] = row_probabilities
    baseline_split = {
        **split,
        "test_df": probability_frame,
    }

    predictions = predict_matches_for_split(
        baseline_split,
        SuppliedProbabilityModel(),
        IdentityScaler(),
        ["_baseline_probability"],
    )
    predictions.insert(0, "method", method)
    return predictions


def baseline_probabilities_for_split(split):
    # Train only the one learned baseline; the other methods are fixed rules.
    train_df = split["train_df"]
    test_df = split["test_df"]

    ranking_model, ranking_scaler, ranking_fill_values = fit_ranking_logistic(
        train_df
    )

    return {
        "coin_flip": coin_flip_probabilities(test_df),
        "higher_ranked": higher_ranked_probabilities(test_df),
        "ranking_logistic": ranking_logistic_probabilities(
            test_df,
            ranking_model,
            ranking_scaler,
            ranking_fill_values,
        ),
        "standard_elo": elo_probabilities(test_df, "elo_gap"),
        "surface_elo": elo_probabilities(test_df, "surface_elo_gap"),
    }


def full_xgboost_predictions_for_split(split):
    # Train the complete model on past matches and predict the held-out year.
    model, scaler, features = train_model_for_split(
        split,
        model_type="xgboost",
        features=None,
    )

    predictions = predict_matches_for_split(
        split,
        model,
        scaler,
        features,
    )
    predictions.insert(0, "method", "full_xgboost")
    return predictions


def build_overall_summary(predictions):
    # Score the pooled match predictions rather than averaging yearly percentages.
    rows = []

    for method, method_predictions in predictions.groupby("method", sort=False):
        scored_predictions = method_predictions
        probability_metrics_available = method != "higher_ranked"

        if method == "higher_ranked":
            scored_predictions = method_predictions[
                method_predictions["predicted_win_probability"] != 0.5
            ]

        metrics = calculate_classification_metrics(
            scored_predictions["actual_result"].tolist(),
            scored_predictions["predicted_win_probability"].tolist(),
        )

        if method == "coin_flip":
            metrics["accuracy"] = 0.5

        rows.append({
            "method": method,
            "label": METHOD_LABELS[method],
            "num_matches": len(scored_predictions),
            "coverage": len(scored_predictions) / len(method_predictions),
            "accuracy": metrics["accuracy"],
            "log_loss": (
                metrics["log_loss"] if probability_metrics_available else None
            ),
            "brier_score": (
                metrics["brier_score"] if probability_metrics_available else None
            ),
        })

    return pd.DataFrame(rows)


def run_baseline_backtest(
    start_year=2009,
    end_year=2025,
    data_path=DATA_PATH,
    output_dir=DEFAULT_OUTPUT_DIR,
):
    # Generate each baseline on identical chronological folds.
    df = add_match_ids(load_backtest_data(data_path))
    splits = walk_forward_year_splits(df, start_year, end_year)
    prediction_frames = []

    for split in splits:
        validate_time_split(split)
        print(f"Running baseline fold for {split['test_year']}...")

        for method, probabilities in baseline_probabilities_for_split(split).items():
            prediction_frames.append(
                predictions_from_row_probabilities(
                    split,
                    probabilities,
                    method,
                )
            )

        print(f"Running full XGBoost fold for {split['test_year']}...")
        prediction_frames.append(
            full_xgboost_predictions_for_split(split)
        )

    if not prediction_frames:
        raise ValueError("No baseline folds were created. Check the requested years.")

    predictions = pd.concat(prediction_frames, ignore_index=True)
    summary = build_overall_summary(predictions)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    predictions_path = output_dir / "predictions.csv"
    summary_path = output_dir / "overall_metrics.csv"

    predictions[PREDICTION_COLUMNS].to_csv(predictions_path, index=False)
    summary.to_csv(summary_path, index=False)

    return {
        "predictions": predictions,
        "summary": summary,
        "predictions_path": predictions_path,
        "summary_path": summary_path,
    }


if __name__ == "__main__":
    run_baseline_backtest()
