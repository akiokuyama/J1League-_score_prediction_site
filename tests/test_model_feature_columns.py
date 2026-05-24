from __future__ import annotations

import joblib
import pandas as pd


def test_upcoming_features_have_all_model_columns() -> None:
    model_features = joblib.load("Models/model_features.pkl")
    upcoming = pd.read_csv("Data/features/upcoming_features_2026_special.csv")

    missing = [feature for feature in model_features if feature not in upcoming.columns]
    assert missing == []


def test_upcoming_model_features_have_no_missing_values() -> None:
    model_features = joblib.load("Models/model_features.pkl")
    upcoming = pd.read_csv("Data/features/upcoming_features_2026_special.csv")

    assert not upcoming[model_features].isna().any().any()
