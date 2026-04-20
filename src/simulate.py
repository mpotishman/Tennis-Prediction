from collections import Counter
import random
import time

import pandas as pd

from features import build_player_lookup


AO_2026_START = "2026-01-18"
ROUND_NAMES = {
    1: "R128",
    2: "R64",
    3: "R32",
    4: "R16",
    5: "QF",
    6: "SF",
    7: "F",
}


# def get_bracket(df):
#     ao26 = df[
#         (df["tourney_name"] == "Australian Open")
#         & (df["tourney_date"] >= AO_2026_START)
#         & (df["round"] == "R128")
#     ]

#     pairs = ao26[["player_name", "opponent_name"]].values.tolist()

#     seen = set()
#     unique_pairs = []
#     for p1, p2 in pairs:
#         key = tuple(sorted((p1, p2)))
#         if key not in seen:
#             seen.add(key)
#             unique_pairs.append([p1, p2])

#     print(f"Found {len(unique_pairs)} first round matches")
#     return unique_pairs



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

def get_round_name(round_num):
    return ROUND_NAMES.get(round_num, f"Round {round_num}")


def format_matchup(p1, p2):
    return f"{p1} vs {p2}"


def build_round_probabilities(
    bracket,
    model,
    scaler,
    df,
    features,
    round_num,
    player_cache=None,
    probability_cache=None,
):
    if player_cache is None:
        player_cache = build_player_lookup.build_latest_player_lookup(df)
    matchup_probs = {}

    for p1, p2 in bracket:
        cache_key = (round_num, p1, p2)
        if probability_cache is not None and cache_key in probability_cache:
            matchup_probs[(p1, p2)] = probability_cache[cache_key]
            continue

        row = build_player_lookup.build_feature_row(
            df,
            p1,
            p2,
            round_num=round_num,
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
        prob = model.predict_proba(row_scaled)[0][1]
        matchup_probs[(p1, p2)] = prob

        if probability_cache is not None:
            probability_cache[cache_key] = prob

    return matchup_probs

# this function runs the first round 10000 times
def run_first_round_simulation(bracket, model, scaler, df, features, n=10000):
    # Create one win counter per first-round matchup, e.g. {"Sinner": 0, "Gaston": 0}.
    match_counts = {tuple(pair): Counter() for pair in bracket}
    matchup_probs = build_first_round_probabilities(bracket, model, scaler, df, features)

    for i in range(n):
        # go through each matchup in the bracket - and get the probabilites of each person winning
        # then choose a random number. if random number < p1 win prob, record as p1 win and update the match count winner for that player
        for p1, p2 in bracket:
            prob = matchup_probs[(p1, p2)]
            winner = p1 if random.random() < prob else p2
            match_counts[(p1, p2)][winner] += 1

        # debugging statment here
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


# this function runs the entire tournament 10,000 times
def run_entire_tournament(
    bracket,
    model,
    scaler,
    df,
    features,
    n=10000,
    debug=True,
    debug_runs=1,
    summary_limit=8,
):
    # count how many times each player wins whole tournament
    champion_counts = Counter()
    player_cache = build_player_lookup.build_latest_player_lookup(df)
    probability_cache = {}
    round_matchup_counts = {
        round_num: Counter() for round_num in ROUND_NAMES if round_num >= 2
    }
    start_time = time.time()
    progress_marks = {1, 10, 50, 100}

    for i in range(n):
        # fresh copy of round 1 bracket for this one tournament run
        current_round = [pair[:] for pair in bracket]
        round_num = 1
        show_debug = debug and i < debug_runs

        if show_debug:
            print(f"\n================ TOURNAMENT RUN {i + 1} ================")

        # keep going until only one player left
        while True:
            if show_debug:
                print(f"\n{get_round_name(round_num)} matches:")
                for match_index, (p1, p2) in enumerate(current_round, 1):
                    print(f"  {match_index:>2}. {format_matchup(p1, p2)}")

            # build win probabilities for this round's matchups
            matchup_probs = build_round_probabilities(
                current_round,
                model,
                scaler,
                df,
                features,
                round_num,
                player_cache=player_cache,
                probability_cache=probability_cache,
            )

            winners = []

            # simulate every match in this round once
            for match_index, (p1, p2) in enumerate(current_round, 1):
                prob = matchup_probs[(p1, p2)]
                winner = p1 if random.random() < prob else p2
                winners.append(winner)

                if show_debug:
                    print(
                        f"     winner {match_index:>2}: {winner}"
                        f" ({p1} win prob {prob:.3f})"
                    )

            # if only one winner left, tournament over
            if len(winners) == 1:
                champion_counts[winners[0]] += 1

                if show_debug:
                    print(f"\nChampion: {winners[0]}")
                break

            # pair adjacent winners for next round
            next_round = [
                [winners[j], winners[j + 1]]
                for j in range(0, len(winners), 2)
            ]

            next_round_num = round_num + 1
            for p1, p2 in next_round:
                round_matchup_counts[next_round_num][tuple(sorted((p1, p2)))] += 1

            if show_debug:
                print(f"\nProjected {get_round_name(next_round_num)} matches:")
                for match_index, (p1, p2) in enumerate(next_round, 1):
                    print(f"  {match_index:>2}. {format_matchup(p1, p2)}")

            current_round = next_round
            round_num = next_round_num

        runs_done = i + 1
        if runs_done == debug_runs and debug:
            print(
                f"\nDebug run finished. Running remaining {n - runs_done} tournament simulations..."
            )

        if runs_done in progress_marks or runs_done % 500 == 0 or runs_done == n:
            elapsed = time.time() - start_time
            print(f"\n--- After {runs_done} tournament simulations ({elapsed:.1f}s) ---")
            for player, count in champion_counts.most_common(5):
                print(f"  {player}: {count / runs_done * 100:.1f}% title chance")

    print("\n=== MOST COMMON LATER-ROUND MATCHUPS ===")
    for round_num in range(2, 8):
        counts = round_matchup_counts[round_num]
        if not counts:
            continue

        print(f"\n{get_round_name(round_num)} most common matchups:")
        for (p1, p2), count in counts.most_common(summary_limit):
            print(f"  {format_matchup(p1, p2)}: {count / n * 100:.1f}% of runs")

    print("\n=== TITLE ODDS ===")
    for player, count in champion_counts.most_common(10):
        print(f"  {player}: {count / n * 100:.1f}%")

    return champion_counts

    
    
