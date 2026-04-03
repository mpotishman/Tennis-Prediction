import pandas as pd


# Create 2 rows for each match, so each player has their own perspective
# Eg, for Sinner vs Alcaraz game, currently there is only one record, Sinner as Winner, meaning his stats are in the winner_* fields
# However in other matches where Sinner lost he would be in loser_* fields
# This difference means creating rolling averages for players very difficult, so for each game Sinner plays in he should be player_* regardless, and a new field result to be made (1 for win, 0 for loss)
# This way i can just look for Sinner in the player_name field and create rolling averages that way
def create_two_rows(df):
    print(f'The current size of the dataframe is {len(df)}. After this it should be 2x as big, which is {len(df)*2}')
    rows = []
    
    # iterrows() iterates through every match row in df and gets the index and the row itself
    # now for each match, create a winner row and a loser row, so one row where the player won and opponent lost, and another where the player is the one that lost and the opponent won
    for _, match in df.iterrows():
        
        # create a dictionary of the base info that will stay the same for both the winner and loser rows
        tournament_information = {
            "tourney_id": match["tourney_id"],
            "tourney_name": match["tourney_name"],
            "surface": match["surface"],
            "draw_size": match["draw_size"],
            "tourney_level": match["tourney_level"],
            "tourney_date": match["tourney_date"],
            "match_num": match["match_num"],
        }
        
        # create a dictionary of the match result
        match_result = {
            "score": match["score"],
            "best_of": match["best_of"],
            "round": match["round"],
            "minutes": match["minutes"],
        }
        
        winner = {
            **tournament_information,
            
            "player_id": match['winner_id'],
            "player_seed": match['winner_seed'],
            "player_entry": match['winner_entry'],
            "player_name": match['winner_name'],
            "player_hand": match['winner_hand'],
            "player_ht": match['winner_ht'],
            "player_ioc": match['winner_ioc'],
            "player_age": match['winner_age'],
            "player_rank": match['winner_rank'],
            "player_rank_points": match['winner_rank_points'],
            
            "opponent_id": match['loser_id'],
            "opponent_seed": match['loser_seed'],
            "opponent_entry": match['loser_entry'],
            "opponent_name": match['loser_name'],
            "opponent_hand": match['loser_hand'],
            "opponent_ht": match['loser_ht'],
            "opponent_ioc": match['loser_ioc'],
            "opponent_age": match['loser_age'],
            "opponent_rank": match['loser_rank'],
            "opponent_rank_points": match['loser_rank_points'],
            
            **match_result,
            
            "player_ace": match['w_ace'],
            "player_df": match['w_df'],
            "player_svpt": match['w_svpt'],
            "player_1stIn": match['w_1stIn'],
            "player_1stWon": match['w_1stWon'],
            "player_2ndWon": match['w_2ndWon'],
            "player_SvGms": match['w_SvGms'],
            "player_bpSaved": match['w_bpSaved'],
            "player_bpFaced": match['w_bpFaced'],

            "opponent_ace": match['l_ace'],
            "opponent_df": match['l_df'],
            "opponent_svpt": match['l_svpt'],
            "opponent_1stIn": match['l_1stIn'],
            "opponent_1stWon": match['l_1stWon'],
            "opponent_2ndWon": match['l_2ndWon'],
            "opponent_SvGms": match['l_SvGms'],
            "opponent_bpSaved": match['l_bpSaved'],
            "opponent_bpFaced": match['l_bpFaced'],
            
            "result": 1
        }

        loser = {
            **tournament_information,
            
            "player_id": match['loser_id'],
            "player_seed": match['loser_seed'],
            "player_entry": match['loser_entry'],
            "player_name": match['loser_name'],
            "player_hand": match['loser_hand'],
            "player_ht": match['loser_ht'],
            "player_ioc": match['loser_ioc'],
            "player_age": match['loser_age'],
            "player_rank": match['loser_rank'],
            "player_rank_points": match['loser_rank_points'],
            
            "opponent_id": match['winner_id'],
            "opponent_seed": match['winner_seed'],
            "opponent_entry": match['winner_entry'],
            "opponent_name": match['winner_name'],
            "opponent_hand": match['winner_hand'],
            "opponent_ht": match['winner_ht'],
            "opponent_ioc": match['winner_ioc'],
            "opponent_age": match['winner_age'],
            "opponent_rank": match['winner_rank'],
            "opponent_rank_points": match['winner_rank_points'],
            
            **match_result,
            
            "player_ace": match['l_ace'],
            "player_df": match['l_df'],
            "player_svpt": match['l_svpt'],
            "player_1stIn": match['l_1stIn'],
            "player_1stWon": match['l_1stWon'],
            "player_2ndWon": match['l_2ndWon'],
            "player_SvGms": match['l_SvGms'],
            "player_bpSaved": match['l_bpSaved'],
            "player_bpFaced": match['l_bpFaced'],

            
            "opponent_ace": match['w_ace'],
            "opponent_df": match['w_df'],
            "opponent_svpt": match['w_svpt'],
            "opponent_1stIn": match['w_1stIn'],
            "opponent_1stWon": match['w_1stWon'],
            "opponent_2ndWon": match['w_2ndWon'],
            "opponent_SvGms": match['w_SvGms'],
            "opponent_bpSaved": match['w_bpSaved'],
            "opponent_bpFaced": match['w_bpFaced'],
            
            "result": 0,
            
            
        }
        
        # now add those newly created winner and loser rows 
        rows.append(winner)
        rows.append(loser)
        
    print(f'The current size of this new dataframe is {len(rows)}')

    return pd.DataFrame(rows)