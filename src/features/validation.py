"""Validation checks for generated features and prediction outputs."""

from __future__ import annotations

from typing import Any

import pandas as pd


def validate_no_weather_columns(columns: list[str]) -> list[str]:
    return [col for col in columns if col == "Weather" or str(col).startswith("Weather_")]


def validate_feature_frame(df: pd.DataFrame, model_features: list[str]) -> dict[str, Any]:
    weather_columns = validate_no_weather_columns([str(col) for col in df.columns])
    missing_model_features = [col for col in model_features if col not in df.columns]
    duplicate_rows = int(df.duplicated().sum()) if not df.empty else 0
    return {
        "row_count": int(len(df)),
        "weather_columns": weather_columns,
        "missing_model_features": missing_model_features,
        "extra_columns": [str(col) for col in df.columns if col not in model_features],
        "duplicate_rows": duplicate_rows,
        "valid": not weather_columns and not missing_model_features and duplicate_rows == 0,
    }


def validate_latest_predictions(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for key in ["last_updated", "season", "league", "competition", "category", "matches"]:
        if key not in data:
            errors.append(f"必須キーがありません: {key}")
    if not data.get("matches"):
        errors.append("matches が空です")
    required_match_keys = [
        "match_id",
        "date",
        "home_team",
        "away_team",
        "predicted_score",
        "expected_goals",
        "result_probabilities",
        "score_candidates",
    ]
    for index, match in enumerate(data.get("matches") or []):
        for key in required_match_keys:
            if key not in match:
                errors.append(f"matches[{index}] に必須キーがありません: {key}")
        score = match.get("predicted_score") or {}
        if "home" not in score or "away" not in score:
            errors.append(f"matches[{index}].predicted_score に home/away がありません")
    serialized = str(data)
    if "Weather" in serialized:
        errors.append("出力にWeather関連文字列が含まれています")
    return errors
