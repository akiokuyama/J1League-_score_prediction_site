"""Evaluate generated past prediction results."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import OUTPUT_DIR


def build_model_metrics(past_results: dict[str, Any]) -> dict[str, Any]:
    """Build summary metrics from past prediction result records."""
    matches = [match for match in past_results.get("matches", []) if isinstance(match, dict)]
    evaluated = [_evaluate_match(match) for match in matches]
    evaluated = [item for item in evaluated if item is not None]
    total = len(evaluated)

    score_hits = sum(1 for item in evaluated if item["score_hit"])
    result_hits = sum(1 for item in evaluated if item["result_hit"])
    home_abs_error = sum(item["home_abs_error"] for item in evaluated)
    away_abs_error = sum(item["away_abs_error"] for item in evaluated)
    sections = sorted({item["matchweek"] for item in evaluated if item["matchweek"] is not None})
    dates = sorted({item["date"] for item in evaluated if item["date"]})
    score_exact_match_rate = _safe_divide(score_hits, total)
    home_goal_mae = _safe_divide(home_abs_error, total)
    away_goal_mae = _safe_divide(away_abs_error, total)
    result_accuracy = _safe_divide(result_hits, total)

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "last_updated": datetime.now().isoformat(timespec="seconds"),
        "source": "outputs/past_prediction_results.json",
        "season": past_results.get("season"),
        "league": past_results.get("league"),
        "evaluated_matches": total,
        "sample_size": total,
        "result_accuracy": result_accuracy,
        "score_exact_match_rate": score_exact_match_rate,
        "home_goal_mae": home_goal_mae,
        "away_goal_mae": away_goal_mae,
        "period": {
            "start_date": dates[0] if dates else None,
            "end_date": dates[-1] if dates else None,
        },
        "sections": sections,
        "metrics": {
            "final_score_exact_match_rate": score_exact_match_rate,
            "home_mae": home_goal_mae,
            "away_mae": away_goal_mae,
            "result_accuracy": result_accuracy,
        },
    }


def load_past_prediction_results(path: str | Path = OUTPUT_DIR / "past_prediction_results.json") -> dict[str, Any]:
    target = Path(path)
    if not target.is_absolute():
        target = Path.cwd() / target
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def write_model_metrics(data: dict[str, Any], output_path: str | Path = OUTPUT_DIR / "local" / "model_metrics.json") -> Path:
    path = Path(output_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _evaluate_match(match: dict[str, Any]) -> dict[str, Any] | None:
    predicted = _score_tuple(match.get("predicted_score"))
    actual = _score_tuple(match.get("actual_score"))
    if predicted is None or actual is None:
        return None
    return {
        "matchweek": _safe_int(match.get("matchweek") or match.get("section")),
        "date": str(match.get("date") or match.get("match_date") or ""),
        "score_hit": predicted == actual,
        "result_hit": _outcome(predicted) == _outcome(actual),
        "home_abs_error": abs(predicted[0] - actual[0]),
        "away_abs_error": abs(predicted[1] - actual[1]),
    }


def _score_tuple(score: Any) -> tuple[int, int] | None:
    if not isinstance(score, dict):
        return None
    home = _safe_int(score.get("home"))
    away = _safe_int(score.get("away"))
    if home is None or away is None:
        return None
    return home, away


def _outcome(score: tuple[int, int]) -> str:
    if score[0] > score[1]:
        return "home"
    if score[0] < score[1]:
        return "away"
    return "draw"


def _safe_int(value: Any) -> int | None:
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def _safe_divide(numerator: float, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return float(numerator / denominator)
