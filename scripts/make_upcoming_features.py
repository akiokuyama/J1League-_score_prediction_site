"""Generate upcoming match feature rows."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.features.build_match_features import build_match_features
from src.features.build_upcoming_features import build_upcoming_features
from src.features.validation import validate_feature_frame

import joblib
import pandas as pd


def write_source_report(path: Path, output_path: Path) -> dict[str, object]:
    if not path.exists():
        return {"path": str(output_path), "rows": 0}
    sources = pd.read_csv(path)
    rows = []
    for col in sources.columns:
        counts = sources[col].value_counts(dropna=False).to_dict()
        total = len(sources)
        actual = sum(count for label, count in counts.items() if str(label).startswith("actual"))
        fallback = sum(count for label, count in counts.items() if str(label).startswith("fallback"))
        rows.append(
            {
                "column": col,
                "total_rows": total,
                "actual_count": actual,
                "fallback_count": fallback,
                "actual_rate": actual / total if total else 0,
                "fallback_rate": fallback / total if total else 0,
                "top_source": max(counts, key=counts.get) if counts else "",
                "source_counts": json.dumps(counts, ensure_ascii=False, sort_keys=True),
            }
        )
    report = pd.DataFrame(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(output_path, index=False)
    return {
        "path": str(output_path),
        "rows": int(len(report)),
        "overall_actual_rate": float(report["actual_count"].sum() / report["total_rows"].sum()) if not report.empty else 0,
        "overall_fallback_rate": float(report["fallback_count"].sum() / report["total_rows"].sum()) if not report.empty else 0,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="未来試合用特徴量を生成します")
    parser.add_argument("--season", type=int, default=2026)
    parser.add_argument("--category", default="100yj1")
    return parser.parse_args()


def main() -> int:
    parse_args()
    match_df = build_match_features()
    upcoming_df = build_upcoming_features()
    model_features = joblib.load(PROJECT_ROOT / "Models" / "model_features.pkl")
    validation = validate_feature_frame(upcoming_df, model_features)
    source_report = write_source_report(
        PROJECT_ROOT / "data" / "features" / "upcoming_features_2026_sources.csv",
        PROJECT_ROOT / "data" / "features" / "upcoming_features_2026_source_report.csv",
    )
    print(
        json.dumps(
            {
                "match_features_rows": int(len(match_df)),
                "upcoming_features_rows": int(len(upcoming_df)),
                "validation": validation,
                "source_report": source_report,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
