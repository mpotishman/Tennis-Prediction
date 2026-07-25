import random
from collections import defaultdict, Counter

# find slightly different p serve values so that the predicted win percentage of the player matches the models win percentage
def calibrate_p_serve(p1_serve, p2_serve, target_win_pct, n=3000):
    """Find p_serve values whose simulated win % matches the model's target."""
    avg = (p1_serve + p2_serve) / 2      # keep the serve LEVEL (shape)
    lo, hi = -0.25, 0.25                 # search the GAP (who wins)

    d = 0.0
    for _ in range(18):                  # binary search
        d = (lo + hi) / 2
        match = {
            "player_name": "A", "opponent_name": "B",
            "player_p_serve": avg + d,
            "opponent_p_serve": avg - d,
        }
        wins = sum(score_simulator(match)[0] == "A" for _ in range(n))
        win_pct = 100 * wins / n

        if win_pct < target_win_pct:
            lo = d       # player needs a bigger edge
        else:
            hi = d

    return avg + d, avg - d

def score_simulator(match, best_of=5):
    players_expected_sets, opponents_expected_sets = 0, 0
    sets_to_win = best_of // 2 + 1
    end_predicted_score = []

    turn = 0 if random.random() < 0.5 else 1

    while True:
        final_set = (players_expected_sets == best_of // 2
                     and opponents_expected_sets == best_of // 2)

        # set_simulator returns who opens the next set, so the serve rotation
        # carries on game-by-game across sets like real tennis
        winner, expected_score, turn = set_simulator(
            match["player_p_serve"], match["opponent_p_serve"], turn, final_set
        )
        end_predicted_score.append(expected_score)

        if winner == "player":
            players_expected_sets += 1
        else:
            opponents_expected_sets += 1

        if players_expected_sets == sets_to_win:
            return match["player_name"], end_predicted_score
        if opponents_expected_sets == sets_to_win:
            return match["opponent_name"], end_predicted_score
            
    
    
    
def set_simulator(player_serve_percent, opponent_serve_percent, turn, final_set=False):
    player_games, opponent_games = 0, 0

    while True:
        # --- play ONE game with the current server ---
        if turn == 0:
            game_winner = simulate_game(player_serve_percent)
            # server == player here
            if game_winner == "server":
                player_games += 1
            else:
                opponent_games += 1
        else:
            game_winner = simulate_game(opponent_serve_percent)
            # server == opponent here
            if game_winner == "server":
                opponent_games += 1
            else:
                player_games += 1

        turn = 1 - turn  # serve alternates every game

        # --- tiebreak at 6-6 ---
        if player_games == 6 and opponent_games == 6:
            # `turn` now points at the would-be next server, so they serve the
            # tiebreak first; whoever received first in the tiebreak opens the
            # next set, which is 1 - turn
            winner, loser_tiebreak_points = tiebreak(
                player_serve_percent, opponent_serve_percent, final_set, turn
            )
            if winner == "player":
                player_games += 1
            else:
                opponent_games += 1
            return winner, f"{player_games}-{opponent_games}({loser_tiebreak_points})", 1 - turn

        # --- normal set win: 6+ games AND lead by 2 ---
        # `turn` was already flipped past the last game, so it is the correct
        # opener for the next set
        if player_games >= 6 and player_games - opponent_games >= 2:
            return "player", f"{player_games}-{opponent_games}", turn
        if opponent_games >= 6 and opponent_games - player_games >= 2:
            return "opponent", f"{player_games}-{opponent_games}", turn
        

def simulate_game(server_win_prob):
    server_pts, returner_pts = 0, 0
    while True:
        if simulate_point(server_win_prob):
            server_pts += 1
        else:
            returner_pts += 1
        if server_pts >= 4 and server_pts - returner_pts >= 2:
            return "server"
        if returner_pts >= 4 and returner_pts - server_pts >= 2:
            return "returner"

def simulate_point(server_win_prob):
    return random.random() < server_win_prob   # True = server won the point

# simulate a tiebreak
def tiebreak(player_serve_percent, opponent_serve_percent, final_set, first_server=0):
    if final_set:
        target = 10
    else:
        target = 7

    point_num = 1
    players_expected_point, opponents_expected_point = 0,0

    while True:
        if (point_num // 2) % 2 == 0:
            turn = first_server        # whoever's rotation turn it was at 6-6
        else:
            turn = 1 - first_server
            
        if turn == 0:
            if simulate_point(player_serve_percent):
                players_expected_point += 1
            else:
                opponents_expected_point += 1
        else:
            if simulate_point(opponent_serve_percent):
                opponents_expected_point += 1
            else:
                players_expected_point += 1    
                
        point_num += 1    
        
        if players_expected_point >= target and players_expected_point - opponents_expected_point >= 2:
            return "player", opponents_expected_point
        elif opponents_expected_point >= target and opponents_expected_point - players_expected_point >= 2:
            return "opponent", players_expected_point
        
        
# this function runs the simulated score thousands of time
def run_multiple_score_predictions(match, n=20000):
    scores = Counter()       # (winner, scoreline) -> count
    wins = Counter()         # winner -> count
    set_counts = Counter()   # number of sets -> count

    for _ in range(n):
        winner, scoreline = score_simulator(match)
        scores[(winner, tuple(scoreline))] += 1
        wins[winner] += 1
        set_counts[len(scoreline)] += 1

    p1, p2 = match["player_name"], match["opponent_name"]
    top_winner = p1 if wins[p1] >= wins[p2] else p2

    # how many sets the most likely winner usually needs
    winner_set_counts = Counter()
    for (w, sc), c in scores.items():
        if w == top_winner:
            winner_set_counts[len(sc)] += c
    most_sets, _ = winner_set_counts.most_common(1)[0]

    candidates = [
        (sc, c) for (w, sc), c in scores.items()
        if w == top_winner and len(sc) == most_sets
    ]
    top_count = sum(c for _, c in candidates)

    rng = random.Random(f"{p1} vs {p2} in {most_sets}")
    top_scoreline = rng.choices(
        [sc for sc, _ in candidates],
        weights=[c for _, c in candidates],
    )[0]

    return {
        "most_likely_winner": top_winner,
        "most_likely_score":  " ".join(top_scoreline),
        "most_likely_pct":    round(100 * top_count / n, 1),
        "player_win_pct":     round(100 * wins[p1] / n, 1),
        "opponent_win_pct":   round(100 * wins[p2] / n, 1),
        "most_likely_sets":   most_sets,
        "set_distribution": {
            sets: round(100 * count / n, 1)
            for sets, count in sorted(set_counts.items())
        },
        "simulations": n,
    }

# if __name__ == "__main__":
#     def summarise(p1, p2, label, n=20000):
#         match = {
#             "player_name": "A", "opponent_name": "B",
#             "player_p_serve": p1, "opponent_p_serve": p2,
#         }
#         wins = Counter()
#         scores = Counter()
#         set_counts = Counter()
#         tb_matches = 0
#         tb_examples = Counter()

#         for _ in range(n):
#             winner, scoreline = score_simulator(match)
#             wins[winner] += 1
#             scores[(winner, tuple(scoreline))] += 1
#             set_counts[len(scoreline)] += 1

#             if any("(" in s for s in scoreline):        # this match had a tiebreak
#                 tb_matches += 1
#                 for s in scoreline:
#                     if "(" in s:
#                         tb_examples[s] += 1

#         print(f"\n{label}  (A={p1}, B={p2})")
#         print(f"  A wins {100*wins['A']/n:.1f}%   B wins {100*wins['B']/n:.1f}%")
#         print("  sets:", {k: f"{100*v/n:.0f}%" for k, v in sorted(set_counts.items())})
#         print(f"  matches with a tiebreak: {100*tb_matches/n:.0f}%")
#         print("  example tiebreak sets:", tb_examples.most_common(8))
#         for (w, sc), c in scores.most_common(5):
#             print(f"    {w}: {' '.join(sc)}   {100*c/n:.1f}%")

#     summarise(0.63, 0.63, "Even")
#     summarise(0.70, 0.58, "Clear favourite")
        

    