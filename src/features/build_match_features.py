"""Build match features from processed data."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import FEATURE_DATA_DIR
from src.data.scraping import safe_write_csv
from src.features.build_upcoming_features import build_upcoming_features


def build_match_features(
    matches_path: str | Path = "Data/processed/matches_2026_clean.csv",
    output_path: str | Path = FEATURE_DATA_DIR / "match_features_2026.csv",
) -> pd.DataFrame:
    df = build_upcoming_features(matches_path=matches_path, only_unplayed=False)
    safe_write_csv(df, output_path)
    return df
