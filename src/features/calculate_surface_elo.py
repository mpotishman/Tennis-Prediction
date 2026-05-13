import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from config import TOURNAMENT_K_VALUES

VALID_SURFACES = {"Clay", "Grass", "Hard", "Carpet"}


def calculate_current_surface_elo(
    match,
    player_name: str,
    opponent_name: str,
    surface: str,
    tourney_k_value: dict,
    history_dict: dict,
) -> tuple[float, float]:
    """Update surface-specific ELO ratings and return pre-match ELOs."""
    if pd.isna(surface) or surface not in VALID_SURFACES:
        surface = "Hard"

    if player_name not in history_dict:
        history_dict[player_name] = {s: 1500 for s in VALID_SURFACES}
    if opponent_name not in history_dict:
        history_dict[opponent_name] = {s: 1500 for s in VALID_SURFACES}

    player_pre = history_dict[player_name][surface]
    opponent_pre = history_dict[opponent_name][surface]

    player_expected = 1 / (1 + 10 ** ((opponent_pre - player_pre) / 400))
    opponent_expected = 1 - player_expected

    k = tourney_k_value[match["tourney_level"]]
    history_dict[player_name][surface] = player_pre + k * (1 - player_expected)
    history_dict[opponent_name][surface] = opponent_pre + k * (0 - opponent_expected)

    return player_pre, opponent_pre


def add_surface_elo_to_csv(df):
    """Add pre-match surface ELO columns to the raw match DataFrame."""
    history: dict = {}
    for idx, match in df.iterrows():
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
    return df
