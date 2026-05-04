from collections import Counter
import contextlib
import io
import json
import random

import pandas as pd

from features import build_player_lookup
from predict import DATA_PATH, ao2026_r1_ordered_full_names
from simulate import run_tournament_once
from train import training

SIMULATION_COUNT = 1000
RANDOM_SEED = 42


def main():
    random.seed(RANDOM_SEED)
    df = pd.read_csv(DATA_PATH)

    with contextlib.redirect_stdout(io.StringIO()):
        model, scaler, features = training(df)

    player_lookup_cache = build_player_lookup.build_latest_player_lookup(df)
    probability_cache = {}
    champion_counts = Counter()

    for _ in range(SIMULATION_COUNT):
        winner = run_tournament_once(
            ao2026_r1_ordered_full_names,
            model,
            scaler,
            df,
            features,
            player_lookup_cache,
            probability_cache,
        )
        champion_counts[winner] += 1

    winner, _ = champion_counts.most_common(1)[0]
    print(json.dumps({"winner": winner}))


if __name__ == "__main__":
    main()
