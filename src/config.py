"""Project configuration constants."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEASON = "2026_special"
SEASON_YEAR = 2026
LEAGUE = "J1"
COMPETITION = "明治安田J1百年構想リーグ"
CATEGORY = "100yj1"

RAW_DATA_DIR = PROJECT_ROOT / "Data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "Data" / "processed"
FEATURE_DATA_DIR = PROJECT_ROOT / "Data" / "features"
HTML_CACHE_DIR = RAW_DATA_DIR / "html_cache"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
