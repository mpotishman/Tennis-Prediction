
def calculate_days_rest(match, player_name, last_matchday):
    if player_name not in last_matchday:
        last_matchday[player_name] = match["tourney_date"]
        return None

    previous_matchday = last_matchday[player_name]
    current_matchday = match["tourney_date"]

    days_rest = abs((current_matchday - previous_matchday).days)
    last_matchday[player_name] = current_matchday

    return days_rest


def add_days_rest_to_csv(df):
    last_matchday = {}
    for idx, match in df.iterrows():
        df.at[idx, "winner_days_rest"] = calculate_days_rest(match, match["winner_name"], last_matchday)
        df.at[idx, "loser_days_rest"] = calculate_days_rest(match, match["loser_name"], last_matchday)
    return df
