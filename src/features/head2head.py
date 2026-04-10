import pandas as pd

def calculate_head2head(match, player_name, opponent_name, history_dict):
    # initialise if first time seeing either player
    if player_name not in history_dict:
        history_dict[player_name] = {}
    if opponent_name not in history_dict:
        history_dict[opponent_name] = {}
    if opponent_name not in history_dict[player_name]:
        history_dict[player_name][opponent_name] = []
    if player_name not in history_dict[opponent_name]:
        history_dict[opponent_name][player_name] = []
     
    total = len(history_dict[player_name][opponent_name])
    player_h2h = history_dict[player_name][opponent_name].count(1) / total if total > 0 else 0.5
    
    # the winner always appends 1, loser always appends 0
    history_dict[player_name][opponent_name].append(1)
    history_dict[opponent_name][player_name].append(0)
        
    return player_h2h


def add_h2h_to_csv(df):
    history = {}
    for idx, match in df.iterrows():
        player_h2h = calculate_head2head(match, match["winner_name"], match["loser_name"], history)
        
        df.at[idx, "player_h2h"] = player_h2h
        df.at[idx, "opponent_h2h"] = 1 - player_h2h
        
    return df
    