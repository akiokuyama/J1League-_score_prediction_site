"""Tactical feature helpers."""

from __future__ import annotations


def backline_matchup(home_formation: str, away_formation: str) -> str:
    home_back = str(home_formation).split("-")[0] if home_formation else "4"
    away_back = str(away_formation).split("-")[0] if away_formation else "4"
    if home_back not in {"3", "4"}:
        home_back = "4"
    if away_back not in {"3", "4"}:
        away_back = "4"
    return f"{home_back}_vs_{away_back}"

