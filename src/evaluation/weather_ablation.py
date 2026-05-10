"""Weather feature ablation evaluation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from src.evaluation.model_evaluation import compare_weather_policy


def evaluate_weather_ablation(dataset_path: str | Path = "Data/ML_dataset.csv") -> dict[str, Any]:
    return compare_weather_policy(dataset_path)

