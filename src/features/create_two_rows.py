import pandas as pd
from datetime import datetime

# first, create a dictionary mapping each possible 'tourney_level' to a K value
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

# Create 2 rows for each match, so each player has their own perspective
# Eg, for Sinner vs Alcaraz game, currently there is only one record, Sinner as Winner, meaning his stats are in the winner_* fields
# However in other matches where Sinner lost he would be in loser_* fields
# This difference means creating rolling averages for players very difficult, so for each game Sinner plays in he should be player_* regardless, and a new field result to be made (1 for win, 0 for loss)
# This way i can just look for Sinner in the player_name field and create rolling averages that way


def create_two_rows(df):
    # print(
    #     f'The current size of the dataframe is {len(df)}. After this it should be 2x as big, which is {len(df)*2}')
    # print(f'The current number of headers is {len(df.columns)}')
    rows = []
    last_matchday_local = {}

    # iterrows() iterates through every match row in df and gets the index and the row itself
    # now for each match, create a winner row and a loser row, so one row where the player won and opponent lost, and another where the player is the one that lost and the opponent won
    for _, match in df.iterrows():

        tournament_information = {
            "tourney_name":    match["tourney_name"],
            "surface":         match["surface"],
            "draw_size":       match["draw_size"],
            "tourney_level":   match["tourney_level"],
            "tourney_k_value": tourney_k[match["tourney_level"]],
            "tourney_date":    match["tourney_date"],
            "best_of":         match["best_of"],
            "round":           match["round"],
        }

        winner_elo_gap         = match["player_elo"] - match["opponent_elo"]
        winner_winrate_gap     = 100 * (match["player_winrate_last_10"] - match["opponent_winrate_last_10"])
        winner_surface_elo_gap = match["player_surface_elo"] - match["opponent_surface_elo"]
        winner_rank_gap        = match["winner_rank"] - match["loser_rank"]
        winner_rankpts_gap     = match["winner_rank_points"] - match["loser_rank_points"]
        winner_h2h_gap         = match["player_h2h"] - (1 - match["player_h2h"])
        
        winner_rest = match["winner_days_rest"] if match["winner_days_rest"] is not None else 0
        loser_rest = match["loser_days_rest"] if match["loser_days_rest"] is not None else 0
        days_rest_gap = winner_rest - loser_rest
                

        winner = {
            **tournament_information,
            "player_name":         match["winner_name"],
            "player_hand":         match["winner_hand"],
            "player_ht":           match["winner_ht"],
            "player_age":          match["winner_age"],
            "player_rank":         match["winner_rank"],
            "player_rank_points":  match["winner_rank_points"],
            "player_elo":          match["player_elo"],
            "player_surface_elo":  match["player_surface_elo"],
            "opponent_name":       match["loser_name"],
            "opponent_hand":       match["loser_hand"],
            "opponent_ht":         match["loser_ht"],
            "opponent_age":        match["loser_age"],
            "opponent_rank":       match["loser_rank"],
            "opponent_rank_points": match["loser_rank_points"],
            "opponent_elo":        match["opponent_elo"],
            "opponent_surface_elo": match["opponent_surface_elo"],
            
            "elo_gap":             winner_elo_gap,
            "winrate_gap":         winner_winrate_gap,
            "surface_elo_gap":     winner_surface_elo_gap,
            "rank_gap":            winner_rank_gap,
            "rank_points_gap":     winner_rankpts_gap,
            "h2h_gap":             winner_h2h_gap,
            "days_rest_gap":       days_rest_gap,
            "result": 1,
        }

        loser = {
            **tournament_information,
            "player_name":         match["loser_name"],
            "player_hand":         match["loser_hand"],
            "player_ht":           match["loser_ht"],
            "player_age":          match["loser_age"],
            "player_rank":         match["loser_rank"],
            "player_rank_points":  match["loser_rank_points"],
            "player_elo":          match["opponent_elo"],
            "player_surface_elo":  match["opponent_surface_elo"],
            "opponent_name":       match["winner_name"],
            "opponent_hand":       match["winner_hand"],
            "opponent_ht":         match["winner_ht"],
            "opponent_age":        match["winner_age"],
            "opponent_rank":       match["winner_rank"],
            "opponent_rank_points": match["winner_rank_points"],
            "opponent_elo":        match["player_elo"],
            "opponent_surface_elo": match["player_surface_elo"],
            "elo_gap":             -winner_elo_gap,
            "winrate_gap":         -winner_winrate_gap,
            "surface_elo_gap":     -winner_surface_elo_gap,
            "rank_gap":            -winner_rank_gap,
            "rank_points_gap":     -winner_rankpts_gap,
            "h2h_gap":             -winner_h2h_gap,
            "days_rest_gap":       -days_rest_gap,
            "result": 0,
        }

        rows.append(winner)
        rows.append(loser)

    # print(f'The current size of this new dataframe is {len(rows)}')
    # print(f'The current number of headers is {len(rows[0])}')

    return pd.DataFrame(rows)
