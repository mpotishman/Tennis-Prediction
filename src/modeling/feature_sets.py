FEATURE_SETS = {
    "ranking_only": [
        "rank_gap",
        "rank_points_gap",
    ],
    "elo_only": [
        "elo_gap",
    ],
    "surface_elo_only": [
        "surface_elo_gap",
    ],
    "elo_surface": [
        "elo_gap",
        "surface_elo_gap",
    ],
    "form_only": [
        "winrate_gap",
        "h2h_gap",
        "days_rest_gap",
    ],
    "serve_only": [
        "hold_rate_gap",
        "first_srv_win_rate_gap",
        "second_srv_win_rate_gap",
    ],
    # None tells training() to use its default full numeric feature set.
    "full": None,
}

DEFAULT_FEATURE_SET = "full"
ALL_FEATURE_SET_NAMES = [
    "ranking_only",
    "elo_only",
    "surface_elo_only",
    "elo_surface",
    "form_only",
    "serve_only",
    "full",
]


def available_feature_sets():
    return list(FEATURE_SETS.keys())


def selected_feature_set_names(feature_set):
    if feature_set == "all":
        return ALL_FEATURE_SET_NAMES

    if feature_set not in FEATURE_SETS:
        available = ", ".join(available_feature_sets() + ["all"])
        raise ValueError(f"Unknown feature set: {feature_set}. Available options: {available}")

    return [feature_set]


def feature_columns_for(feature_set):
    if feature_set not in FEATURE_SETS:
        available = ", ".join(available_feature_sets())
        raise ValueError(f"Unknown feature set: {feature_set}. Available options: {available}")

    columns = FEATURE_SETS[feature_set]
    if columns is None:
        return None

    return list(columns)
