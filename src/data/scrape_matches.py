"""Scrape 2026 J.League match schedule/results."""

from __future__ import annotations

import re
from io import StringIO
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import CATEGORY, COMPETITION, LEAGUE, PROCESSED_DATA_DIR, RAW_DATA_DIR, SEASON
from src.data.scraping import empty_frame, fetch_html, safe_write_csv, soup_from_html
from src.data.team_master import to_dataset_code


MATCH_COLUMNS = [
    "season",
    "league",
    "competition",
    "category",
    "section",
    "section_label",
    "match_date",
    "kickoff_time",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "stadium",
    "attendance",
    "status",
    "match_url",
    "match_id",
]


DATA_SITE_URL = "https://data.j-league.or.jp/SFMS01/search?competition_years=20261&competition_frame_ids=35&tv_relay_station_name="
MATCH_SEARCH_URL = "https://www.jleague.jp/match/search/?category%5B%5D=100yj1&year=2026&section="


def _text(value: Any) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def _normalize_digits(value: str) -> str:
    return value.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def _parse_data_site_date(value: Any) -> str | None:
    text = _normalize_digits(_text(value))
    match = re.search(r"(\d{2})/(\d{1,2})/(\d{1,2})", text)
    if not match:
        return None
    year = 2000 + int(match.group(1))
    return f"{year:04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"


def _section_from_label(value: Any) -> int | None:
    text = _normalize_digits(_text(value))
    section_match = re.search(r"第(\d+)節", text)
    if section_match:
        return int(section_match.group(1))
    playoff_match = re.search(r"第(\d+)戦第(\d+)日", text)
    if playoff_match:
        return int(playoff_match.group(1)) * 100 + int(playoff_match.group(2))
    return None


def _score_pair(value: Any) -> tuple[int | None, int | None]:
    text = _normalize_digits(_text(value))
    score_match = re.search(r"(\d+)\s*[-－]\s*(\d+)", text)
    if not score_match:
        return None, None
    return int(score_match.group(1)), int(score_match.group(2))


def _match_id_section(value: Any) -> str:
    if pd.isna(value):
        return "unknown"
    try:
        return str(int(float(value)))
    except (TypeError, ValueError):
        return str(value)


def _status_from_scores(home_score: Any, away_score: Any, text: str) -> str:
    if pd.notna(home_score) and pd.notna(away_score):
        return "finished"
    if any(word in text for word in ["中止", "延期", "未定"]):
        return "postponed_or_tbd"
    return "unplayed"


def _parse_tables(html: str, url: str) -> pd.DataFrame:
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        tables = []

    rows: list[dict[str, Any]] = []
    for table in tables:
        table.columns = [str(col) for col in table.columns]
        joined_cols = " ".join(table.columns)
        if not any(token in joined_cols for token in ["ホーム", "アウェイ", "試合", "会場", "スコア"]):
            continue
        for _, raw in table.iterrows():
            text = " ".join(str(v) for v in raw.to_list())
            score_match = re.search(r"(\d+)\s*[-－]\s*(\d+)", text)
            home_score = int(score_match.group(1)) if score_match else None
            away_score = int(score_match.group(2)) if score_match else None
            teams = re.split(r"\s+(?:VS|vs|対)\s+", text)
            if len(teams) >= 2:
                home_team = teams[0].split()[-1]
                away_team = teams[1].split()[0]
            else:
                continue
            date_match = re.search(r"(2026[/-]\d{1,2}[/-]\d{1,2})", text)
            kickoff_match = re.search(r"(\d{1,2}:\d{2})", text)
            section_match = re.search(r"第?(\d+)節", text)
            rows.append(
                {
                    "season": SEASON,
                    "league": LEAGUE,
                    "competition": COMPETITION,
                    "category": CATEGORY,
                    "section": int(section_match.group(1)) if section_match else None,
                    "match_date": date_match.group(1).replace("/", "-") if date_match else None,
                    "kickoff_time": kickoff_match.group(1) if kickoff_match else None,
                    "home_team": to_dataset_code(home_team),
                    "away_team": to_dataset_code(away_team),
                    "home_score": home_score,
                    "away_score": away_score,
                    "stadium": None,
                    "attendance": None,
                    "status": _status_from_scores(home_score, away_score, text),
                    "match_url": url,
                }
            )
    return pd.DataFrame(rows)


def _parse_match_links(html: str, url: str) -> pd.DataFrame:
    soup = soup_from_html(html)
    rows: list[dict[str, Any]] = []
    for node in soup.select("a[href*='/match/']"):
        text = " ".join(node.get_text(" ", strip=True).split())
        if "VS" not in text and "vs" not in text and not re.search(r"\d+\s*[-－]\s*\d+", text):
            continue
        score_match = re.search(r"(\d+)\s*[-－]\s*(\d+)", text)
        home_score = int(score_match.group(1)) if score_match else None
        away_score = int(score_match.group(2)) if score_match else None
        teams = re.split(r"\s+(?:VS|vs)\s+", text)
        if len(teams) < 2:
            continue
        href = node.get("href", "")
        match_url = href if href.startswith("http") else f"https://www.jleague.jp{href}"
        rows.append(
            {
                "season": SEASON,
                "league": LEAGUE,
                "competition": COMPETITION,
                "category": CATEGORY,
                "section": None,
                "match_date": None,
                "kickoff_time": None,
                "home_team": to_dataset_code(teams[0].strip()),
                "away_team": to_dataset_code(teams[1].strip()),
                "home_score": home_score,
                "away_score": away_score,
                "stadium": None,
                "attendance": None,
                "status": _status_from_scores(home_score, away_score, text),
                "match_url": match_url,
            }
        )
    return pd.DataFrame(rows)


def _parse_data_site_tables(html: str, url: str) -> pd.DataFrame:
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        tables = []

    rows: list[dict[str, Any]] = []
    for table in tables:
        table.columns = [str(col) for col in table.columns]
        required = {"シーズン", "大会", "節", "試合日", "K/O時刻", "ホーム", "スコア", "アウェイ", "スタジアム"}
        if not required.issubset(set(table.columns)):
            continue
        for _, raw in table.iterrows():
            home_score, away_score = _score_pair(raw.get("スコア"))
            section_label = _text(raw.get("節")) or None
            home_team = to_dataset_code(_text(raw.get("ホーム")))
            away_team = to_dataset_code(_text(raw.get("アウェイ")))
            row_text = " ".join(_text(value) for value in raw.to_list())
            rows.append(
                {
                    "season": SEASON,
                    "league": LEAGUE,
                    "competition": _text(raw.get("大会")) or COMPETITION,
                    "category": CATEGORY,
                    "section": _section_from_label(section_label),
                    "section_label": section_label,
                    "match_date": _parse_data_site_date(raw.get("試合日")),
                    "kickoff_time": _text(raw.get("K/O時刻")) or None,
                    "home_team": home_team,
                    "away_team": away_team,
                    "home_score": home_score,
                    "away_score": away_score,
                    "stadium": _text(raw.get("スタジアム")) or None,
                    "attendance": raw.get("入場者数") if pd.notna(raw.get("入場者数")) else None,
                    "status": _status_from_scores(home_score, away_score, row_text),
                    "match_url": url,
                }
            )
    return pd.DataFrame(rows)


def _parse_matchlist_sections(html: str) -> pd.DataFrame:
    soup = soup_from_html(html)
    rows: list[dict[str, Any]] = []
    for section_node in soup.select("section.matchlistWrap"):
        date_text = section_node.select_one(".timeStamp h4")
        date_value = None
        if date_text:
            match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_text.get_text(strip=True))
            if match:
                date_value = f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"

        section_text = section_node.select_one(".leagAccTit h5")
        section_value = None
        if section_text:
            match = re.search(r"第(\d+)節", section_text.get_text(" ", strip=True))
            if match:
                section_value = int(match.group(1))

        for tr in section_node.select("table.matchTable > tbody > tr"):
            match_cell = tr.select_one("td.match")
            stadium_cell = tr.select_one("td.stadium")
            if match_cell is None:
                continue
            clubs = match_cell.select("td.clubName")
            points = match_cell.select("td.point")
            if len(clubs) < 2:
                continue
            home_text = clubs[0].get_text(" ", strip=True)
            away_text = clubs[1].get_text(" ", strip=True)
            home_score = None
            away_score = None
            if len(points) >= 2:
                if points[0].get_text(strip=True).isdigit():
                    home_score = int(points[0].get_text(strip=True))
                if points[1].get_text(strip=True).isdigit():
                    away_score = int(points[1].get_text(strip=True))
            status_text = match_cell.select_one("td.status")
            text = status_text.get_text(" ", strip=True) if status_text else match_cell.get_text(" ", strip=True)
            link = match_cell.select_one("a[href*='/match/']")
            href = link.get("href", "") if link else ""
            match_url = href if href.startswith("http") else f"https://www.jleague.jp{href}"
            stadium_text = stadium_cell.get_text(" ", strip=True) if stadium_cell else ""
            kickoff_match = re.search(r"(\d{1,2}:\d{2})", stadium_text)
            stadium = re.sub(r"\d{1,2}:\d{2}", "", stadium_text).strip() or None
            rows.append(
                {
                    "season": SEASON,
                    "league": LEAGUE,
                    "competition": COMPETITION,
                    "category": CATEGORY,
                    "section": section_value,
                    "section_label": f"第{section_value}節" if section_value else None,
                    "match_date": date_value,
                    "kickoff_time": kickoff_match.group(1) if kickoff_match else None,
                    "home_team": to_dataset_code(home_text),
                    "away_team": to_dataset_code(away_text),
                    "home_score": home_score,
                    "away_score": away_score,
                    "stadium": stadium,
                    "attendance": None,
                    "status": _status_from_scores(home_score, away_score, text),
                    "match_url": match_url,
                }
            )
    return pd.DataFrame(rows)


def scrape_matches_2026(*, use_cache: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    info: dict[str, Any] = {"url": DATA_SITE_URL, "fallback_url": MATCH_SEARCH_URL, "warnings": []}
    try:
        fetched = fetch_html(DATA_SITE_URL, use_cache=use_cache)
        info["cache_path"] = str(fetched.cache_path)
        info["from_cache"] = fetched.from_cache
        df = _parse_data_site_tables(fetched.html, DATA_SITE_URL)
        if df.empty:
            info["warnings"].append("J.League Data Siteから試合行を抽出できませんでした。jleague.jp側にフォールバックします。")
            fetched = fetch_html(MATCH_SEARCH_URL, use_cache=use_cache)
            info["fallback_cache_path"] = str(fetched.cache_path)
            info["fallback_from_cache"] = fetched.from_cache
            df = _parse_matchlist_sections(fetched.html)
        if df.empty:
            df = _parse_tables(fetched.html, MATCH_SEARCH_URL)
        if df.empty:
            df = _parse_match_links(fetched.html, MATCH_SEARCH_URL)
        if df.empty:
            info["warnings"].append("Jリーグ公式HTMLから試合行を抽出できませんでした。")
            df = empty_frame(MATCH_COLUMNS)
    except Exception as exc:  # noqa: BLE001
        info["warnings"].append(str(exc))
        df = empty_frame(MATCH_COLUMNS)

    if not df.empty:
        df = df.reindex(columns=[col for col in MATCH_COLUMNS if col != "match_id"])
        df["match_id"] = (
            df["season"].astype(str)
            + "-"
            + df["category"].astype(str)
            + "-"
            + df["section"].map(_match_id_section)
            + "-"
            + df["home_team"].astype(str)
            + "-vs-"
            + df["away_team"].astype(str)
        )
    else:
        df = empty_frame(MATCH_COLUMNS)

    raw_path = RAW_DATA_DIR / "matches" / "schedule_2026_100yj1.csv"
    processed_path = PROCESSED_DATA_DIR / "matches_2026_clean.csv"
    safe_write_csv(df, raw_path)
    safe_write_csv(df, processed_path)
    info["rows"] = int(len(df))
    info["raw_path"] = str(raw_path)
    info["processed_path"] = str(processed_path)
    return df, info
