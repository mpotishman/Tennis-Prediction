"""Download the processed dataset when it is not already present.

The production image deliberately excludes the large dataset. A deployment host
provides TENNIS_DATA_URL and this script installs the file before Next.js starts.
"""

from __future__ import annotations

import gzip
import hashlib
import os
import shutil
import sys
import tempfile
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TARGET = Path(
    os.environ.get(
        "TENNIS_DATA_PATH",
        PROJECT_ROOT / "data" / "processed" / "combined.csv",
    )
).expanduser()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    if TARGET.is_file() and TARGET.stat().st_size > 0:
        print(f"Using tennis data at {TARGET}")
        return

    source_url = os.environ.get("TENNIS_DATA_URL")
    if not source_url:
        raise SystemExit(
            "Processed tennis data is missing. Set TENNIS_DATA_URL to a public "
            "combined.csv or combined.csv.gz download URL."
        )

    TARGET.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        source_url,
        headers={"User-Agent": "Tennis-Predictor/1.0"},
    )
    authorization = os.environ.get("TENNIS_DATA_AUTH_HEADER")
    if authorization:
        request.add_header("Authorization", authorization)

    with tempfile.TemporaryDirectory(dir=TARGET.parent) as temporary_directory:
        downloaded = Path(temporary_directory) / "download"
        prepared = Path(temporary_directory) / "combined.csv"

        print("Downloading processed tennis data...")
        with urllib.request.urlopen(request, timeout=300) as response:
            with downloaded.open("wb") as destination:
                shutil.copyfileobj(response, destination)

        is_gzip = urlparse(source_url).path.lower().endswith(".gz")
        if is_gzip:
            print("Decompressing processed tennis data...")
            with gzip.open(downloaded, "rb") as source:
                with prepared.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        else:
            downloaded.replace(prepared)

        expected_hash = os.environ.get("TENNIS_DATA_SHA256", "").strip().lower()
        if expected_hash:
            actual_hash = sha256(prepared)
            if actual_hash != expected_hash:
                raise SystemExit(
                    "Downloaded dataset checksum did not match "
                    f"TENNIS_DATA_SHA256 (received {actual_hash})."
                )

        if prepared.stat().st_size == 0:
            raise SystemExit("The downloaded tennis dataset was empty.")

        prepared.replace(TARGET)

    print(f"Tennis data ready at {TARGET}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Could not prepare tennis data: {error}", file=sys.stderr)
        raise SystemExit(1) from error
