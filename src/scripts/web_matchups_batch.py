"""Predict multiple matchups after loading or training the model once."""

import contextlib
import hashlib
import io
import json
import sys
from pathlib import Path

import joblib
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.config import DATA_PATH
from features import build_player_lookup
from modeling.train import training
from simulation.simulate import get_match_probability


ARTIFACT_DIRECTORY = Path(DATA_PATH).parent / "model_artifacts"


def _artifact_path(model_type, features):
    signature = json.dumps(
        {"model_type": model_type, "features": features},
        sort_keys=True,
    )
    digest = hashlib.sha256(signature.encode("utf-8")).hexdigest()[:12]
    return ARTIFACT_DIRECTORY / f"matchup_{model_type}_{digest}.joblib"


def _dataset_signature():
    data_file = Path(DATA_PATH)
    stat = data_file.stat()
    return {"size": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def load_or_train_model(df, model_type, features):
    """Reuse a saved model unless the dataset or requested features changed."""
    artifact_path = _artifact_path(model_type, features)
    dataset_signature = _dataset_signature()

    if artifact_path.exists():
        artifact = joblib.load(artifact_path)
        if artifact.get("dataset_signature") == dataset_signature:
            return (
                artifact["model"],
                artifact["scaler"],
                artifact["features"],
                True,
            )

    with contextlib.redirect_stdout(io.StringIO()):
        model, scaler, model_features = training(
            df,
            None,
            model_type,
            features,
        )

    ARTIFACT_DIRECTORY.mkdir(parents=True, exist_ok=True)
    temporary_path = artifact_path.with_suffix(".joblib.part")
    joblib.dump(
        {
            "dataset_signature": dataset_signature,
            "model": model,
            "scaler": scaler,
            "features": model_features,
        },
        temporary_path,
    )
    temporary_path.replace(artifact_path)

    return model, scaler, model_features, False


def main():
    matchups = json.loads(sys.argv[1])
    model_type = sys.argv[2] if len(sys.argv) > 2 else "xgboost"
    features = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    year_end = int(sys.argv[4]) if len(sys.argv) > 4 else 2026

    df = pd.read_csv(DATA_PATH)
    model, scaler, model_features, used_cached_model = load_or_train_model(
        df,
        model_type,
        features,
    )

    # Every matchup uses the same latest snapshot, so build it once.
    player_lookup = build_player_lookup.build_latest_player_lookup(
        df,
        cutoff=f"{year_end}-12-31",
    )
    probability_cache = {}
    predictions = []

    for matchup in matchups:
        player1 = matchup["player1"]
        player2 = matchup["player2"]
        probability = get_match_probability(
            player1,
            player2,
            4,
            model,
            scaler,
            df,
            model_features,
            player_lookup,
            probability_cache,
            year_end,
            year_end,
        )
        player1_probability = round(probability * 100, 1)

        predictions.append(
            {
                "matchId": str(matchup["matchId"]),
                "player1": player1,
                "player2": player2,
                "player1Probability": player1_probability,
                "player2Probability": round(100 - player1_probability, 1),
            }
        )

    print(
        json.dumps(
            {
                "predictions": predictions,
                "modelType": model_type,
                "usedCachedModel": used_cached_model,
            }
        )
    )


if __name__ == "__main__":
    main()
