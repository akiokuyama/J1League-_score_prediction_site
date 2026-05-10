"""Evaluate whether Weather features should be retained."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "soccer_score_app_matplotlib"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.weather_ablation import evaluate_weather_ablation


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="天候特徴量の有無による評価比較")
    parser.add_argument("--dataset", default="Data/ML_dataset.csv")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        result = evaluate_weather_ablation(args.dataset)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"[ERROR] 天候特徴量評価に失敗しました: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
