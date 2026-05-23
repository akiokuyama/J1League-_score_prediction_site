"""Validate public prediction output JSON files."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


REQUIRED_MATCH_KEYS = {"match_id", "home_team", "away_team", "predicted_score", "result_probabilities"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate prediction output JSON files")
    parser.add_argument("--latest", default="outputs/latest_predictions.json")
    parser.add_argument("--all-unplayed", default="outputs/all_unplayed_predictions.json")
    return parser.parse_args()


def load_json(path: str | Path) -> dict[str, Any]:
    target = Path(path)
    if not target.exists():
        raise ValueError(f"missing file: {target}")
    data = json.loads(target.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"top-level JSON must be an object: {target}")
    return data


def contains_weather_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            if key_text == "Weather" or key_text.startswith("Weather_"):
                return True
            if contains_weather_key(child):
                return True
    elif isinstance(value, list):
        return any(contains_weather_key(item) for item in value)
    return False


def validate_latest(path: str | Path) -> dict[str, Any]:
    data = load_json(path)
    matches = data.get("matches")
    if not isinstance(matches, list) or not matches:
        raise ValueError("latest predictions must contain non-empty matches")
    if contains_weather_key(data):
        raise ValueError("latest predictions contain Weather keys")
    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            raise ValueError(f"match must be an object: index={index}")
        missing = REQUIRED_MATCH_KEYS - set(match)
        if missing:
            raise ValueError(f"match is missing required keys: index={index}, missing={sorted(missing)}")
    return data


def validate_all_unplayed(path: str | Path) -> dict[str, Any]:
    data = load_json(path)
    matches = data.get("matches")
    if not isinstance(matches, list):
        raise ValueError("all-unplayed predictions must contain matches list")
    return data


def main() -> int:
    args = parse_args()
    try:
        latest = validate_latest(args.latest)
        all_unplayed = validate_all_unplayed(args.all_unplayed)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] prediction output validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"[OK] latest matches: {len(latest.get('matches', []))}")
    print(f"[OK] all_unplayed matches: {len(all_unplayed.get('matches', []))}")
    warnings = latest.get("warnings") or []
    if warnings:
        print(f"[WARN] latest warnings: {warnings}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
