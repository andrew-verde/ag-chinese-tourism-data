#!/usr/bin/env python3
"""Run the Fukui Xiaohongshu pull and analysis as one command."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run_step(command: list[str]) -> None:
    print("\n$ " + " ".join(command))
    subprocess.run(command, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Fukui Xiaohongshu collection and analysis.")
    parser.add_argument(
        "--keyword",
        action="append",
        help="Xiaohongshu search keyword. Repeat or pass comma-separated values. Defaults to the scraper's Fukui keyword set.",
    )
    parser.add_argument("--raw-output", default="data/raw/social/fukui_xhs_reviews.csv", help="CSV created by the data pull")
    parser.add_argument("--analysis-output", default="data/processed/fukui_xhs_analysis.csv", help="CSV created by the analysis step")
    parser.add_argument("--scrolls", type=int, default=16, help="Number of scroll steps during the pull")
    parser.add_argument("--delay", type=float, default=1.8, help="Seconds to wait after each scroll")
    parser.add_argument("--no-growth-limit", type=int, default=4, help="Stop a keyword after this many consecutive scrolls add no new notes")
    parser.add_argument("--top", type=int, default=20, help="Number of top keywords to print in analysis")
    parser.add_argument("--headless", action="store_true", help="Run the browser without showing a window")
    parser.add_argument("--skip-pull", action="store_true", help="Run only analysis using an existing raw CSV")
    parser.add_argument("--replace", action="store_true", help="Replace raw output instead of merging with existing rows")
    parser.add_argument("--allow-shrink", action="store_true", help="Allow an intentional replace with fewer rows")
    parser.add_argument("--allow-empty", action="store_true", help="Allow writing an intentionally empty raw CSV")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent

    if not args.skip_pull:
        pull_command = [
            sys.executable,
            "-m", "src.scrapers.xhs_fukui_reviews",
            "--output",
            args.raw_output,
            "--scrolls",
            str(args.scrolls),
            "--delay",
            str(args.delay),
            "--no-growth-limit",
            str(args.no_growth_limit),
        ]
        for keyword in args.keyword or []:
            pull_command.extend(["--keyword", keyword])
        if args.headless:
            pull_command.append("--headless")
        if args.replace:
            pull_command.append("--replace")
        if args.allow_shrink:
            pull_command.append("--allow-shrink")
        if args.allow_empty:
            pull_command.append("--allow-empty")
        run_step(pull_command)

    analysis_command = [
        sys.executable,
        "-m", "src.analysis.xhs_fukui_analysis",
        "--input",
        args.raw_output,
        "--output",
        args.analysis_output,
        "--top",
        str(args.top),
    ]
    run_step(analysis_command)


if __name__ == "__main__":
    main()
