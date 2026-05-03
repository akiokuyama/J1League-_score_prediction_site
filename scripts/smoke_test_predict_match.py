"""Smoke test for the single-match prediction function."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import warnings
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "soccer_score_app_matplotlib"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
warnings.filterwarnings(
    "ignore",
    message="Could not find the number of physical cores.*",
    category=UserWarning,
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.predict.feature_preprocess import resolve_dataset_path
from src.predict.predict_match import predict_match


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="単一試合予測のスモークテスト")
    parser.add_argument("--home", help="ホームチーム名")
    parser.add_argument("--away", help="アウェイチーム名")
    parser.add_argument("--date", help="試合日 YYYY-MM-DD")
    return parser.parse_args()


def default_match() -> tuple[str, str, str | None]:
    dataset_path = resolve_dataset_path()
    df = pd.read_csv(dataset_path)
    if df.empty:
        raise ValueError(f"Dataset is empty: {dataset_path}")
    row = df.tail(1).iloc[0]
    return str(row["Home"]), str(row["Away"]), str(row["Date"]) if "Date" in row else None


def main() -> int:
    args = parse_args()
    try:
        home, away, match_date = args.home, args.away, args.date
        if not home or not away:
            home, away, default_date = default_match()
            match_date = match_date or default_date

        result = predict_match(home_team=home, away_team=away, match_date=match_date)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("[OK] 単一試合予測テスト成功")
        return 0
    except Exception as exc:
        print(f"[ERROR] 単一試合予測テスト失敗: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
