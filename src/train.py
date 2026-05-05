import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from xgboost import XGBClassifier


def random_forest(X_train, y_train, X_test, y_test):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return model, accuracy_score(y_test, predictions)


def xgboost(X_train, y_train, X_test, y_test):
    model = XGBClassifier(
        n_estimators=500,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.7,
        colsample_bytree=0.7,
        random_state=42,
        eval_metric="logloss"
    )
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return model, accuracy_score(y_test, predictions)


def tune_xgboost(X_train, y_train):
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
    predictions = model.predict(X_test)
    return model, accuracy_score(y_test, predictions)


def training(df, features, model_type="xgboost"):

    print("\nTraining set features:")
    print(features)

    surface_map = {"Hard": 0, "Clay": 1, "Grass": 2}
    df["surface"] = df["surface"].map(surface_map).fillna(-1)

    round_map = {
        "R128": 1,
        "R64": 2,
        "R32": 3,
        "R16": 4,
        "QF": 5,
        "SF": 6,
        "F": 7,
        "RR": 3,
        "BR": 6,
        "3rd/4th": 6,
    }
    df["round"] = df["round"].map(round_map).fillna(-1)

    hand_map = {"R": 0, "L": 1}
    df["player_hand"] = df["player_hand"].map(hand_map).fillna(-1)
    df["opponent_hand"] = df["opponent_hand"].map(hand_map).fillna(-1)

    level_map = {
        "G": 4,
        "M": 3,
        "F": 3,
        "A": 2,
        "500": 2,
        "O": 2,
        "250": 1,
        "D": 1,
    }
    df["tourney_level"] = df["tourney_level"].map(level_map).fillna(-1).astype(int)

    train_ao26 = df[df["tourney_date"] < "2026-01-18"]
    test_ao26 = df[
        (df["tourney_date"] >= "2026-01-18")
        & (df["tourney_date"] <= "2026-02-02")
        & (df["tourney_name"] == "Australian Open")
    ]

    X_train = train_ao26[features]
    y_train = train_ao26["result"]
    X_test = test_ao26[features]
    y_test = test_ao26["result"]

    X_train = X_train.fillna(X_train.median())
    X_test = X_test.fillna(X_train.median())

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

    print(f"\nAO 2026 standalone: {label}={score:.3f}")

    return model, scaler, features
