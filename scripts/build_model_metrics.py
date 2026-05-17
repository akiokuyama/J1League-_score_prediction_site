"""Build local-only model metrics from past prediction results."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "soccer_score_app_matplotlib"))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.evaluation.model_metrics import build_model_metrics, load_past_prediction_results, write_model_metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ローカル確認用のモデル評価指標JSONを生成します。Streamlit画面やユーザー向け表示には使用しません。")
    parser.add_argument("--past-results", default="outputs/past_prediction_results.json")
    parser.add_argument("--output", default="outputs/local/model_metrics.json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    past_results = load_past_prediction_results(args.past_results)
    metrics = build_model_metrics(past_results)
    output_path = write_model_metrics(metrics, args.output)
    print(json.dumps({"output": str(output_path), "evaluated_matches": metrics.get("evaluated_matches"), "metrics": metrics.get("metrics")}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
