#!/usr/bin/env python3
"""Compare reproduced experiment summaries with numerical tolerance."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


def compare(expected: Any, actual: Any, path: str = "root") -> list[str]:
    errors: list[str] = []
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            return [f"{path}: expected object, found {type(actual).__name__}"]
        for key in expected.keys() | actual.keys():
            child = f"{path}.{key}"
            if key not in expected:
                errors.append(f"{child}: unexpected key")
            elif key not in actual:
                errors.append(f"{child}: missing key")
            else:
                errors.extend(compare(expected[key], actual[key], child))
        return errors

    if isinstance(expected, float):
        if not isinstance(actual, (int, float)) or not math.isclose(
            expected,
            float(actual),
            rel_tol=1e-10,
            abs_tol=1e-12,
        ):
            errors.append(f"{path}: expected {expected!r}, found {actual!r}")
        return errors

    if expected != actual:
        errors.append(f"{path}: expected {expected!r}, found {actual!r}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("expected", type=Path)
    parser.add_argument("actual", type=Path)
    args = parser.parse_args()

    expected = json.loads(args.expected.read_text(encoding="utf-8"))
    actual = json.loads(args.actual.read_text(encoding="utf-8"))
    errors = compare(expected, actual)
    if errors:
        raise SystemExit("Result verification failed:\n" + "\n".join(errors))
    print("Reproduced summary matches committed reference within tolerance.")


if __name__ == "__main__":
    main()
