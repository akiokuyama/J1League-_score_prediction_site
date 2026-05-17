"""Display formatters for the Streamlit app."""

from __future__ import annotations

from datetime import datetime
from typing import Any


def format_datetime_jp(value: str | None) -> str:
    """ISO datetimeを '2026年5月10日 14時55分' 形式に変換する。"""
    if not value:
        return "-"
    try:
        normalized = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return str(value)
    return f"{dt.year}年{dt.month}月{dt.day}日 {dt.hour}時{dt.minute:02d}分"


def format_date(value: Any) -> str:
    if value is None or value == "":
        return "-"
    try:
        dt = datetime.fromisoformat(str(value))
        return f"{dt.year}年{dt.month}月{dt.day}日"
    except ValueError:
        return str(value)


def format_percent(value: float | int | None, digits: int = 1) -> str:
    """0.5121 -> '51.2%' に変換する。"""
    if value is None:
        return "-"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "-"
    if numeric < 0:
        numeric = 0.0
    if numeric <= 1:
        numeric *= 100
    return f"{numeric:.{digits}f}%"


def format_score(score: dict | None) -> str:
    """{'home': 1, 'away': 0} -> '1-0' に変換する。"""
    if not isinstance(score, dict):
        return "-"
    home = score.get("home")
    away = score.get("away")
    if home is None or away is None:
        return "-"
    try:
        return f"{int(home)}-{int(away)}"
    except (TypeError, ValueError):
        return f"{home}-{away}"


def format_accuracy(hits: int, total: int) -> str:
    """2, 3 -> '66.7%（2/3）' に変換する。"""
    if total <= 0:
        return "0.0%（0/0）"
    return f"{hits / total * 100:.1f}%（{hits}/{total}）"


def format_optional_parts(*parts: Any) -> str:
    values = [str(part) for part in parts if part not in (None, "")]
    return " / ".join(values) if values else "-"
