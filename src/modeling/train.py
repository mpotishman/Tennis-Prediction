# Trains the match-prediction model and returns (model, scaler, feature_list).
# Supports XGBoost, Random Forest, and Logistic Regression.
# Pass tournament_start_date to train only on pre-tournament data;
# pass None to train on all available data (used for head-to-head matchup predictions).

import pandas as pd
from pandas.api.types import is_numeric_dtype
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier


SURFACE_MAP = {"Hard": 0, "Clay": 1, "Grass": 2, "Carpet": 3}
ROUND_MAP = {
    "R128": 1, "R64": 2, "R32": 3, "R16": 4,
    "QF": 5, "SF": 6, "F": 7,
    "RR": 3, "BR": 6, "3rd/4th": 6,
}
HAND_MAP = {"R": 0, "L": 1}
LEVEL_MAP = {"G": 4, "M": 3, "F": 3, "A": 2, "500": 2, "O": 2, "250": 1, "D": 1}

EXCLUDED_FEATURE_COLUMNS = {
    "result", "player_name", "opponent_name", "tourney_name", "tourney_date",
    # Match-outcome columns would leak the result if used as features.
    "player_won_games", "player_won_games_percentage",
    "opponent_won_games", "opponent_won_games_percentage",
    # Backtest bookkeeping columns, not model signals.
    "match_id", "row_in_match",
}


def prepare_model_dataframe(df):
    """Apply the categorical encodings expected by the sklearn/XGBoost models."""
    df = df.copy()
    df["tourney_date"] = pd.to_datetime(df["tourney_date"])
    df["surface"] = df["surface"].map(SURFACE_MAP).fillna(-1)
    df["round"] = df["round"].map(ROUND_MAP).fillna(-1)
    df["player_hand"] = df["player_hand"].map(HAND_MAP).fillna(-1)
    df["opponent_hand"] = df["opponent_hand"].map(HAND_MAP).fillna(-1)
    df["tourney_level"] = df["tourney_level"].map(LEVEL_MAP).fillna(-1).astype(int)
    return df


def default_feature_columns(df):
    """Return numeric model features, excluding labels, names, outcomes, and ids."""
    return [
        column for column in df.columns
        if column not in EXCLUDED_FEATURE_COLUMNS
        and is_numeric_dtype(df[column])
    ]


def random_forest(X_train, y_train):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model


def xgboost(X_train, y_train):
    model = XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.7,
        colsample_bytree=0.7,
        random_state=42,
        eval_metric="logloss",
    )
    model.fit(X_train, y_train)
    return model


def tune_xgboost(X_train, y_train):
    """Grid-search XGBoost hyperparameters with 5-fold cross-validation."""
    param_grid = {
        "n_estimators": [100, 300, 500],
        "learning_rate": [0.01, 0.05, 0.1],
        "max_depth": [3, 4, 5],
        "subsample": [0.7, 0.8, 0.9],
        "colsample_bytree": [0.7, 0.8, 0.9],
    }
    model = XGBClassifier(random_state=42, eval_metric="logloss")
    grid = GridSearchCV(model, param_grid, cv=5, scoring="accuracy", n_jobs=-1)
    grid.fit(X_train, y_train)
    print(f"Best params: {grid.best_params_}")
    print(f"Best CV score: {grid.best_score_:.3f}")
    return grid.best_estimator_


def logistical_regression(X_train, y_train):
    model = LogisticRegression(max_iter=5000)
    model.fit(X_train, y_train)
    return model


def training(df, tournament_start_date=None, model_type="xgboost", features=None):
    """Train a match-prediction model and return (model, scaler, features).

    tournament_start_date: if provided, only trains on matches before this date.
    Pass None to train on all available data (used for matchup predictions).
    """
    df = prepare_model_dataframe(df)

    if tournament_start_date:
        train_df = df[df["tourney_date"] < pd.Timestamp(tournament_start_date)]
    else:
        train_df = df

    if features is None:
        features = default_feature_columns(train_df)

    feature_fill_values = train_df[features].median().fillna(0)
    X_train = train_df[features].fillna(feature_fill_values)
    y_train = train_df["result"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    scaler.feature_fill_values = feature_fill_values

    if model_type == "xgboost":
        model = xgboost(X_train_scaled, y_train)
    elif model_type == "random_forest":
        model = random_forest(X_train_scaled, y_train)
    elif model_type == "logistic":
        model = logistical_regression(X_train_scaled, y_train)
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    return model, scaler, features
