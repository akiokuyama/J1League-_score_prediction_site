"""Validate past prediction result JSON used by the app."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate past prediction results JSON")
    parser.add_argument("--path", default="outputs/past_prediction_results.json")
    return parser.parse_args()


def validate_past_prediction_results(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        raise ValueError(f"missing file: {target}")
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    if "matches" not in data:
        raise ValueError("missing matches key")
    if not isinstance(data["matches"], list):
        raise ValueError("matches must be a list")
    return data


def main() -> int:
    args = parse_args()
    try:
        data = validate_past_prediction_results(args.path)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] past prediction result validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"[OK] past prediction result matches: {len(data.get('matches', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
