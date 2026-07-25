import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from evaluation.backtest_runner import run_backtest
from modeling.feature_sets import DEFAULT_FEATURE_SET, available_feature_sets


def parse_args():
    parser = argparse.ArgumentParser(description="Tennis Predictor command-line tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    backtest_parser = subparsers.add_parser(
        "backtest",
        help="Run a walk-forward historical backtest.",
    )
    backtest_parser.add_argument("--start-year", type=int, default=2019)
    backtest_parser.add_argument("--end-year", type=int, default=2025)
    backtest_parser.add_argument(
        "--model-type",
        choices=["xgboost", "random_forest", "logistic"],
        default="xgboost",
    )
    backtest_parser.add_argument(
        "--feature-set",
        choices=available_feature_sets() + ["all"],
        default=DEFAULT_FEATURE_SET,
        help="Named feature group to backtest, or 'all' to compare every group.",
    )
    backtest_parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "outputs" / "backtests"),
    )

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "backtest":
        result = run_backtest(
            start_year=args.start_year,
            end_year=args.end_year,
            model_type=args.model_type,
            feature_set=args.feature_set,
            output_dir=args.output_dir,
        )

        print("\nBacktest complete.")
        print(f"Predictions: {result['predictions_path']}")
        print(f"Summary: {result['summary_path']}")
        print("\nSummary metrics:")
        print(result["summary"].to_string(index=False))


if __name__ == "__main__":
    main()
