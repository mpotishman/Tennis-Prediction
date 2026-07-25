import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import TOURNAMENT_K_VALUES


def _expected_win_pct(player_elo: float, opponent_elo: float) -> float:
    return 1 / (1 + 10 ** ((opponent_elo - player_elo) / 400))


def calculate_elo(
    match,
    player_name: str,
    opponent_name: str,
    players_elo: dict,
    tourney_k_value: dict,
) -> tuple[float, float]:
    """Update ELO ratings after a match and return pre-match ELOs."""
    if player_name not in players_elo:
        players_elo[player_name] = 1500
    if opponent_name not in players_elo:
        players_elo[opponent_name] = 1500

    player_pre_elo = players_elo[player_name]
    opponent_pre_elo = players_elo[opponent_name]

    player_expected = _expected_win_pct(player_pre_elo, opponent_pre_elo)
    opponent_expected = 1 - player_expected

    # Scale the update by how dominant the win was. "player" is the match
    # winner at this stage, so winner_games are the player's games.
    winner_games = match["winner_games"]
    loser_games = match["loser_games"]
    if math.isnan(winner_games) or math.isnan(loser_games):
        margin_multiplier = 1.0  # retirement / walkover — no margin info
    else:
        game_margin = max(winner_games - loser_games, 0)
        elo_diff = player_pre_elo - opponent_pre_elo  # winner's pre-match edge
        margin_multiplier = math.log(game_margin + 1) * (2.2 / (elo_diff * 0.001 + 2.2))
        margin_multiplier = min(max(margin_multiplier, 0.5), 2.0)  # floor + cap

    k = tourney_k_value[match["tourney_level"]] * margin_multiplier
    players_elo[player_name] = player_pre_elo + k * (1 - player_expected)
    players_elo[opponent_name] = opponent_pre_elo + k * (0 - opponent_expected)

    return player_pre_elo, opponent_pre_elo


def add_elo_to_csv(df):
    """Add pre-match ELO columns to the raw match DataFrame."""
    players_elo: dict = {}
    for idx, match in df.iterrows():
        player_elo, opponent_elo = calculate_elo(
            match, match["winner_name"], match["loser_name"],
            players_elo, TOURNAMENT_K_VALUES,
        )
        df.at[idx, "player_elo"] = player_elo
        df.at[idx, "opponent_elo"] = opponent_elo
    return df
