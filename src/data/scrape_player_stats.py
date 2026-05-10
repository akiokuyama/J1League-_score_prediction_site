"""Fetch Football Lab player stat pages."""

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.data.scraping import empty_frame, fetch_html, safe_write_csv
from src.data.team_master import FOOTBALL_LAB_CODES


PLAYER_COLUMN_MAP = {
    "順位": "rank",
    "Unnamed: 1": "position",
    "Unnamed: 2": "player",
    "ポイントCBP": "cbp",
    "90分平均": "cbp_90",
    "出場試合出場": "played_games",
    "ゴール": "goals",
    "アシスト": "assists",
}


def normalize_player_stats(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return empty_frame(
            [
                "rank",
                "position",
                "player",
                "cbp",
                "cbp_90",
                "played_games",
                "goals",
                "assists",
                "team",
                "source_url",
                "scorer_score",
            ]
        )
    normalized = df.rename(columns={col: PLAYER_COLUMN_MAP.get(str(col), str(col)) for col in df.columns}).copy()
    for col in ["rank", "cbp", "cbp_90", "played_games", "goals", "assists"]:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)
    for col in ["position", "player", "team", "source_url"]:
        if col not in normalized.columns:
            normalized[col] = ""
        normalized[col] = normalized[col].astype(str).str.strip()
    normalized["scorer_score"] = (
        normalized.get("goals", 0).astype(float) * 3
        + normalized.get("assists", 0).astype(float)
        + normalized.get("cbp_90", 0).astype(float)
    )
    columns = [
        "rank",
        "position",
        "player",
        "cbp",
        "cbp_90",
        "played_games",
        "goals",
        "assists",
        "team",
        "source_url",
        "scorer_score",
    ]
    return normalized[[col for col in columns if col in normalized.columns]]


def scrape_player_stats_2026(*, use_cache: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    frames: list[pd.DataFrame] = []
    info: dict[str, Any] = {"warnings": []}
    for team_code, lab_code in FOOTBALL_LAB_CODES.items():
        # Football Lab's 2026 player ranking is served from the current page.
        # Adding ?year=2026 redirects/returns the 2025 season page.
        url = f"https://www.football-lab.jp/{lab_code}/ranking"
        try:
            fetched = fetch_html(url, use_cache=use_cache, delay_seconds=0.2, retries=1, timeout=10)
            tables = pd.read_html(StringIO(fetched.html))
            if tables:
                table = tables[0].copy()
                table.columns = [str(col) for col in table.columns]
                table["team"] = team_code
                table["source_url"] = url
                frames.append(table)
        except Exception as exc:  # noqa: BLE001
            info["warnings"].append(f"{team_code}: {exc}")

    raw_path = RAW_DATA_DIR / "player_stats" / "player_stats_2026.csv"
    processed_path = PROCESSED_DATA_DIR / "player_stats_2026_clean.csv"
    if not frames:
        info["warnings"].append("全チームの選手スタッツ取得に失敗したため、既存CSVは上書きしません")
        existing = _read_existing_processed(processed_path)
        info["rows"] = int(len(existing))
        info["raw_path"] = str(raw_path)
        info["processed_path"] = str(processed_path)
        info["used_existing"] = True
        return existing, info

    raw_df = pd.concat(frames, ignore_index=True)
    df = normalize_player_stats(raw_df)
    safe_write_csv(raw_df, raw_path)
    safe_write_csv(df, processed_path)
    info["rows"] = int(len(df))
    info["raw_path"] = str(raw_path)
    info["processed_path"] = str(processed_path)
    return df, info


def _read_existing_processed(path: str | Path) -> pd.DataFrame:
    existing_path = Path(path)
    if existing_path.exists() and existing_path.stat().st_size > 0:
        return pd.read_csv(existing_path)
    return normalize_player_stats(empty_frame(["team", "player"]))
