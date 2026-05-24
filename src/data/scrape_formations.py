"""Fetch Football Lab formation pages."""

from __future__ import annotations

from io import StringIO
from typing import Any

import pandas as pd

from src.config import PROCESSED_DATA_DIR, RAW_DATA_DIR
from src.data.scraping import empty_frame, fetch_html, safe_write_csv
from src.data.team_master import FOOTBALL_LAB_CODES


def _parse_primary_formation(html: str) -> tuple[str, int | None]:
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        return "Unknown", None
    for table in tables:
        df = table.copy()
        df.columns = [str(col) for col in df.columns]
        if "システム名" not in df.columns or "試合" not in df.columns:
            continue
        df = df[df["システム名"].astype(str) != "合計"].copy()
        df["matches"] = pd.to_numeric(df["試合"], errors="coerce")
        df = df.dropna(subset=["matches"])
        if df.empty:
            continue
        top = df.sort_values("matches", ascending=False).iloc[0]
        return str(top["システム名"]), int(top["matches"])
    return "Unknown", None


def scrape_formations_2026_special(*, use_cache: bool = False) -> tuple[pd.DataFrame, dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    info: dict[str, Any] = {"warnings": []}
    for team_code, lab_code in FOOTBALL_LAB_CODES.items():
        url = f"https://www.football-lab.jp/{lab_code}/formation/"
        try:
            fetched = fetch_html(url, use_cache=use_cache, delay_seconds=0.2, retries=1, timeout=10)
            formation, starts = _parse_primary_formation(fetched.html)
            rows.append(
                {
                    "team": team_code,
                    "formation": formation,
                    "formation_starts": starts,
                    "source_url": url,
                    "html_length": len(fetched.html),
                }
            )
        except Exception as exc:  # noqa: BLE001
            info["warnings"].append(f"{team_code}: {exc}")

    df = pd.DataFrame(rows) if rows else empty_frame(["team", "formation", "formation_starts", "source_url", "html_length"])
    raw_path = RAW_DATA_DIR / "formations" / "formations_2026_special.csv"
    processed_path = PROCESSED_DATA_DIR / "formations_2026_special_clean.csv"
    safe_write_csv(df, raw_path)
    safe_write_csv(df, processed_path)
    info["rows"] = int(len(df))
    info["raw_path"] = str(raw_path)
    info["processed_path"] = str(processed_path)
    return df, info
