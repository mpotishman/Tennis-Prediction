import sys
from pathlib import Path

import pandas as pd

SRC_ROOT = Path(__file__).resolve().parents[1]
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.config import DATA_PATH, PROJECT_ROOT
from evaluation.metrics import calculate_classification_metrics
from evaluation.splits import walk_forward_year_splits, validate_time_split
from modeling.feature_sets import DEFAULT_FEATURE_SET, feature_columns_for, selected_feature_set_names
from modeling.train import prepare_model_dataframe, training


DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "outputs" / "backtests"

FEATURE_SET_ORDER = [
    "full",
    "elo_only",
    "surface_elo_only",
    "ranking_only",
    "elo_surface",
    "form_only",
    "serve_only",
]

PREDICTION_OUTPUT_COLUMNS = [
    "feature_set",
    "model_type",
    "test_year",
    "date",
    "tournament",
    "player_1",
    "player_2",
    "predicted_win_probability",
    "predicted_winner",
    "actual_winner",
    "correct",
]


def load_backtest_data(data_path=DATA_PATH):
    """Load the processed two-row-per-match training data."""
    df = pd.read_csv(data_path)
    df["tourney_date"] = pd.to_datetime(df["tourney_date"])
    return df


def add_match_ids(df):
    """Add an id that connects the two rows belonging to the same real match."""
    df = df.copy().reset_index(drop=True)
    df["match_id"] = df.index // 2
    df["row_in_match"] = df.index % 2
    return df


def train_model_for_split(split, model_type="xgboost", features=None):
    """Train one fresh model using only this split's historical training rows."""
    train_df = split["train_df"]
    model, scaler, model_features = training(
        train_df,
        tournament_start_date=None,
        model_type=model_type,
        features=features,
    )
    return model, scaler, model_features


def _validate_feature_columns(df, features, feature_set):
    if features is None:
        return

    missing = [feature for feature in features if feature not in df.columns]
    if missing:
        raise ValueError(
            f"Feature set '{feature_set}' contains columns that are not in the data: {missing}"
        )


def _feature_matrix_for_prediction(test_df, scaler, features):
    model_df = prepare_model_dataframe(test_df)
    X_test = model_df[features].copy()

    fill_values = getattr(scaler, "feature_fill_values", None)
    if fill_values is not None:
        X_test = X_test.fillna(fill_values)
    else:
        X_test = X_test.fillna(X_test.median(numeric_only=True).fillna(0))

    return X_test.fillna(0)


def _validate_match_group(match_id, match_rows):
    if len(match_rows) != 2:
        raise ValueError(
            f"Expected exactly 2 rows for match_id={match_id}, found {len(match_rows)}."
        )

    results = set(match_rows["result"].tolist())
    if results != {0, 1}:
        raise ValueError(
            f"Expected one winner row and one loser row for match_id={match_id}."
        )


def _prediction_row_from_match(test_year, match_id, match_rows):
    _validate_match_group(match_id, match_rows)

    players = sorted(match_rows["player_name"].tolist())
    player_1, player_2 = players[0], players[1]

    player_1_row = match_rows[match_rows["player_name"] == player_1].iloc[0]
    actual_winner = match_rows.loc[
        match_rows["result"] == 1, "player_name"
    ].iloc[0]
    predicted_probability = float(
        player_1_row["predicted_win_probability"]
    )

    predicted_winner = (
        player_1 if predicted_probability >= 0.5 else player_2
    )

    return {
        "test_year": test_year,
        "match_id": match_id,
        "date": pd.Timestamp(
            player_1_row["tourney_date"]
        ).date().isoformat(),
        "tournament": player_1_row["tourney_name"],
        "player_1": player_1,
        "player_2": player_2,
        "predicted_win_probability": predicted_probability,
        "predicted_winner": predicted_winner,
        "actual_winner": actual_winner,
        "actual_result": int(player_1_row["result"]),
        "correct": predicted_winner == actual_winner,
    }


def predict_matches_for_split(split, model, scaler, features):
    """Predict one held-out year and return one output row per real match."""
    test_df = split["test_df"].copy()
    X_test = _feature_matrix_for_prediction(
        test_df,
        scaler,
        features,
    )

    test_df["predicted_win_probability"] = model.predict_proba(
        scaler.transform(X_test)
    )[:, 1]

    prediction_rows = []
    for match_id, match_rows in test_df.groupby(
        "match_id",
        sort=True,
    ):
        prediction_rows.append(
            _prediction_row_from_match(
                split["test_year"],
                match_id,
                match_rows,
            )
        )

    return pd.DataFrame(prediction_rows)


def run_backtest(
    start_year=2009,
    end_year=2025,
    model_type="xgboost",
    feature_set=DEFAULT_FEATURE_SET,
    features=None,
    data_path=DATA_PATH,
    output_dir=DEFAULT_OUTPUT_DIR,
):
    """
    Run the walk-forward backtest.

    This function coordinates the whole flow:
    load data -> create splits -> train yearly models -> predict -> score -> save.
    """
    df = load_backtest_data(data_path)
    df = add_match_ids(df)

    splits = walk_forward_year_splits(
        df,
        start_year,
        end_year,
    )

    feature_set_names = selected_feature_set_names(feature_set)

    feature_set_names = sorted(
        feature_set_names,
        key=lambda name: (
            FEATURE_SET_ORDER.index(name)
            if name in FEATURE_SET_ORDER
            else len(FEATURE_SET_ORDER)
        ),
    )

    all_prediction_frames = []
    summary_rows = []

    for feature_set_name in feature_set_names:
        selected_features = features
        if selected_features is None:
            selected_features = feature_columns_for(
                feature_set_name
            )

        _validate_feature_columns(
            df,
            selected_features,
            feature_set_name,
        )

        print(f"\nRunning feature set: {feature_set_name}")

        for split in splits:
            validate_time_split(split)

            test_year = split["test_year"]
            print(f"Running backtest fold for {test_year}...")

            model, scaler, model_features = train_model_for_split(
                split,
                model_type=model_type,
                features=selected_features,
            )

            predictions_df = predict_matches_for_split(
                split,
                model,
                scaler,
                model_features,
            )

            predictions_df.insert(
                0,
                "model_type",
                model_type,
            )
            predictions_df.insert(
                0,
                "feature_set",
                feature_set_name,
            )

            metrics = calculate_classification_metrics(
                predictions_df["actual_result"].tolist(),
                predictions_df[
                    "predicted_win_probability"
                ].tolist(),
            )

            all_prediction_frames.append(predictions_df)

            summary_rows.append({
                "feature_set": feature_set_name,
                "model_type": model_type,
                "test_year": test_year,
                "num_matches": len(predictions_df),
                **metrics,
            })

            print(
                f"{feature_set_name} {test_year}: "
                f"{len(predictions_df)} matches | "
                f"accuracy={metrics['accuracy']:.3f} | "
                f"log_loss={metrics['log_loss']:.3f} | "
                f"brier={metrics['brier_score']:.3f}"
            )

    if not all_prediction_frames:
        raise ValueError(
            "No backtest folds were created. "
            "Check the requested year range."
        )

    output_dir = Path(output_dir)
    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    predictions_df = pd.concat(
        all_prediction_frames,
        ignore_index=True,
    )
    summary_df = pd.DataFrame(summary_rows)

    predictions_path = output_dir / "predictions.csv"
    summary_path = output_dir / "summary_metrics.csv"

    predictions_df[
        PREDICTION_OUTPUT_COLUMNS
    ].to_csv(
        predictions_path,
        index=False,
    )

    summary_df.to_csv(
        summary_path,
        index=False,
    )

    return {
        "predictions": predictions_df,
        "summary": summary_df,
        "predictions_path": predictions_path,
        "summary_path": summary_path,
    }
    
if __name__ == "__main__":
    run_backtest(
        start_year=2009,
        end_year=2025,
        feature_set="all",
        output_dir=PROJECT_ROOT / "outputs" / "backtests" / "feature_sets",
    )