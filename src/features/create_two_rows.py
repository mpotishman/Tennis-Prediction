import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.config import TOURNAMENT_K_VALUES

# NEXT TIME, GET MATCH["WINNER_GAMES"] AND PUT IT AS PLAYER AND OPPONENT GAMES, AND ADD WINNER_GAMES/WINNER_GAMES+LOSER_GAMES FOR PERCENTAGE OF GAMES WON


def create_two_rows(df) -> pd.DataFrame:
    """Expand each match into two rows — one per player — with all gap features."""
    rows = []

    for _, match in df.iterrows():
        tournament_information = {
            "tourney_name":    match["tourney_name"],
            "surface":         match["surface"],
            "draw_size":       match["draw_size"],
            "tourney_level":   match["tourney_level"],
            "tourney_k_value": TOURNAMENT_K_VALUES[match["tourney_level"]],
            "tourney_date":    match["tourney_date"],
            "best_of":         match["best_of"],
            "round":           match["round"],
        }
    
        
        

        elo_gap            = match["player_elo"] - match["opponent_elo"]
        winrate_gap        = 100 * (match["player_winrate_last_10"] - match["opponent_winrate_last_10"])
        surface_elo_gap    = match["player_surface_elo"] - match["opponent_surface_elo"]
        rank_gap           = match["winner_rank"] - match["loser_rank"]
        rankpts_gap        = match["winner_rank_points"] - match["loser_rank_points"]
        h2h_gap            = match["player_h2h"] - (1 - match["player_h2h"])
        age_gap            = match["winner_age"] - match["loser_age"]
        days_rest_gap      = (match["winner_days_rest"] or 0) - (match["loser_days_rest"] or 0)
        hold_rate_gap      = match["winner_hold_rate_last20"] - match["loser_hold_rate_last20"]
        first_srv_gap      = match["winner_first_srv_win_rate_last20"] - match["loser_first_srv_win_rate_last20"]
        second_srv_gap     = match["winner_second_srv_win_rate_last20"] - match["loser_second_srv_win_rate_last20"]

        winner = {
            **tournament_information,
            "player_name":               match["winner_name"],
            "player_hand":               match["winner_hand"],
            "player_ht":                 match["winner_ht"],
            "player_age":                match["winner_age"],
            "player_rank":               match["winner_rank"],
            "player_rank_points":        match["winner_rank_points"],
            "player_elo":                match["player_elo"],
            "player_surface_elo":        match["player_surface_elo"],
            "player_hard_surface_elo":   match["player_hard_surface_elo"],
            "player_clay_surface_elo":   match["player_clay_surface_elo"],
            "player_grass_surface_elo":  match["player_grass_surface_elo"],
            "player_carpet_surface_elo": match["player_carpet_surface_elo"],
            "player_hold_rate":          match["winner_hold_rate_last20"],
            "player_first_srv_win_rate": match["winner_first_srv_win_rate_last20"],
            "player_second_srv_win_rate":match["winner_second_srv_win_rate_last20"],
            "player_first_in_rate":      match["winner_first_in_rate_last20"],
            "player_p_serve":            match["winner_p_serve_last20"],
            "player_winrate":            match["player_winrate_last_10"],
            "player_won_games":          match["winner_games"],
            "player_won_games_percentage": (match["winner_games"]/(match["winner_games"] + match["loser_games"])) * 100,
                        
            "opponent_name":             match["loser_name"],
            "opponent_hand":             match["loser_hand"],
            "opponent_ht":               match["loser_ht"],
            "opponent_age":              match["loser_age"],
            "opponent_rank":             match["loser_rank"],
            "opponent_rank_points":      match["loser_rank_points"],
            "opponent_elo":              match["opponent_elo"],
            "opponent_surface_elo":      match["opponent_surface_elo"],
            "opponent_hard_surface_elo": match["opponent_hard_surface_elo"],
            "opponent_clay_surface_elo": match["opponent_clay_surface_elo"],
            "opponent_grass_surface_elo":match["opponent_grass_surface_elo"],
            "opponent_carpet_surface_elo":match["opponent_carpet_surface_elo"],
            "opponent_hold_rate":        match["loser_hold_rate_last20"],
            "opponent_first_srv_win_rate":match["loser_first_srv_win_rate_last20"],
            "opponent_second_srv_win_rate":match["loser_second_srv_win_rate_last20"],
            "opponent_first_in_rate":    match["loser_first_in_rate_last20"],
            "opponent_p_serve":          match["loser_p_serve_last20"],
            "opponent_winrate":          match["opponent_winrate_last_10"],
            "opponent_won_games":          match["loser_games"],
            "opponent_won_games_percentage": (match["loser_games"]/(match["winner_games"] + match["loser_games"])) * 100,
            
            "elo_gap":                   elo_gap,
            "winrate_gap":               winrate_gap,
            "surface_elo_gap":           surface_elo_gap,
            "rank_gap":                  rank_gap,
            "rank_points_gap":           rankpts_gap,
            "h2h_gap":                   h2h_gap,
            "days_rest_gap":             days_rest_gap,
            "age_gap":                   age_gap,
            "hold_rate_gap":             hold_rate_gap,
            "first_srv_win_rate_gap":    first_srv_gap,
            "second_srv_win_rate_gap":   second_srv_gap,
            "result": 1,
        }

        loser = {
            **tournament_information,
            "player_name":               match["loser_name"],
            "player_hand":               match["loser_hand"],
            "player_ht":                 match["loser_ht"],
            "player_age":                match["loser_age"],
            "player_rank":               match["loser_rank"],
            "player_rank_points":        match["loser_rank_points"],
            "player_elo":                match["opponent_elo"],
            "player_surface_elo":        match["opponent_surface_elo"],
            "player_hard_surface_elo":   match["opponent_hard_surface_elo"],
            "player_clay_surface_elo":   match["opponent_clay_surface_elo"],
            "player_grass_surface_elo":  match["opponent_grass_surface_elo"],
            "player_carpet_surface_elo": match["opponent_carpet_surface_elo"],
            "player_hold_rate":          match["loser_hold_rate_last20"],
            "player_first_srv_win_rate": match["loser_first_srv_win_rate_last20"],
            "player_second_srv_win_rate":match["loser_second_srv_win_rate_last20"],
            "player_first_in_rate":      match["loser_first_in_rate_last20"],
            "player_p_serve":            match["loser_p_serve_last20"],
            "player_winrate":            match["opponent_winrate_last_10"],
            "player_won_games":          match["loser_games"],
            "player_won_games_percentage": (match["loser_games"]/(match["winner_games"] + match["loser_games"])) * 100,
            
            "opponent_name":             match["winner_name"],
            "opponent_hand":             match["winner_hand"],
            "opponent_ht":               match["winner_ht"],
            "opponent_age":              match["winner_age"],
            "opponent_rank":             match["winner_rank"],
            "opponent_rank_points":      match["winner_rank_points"],
            "opponent_elo":              match["player_elo"],
            "opponent_surface_elo":      match["player_surface_elo"],
            "opponent_hard_surface_elo": match["player_hard_surface_elo"],
            "opponent_clay_surface_elo": match["player_clay_surface_elo"],
            "opponent_grass_surface_elo":match["player_grass_surface_elo"],
            "opponent_carpet_surface_elo":match["player_carpet_surface_elo"],
            "opponent_hold_rate":        match["winner_hold_rate_last20"],
            "opponent_first_srv_win_rate":match["winner_first_srv_win_rate_last20"],
            "opponent_second_srv_win_rate":match["winner_second_srv_win_rate_last20"],
            "opponent_first_in_rate":    match["winner_first_in_rate_last20"],
            "opponent_p_serve":          match["winner_p_serve_last20"],
            "opponent_winrate":          match["player_winrate_last_10"],
            "opponent_won_games":          match["winner_games"],
            "opponent_won_games_percentage": (match["winner_games"]/(match["winner_games"] + match["loser_games"])) * 100,
            
            "elo_gap":                   -elo_gap,
            "winrate_gap":               -winrate_gap,
            "surface_elo_gap":           -surface_elo_gap,
            "rank_gap":                  -rank_gap,
            "rank_points_gap":           -rankpts_gap,
            "h2h_gap":                   -h2h_gap,
            "days_rest_gap":             -days_rest_gap,
            "age_gap":                   -age_gap,
            "hold_rate_gap":             -hold_rate_gap,
            "first_srv_win_rate_gap":    -first_srv_gap,
            "second_srv_win_rate_gap":   -second_srv_gap,
            "result": 0,
        }

        rows.append(winner)
        rows.append(loser)

    return pd.DataFrame(rows)
