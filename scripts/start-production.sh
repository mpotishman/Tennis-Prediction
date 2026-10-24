#!/bin/sh
set -eu

python scripts/prepare_runtime_data.py
exec npm start
