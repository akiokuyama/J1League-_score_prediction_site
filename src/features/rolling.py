"""Rolling feature helpers."""

from __future__ import annotations

import pandas as pd


def latest_team_rows(df: pd.DataFrame, team: str) -> pd.DataFrame:
    if "Date" in df.columns:
        df = df.copy()
        df["_date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df.sort_values("_date")
    return df

