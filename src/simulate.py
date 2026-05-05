# this file will have 3 functions
# 1) Simulate Match - Uses the function build_feature_row which returns the elo gap, rank gap etc between 2 players
#    scales the information, predicts it using predict_proba, then randomly selects a number and if < prob player 1 gets returned

# 2) run_tournament_once - takes the 64 pairs, and then calls simulate match on each pair, then takes the winners and matches them up against each other
#    and keeps calling simulate match until theres only 1 player left

# 3) run_multiple_tournaments - calls simulate_once 10,000 times

from collections import Counter
import random

import pandas as pd

from features import build_player_lookup

def get_match_probability(p1, p2, round_num, model, scaler, df, features, player_lookup_cache, probability_cache):
    cache_key = (round_num, p1, p2)

    if cache_key in probability_cache:
        return probability_cache[cache_key]

    players_comparison = build_player_lookup.build_feature_row(
        df,
        p1,
        p2,
        round_num,
        player_lookup=player_lookup_cache,
    )

    if players_comparison is None:
        probability_cache[cache_key] = 0.5
        return 0.5

    players_comparison_df = pd.DataFrame([players_comparison])[features]

    fill_values = getattr(scaler, "feature_fill_values", None)
    if fill_values is not None:
        players_comparison_df = players_comparison_df.fillna(fill_values)
    else:
        players_comparison_df = players_comparison_df.fillna(
            players_comparison_df.median(numeric_only=True)
        )

    players_comparison_scaled = scaler.transform(players_comparison_df)
    player_1_prob = model.predict_proba(players_comparison_scaled)[0][1]

    probability_cache[cache_key] = player_1_prob
    return player_1_prob


def simulate_match(p1, p2, round_num, model, scaler, df, features, player_lookup_cache, probability_cache):
    player_1_prob = get_match_probability(
        p1,
        p2,
        round_num,
        model,
        scaler,
        df,
        features,
        player_lookup_cache,
        probability_cache,
    )

    random_number = random.random()
    if random_number < player_1_prob:
        return p1
    return p2


# take in the bracket, and call simulate_match to get the winner - add the winner to a new braacket list and keep doing until bracket is length 1
def run_tournament_once(bracket, model, scaler, df, features, player_lookup_cache, probability_cache):
    bracket = list(bracket)
    round_num = 1

    while len(bracket) > 1:
        next_round = []
        for i in range(0, len(bracket), 2):
            winner = simulate_match(
                bracket[i],
                bracket[i + 1],
                round_num,
                model,
                scaler,
                df,
                features,
                player_lookup_cache,
                probability_cache,
            )
            next_round.append(winner)
        bracket = next_round
        round_num += 1

    return bracket[0]



def run_multiple_tournaments(bracket, model, scaler, df, features, n):
    round_matchups = {2: Counter(), 3: Counter(), 4: Counter(), 5: Counter(), 6: Counter(), 7: Counter()}
    player_lookup_cache = build_player_lookup.build_latest_player_lookup(df)
    probability_cache = {}

    for i in range(n):
        winner = run_tournament_once(
            bracket,
            model,
            scaler,
            df,
            features,
            player_lookup_cache,
            probability_cache,
        )
        round_matchups[7][winner] += 1

        if (i + 1) % 500 == 0:
            print(f"Finished {i + 1} simulations")

    print(round_matchups[7])
    return round_matchups[7]
