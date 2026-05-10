"""Model evaluation entry points."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.models.train_score_models import train_and_evaluate


def compare_weather_policy(dataset_path: str | Path) -> dict[str, Any]:
    with_weather = train_and_evaluate(dataset_path, exclude_weather=False)
    without_weather = train_and_evaluate(dataset_path, exclude_weather=True)

    deltas = {
        key: without_weather.metrics[key] - with_weather.metrics[key]
        for key in without_weather.metrics
        if key in with_weather.metrics
    }

    return {
        "with_weather": {
            "feature_count": len(with_weather.feature_names),
            "metrics": with_weather.metrics,
        },
        "without_weather": {
            "feature_count": len(without_weather.feature_names),
            "metrics": without_weather.metrics,
        },
        "delta_without_minus_with": deltas,
    }

