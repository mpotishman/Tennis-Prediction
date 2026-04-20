import pandas as pd

AO_2026_START = "2026-01-18"


def build_latest_player_lookup(df, cutoff=AO_2026_START):
    filtered = df[df["tourney_date"] < cutoff].sort_values("tourney_date", ascending=False)
    latest_rows = filtered.drop_duplicates(subset=["player_name"], keep="first")

    lookup = {}
    for _, latest in latest_rows.iterrows():
        lookup[latest["player_name"]] = {
            "elo": latest["player_elo"],
            "surface_elo": latest["player_surface_elo"],
            "rank": latest["player_rank"],
            "rank_points": latest["player_rank_points"],
            "last_match_date": latest["tourney_date"],
            "hold_rate": latest["player_hold_rate"],
            "first_srv_win_rate": latest["player_first_srv_win_rate"],
            "second_srv_win_rate": latest["player_second_srv_win_rate"],
            "winrate": latest["player_winrate"],
        }

    return lookup


def build_player_lookup(df, player_name):
    filtered = df[df["tourney_date"] < AO_2026_START].sort_values("tourney_date", ascending=False)
    player_rows = filtered[filtered["player_name"] == player_name]
    
    if len(player_rows) == 0:
        return None
    
    latest = player_rows.iloc[0]
    return {
        "elo": latest["player_elo"],
        "surface_elo": latest["player_surface_elo"],
        "rank": latest["player_rank"],
        "rank_points": latest["player_rank_points"],
        "last_match_date": latest["tourney_date"],
        "hold_rate": latest["player_hold_rate"],
        "first_srv_win_rate": latest["player_first_srv_win_rate"],
        "second_srv_win_rate": latest["player_second_srv_win_rate"],
        "winrate": latest["player_winrate"],
    }
    
def build_feature_row(df, player_name, opponent_name, round_num, player_lookup=None):
    if player_lookup is None:
        player = build_player_lookup(df, player_name)
        opponent = build_player_lookup(df, opponent_name)
    else:
        player = player_lookup.get(player_name)
        opponent = player_lookup.get(opponent_name)
    
    if player is None or opponent is None:
        return None

    ao_start = pd.Timestamp(AO_2026_START)
    player_rest = (ao_start - pd.Timestamp(player["last_match_date"])).days
    opponent_rest = (ao_start - pd.Timestamp(opponent["last_match_date"])).days

    return {
        'elo_gap': player["elo"] - opponent["elo"],
        'tourney_k_value': 1.0,
        'best_of': 5,
        'surface': 0,
        'tourney_level': 4,
        'round': round_num,
        'winrate_gap': (player["winrate"] - opponent["winrate"]) * 100,
        'surface_elo_gap': player["surface_elo"] - opponent["surface_elo"],
        'rank_gap': player["rank"] - opponent["rank"],
        'rank_points_gap': player["rank_points"] - opponent["rank_points"],
        'days_rest_gap': player_rest - opponent_rest,
        'hold_rate_gap': player["hold_rate"] - opponent["hold_rate"],
        'first_srv_win_rate_gap': player["first_srv_win_rate"] - opponent["first_srv_win_rate"],
        'second_srv_win_rate_gap': player["second_srv_win_rate"] - opponent["second_srv_win_rate"]
    }
