"""
AI Finance Controller — CLI Entry Point
RazorPay Hackathon Track 04

Usage:
    python main.py                     # run with default seed=42
    python main.py --seed 123          # custom seed
    python main.py --no-verbose        # quiet mode
    python main.py --output-dir ./out  # custom output directory
"""
from __future__ import annotations

import sys
import os

# Ensure project root is on the path regardless of where python is invoked from
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv optional; env vars can be set directly


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Finance Controller — RazorPay Hackathon Track 04"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for synthetic data generation (default: 42)",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        help="Directory for output files (default: output/)",
    )
    parser.add_argument(
        "--no-verbose",
        action="store_true",
        help="Suppress stage-by-stage progress output",
    )
    args = parser.parse_args()

    from src.pipeline import run_pipeline

    report = run_pipeline(
        seed=args.seed,
        output_dir=args.output_dir,
        verbose=not args.no_verbose,
    )

    # Exit with non-zero code if there are HIGH priority unresolved exceptions
    high_count = sum(
        1 for e in report.exceptions if e.priority.value == "HIGH"
    )
    if high_count > 0:
        print(f"\n⚠  {high_count} HIGH-priority exceptions require attention.")
        sys.exit(1)
    else:
        print("\n✓ Pipeline complete. No HIGH-priority exceptions.")
        sys.exit(0)


if __name__ == "__main__":
    main()
