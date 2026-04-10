def winrate_last_10_matches(match, player_name, history_dict):
    # initialize history if player not seen before
    if player_name not in history_dict:
        history_dict[player_name] = []

    # get last 10 results BEFORE this match
    last_10 = history_dict[player_name][-10:]

    matches_played = len(last_10)

    # neutral starting value if no history
    if matches_played == 0:
        winrate_last_10 = 0.5
    else:
        winrate_last_10 = sum(last_10) / matches_played

    # determine result of current match
    if player_name == match["winner_name"]:
        result = 1
    else:
        result = 0

    # update history AFTER computing feature
    history_dict[player_name].append(result)

    return winrate_last_10

def add_winrate_last_10_to_csv(df):
    player_history = {}

    for idx, match in df.iterrows():

        player_winrate_last_10 = winrate_last_10_matches(
            match,
            match["winner_name"],
            player_history
        )

        opponent_winrate_last_10 = winrate_last_10_matches(
            match,
            match["loser_name"],
            player_history
        )

        df.at[idx, "player_winrate_last_10"] = player_winrate_last_10
        df.at[idx, "opponent_winrate_last_10"] = opponent_winrate_last_10

    return df

def add_winrate_gap(df):
    df["winrate_gap"] = (
        df["player_winrate_last_10"]
        - df["opponent_winrate_last_10"]
    )
    return df