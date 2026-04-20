import pandas as pd
import numpy as np
from collections import defaultdict, deque

WINDOW = 20


def safe_div(a, b):
    if b == 0:
        return np.nan
    return a / b


def compute_rates(prefix, row):
    svpt = row[f"{prefix}_svpt"]
    first_in = row[f"{prefix}_1stIn"]
    first_won = row[f"{prefix}_1stWon"]
    second_won = row[f"{prefix}_2ndWon"]
    sv_gms = row[f"{prefix}_SvGms"]
    bp_saved = row[f"{prefix}_bpSaved"]
    bp_faced = row[f"{prefix}_bpFaced"]

    breaks_conceded = bp_faced - bp_saved

    hold_rate = 1 - safe_div(breaks_conceded, sv_gms)

    first_srv_win_rate = safe_div(first_won, first_in)

    second_srv_win_rate = safe_div(
        second_won,
        svpt - first_in
    )

    return (
        hold_rate,
        first_srv_win_rate,
        second_srv_win_rate
    )


def add_serve_stats_to_csv(df):

    player_history = defaultdict(
        lambda: {
            "hold": deque(maxlen=WINDOW),
            "first": deque(maxlen=WINDOW),
            "second": deque(maxlen=WINDOW)
        }
    )

    hold_list = []
    first_list = []
    second_list = []

    df = df.sort_values("tourney_date")

    for _, row in df.iterrows():

        winner = row["winner_id"]
        loser = row["loser_id"]

        # ---- stamp current rolling averages ----

        def get_avg(player, key):
            hist = player_history[player][key]
            if len(hist) == 0:
                return np.nan
            return np.mean(hist)

        hold_list.append(get_avg(winner, "hold"))
        first_list.append(get_avg(winner, "first"))
        second_list.append(get_avg(winner, "second"))

        hold_list.append(get_avg(loser, "hold"))
        first_list.append(get_avg(loser, "first"))
        second_list.append(get_avg(loser, "second"))

        # ---- compute current match rates ----

        w_rates = compute_rates("w", row)
        l_rates = compute_rates("l", row)

        player_history[winner]["hold"].append(w_rates[0])
        player_history[winner]["first"].append(w_rates[1])
        player_history[winner]["second"].append(w_rates[2])

        player_history[loser]["hold"].append(l_rates[0])
        player_history[loser]["first"].append(l_rates[1])
        player_history[loser]["second"].append(l_rates[2])

    df["winner_hold_rate_last20"] = hold_list[0::2]
    df["loser_hold_rate_last20"] = hold_list[1::2]

    df["winner_first_srv_win_rate_last20"] = first_list[0::2]
    df["loser_first_srv_win_rate_last20"] = first_list[1::2]

    df["winner_second_srv_win_rate_last20"] = second_list[0::2]
    df["loser_second_srv_win_rate_last20"] = second_list[1::2]

    return df