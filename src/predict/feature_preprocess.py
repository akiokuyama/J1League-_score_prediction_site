"""Preprocess existing ML-table rows into model input features.

This module does not recreate the RawData-to-ML_dataset feature engineering
implemented in Notebook/01 and Notebook/02. It only prepares an already
feature-engineered row for inference.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATASET_CANDIDATES = (
    Path("Data/ML_dataset.csv"),
    Path("data/ML_dataset.csv"),
    Path("Data/ml_dataset.csv"),
    Path("data/ml_dataset.csv"),
)

DROP_COLS = [
    "Season",
    "Section",
    "Date",
    "Score",
    "Home",
    "Away",
    "Stadium",
    "Home_Goals",
    "Away_Goals",
    "Goal_Diff",
    "Match_Result",
]

CAT_COLS = [
    "Weather",
    "Backline_Matchup",
    "Home_Formation",
    "Away_Formation",
]

CAT_DUMMY_PREFIXES = tuple(f"{col}_" for col in CAT_COLS)


def resolve_dataset_path(dataset_path: str | Path | None = None) -> Path:
    """Resolve the reference dataset path."""

    if dataset_path is not None:
        path = Path(dataset_path).expanduser()
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        if path.is_file():
            return path.resolve()
        raise FileNotFoundError(f"Dataset file not found: {path}")

    for candidate in DATASET_CANDIDATES:
        path = PROJECT_ROOT / candidate
        if path.is_file():
            return path.resolve()

    csv_files = sorted(PROJECT_ROOT.glob("**/*.csv"))
    discovered = "\n".join(f"  - {path.relative_to(PROJECT_ROOT)}" for path in csv_files[:30])
    raise FileNotFoundError(
        "ML_dataset.csv was not found. CSV files discovered:\n"
        f"{discovered or '  (none)'}"
    )


def load_reference_dataset(dataset_path: str | Path | None = None) -> pd.DataFrame:
    """Load the already feature-engineered ML_dataset.csv."""

    return pd.read_csv(resolve_dataset_path(dataset_path))


def _coerce_to_dataframe(row_or_df: pd.Series | pd.DataFrame | dict[str, Any]) -> pd.DataFrame:
    if isinstance(row_or_df, pd.DataFrame):
        return row_or_df.copy()
    if isinstance(row_or_df, pd.Series):
        return row_or_df.to_frame().T
    if isinstance(row_or_df, dict):
        return pd.DataFrame([row_or_df])
    raise TypeError(
        "row_or_df must be a pandas Series, pandas DataFrame, or dict[str, Any]. "
        f"Got {type(row_or_df).__name__}."
    )


def prepare_features_for_model(
    row_or_df: pd.Series | pd.DataFrame | dict[str, Any],
    model_features: list[str],
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """
    Prepare one or more already feature-engineered rows for model inference.

    Returns:
      - X: DataFrame aligned to model_features
      - diagnostics: column mismatch and conversion details
    """

    if not model_features:
        raise ValueError("model_features must not be empty.")

    df = _coerce_to_dataframe(row_or_df)
    drop_cols = [col for col in DROP_COLS if col in df.columns]
    cat_cols = [col for col in CAT_COLS if col in df.columns and col not in drop_cols]

    X = df.drop(columns=drop_cols, errors="ignore")
    X = pd.get_dummies(X, columns=cat_cols, dummy_na=False)

    non_numeric_columns: list[str] = []
    for col in X.columns:
        converted = pd.to_numeric(X[col], errors="coerce")
        converted = converted.mask(np.isinf(converted), np.nan)
        had_values = X[col].notna()
        failed = had_values & converted.isna()
        if failed.any():
            non_numeric_columns.append(str(col))
        X[col] = converted

    missing_columns = [col for col in model_features if col not in X.columns]
    missing_dummy_columns = [
        str(col) for col in missing_columns if str(col).startswith(CAT_DUMMY_PREFIXES)
    ]
    missing_non_dummy_columns = [
        str(col) for col in missing_columns if not str(col).startswith(CAT_DUMMY_PREFIXES)
    ]
    extra_columns = [str(col) for col in X.columns if col not in model_features]

    X = X.reindex(columns=model_features, fill_value=0)
    X = X.fillna(0)

    diagnostics = {
        "missing_columns": [str(col) for col in missing_columns],
        "missing_dummy_columns": missing_dummy_columns,
        "missing_non_dummy_columns": missing_non_dummy_columns,
        "extra_columns": extra_columns,
        "non_numeric_columns": non_numeric_columns,
    }
    return X, diagnostics
