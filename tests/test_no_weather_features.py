from __future__ import annotations

import json
from pathlib import Path

import joblib


def test_model_features_do_not_include_weather() -> None:
    features = joblib.load("Models/model_features.pkl")
    weather_features = [feature for feature in features if str(feature) == "Weather" or str(feature).startswith("Weather_")]
    assert weather_features == []


def test_latest_predictions_do_not_include_weather_text() -> None:
    path = Path("outputs/latest_predictions.json")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    json.loads(text)
    assert "Weather" not in text
