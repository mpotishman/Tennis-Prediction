import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import TOURNAMENT_K_VALUES

SURFACES = ("Hard", "Clay", "Grass", "Carpet")
VALID_SURFACES = set(SURFACES)
SURFACE_COLUMN_NAMES = {
    "Hard": "hard",
    "Clay": "clay",
    "Grass": "grass",
    "Carpet": "carpet",
}


def _normalise_surface(surface: str) -> str:
    if pd.isna(surface) or surface not in VALID_SURFACES:
        return "Hard"
    return surface


def _ensure_player_surface_history(history_dict: dict, player_name: str) -> dict:
    if player_name not in history_dict:
        history_dict[player_name] = {surface: 1500 for surface in SURFACES}
    else:
        for surface in SURFACES:
            history_dict[player_name].setdefault(surface, 1500)
    return history_dict[player_name]


def calculate_current_surface_elo(
    match,
    player_name: str,
    opponent_name: str,
    surface: str,
    tourney_k_value: dict,
    history_dict: dict,
) -> tuple[float, float]:
    """Update surface-specific ELO ratings and return pre-match ELOs."""
    surface = _normalise_surface(surface)

    player_history = _ensure_player_surface_history(history_dict, player_name)
    opponent_history = _ensure_player_surface_history(history_dict, opponent_name)

    player_pre = player_history[surface]
    opponent_pre = opponent_history[surface]

    player_expected = 1 / (1 + 10 ** ((opponent_pre - player_pre) / 400))
    opponent_expected = 1 - player_expected

    k = tourney_k_value[match["tourney_level"]]
    player_history[surface] = player_pre + k * (1 - player_expected)
    opponent_history[surface] = opponent_pre + k * (0 - opponent_expected)

    return player_pre, opponent_pre


def add_surface_elo_to_csv(df):
    """Add pre-match surface ELO columns to the raw match DataFrame."""
    history: dict = {}
    for idx, match in df.iterrows():
        player_surface_snapshot = _ensure_player_surface_history(
            history,
            match["winner_name"],
        ).copy()
        opponent_surface_snapshot = _ensure_player_surface_history(
            history,
            match["loser_name"],
        ).copy()

        p_elo, o_elo = calculate_current_surface_elo(
            match,
            match["winner_name"],
            match["loser_name"],
            match["surface"],
            TOURNAMENT_K_VALUES,
            history,
        )
        df.at[idx, "player_surface_elo"] = p_elo
        df.at[idx, "opponent_surface_elo"] = o_elo

        for surface, column_name in SURFACE_COLUMN_NAMES.items():
            df.at[idx, f"player_{column_name}_surface_elo"] = player_surface_snapshot[surface]
            df.at[idx, f"opponent_{column_name}_surface_elo"] = opponent_surface_snapshot[surface]

    return df
