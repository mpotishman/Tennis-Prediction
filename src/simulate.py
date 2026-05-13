from collections import Counter
import random
import pandas as pd

from features import build_player_lookup


def get_match_probability(
    p1: str,
    p2: str,
    round_num: int,
    model,
    scaler,
    df,
    features: list,
    player_lookup_cache: dict | None,
    probability_cache: dict,
    p1year_end: int = 2026,
    p2year_end: int = 2026,
) -> float:
    """Return P(p1 beats p2), using the cache to avoid recomputing."""
    cache_key = (round_num, p1, p2)
    if cache_key in probability_cache:
        return probability_cache[cache_key]

    players_comparison = build_player_lookup.build_feature_row(
        df, p1, p2, round_num, p1year_end, p2year_end,
        player_lookup=player_lookup_cache,
    )

    if players_comparison is None:
        probability_cache[cache_key] = 0.5
        return 0.5

    players_comparison_df = pd.DataFrame([players_comparison])[features]

    fill_values = getattr(scaler, "feature_fill_values", None)
    players_comparison_df = players_comparison_df.fillna(
        fill_values if fill_values is not None
        else players_comparison_df.median(numeric_only=True)
    )

    prob = model.predict_proba(scaler.transform(players_comparison_df))[0][1]
    probability_cache[cache_key] = prob
    return prob


def simulate_match(
    p1: str,
    p2: str,
    round_num: int,
    model,
    scaler,
    df,
    features: list,
    player_lookup_cache: dict | None,
    probability_cache: dict,
) -> str:
    """Simulate a single match and return the winner's name."""
    prob = get_match_probability(
        p1, p2, round_num, model, scaler, df, features,
        player_lookup_cache, probability_cache,
    )
    return p1 if random.random() < prob else p2


def run_tournament_once(
    bracket: list,
    model,
    scaler,
    df,
    features: list,
    player_lookup_cache: dict | None,
    probability_cache: dict,
) -> tuple[str, dict]:
    """Simulate a full single-elimination tournament and return (winner, round results)."""
    bracket = list(bracket)
    round_num = 1
    bracket_results = {}

    while len(bracket) > 1:
        next_round = []
        bracket_results[round_num] = {}
        for i in range(0, len(bracket), 2):
            winner = simulate_match(
                bracket[i], bracket[i + 1], round_num,
                model, scaler, df, features,
                player_lookup_cache, probability_cache,
            )
            next_round.append(winner)
            bracket_results[round_num][i // 2] = winner
        bracket = next_round
        round_num += 1

    return bracket[0], bracket_results


def run_multiple_tournaments(
    bracket: list,
    model,
    scaler,
    df,
    features: list,
    n: int,
) -> tuple[Counter, dict]:
    """Run n tournament simulations and aggregate results."""
    champion_counts = Counter()
    player_lookup_cache = build_player_lookup.build_latest_player_lookup(df)
    probability_cache: dict = {}
    bracket_counts: dict = {}

    for _ in range(n):
        winner, bracket_results = run_tournament_once(
            bracket, model, scaler, df, features,
            player_lookup_cache, probability_cache,
        )
        champion_counts[winner] += 1

        for round_num, matches in bracket_results.items():
            if round_num not in bracket_counts:
                bracket_counts[round_num] = {}
            for match_pos, player in matches.items():
                if match_pos not in bracket_counts[round_num]:
                    bracket_counts[round_num][match_pos] = Counter()
                bracket_counts[round_num][match_pos][player] += 1

    return champion_counts, bracket_counts
