import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier

from config import AO_2026_START, AO_2026_END


def random_forest(X_train, y_train, X_test, y_test):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    return model, accuracy_score(y_test, model.predict(X_test))


def xgboost(X_train, y_train, X_test, y_test):
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
    return model, accuracy_score(y_test, model.predict(X_test))


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


def logistical_regression(X_train, y_train, X_test, y_test):
    model = LogisticRegression(max_iter=5000)
    model.fit(X_train, y_train)
    return model, accuracy_score(y_test, model.predict(X_test))


def training(df, features=None, model_type="xgboost"):
    """Train a match-prediction model and return (model, scaler, features)."""
    surface_map = {"Hard": 0, "Clay": 1, "Grass": 2}
    df["surface"] = df["surface"].map(surface_map).fillna(-1)

    round_map = {
        "R128": 1, "R64": 2, "R32": 3, "R16": 4,
        "QF": 5, "SF": 6, "F": 7,
        "RR": 3, "BR": 6, "3rd/4th": 6,
    }
    df["round"] = df["round"].map(round_map).fillna(-1)

    hand_map = {"R": 0, "L": 1}
    df["player_hand"] = df["player_hand"].map(hand_map).fillna(-1)
    df["opponent_hand"] = df["opponent_hand"].map(hand_map).fillna(-1)

    level_map = {"G": 4, "M": 3, "F": 3, "A": 2, "500": 2, "O": 2, "250": 1, "D": 1}
    df["tourney_level"] = df["tourney_level"].map(level_map).fillna(-1).astype(int)

    train_df = df[df["tourney_date"] < AO_2026_START]
    test_df = df[
        (df["tourney_date"] >= AO_2026_START)
        & (df["tourney_date"] <= AO_2026_END)
        & (df["tourney_name"] == "Australian Open")
    ]

    if features is None:
        features = [
            c for c in train_df.columns
            if c not in {"result", "player_name", "opponent_name", "tourney_name", "tourney_date"}
            and train_df[c].dtype in [float, int, "float64", "int64"]
        ]

    X_train = train_df[features].fillna(train_df[features].median())
    y_train = train_df["result"]
    X_test = test_df[features].fillna(X_train.median())
    y_test = test_df["result"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    scaler.feature_fill_values = X_train.median()

    if model_type == "xgboost":
        model, score = xgboost(X_train_scaled, y_train, X_test_scaled, y_test)
        label = "XGB"
    elif model_type == "random_forest":
        model, score = random_forest(X_train_scaled, y_train, X_test_scaled, y_test)
        label = "RF"
    elif model_type == "logistic":
        model, score = logistical_regression(X_train_scaled, y_train, X_test_scaled, y_test)
        label = "LR"
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    print(f"AO 2026 test accuracy: {label}={score:.3f}")
    return model, scaler, features
