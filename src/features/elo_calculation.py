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

# calculate the new elo after winning or losing - done by first getting the players expected win percentage, then feeding that into a formula to update player elo, then updating the dictionary containing players elo
def calculate_elo(match, player_name, opponent_name, players_elo, tourney_k_value):
    if player_name not in players_elo:
        players_elo[player_name] = 1500
    if opponent_name not in players_elo:
        players_elo[opponent_name] = 1500

    player_pre_elo = players_elo[player_name]
    opponent_pre_elo = players_elo[opponent_name]

    player_expected_win_percent = 1 / \
        (1+10**((players_elo[opponent_name] -
         players_elo[player_name])/400))
    opponent_expected_win_percent = 1 / \
        (1+10**((players_elo[player_name] -
         players_elo[opponent_name])/400))

    player_new_elo = players_elo[player_name] + (
        tourney_k_value[match["tourney_level"]] * (1 - player_expected_win_percent))
    opponent_new_elo = players_elo[opponent_name] + (
        tourney_k_value[match["tourney_level"]] * (0 - opponent_expected_win_percent))

    players_elo[player_name] = player_new_elo
    players_elo[opponent_name] = opponent_new_elo

    return player_pre_elo, opponent_pre_elo

# this function adds each players elo to the RAW dataset, BEFORE two rows are created for each match
def add_elo_to_csv(df):
    players_elo_local = {}
    for idx, match in df.iterrows():
        player_elo, opponent_elo = calculate_elo(
            match, match["winner_name"], match["loser_name"], players_elo_local, tourney_k)
        
        # if idx == df.index[0]:
        #     print(f"First match: {match['winner_name']} ELO = {player_elo}, {match['loser_name']} ELO = {opponent_elo}")

        df.at[idx, "player_elo"] = player_elo
        df.at[idx, "opponent_elo"] = opponent_elo

    return df
