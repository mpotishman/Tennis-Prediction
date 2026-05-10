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

def get_match_probability(p1, p2, round_num, model, scaler, df, features, player_lookup_cache, probability_cache, p1year_end=2026, p2year_end=2026):
    cache_key = (round_num, p1, p2)

    if cache_key in probability_cache:
        return probability_cache[cache_key]

    players_comparison = build_player_lookup.build_feature_row(
        df,
        p1,
        p2,
        round_num,
        p1year_end,
        p2year_end,
        player_lookup=player_lookup_cache,
    )
    
    # create a function to get a players earliest year involvement, set it to a variable
    p1earliest_year = get_earliest_year(df, p1)
    p2earliest_year = get_earliest_year(df, p2)

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


# take in the bracket, and call simulate_match to get the winner - add the winner to a new bracket list and keep doing until bracket is length 1
def run_tournament_once(bracket, model, scaler, df, features, player_lookup_cache, probability_cache):
    bracket = list(bracket)
    round_num = 1
    bracket_results = {}

    while len(bracket) > 1:
        next_round = []
        bracket_results[round_num] = {}
        for i in range(0, len(bracket), 2):
            match_pos = i // 2
            winner = simulate_match(
                bracket[i], bracket[i+1], round_num,
                model, scaler, df, features,
                player_lookup_cache, probability_cache,
            )
            next_round.append(winner)
            bracket_results[round_num][match_pos] = winner
        bracket = next_round
        round_num += 1

    return bracket[0], bracket_results


def run_multiple_tournaments(bracket, model, scaler, df, features, n):
    champion_counts = Counter()
    player_lookup_cache = build_player_lookup.build_latest_player_lookup(df)
    probability_cache = {}
    bracket_counts = {}  # { round_num: { match_pos: Counter } }

    for i in range(n):
        winner, bracket_results = run_tournament_once(
            bracket,
            model,
            scaler,
            df,
            features,
            player_lookup_cache,
            probability_cache,
        )
        champion_counts[winner] += 1

        # bracket results is in the form of {round num: {matchNum : winner}}
        # loop through the round num and the match, if there is no round num add it
        # then for the match number and winner in inner dict, create a counter that counts hoow many times that player is in the match pos for that round

        
        for round_num, matches in bracket_results.items():
            if round_num not in bracket_counts:
                bracket_counts[round_num] = {}
            for match_pos, player in matches.items():
                if match_pos not in bracket_counts[round_num]:
                    bracket_counts[round_num][match_pos] = Counter()
                bracket_counts[round_num][match_pos][player] += 1

    return champion_counts, bracket_counts
                
    # # now sort match rounds so need 64 most common in r2, 32 most common in r3 etc
    # round_size_map = {
    #     2: 64,
    #     3: 32,
    #     4: 16,
    #     5: 8,
    #     6: 4,
    #     7: 2,
    #     8: 1
    # }
    
    # common_matchups = {}
    # for round_num, size in round_size_map.items():
    #     common_matchups[round_num] = dict(match_round_counts[round_num].most_common(size))
         
        
    return champion_counts, common_matchups

def get_earliest_year(df, player):
    player_rows = df[df["player_name"] == player]
    if len(player_rows) == 0:
        return None
    earliest_date = player_rows["tourney_date"].min()
    return int(earliest_date[:4])