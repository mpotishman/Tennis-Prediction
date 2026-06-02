# App-wide constants: ELO K-values, data path, and legacy date references used
# by the player lookup feature builder.

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "combined.csv"

# Legacy date constants still referenced by features/build_player_lookup.py.
AO_2026_START = "2026-01-18"
AO_2026_END = "2026-02-02"
ROLAND_GARROS_START = "2026-05-18"

TOURNAMENT_K_VALUES = {
    'G': 1.00,
    'F': 0.90,
    'M': 0.85,
    'O': 0.80,
    'A': 0.75,
    '500': 0.75,
    '250': 0.70,
    'D': 0.60,
}
