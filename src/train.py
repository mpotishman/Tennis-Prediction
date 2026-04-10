import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

def random_forest(X_train, y_train, X_test, y_test):
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return accuracy_score(y_test, predictions)

def xgboost(X_train, y_train, X_test, y_test):
    model = XGBClassifier(n_estimators=100, random_state=42, eval_metric="logloss")
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)
    return accuracy_score(y_test, predictions)

def leakage_scan(df, features, target_col="result", min_count=50, min_class_frac=0.1, max_report=10):
    # Flag suspicious feature/label relationships that look like leakage.
    warnings = []
    if target_col not in df.columns:
        return warnings

    # Cache class counts for later thresholds.
    class_counts = df[target_col].value_counts()
    if class_counts.empty:
        return warnings

    for feature in features:
        if feature not in df.columns:
            continue

        s = df[feature]

        # Missingness leakage: if one class is mostly missing and the other isn't.
        if s.isna().any():
            miss_rate = df.groupby(target_col)[feature].apply(lambda x: x.isna().mean())
            if len(miss_rate) == 2 and miss_rate.max() >= 0.9 and miss_rate.min() <= 0.1:
                warnings.append(
                    (feature, f"missingness strongly tied to result {miss_rate.to_dict()}")
                )

        # Value exclusivity leakage: a value appears only with one class at scale.
        vc = df[[feature, target_col]].dropna().groupby(feature)[target_col].value_counts().unstack(fill_value=0)
        for cls in [0, 1]:
            if cls not in vc.columns:
                vc[cls] = 0

        for val, row in vc.iterrows():
            exclusive = (row[0] == 0) != (row[1] == 0)
            if not exclusive:
                continue
            cls = 1 if row[0] == 0 else 0
            cnt = int(row[cls])
            class_total = int(class_counts.get(cls, 0))
            if cnt >= min_count and class_total > 0 and (cnt / class_total) >= min_class_frac:
                if isinstance(val, float):
                    val_repr = round(val, 6)
                else:
                    val_repr = val
                warnings.append(
                    (feature, f"value {val_repr!r} appears only with result={cls} (count={cnt})")
                )
                break

        # Simple numeric separation: one class entirely above/below the other.
        if pd.api.types.is_numeric_dtype(s):
            s0 = s[df[target_col] == 0].dropna()
            s1 = s[df[target_col] == 1].dropna()
            if not s0.empty and not s1.empty:
                if s0.max() < s1.min() or s1.max() < s0.min():
                    warnings.append((feature, "perfect numeric separation between classes"))

        # Cap the number of warnings to avoid noisy output.
        if len(warnings) >= max_report:
            break

    return warnings



    

# =============================================================
# FUNCTIONS FOR DIFFERENT MODELS
def logistical_regression(X_train, y_train, X_test, y_test):
   
    # define the model - max_iter means to try up to 1000 iterations to converge
    model = LogisticRegression(max_iter=5000)
    
    # The actual training, where the model looks at features and results together and learns the weight
    model.fit(X_train, y_train)
    
    # feeds in A0 2026 features, and it spits out either 1 or 0
    predictions = model.predict(X_test)
    
    # compares prediction to real results
    return accuracy_score(y_test, predictions)


def training(df):
    features = ['player_elo', 'opponent_elo', 'player_rank', 'opponent_rank', 'player_rank_points', 'opponent_rank_points', 'player_age', 'opponent_age', 'player_ht', 'elo_gap',
                'opponent_ht', 'player_days_rest', 'opponent_days_rest', 'tourney_k_value', 'best_of', 'draw_size', 'surface', 'tourney_level', 'round', 'player_hand', 'opponent_hand']

    surface_map = {"Hard": 0, "Clay": 1, "Grass": 2}
    df["surface"] = df["surface"].map(surface_map).fillna(-1)

    round_map = {"R128": 1, "R64": 2, "R32": 3, "R16": 4,
                 "QF": 5, "SF": 6, "F": 7, "RR": 3, "BR": 6, "3rd/4th": 6}
    df["round"] = df["round"].map(round_map).fillna(-1)

    hand_map = {"R": 0, "L": 1}
    df["player_hand"] = df["player_hand"].map(hand_map).fillna(-1)
    df["opponent_hand"] = df["opponent_hand"].map(hand_map).fillna(-1)

    level_map = {"G": 4, "M": 3, "F": 3, "A": 2, "500": 2, "O": 2, "250": 1, "D": 1}
    df["tourney_level"] = df["tourney_level"].map(level_map).fillna(-1).astype(int)

    tournaments = [
        ("Australian Open 2025", "2025-01-12", "2025-01-26", "Australian Open"),
        ("French Open 2025",     "2025-05-19", "2025-06-08", "Roland Garros"),
        ("Wimbledon 2025",       "2025-06-30", "2025-07-13", "Wimbledon"),
        ("US Open 2025",         "2025-08-25", "2025-09-07", "US Open"),
        ("Australian Open 2026", "2026-01-18", "2026-02-02", "Australian Open"),
    ]

    lr_accuracies = []
    rf_accuracies = []
    xgb_accuracies = []

    for tourney_label, start, end, tourney_name in tournaments:
        train = df[df["tourney_date"] < start]
        test = df[
            (df["tourney_date"] >= start) &
            (df["tourney_date"] <= end) &
            (df["tourney_name"] == tourney_name)
        ]

        if len(test) == 0:
            print(f"{tourney_label}: no data found, skipping")
            continue

        X_train = train[features]
        y_train = train["result"]
        X_test = test[features]
        y_test = test["result"]

        X_train = X_train.fillna(X_train.median())
        X_test = X_test.fillna(X_train.median())

        lr = logistical_regression(X_train, y_train, X_test, y_test)
        rf = random_forest(X_train, y_train, X_test, y_test)
        xgb = xgboost(X_train, y_train, X_test, y_test)
        print(f"{tourney_label}: LR={lr:.3f} RF={rf:.3f} XGB={xgb:.3f}")
        lr_accuracies.append(lr)
        rf_accuracies.append(rf)
        xgb_accuracies.append(xgb)
    print(f"\nAverage LR:  {sum(lr_accuracies) / len(lr_accuracies):.3f}")
    print(f"Average RF:  {sum(rf_accuracies) / len(rf_accuracies):.3f}")
    print(f"Average XGB: {sum(xgb_accuracies) / len(xgb_accuracies):.3f}")