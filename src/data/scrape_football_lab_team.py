"""Fetch Football Lab team-level pages where available."""

from __future__ import annotations

from datetime import datetime
from io import StringIO
import re
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from src.config import RAW_DATA_DIR
from src.data.scraping import empty_frame, fetch_html, safe_write_csv
from src.data.team_master import TEAM_NAME_TO_CODE


FOOTBALL_LAB_URLS = {
    "expected": "https://www.football-lab.jp/summary/team_ranking/j1001?data=expected&year=100",
    "kagi": "https://www.football-lab.jp/summary/team_ranking/j1001?data=kagi&year=100",
    "goal_patterns": "https://www.football-lab.jp/summary/team_ranking/j1001?data=goal&year=100",
    "team_styles": "https://www.football-lab.jp/summary/team_style/j1001?year=100&data=21",
}


def _to_team_code(text: object) -> str:
    value = str(text).replace("\u3000", " ").strip()
    if value in TEAM_NAME_TO_CODE:
        return TEAM_NAME_TO_CODE[value]
    for name, code in sorted(TEAM_NAME_TO_CODE.items(), key=lambda item: len(item[0]), reverse=True):
        if name and name in value:
            return code
    return value


def _add_team_code(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    result = df.copy()
    team_col = None
    best_matches = -1
    for col in result.columns:
        values = result[col].map(_to_team_code)
        matches = int(values.astype(str).isin(set(TEAM_NAME_TO_CODE.values())).sum())
        if matches > best_matches:
            best_matches = matches
            team_col = col
    if team_col is not None:
        result.insert(0, "team", result[team_col].map(_to_team_code))
        result.insert(1, "team_name", result[team_col].astype(str))
    return result


def _parse_goal_patterns(html: str) -> pd.DataFrame:
    header_match = re.search(r"\['チーム'(?P<cols>[^\]]+)\]", html)
    if not header_match:
        return empty_frame(["team"])
    pattern_columns = re.findall(r"'([^']+)'", header_match.group("cols"))
    rows: list[dict[str, Any]] = []
    for team_name, values_text in re.findall(r"\['([^']+)'((?:,\s*-?\d+(?:\.\d+)?)+)\]", html):
        values = [float(value) for value in re.findall(r"-?\d+(?:\.\d+)?", values_text)]
        if len(values) != len(pattern_columns):
            continue
        row: dict[str, Any] = {
            "team": _to_team_code(team_name),
            "team_name": team_name,
        }
        row.update(dict(zip(pattern_columns, values, strict=False)))
        rows.append(row)
    df = pd.DataFrame(rows)
    if df.empty:
        return empty_frame(["team"])
    return df.drop_duplicates(subset=["team"], keep="first").reset_index(drop=True)


def _parse_tables(html: str, key: str) -> pd.DataFrame:
    if key == "goal_patterns":
        return _parse_goal_patterns(html)
    tables = pd.read_html(StringIO(html))
    if not tables:
        return empty_frame(["team"])
    if key == "team_styles":
        frames = []
        for idx, table in enumerate(tables):
            df = table.copy()
            df.columns = [str(col) for col in df.columns]
            df = _add_team_code(df)
            df["table_index"] = idx
            frames.append(df)
        return pd.concat(frames, ignore_index=True) if frames else empty_frame(["team"])

    frames = []
    for idx, table in enumerate(tables):
        df = table.copy()
        df.columns = [str(col) for col in df.columns]
        df = _add_team_code(df)
        df["table_index"] = idx
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else empty_frame(["team"])


def scrape_football_lab_team_2026(*, use_cache: bool = False) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    today = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d")
    frames: dict[str, pd.DataFrame] = {}
    info: dict[str, Any] = {"urls": FOOTBALL_LAB_URLS, "warnings": []}

    for key, url in FOOTBALL_LAB_URLS.items():
        try:
            fetched = fetch_html(url, use_cache=use_cache, delay_seconds=0.2, retries=1, timeout=10)
            df = _parse_tables(fetched.html, key)
        except Exception as exc:  # noqa: BLE001
            info["warnings"].append(f"{key}: {exc}")
            df = empty_frame(["team"])

        frames[key] = df
        if key == "goal_patterns":
            path = RAW_DATA_DIR / "football_lab" / "goal_patterns" / f"goal_patterns_2026_asof_{today}.csv"
        elif key == "team_styles":
            path = RAW_DATA_DIR / "football_lab" / "team_styles" / f"team_styles_2026_asof_{today}.csv"
        else:
            path = RAW_DATA_DIR / "football_lab" / f"{key}_2026.csv"
        safe_write_csv(df, path)
        info[f"{key}_path"] = str(path)
        info[f"{key}_rows"] = int(len(df))

    return frames, info
