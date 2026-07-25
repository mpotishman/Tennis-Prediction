
def get_player_games(score):
    if not isinstance(score, str) or not score.strip():
        return None, None
    
    winner_games, loser_games = 0,0
    
    for set_score in score.split():
        set_score = set_score.split("(")[0]   # strip tiebreak points -> "6-7"
        games = set_score.split("-")
        
        # games eg =  ["5","7"]
        
        if len(games) != 2 or not games[0].isdigit() or not games[1].isdigit():
            return None, None
        
        winner_games += int(games[0])
        loser_games += int(games[1])
        
    return winner_games, loser_games


