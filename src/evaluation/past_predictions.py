"""Build past prediction result records from prediction history and actual scores."""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from src.config import LEAGUE, OUTPUT_DIR, PROCESSED_DATA_DIR, SEASON


HISTORY_TIMESTAMP_RE = re.compile(r"_(\d{8}_\d{6})\.json$")


def build_past_prediction_results(
    history_dir: str | Path = OUTPUT_DIR / "prediction_history",
    matches_path: str | Path = PROCESSED_DATA_DIR / "matches_2026_special_clean.csv",
    season: str = SEASON,
    league: str = LEAGUE,
) -> dict[str, Any]:
    """Return past prediction results joined with actual finished match scores."""
    match_rows = _load_match_rows(matches_path)
    predictions, history_info = _load_latest_history_predictions(history_dir)
    diagnostics = _build_diagnostics(predictions, match_rows, history_info)

    matches: list[dict[str, Any]] = []
    for match_id in sorted(predictions):
        prediction = predictions.get(match_id)
        actual = match_rows.get(match_id)
        if not prediction or actual is None:
            continue
        if not _is_finished(actual) or not _has_complete_score(actual):
            continue
        matches.append(_build_result_record(prediction, actual))

    matches.sort(key=lambda item: (str(item.get("date") or ""), int(item.get("matchweek") or 0), str(item.get("match_id") or "")))
    return {
        "generated_at": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds"),
        "season": season,
        "league": league,
        "source": {
            "prediction_history": str(history_dir),
            "actual_matches": str(matches_path),
        },
        "diagnostics": diagnostics,
        "matches": matches,
    }


def write_past_prediction_results(
    data: dict[str, Any],
    output_path: str | Path = OUTPUT_DIR / "past_prediction_results.json",
) -> Path:
    """Write past prediction results JSON."""
    path = Path(output_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _load_match_rows(matches_path: str | Path) -> dict[str, dict[str, Any]]:
    path = Path(matches_path)
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    required = {"match_id", "home_score", "away_score"}
    if df.empty or not required.issubset(df.columns):
        return {}

    normalized = df.copy()
    normalized["home_score"] = pd.to_numeric(normalized["home_score"], errors="coerce")
    normalized["away_score"] = pd.to_numeric(normalized["away_score"], errors="coerce")
    normalized = normalized.dropna(subset=["match_id"])

    rows: dict[str, dict[str, Any]] = {}
    for _, row in normalized.iterrows():
        rows[str(row["match_id"])] = row.to_dict()
    return rows


def _load_latest_history_predictions(history_dir: str | Path) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    directory = Path(history_dir)
    if not directory.is_absolute():
        directory = Path.cwd() / directory
    if not directory.exists():
        return {}, {"prediction_history_files": 0, "prediction_history_matches": 0}

    selected: dict[str, tuple[datetime, dict[str, Any]]] = {}
    files = sorted(directory.glob("*.json"))
    total_matches = 0
    for path in files:
        timestamp = _history_timestamp(path)
        data = _read_json(path)
        for match in data.get("matches", []) if isinstance(data, dict) else []:
            if not isinstance(match, dict) or not match.get("match_id"):
                continue
            total_matches += 1
            match_id = str(match["match_id"])
            current = selected.get(match_id)
            if current is None or timestamp >= current[0]:
                selected[match_id] = (timestamp, match)
    info = {
        "prediction_history_files": len(files),
        "prediction_history_matches": total_matches,
    }
    return {match_id: match for match_id, (_, match) in selected.items()}, info


def _build_result_record(prediction: dict[str, Any], actual: dict[str, Any]) -> dict[str, Any]:
    predicted_score = prediction.get("predicted_score") if isinstance(prediction.get("predicted_score"), dict) else {}
    actual_score = {
        "home": _safe_int(actual.get("home_score")),
        "away": _safe_int(actual.get("away_score")),
    }
    predicted_result = _result_from_score(predicted_score)
    actual_result = _result_from_score(actual_score)
    return {
        "match_id": str(actual.get("match_id") or prediction.get("match_id") or ""),
        "matchweek": _safe_int(actual.get("section") or prediction.get("section") or prediction.get("matchweek")),
        "date": _first_non_empty(actual.get("match_date"), prediction.get("date"), prediction.get("match_date")),
        "kickoff": _first_non_empty(actual.get("kickoff_time"), prediction.get("kickoff")),
        "venue": _first_non_empty(actual.get("stadium"), prediction.get("venue")),
        "home_team": _first_non_empty(actual.get("home_team"), prediction.get("home_team")),
        "away_team": _first_non_empty(actual.get("away_team"), prediction.get("away_team")),
        "predicted_score": predicted_score,
        "actual_score": actual_score,
        "predicted_result": predicted_result,
        "actual_result": actual_result,
        "is_result_correct": predicted_result is not None and predicted_result == actual_result,
        "is_score_correct": _score_tuple(predicted_score) == _score_tuple(actual_score),
        "result_probabilities": prediction.get("result_probabilities") if isinstance(prediction.get("result_probabilities"), dict) else {},
        "score_candidates": prediction.get("score_candidates") if isinstance(prediction.get("score_candidates"), list) else [],
    }


def _build_diagnostics(
    predictions: dict[str, dict[str, Any]],
    match_rows: dict[str, dict[str, Any]],
    history_info: dict[str, int],
) -> dict[str, int]:
    matched_ids = [match_id for match_id in predictions if match_id in match_rows]
    matched_rows = [match_rows[match_id] for match_id in matched_ids]
    finished_rows = [row for row in matched_rows if _is_finished(row)]
    score_complete_rows = [row for row in matched_rows if _has_complete_score(row)]
    evaluation_rows = [row for row in matched_rows if _is_finished(row) and _has_complete_score(row)]
    return {
        "prediction_history_files": int(history_info.get("prediction_history_files", 0)),
        "prediction_history_matches": int(history_info.get("prediction_history_matches", 0)),
        "prediction_history_unique_matches": len(predictions),
        "matches_rows": len(match_rows),
        "match_id_matched": len(matched_ids),
        "finished_matched": len(finished_rows),
        "score_complete_matched": len(score_complete_rows),
        "evaluation_target_matches": len(evaluation_rows),
        "unmatched_prediction_matches": len(predictions) - len(matched_ids),
        "matched_but_unplayed": sum(1 for row in matched_rows if not _is_finished(row)),
        "matched_but_missing_score": sum(1 for row in matched_rows if not _has_complete_score(row)),
    }


def _is_finished(row: dict[str, Any]) -> bool:
    return str(row.get("status") or "").strip().lower() == "finished"


def _has_complete_score(row: dict[str, Any]) -> bool:
    return _safe_int(row.get("home_score")) is not None and _safe_int(row.get("away_score")) is not None


def _score_tuple(score: dict[str, Any]) -> tuple[int, int] | None:
    home = _safe_int(score.get("home"))
    away = _safe_int(score.get("away"))
    if home is None or away is None:
        return None
    return home, away


def _result_from_score(score: dict[str, Any]) -> str | None:
    values = _score_tuple(score)
    if values is None:
        return None
    if values[0] > values[1]:
        return "home_win"
    if values[0] < values[1]:
        return "away_win"
    return "draw"


def _history_timestamp(path: Path) -> datetime:
    match = HISTORY_TIMESTAMP_RE.search(path.name)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d_%H%M%S")
        except ValueError:
            pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _first_non_empty(*values: Any) -> Any:
    for value in values:
        if value is not None and str(value) != "" and str(value).lower() != "nan":
            return value
    return None


def _safe_int(value: Any) -> int | None:
    try:
        if pd.isna(value):
            return None
        return int(float(value))
    except (TypeError, ValueError):
        return None
