#!/usr/bin/env python3
"""Run the fixed-seed CERBERUS Vigil experiment and write all outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from cerberus_vigil import ExperimentConfig, run_monte_carlo
from cerberus_vigil.io import write_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parent / "results",
        help="output directory (default: ./results)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = ExperimentConfig()
    summary, representative, levels = run_monte_carlo(config)
    write_outputs(args.out, config, summary, representative, levels)
    print(json.dumps(summary.to_dict(), indent=2))


if __name__ == "__main__":
    main()
