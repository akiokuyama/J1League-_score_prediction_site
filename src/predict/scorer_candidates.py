"""Build scorer candidate rankings from player stats."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


SCORER_COLUMNS = ["scorer_score", "score", "probability", "goals", "assists", "cbp_90", "played_games"]


def calculate_goal_propensity_score(row: pd.Series | dict[str, Any]) -> float:
    """Return Goal Propensity Score from Football Lab player stats."""
    played_games = _to_float(row.get("played_games"), 0.0)
    denominator = played_games if played_games > 0 else 1.0
    goal_point_90 = _first_numeric(row, ["goal_point_90", "goals_90"], _to_float(row.get("goals"), 0.0) / denominator)
    shoot_point_90 = _first_numeric(row, ["shoot_point_90", "shots_90"], _to_float(row.get("assists"), 0.0) / denominator)
    cbp_attack_90 = _first_numeric(row, ["cbp_attack_90", "attack_cbp_90"], _to_float(row.get("cbp_90"), 0.0))

    score = goal_point_90 * 1.0 + shoot_point_90 * 0.5 + cbp_attack_90 * 0.2
    if played_games < 3:
        score *= 0.1

    position = str(row.get("position") or "").upper()
    if position == "FW":
        score *= 1.2
    elif position == "DF":
        score *= 0.8

    return max(float(score), 0.0)


def add_scorer_score(df: pd.DataFrame) -> pd.DataFrame:
    """Return a copy with scorer_score populated."""
    normalized = df.copy()
    for col in ["goals", "assists", "cbp_90"]:
        if col not in normalized.columns:
            normalized[col] = 0
        normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)
    normalized["scorer_score"] = normalized.apply(calculate_goal_propensity_score, axis=1)
    normalized["score"] = normalized["scorer_score"]
    return normalized


def build_team_scorer_candidates(df: pd.DataFrame, top_n: int = 5) -> dict[str, list[dict[str, Any]]]:
    """Build top scorer candidates per team."""
    required = {"team", "player"}
    if df.empty or not required.issubset(df.columns):
        return {}

    normalized = add_scorer_score(df)
    for col in SCORER_COLUMNS:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)
    for col in ["team", "player", "position"]:
        if col not in normalized.columns:
            normalized[col] = ""
        normalized[col] = normalized[col].astype(str).str.strip()

    candidates: dict[str, list[dict[str, Any]]] = {}
    for team, team_df in normalized.groupby("team"):
        ranked = team_df.sort_values(["scorer_score", "goals", "assists", "cbp_90"], ascending=False).head(top_n).copy()
        total_score = float(ranked["scorer_score"].clip(lower=0).sum())
        if total_score <= 0:
            candidates[str(team)] = []
            continue
        candidates[str(team)] = [
            {
                "rank": int(rank),
                "player": str(row.get("player", "")),
                "team": str(team),
                "position": str(row.get("position", "")),
                "score": float(_to_float(row.get("scorer_score"), 0.0)),
                "probability": float(max(_to_float(row.get("scorer_score"), 0.0), 0.0) / total_score),
                "source": "football_lab_player_stats",
                "goals": int(_to_float(row.get("goals"), 0.0)),
                "assists": int(_to_float(row.get("assists"), 0.0)),
                "cbp_90": float(_to_float(row.get("cbp_90"), 0.0)),
                "played_games": int(_to_float(row.get("played_games"), 0.0)),
                "scorer_score": float(_to_float(row.get("scorer_score"), 0.0)),
            }
            for rank, (_, row) in enumerate(ranked.iterrows(), start=1)
        ]
    return candidates


def load_team_scorer_candidates(path: str | Path = "data/processed/player_stats_2026_clean.csv", top_n: int = 5) -> dict[str, list[dict[str, Any]]]:
    """Load player stats CSV and return top scorer candidates per team."""
    file = Path(path)
    if not file.is_absolute():
        file = Path.cwd() / file
    if not file.exists():
        return {}
    df = pd.read_csv(file)
    return build_team_scorer_candidates(df, top_n=top_n)


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _first_numeric(row: pd.Series | dict[str, Any], keys: list[str], default: float) -> float:
    for key in keys:
        value = _to_float(row.get(key), float("nan"))
        if value == value:
            return value
    return default
