from collections import Counter
import random

import pandas as pd

from features import build_player_lookup


AO_2026_START = "2026-01-18"


def get_bracket(df):
    ao26 = df[
        (df["tourney_name"] == "Australian Open")
        & (df["tourney_date"] >= AO_2026_START)
        & (df["round"] == "R128")
    ]

    pairs = ao26[["player_name", "opponent_name"]].values.tolist()

    seen = set()
    unique_pairs = []
    for p1, p2 in pairs:
        key = tuple(sorted((p1, p2)))
        if key not in seen:
            seen.add(key)
            unique_pairs.append([p1, p2])

    unique_pairs.sort(key=lambda pair: tuple(sorted(pair)))
    print(f"Found {len(unique_pairs)} first round matches")
    return unique_pairs


def build_first_round_probabilities(bracket, model, scaler, df, features):
    player_cache = build_player_lookup.build_latest_player_lookup(df)
    matchup_probs = {}

    for p1, p2 in bracket:
        row = build_player_lookup.build_feature_row(
            df,
            p1,
            p2,
            round_num=1,
            player_lookup=player_cache,
        )
        if row is None:
            matchup_probs[(p1, p2)] = 0.5
            continue

        row_df = pd.DataFrame([row])[features]
        fill_values = getattr(scaler, "feature_fill_values", None)
        if fill_values is not None:
            row_df = row_df.fillna(fill_values)
        else:
            row_df = row_df.fillna(row_df.median(numeric_only=True))

        row_scaled = scaler.transform(row_df)
        matchup_probs[(p1, p2)] = model.predict_proba(row_scaled)[0][1]

    return matchup_probs


def run_first_round_simulation(bracket, model, scaler, df, features, n=10000):
    match_counts = {tuple(pair): Counter() for pair in bracket}
    matchup_probs = build_first_round_probabilities(bracket, model, scaler, df, features)

    for i in range(n):
        for p1, p2 in bracket:
            prob = matchup_probs[(p1, p2)]
            winner = p1 if random.random() < prob else p2
            match_counts[(p1, p2)][winner] += 1

        if (i + 1) % 500 == 0:
            print(f"\n--- After {i + 1} first-round simulations ---")
            for p1, p2 in bracket[:5]:
                counts = match_counts[(p1, p2)]
                p1_pct = 100 * counts[p1] / (i + 1)
                p2_pct = 100 * counts[p2] / (i + 1)
                print(f"  {p1} vs {p2}: {p1_pct:.1f}% / {p2_pct:.1f}%")

    print("\n=== FIRST ROUND RESULTS ===")
    for p1, p2 in bracket:
        counts = match_counts[(p1, p2)]
        p1_pct = 100 * counts[p1] / n
        p2_pct = 100 * counts[p2] / n
        print(f"{p1} vs {p2}: {p1_pct:.1f}% / {p2_pct:.1f}%")

    return match_counts
