"""Fetch or derive standings data."""

from __future__ import annotations

from typing import Any
from io import StringIO

import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR, SEASON
from src.data.scraping import empty_frame, fetch_html, safe_write_csv
from src.data.team_master import to_dataset_code


STANDINGS_COLUMNS = ["season", "division", "team", "rank", "points", "played", "wins", "draws", "losses"]
DIVISIONS = ["EAST", "WEST"]
STANDINGS_COLUMN_MAP = {
    "順位": "rank",
    "クラブ名": "team_name",
    "勝点": "points",
    "試合数": "played",
    "勝": "wins",
    "PK勝": "pk_wins",
    "PK負": "pk_losses",
    "負": "losses",
    "得点": "goals_for",
    "失点": "goals_against",
    "得失点": "goal_diff",
    "直近5試合": "last_5",
}


def scrape_standings_2026_special(*, use_cache: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    url = "https://www.jleague.jp/standings/j1/"
    info: dict[str, Any] = {"url": url, "warnings": []}
    try:
        fetched = fetch_html(url, use_cache=use_cache)
        info["cache_path"] = str(fetched.cache_path)
        tables = pd.read_html(StringIO(fetched.html))
        frames = []
        for idx, table in enumerate(tables[: len(DIVISIONS)]):
            frame = table.copy()
            frame.columns = [str(col) for col in frame.columns]
            frame.insert(0, "division", DIVISIONS[idx])
            frames.append(frame)
        raw_df = pd.concat(frames, ignore_index=True) if frames else empty_frame(STANDINGS_COLUMNS)
        df = normalize_standings(raw_df)
        info["divisions"] = {division: int((df["division"] == division).sum()) for division in DIVISIONS}
        if len(tables) < len(DIVISIONS):
            info["warnings"].append(f"順位表テーブルが不足しています: expected={len(DIVISIONS)}, actual={len(tables)}")
    except Exception as exc:  # noqa: BLE001
        info["warnings"].append(str(exc))
        raw_df = empty_frame(STANDINGS_COLUMNS)
        df = empty_frame(STANDINGS_COLUMNS)

    raw_path = RAW_DATA_DIR / "standings" / "standings_2026_special.csv"
    processed_path = PROCESSED_DATA_DIR / "standings_2026_special_clean.csv"
    safe_write_csv(raw_df, raw_path)
    safe_write_csv(df, processed_path)
    info["rows"] = int(len(df))
    info["raw_path"] = str(raw_path)
    info["processed_path"] = str(processed_path)
    return df, info


def normalize_standings(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return empty_frame(
            [
                "season",
                "division",
                "rank",
                "team",
                "team_name",
                "points",
                "played",
                "wins",
                "pk_wins",
                "pk_losses",
                "losses",
                "goals_for",
                "goals_against",
                "goal_diff",
            ]
        )

    normalized = df.drop(columns=[col for col in df.columns if str(col).startswith("Unnamed")], errors="ignore")
    normalized = normalized.rename(columns=STANDINGS_COLUMN_MAP)
    if "team_name" in normalized.columns:
        normalized["team_name"] = normalized["team_name"].astype(str).map(_dedupe_repeated_name)
        normalized["team"] = normalized["team_name"].map(to_dataset_code)
    normalized.insert(0, "season", SEASON)

    for col in ["rank", "points", "played", "wins", "pk_wins", "pk_losses", "losses", "goals_for", "goals_against", "goal_diff"]:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0).astype(int)

    columns = [
        "season",
        "division",
        "rank",
        "team",
        "team_name",
        "points",
        "played",
        "wins",
        "pk_wins",
        "pk_losses",
        "losses",
        "goals_for",
        "goals_against",
        "goal_diff",
        "last_5",
    ]
    return normalized[[col for col in columns if col in normalized.columns]]


def _dedupe_repeated_name(value: str) -> str:
    text = str(value).strip()
    midpoint = len(text) // 2
    if len(text) % 2 == 0 and text[:midpoint] == text[midpoint:]:
        return text[:midpoint]
    return text
