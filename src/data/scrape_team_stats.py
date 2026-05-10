"""Fetch J.League team statistics."""

from __future__ import annotations

import re
from typing import Any

import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.data.scraping import empty_frame, fetch_html, safe_write_csv
from src.data.scraping import soup_from_html
from src.data.team_master import to_dataset_code


TEAM_STAT_TYPES = {
    "shoot": "Total Shots",
    "shoot_on_target": "Shots on Target",
    "suffer_shoot": "Total Shots Against",
    "score": "Total Goals",
    "lost": "Total Goals Against",
    "clean_sheet": "Clean Sheets",
    "pass_count": "Total Passes",
    "dribble_count": "Total Dribbles",
    "through_pass_count": "Total Through Balls",
    "cross_count": "Total Crosses",
    "clear_count": "Total Clearances",
    "tackle_count": "Total Tackles",
    "block_count": "Total Blocks",
    "foul_count": "Total Fouls",
    "intercept_count": "Total Interceptions",
    "air_battle_win_count": "Aerial Duels Won",
    "yellow_count": "Yellow Cards",
    "red_count": "Red Cards",
    "ball_rate": "Average Possession",
    "chance_create": "Chances Created",
    "one_on_one": "Duels Won",
    "recovery_count": "Recoveries",
    "expected_goals": "Expected Goals",
    "expected_goals_against": "Expected Goals Against",
    "distance_per_game": "Avg Distance Covered",
    "sprint_per_game": "Avg Sprints",
}


def _parse_stat_value(text: str) -> float | None:
    cleaned = str(text).replace(",", "").replace("%", "").strip()
    match = re.search(r"-?\d+(?:\.\d+)?", cleaned)
    if not match:
        return None
    return float(match.group(0))


def _parse_ranking_cards(html: str, stat_type: str, label: str) -> pd.DataFrame:
    soup = soup_from_html(html)
    rows: list[dict[str, Any]] = []
    ranking_list = soup.select_one("ul.ranking_list")
    if ranking_list is None:
        return empty_frame(["rank", "team", "team_name", "value", "stat_type", "stat_label"])

    for item in ranking_list.select("li"):
        rank_el = item.select_one("p.number, p.number_1, p.number_2, p.number_3")
        team_el = item.select_one("p.team")
        value_el = item.select_one("div[class^='ranking_stats'] p")
        if team_el is None or value_el is None:
            continue

        team_name = team_el.get_text(" ", strip=True)
        value_text = value_el.get_text(" ", strip=True)
        rank = int(_parse_stat_value(rank_el.get_text(" ", strip=True))) if rank_el else None
        value = _parse_stat_value(value_text)
        rows.append(
            {
                "rank": rank,
                "team": to_dataset_code(team_name),
                "team_name": team_name,
                "value": value,
                "value_text": value_text,
                "stat_type": stat_type,
                "stat_label": label,
            }
        )

    return pd.DataFrame(rows)


def scrape_team_stats_2026(*, use_cache: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    frames: list[pd.DataFrame] = []
    info: dict[str, Any] = {"urls": [], "warnings": []}
    for stat_type, label in TEAM_STAT_TYPES.items():
        url = f"https://www.jleague.jp/stats/j1/club/2026/{stat_type}/"
        info["urls"].append(url)
        try:
            fetched = fetch_html(url, use_cache=use_cache, delay_seconds=0.2, retries=1, timeout=10)
            table = _parse_ranking_cards(fetched.html, stat_type, label)
            if table.empty:
                info["warnings"].append(f"{stat_type}: ranking_list を検出できませんでした")
            else:
                frames.append(table)
        except Exception as exc:  # noqa: BLE001
            info["warnings"].append(f"{stat_type}: {exc}")

    df = pd.concat(frames, ignore_index=True) if frames else empty_frame(["stat_type", "stat_label"])
    raw_path = RAW_DATA_DIR / "team_stats" / "team_stats_2026.csv"
    processed_path = PROCESSED_DATA_DIR / "team_stats_2026_clean.csv"
    safe_write_csv(df, raw_path)
    safe_write_csv(df, processed_path)
    info["rows"] = int(len(df))
    info["raw_path"] = str(raw_path)
    info["processed_path"] = str(processed_path)
    return df, info
