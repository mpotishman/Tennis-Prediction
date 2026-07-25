import pandas as pd

def walk_forward_year_splits(df, start_year, end_year, date_col="tourney_date"):
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])
    df = df.sort_values(date_col).reset_index(drop=True)

    splits = []

    for test_year in range(start_year, end_year + 1):
        test_start = pd.Timestamp(f"{test_year}-01-01")
        test_end = pd.Timestamp(f"{test_year + 1}-01-01")

        train_df = df[df[date_col] < test_start].copy()

        test_df = df[
            (df[date_col] >= test_start)
            & (df[date_col] < test_end)
        ].copy()

        if train_df.empty or test_df.empty:
            continue

        splits.append({
            "test_year": test_year,
            "test_start": test_start,
            "test_end": test_end,
            "train_df": train_df,
            "test_df": test_df,
        })

    return splits


def validate_time_split(split, date_col="tourney_date"):

    train_df = split["train_df"]
    test_df = split["test_df"]

    latest_train_date = train_df[date_col].max()
    earliest_test_date = test_df[date_col].min()

    if latest_train_date >= earliest_test_date:
        raise ValueError(
            f"Temporal leakage: train date {latest_train_date} "
            f"is not before test date {earliest_test_date}"
        )