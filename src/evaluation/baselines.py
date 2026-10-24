# Simple comparison methods for the full tennis model.

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler


RANKING_FEATURES = ["rank_gap", "rank_points_gap"]


def coin_flip_probabilities(test_df):
    # A neutral probability baseline is useful for checking the scoring pipeline.
    return np.full(len(test_df), 0.5, dtype=float)


def higher_ranked_probabilities(test_df):
    # Lower ATP rank numbers are better; unknown or tied rankings stay unresolved.
    probabilities = np.full(len(test_df), 0.5, dtype=float)
    valid = test_df["player_rank"].notna() & test_df["opponent_rank"].notna()
    probabilities[valid & (test_df["player_rank"] < test_df["opponent_rank"])] = 1.0
    probabilities[valid & (test_df["player_rank"] > test_df["opponent_rank"])] = 0.0
    return probabilities


def elo_probabilities(test_df, gap_column="elo_gap"):
    # The standard Elo curve turns a pre-match rating gap into a win probability.
    elo_gap = test_df[gap_column].fillna(0).astype(float)
    return 1 / (1 + np.power(10.0, -elo_gap / 400.0))


def fit_ranking_logistic(train_df):
    # Fit imputation and scaling on past matches only so the baseline stays leak-free.
    fill_values = train_df[RANKING_FEATURES].median().fillna(0)
    X_train = train_df[RANKING_FEATURES].fillna(fill_values)
    y_train = train_df["result"]

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = LogisticRegression(max_iter=2000, random_state=42)
    model.fit(X_train_scaled, y_train)

    return model, scaler, fill_values


def ranking_logistic_probabilities(test_df, model, scaler, fill_values):
    # Apply the historical ranking model to the held-out year.
    X_test = test_df[RANKING_FEATURES].fillna(fill_values)
    X_test_scaled = scaler.transform(X_test)
    return model.predict_proba(X_test_scaled)[:, 1]
