# Builds player stat snapshots used during simulation.
# build_latest_player_lookup: returns every player's most recent stats before a cutoff date (used in tournament simulation).
# build_feature_row: builds a single feature row for a head-to-head matchup prediction.

import sys
from pathlib import Path
import pandas as pd
import unicodedata
import re

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.tournament_mapping import TOURNAMENT_METADATA

SURFACE_ELO_COLUMNS = {
    "Hard": "player_hard_surface_elo",
    "Clay": "player_clay_surface_elo",
    "Grass": "player_grass_surface_elo",
    "Carpet": "player_carpet_surface_elo",
}

DEFAULT_MATCH_CONTEXT = {
    "start_date": "2026-12-31",
    "surface": "Hard",
    "surface_code": 0,
    "tourney_level_code": 4,
    "tourney_k_value": 1.0,
    "best_of": 5,
}

# Letters that NFKD does NOT decompose into ASCII + combining marks, so they
# would otherwise be dropped by the [^a-z0-9] filter (e.g. "Møller" -> "mller").
# Map them explicitly to their conventional ASCII form.
SPECIAL_CHAR_MAP = {
    "ø": "o", "æ": "ae", "œ": "oe", "å": "a",
    "ł": "l", "đ": "d", "ð": "d", "þ": "th",
    "ß": "ss", "ı": "i", "ŋ": "n",
}


# removes accents, spaces, hyphens, apostrophes, periods, etc.
def canonical_name(name):
    if name is None:
        return ""

    name = str(name).lower().strip()

    # fold letters NFKD can't handle: "Møller" -> "moller", "Đoković" -> "dokovic"
    name = "".join(SPECIAL_CHAR_MAP.get(char, char) for char in name)

    # remove accents: "Kecmanović" -> "Kecmanovic"
    name = unicodedata.normalize("NFKD", name)
    name = "".join(char for char in name if not unicodedata.combining(char))

    # keep only letters and numbers
    name = re.sub(r"[^a-z0-9]", "", name)

    return name


def _row_value(row, column: str, fallback=None):
    if column in row.index:
        return row[column]
    return fallback


def _extract_stats(row) -> dict:
    fallback_surface_elo = row["player_surface_elo"]

    return {
        "elo":                  row["player_elo"],
        "surface_elo":          fallback_surface_elo,
        "surface_elos": {
            surface: _row_value(row, column, fallback_surface_elo)
            for surface, column in SURFACE_ELO_COLUMNS.items()
        },
        "rank":                 row["player_rank"],
        "rank_points":          row["player_rank_points"],
        "last_match_date":      row["tourney_date"],
        "hold_rate":            row["player_hold_rate"],
        "first_srv_win_rate":   row["player_first_srv_win_rate"],
        "second_srv_win_rate":  row["player_second_srv_win_rate"],
        "winrate":              row["player_winrate"],
    }


def _filtered_before(df, cutoff):
    cutoff_date = pd.Timestamp(cutoff)
    tourney_dates = pd.to_datetime(df["tourney_date"])
    filtered = df.loc[tourney_dates < cutoff_date].copy()
    filtered["_lookup_tourney_date"] = tourney_dates.loc[filtered.index]
    return filtered.sort_values("_lookup_tourney_date", ascending=False)


def build_latest_player_lookup(df, cutoff) -> dict:
    """Return each player's most recent stats before the cutoff date."""
    filtered = _filtered_before(df, cutoff)
    latest_rows = filtered.drop_duplicates(subset=["player_name"], keep="first")
    return {canonical_name(row["player_name"]): _extract_stats(row) for _, row in latest_rows.iterrows()}


def build_player_lookup(df, player_name: str, year_end: int = 2026, cutoff=None) -> dict | None:
    """Return a single player's most recent stats before cutoff/year_end."""
    end_date = cutoff or f"{year_end}-12-31"
    filtered = _filtered_before(df, end_date)
    player_rows = filtered[filtered["player_name"].apply(canonical_name) == canonical_name(player_name)]

    if player_rows.empty:
        return None

    return _extract_stats(player_rows.iloc[0])


def _metadata_for(tournament_selected: str | None, p1year_end: int, p2year_end: int) -> dict:
    if tournament_selected is None:
        context = DEFAULT_MATCH_CONTEXT.copy()
        context["start_date"] = f"{max(int(p1year_end), int(p2year_end))}-12-31"
        return context

    metadata = TOURNAMENT_METADATA.get(tournament_selected)
    if metadata is None:
        raise ValueError(f"Unknown tournament: {tournament_selected}")
    if not metadata.get("start_date"):
        raise ValueError(f"{tournament_selected} does not have a playable start date.")
    return metadata


def _surface_elo(stats: dict, surface: str) -> float:
    value = stats["surface_elos"].get(surface, stats["surface_elo"])
    if pd.isna(value):
        return stats["surface_elo"]
    return value


def build_feature_row(
    df,
    player_name: str,
    opponent_name: str,
    round_num: int,
    p1year_end: int,
    p2year_end: int,
    player_lookup: dict | None = None,
    tournament_selected: str | None = None,
) -> dict | None:
    """Build a single feature row for a hypothetical matchup."""
    metadata = _metadata_for(tournament_selected, p1year_end, p2year_end)

    if player_lookup is None:
        cutoff = metadata["start_date"] if tournament_selected is not None else None
        player = build_player_lookup(df, player_name, p1year_end, cutoff=cutoff)
        opponent = build_player_lookup(df, opponent_name, p2year_end, cutoff=cutoff)
    else:
        player = player_lookup.get(canonical_name(player_name))
        opponent = player_lookup.get(canonical_name(opponent_name))

    player_missing = player is None
    opponent_missing = opponent is None

    if player_missing or opponent_missing:
        return player_missing, opponent_missing, None
    
    surface = metadata["surface"]

    if tournament_selected is None:
        days_rest_gap = 0
    else:
        start = pd.Timestamp(metadata["start_date"])
        player_rest = (start - pd.Timestamp(player["last_match_date"])).days
        opponent_rest = (start - pd.Timestamp(opponent["last_match_date"])).days
        days_rest_gap = player_rest - opponent_rest
        
    return False, False, {
            "elo_gap":                  player["elo"] - opponent["elo"],
            "tourney_k_value":          metadata["tourney_k_value"],
            "best_of":                  metadata["best_of"],
            "surface":                  metadata["surface_code"],
            "tourney_level":            metadata["tourney_level_code"],
            "round":                    round_num,
            "winrate_gap":              (player["winrate"] - opponent["winrate"]) * 100,
            "surface_elo_gap":          _surface_elo(player, surface) - _surface_elo(opponent, surface),
            "rank_gap":                 player["rank"] - opponent["rank"],
            "rank_points_gap":          player["rank_points"] - opponent["rank_points"],
            "days_rest_gap":            days_rest_gap,
            "hold_rate_gap":            player["hold_rate"] - opponent["hold_rate"],
            "first_srv_win_rate_gap":   player["first_srv_win_rate"] - opponent["first_srv_win_rate"],
            "second_srv_win_rate_gap":  player["second_srv_win_rate"] - opponent["second_srv_win_rate"],
        }
