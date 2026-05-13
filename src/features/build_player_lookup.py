import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import AO_2026_START


def _extract_stats(row) -> dict:
    return {
        "elo":                  row["player_elo"],
        "surface_elo":          row["player_surface_elo"],
        "rank":                 row["player_rank"],
        "rank_points":          row["player_rank_points"],
        "last_match_date":      row["tourney_date"],
        "hold_rate":            row["player_hold_rate"],
        "first_srv_win_rate":   row["player_first_srv_win_rate"],
        "second_srv_win_rate":  row["player_second_srv_win_rate"],
        "winrate":              row["player_winrate"],
    }


def build_latest_player_lookup(df, cutoff: str = AO_2026_START) -> dict:
    """Return each player's most recent stats before the cutoff date."""
    filtered = df[df["tourney_date"] < cutoff].sort_values("tourney_date", ascending=False)
    latest_rows = filtered.drop_duplicates(subset=["player_name"], keep="first")
    return {row["player_name"]: _extract_stats(row) for _, row in latest_rows.iterrows()}


def build_player_lookup(df, player_name: str, year_end: int = 2026) -> dict | None:
    """Return a single player's most recent stats up to year_end (capped at AO start)."""
    end_date = min(f"{year_end}-12-31", AO_2026_START)
    filtered = df[df["tourney_date"] < end_date].sort_values("tourney_date", ascending=False)
    player_rows = filtered[filtered["player_name"] == player_name]

    if player_rows.empty:
        return None

    return _extract_stats(player_rows.iloc[0])


def build_feature_row(
    df,
    player_name: str,
    opponent_name: str,
    round_num: int,
    p1year_end: int,
    p2year_end: int,
    player_lookup: dict | None = None,
) -> dict | None:
    """Build a single feature row for a hypothetical matchup."""
    if player_lookup is None:
        player = build_player_lookup(df, player_name, p1year_end)
        opponent = build_player_lookup(df, opponent_name, p2year_end)
    else:
        player = player_lookup.get(player_name)
        opponent = player_lookup.get(opponent_name)

    if player is None or opponent is None:
        return None

    ao_start = pd.Timestamp(AO_2026_START)
    player_rest = (ao_start - pd.Timestamp(player["last_match_date"])).days
    opponent_rest = (ao_start - pd.Timestamp(opponent["last_match_date"])).days

    return {
        "elo_gap":                  player["elo"] - opponent["elo"],
        "tourney_k_value":          1.0,
        "best_of":                  5,
        "surface":                  0,
        "tourney_level":            4,
        "round":                    round_num,
        "winrate_gap":              (player["winrate"] - opponent["winrate"]) * 100,
        "surface_elo_gap":          player["surface_elo"] - opponent["surface_elo"],
        "rank_gap":                 player["rank"] - opponent["rank"],
        "rank_points_gap":          player["rank_points"] - opponent["rank_points"],
        "days_rest_gap":            player_rest - opponent_rest,
        "hold_rate_gap":            player["hold_rate"] - opponent["hold_rate"],
        "first_srv_win_rate_gap":   player["first_srv_win_rate"] - opponent["first_srv_win_rate"],
        "second_srv_win_rate_gap":  player["second_srv_win_rate"] - opponent["second_srv_win_rate"],
    }
