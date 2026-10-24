"""Download TennisMyLife data and build the model-ready combined dataset.

The remote manifest is mirrored under ``data/raw`` (including nested folders
such as ``atp_quali``).  The feature pipeline intentionally consumes only the
top-level yearly tour files (for example ``2026.csv``), matching the dataset
the project used before the downloader was added.  The processed result remains
at ``data/processed/combined.csv``.
"""

import json
import re
import ssl
import sys
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from features import add_raw_data
from features import create_two_rows
from features import score_dominance


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "combined.csv"
DATA_FILES_API = "https://stats.tennismylife.org/api/data-files"
YEARLY_TOUR_FILE = re.compile(r"^\d{4}\.csv$")
OPEN_ERA_START_YEAR = 1968
USER_AGENT = "Tennis-Prediction data loader"

try:
    import certifi

    SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CONTEXT = ssl.create_default_context()


def _is_live_ongoing_file(name):
    """Return whether a manifest entry is expected to change during download."""
    return PurePosixPath(name).name.endswith("ongoing_tourneys.csv")


def _open_url(url):
    """Open a data URL with a user agent and a finite timeout."""
    return urlopen(
        Request(url, headers={"User-Agent": USER_AGENT}),
        timeout=60,
        context=SSL_CONTEXT,
    )


def _safe_destination(name):
    """Map a manifest name below data/raw without allowing path traversal."""
    relative_path = PurePosixPath(name)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise ValueError(f"Unsafe filename in data manifest: {name!r}")
    return RAW_DIRECTORY.joinpath(*relative_path.parts)


def download_raw_data():
    """Mirror every file in the TennisMyLife manifest into data/raw."""
    RAW_DIRECTORY.mkdir(parents=True, exist_ok=True)

    with _open_url(DATA_FILES_API) as response:
        manifest = json.load(response)

    files = manifest.get("files", [])
    if not files:
        raise RuntimeError("The TennisMyLife data manifest did not contain any files")

    downloaded = 0
    skipped = 0
    for file_info in files:
        destination = _safe_destination(file_info["name"])
        expected_size = int(file_info["size"])

        # A matching size makes repeated loader runs quick and resumable.
        if destination.is_file() and destination.stat().st_size == expected_size:
            skipped += 1
            continue

        destination.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = destination.with_name(f"{destination.name}.part")

        try:
            with _open_url(file_info["url"]) as response:
                with temporary_path.open("wb") as output:
                    while chunk := response.read(1024 * 1024):
                        output.write(chunk)

            actual_size = temporary_path.stat().st_size
            if actual_size != expected_size:
                if not _is_live_ongoing_file(file_info["name"]) or actual_size == 0:
                    raise RuntimeError(
                        f"Download size mismatch for {file_info['name']}: "
                        f"expected {expected_size}, received {actual_size}"
                    )

                # These files are regenerated while tournaments are in progress,
                # so their size can legitimately change after the manifest was
                # fetched. urllib still verifies the HTTP response itself; only
                # the now-stale manifest size is ignored for these live files.
                print(
                    f"Accepted updated live file {file_info['name']} "
                    f"({actual_size} bytes; manifest listed {expected_size})"
                )
            temporary_path.replace(destination)
            downloaded += 1
            print(f"Downloaded {file_info['name']}")
        finally:
            temporary_path.unlink(missing_ok=True)

    print(
        f"Raw data ready in {RAW_DIRECTORY} "
        f"({downloaded} downloaded, {skipped} already current)"
    )


def load_yearly_tour_data():
    """Load the top-level yearly ATP tour CSVs used by the feature pipeline."""
    yearly_files = sorted(
        path
        for path in RAW_DIRECTORY.iterdir()
        if (
            path.is_file()
            and YEARLY_TOUR_FILE.fullmatch(path.name)
            and int(path.stem) >= OPEN_ERA_START_YEAR
        )
    )
    if not yearly_files:
        raise RuntimeError(f"No yearly tour CSV files found in {RAW_DIRECTORY}")

    frames = [pd.read_csv(path) for path in yearly_files]
    expected_total_rows = sum(len(frame) for frame in frames)
    all_data = pd.concat(frames, ignore_index=True)

    all_data["tourney_date"] = pd.to_datetime(
        all_data["tourney_date"], format="%Y%m%d"
    )
    all_data["match_num"] = pd.to_numeric(all_data["match_num"], errors="coerce")

    games = all_data["score"].apply(
        lambda score: pd.Series(score_dominance.get_player_games(score))
    )
    all_data["winner_games"] = pd.to_numeric(games[0], errors="coerce")
    all_data["loser_games"] = pd.to_numeric(games[1], errors="coerce")

    serve_stat_columns = [
        "w_svpt",
        "w_1stIn",
        "w_1stWon",
        "w_2ndWon",
        "w_SvGms",
        "w_bpSaved",
        "w_bpFaced",
        "l_svpt",
        "l_1stIn",
        "l_1stWon",
        "l_2ndWon",
        "l_SvGms",
        "l_bpSaved",
        "l_bpFaced",
    ]
    for column in serve_stat_columns:
        all_data[column] = pd.to_numeric(all_data[column], errors="coerce")

    return all_data, expected_total_rows


def build_combined_data():
    """Run feature engineering and save data/processed/combined.csv."""
    all_data, expected_total_rows = load_yearly_tour_data()
    all_data = all_data.sort_values(
        ["tourney_date", "tourney_id", "match_num"]
    ).reset_index(drop=True)

    print(
        f"Loaded {len(all_data)} rows | date range: "
        f"{all_data['tourney_date'].min().date()} to "
        f"{all_data['tourney_date'].max().date()}"
    )

    all_data = add_raw_data.add_raw_data_to_csv(all_data)
    print(f"Features added: {len(all_data.columns)} columns")

    all_data = create_two_rows.create_two_rows(all_data)
    print(f"Reshaped to {len(all_data)} rows (expected {expected_total_rows * 2})")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    all_data.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved to {OUTPUT_PATH} — shape: {all_data.shape}")


def main():
    download_raw_data()
    build_combined_data()


if __name__ == "__main__":
    main()
