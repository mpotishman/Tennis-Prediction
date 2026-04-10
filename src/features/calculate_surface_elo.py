import pandas as pd

tourney_k = {
    'G': 1.00,
    'F': 0.90,
    'M': 0.85,
    'O': 0.80,
    'A': 0.75,
    '500': 0.75,
    '250': 0.70,
    'D': 0.60
}

VALID_SURFACES = {"Clay", "Grass", "Hard", "Carpet"}

def calculate_current_surface_elo(
    match,
    player_name,
    opponent_name,
    surface,
    tourney_k_value,
    history_dict
):

    # -------------------------
    # FIX: surface sanitisation
    # -------------------------
    if pd.isna(surface) or surface not in VALID_SURFACES:
        surface = "Hard"

    # -------------------------
    # INIT PLAYER STATE
    # -------------------------
    if player_name not in history_dict:
        history_dict[player_name] = {s: 1500 for s in VALID_SURFACES}
    if opponent_name not in history_dict:
        history_dict[opponent_name] = {s: 1500 for s in VALID_SURFACES}

    # -------------------------
    # PRE MATCH ELO
    # -------------------------
    player_pre = history_dict[player_name][surface]
    opponent_pre = history_dict[opponent_name][surface]

    # -------------------------
    # EXPECTED SCORE
    # -------------------------
    player_expected = 1 / (1 + 10 ** ((opponent_pre - player_pre) / 400))
    opponent_expected = 1 - player_expected

    k = tourney_k_value[match["tourney_level"]]

    # -------------------------
    # UPDATE ELO (single logic)
    # -------------------------
    history_dict[player_name][surface] = player_pre + k * (1 - player_expected)
    history_dict[opponent_name][surface] = opponent_pre + k * (0 - opponent_expected)

    return player_pre, opponent_pre


def add_surface_elo_to_csv(df):
    history = {}

    for idx, match in df.iterrows():
        p_elo, o_elo = calculate_current_surface_elo(
            match,
            match["winner_name"],
            match["loser_name"],
            match["surface"],
            tourney_k,
            history
        )

        df.at[idx, "player_surface_elo"] = p_elo
        df.at[idx, "opponent_surface_elo"] = o_elo

    return df