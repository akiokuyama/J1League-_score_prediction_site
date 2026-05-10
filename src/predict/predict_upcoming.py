"""Batch prediction for upcoming matches."""

from __future__ import annotations

import csv
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from src.config import CATEGORY, COMPETITION, LEAGUE, OUTPUT_DIR, SEASON
from src.features.validation import validate_latest_predictions, validate_no_weather_columns
from src.predict.predict_match import predict_match


def load_upcoming_features(path: str | Path = "data/features/upcoming_features_2026.csv") -> pd.DataFrame:
    return pd.read_csv(path)


def load_scorer_candidates(path: str | Path = "data/processed/player_stats_2026_clean.csv", top_n: int = 5) -> dict[str, list[dict[str, Any]]]:
    file = Path(path)
    if not file.is_absolute():
        file = Path.cwd() / file
    if not file.exists():
        return {}
    df = pd.read_csv(file)
    required = {"team", "player", "scorer_score"}
    if df.empty or not required.issubset(df.columns):
        return {}
    for col in ["scorer_score", "goals", "assists", "cbp_90", "played_games"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    candidates: dict[str, list[dict[str, Any]]] = {}
    for team, team_df in df.groupby("team"):
        ranked = team_df.sort_values(["scorer_score", "goals", "assists", "cbp_90"], ascending=False).head(top_n)
        candidates[str(team)] = [
            {
                "player": str(row.get("player", "")),
                "position": str(row.get("position", "")),
                "goals": int(row.get("goals", 0)),
                "assists": int(row.get("assists", 0)),
                "cbp_90": float(row.get("cbp_90", 0)),
                "played_games": int(row.get("played_games", 0)),
                "scorer_score": float(row.get("scorer_score", 0)),
            }
            for _, row in ranked.iterrows()
        ]
    return candidates


def select_prediction_targets(
    df: pd.DataFrame,
    mode: str = "next_section",
    *,
    date_from: str | None = None,
    date_to: str | None = None,
) -> pd.DataFrame:
    if df.empty:
        return df
    targets = df.copy()
    if "status" in targets.columns:
        targets = targets[targets["status"].astype(str).isin(["unplayed", "postponed_or_tbd"])]

    if mode == "next_section":
        if "section" in targets.columns and not targets["section"].dropna().empty:
            section = targets["section"].dropna().astype(float).min()
            targets = targets[targets["section"].astype(float) == section]
    elif mode == "all_unplayed":
        pass
    elif mode == "date_range":
        if "match_date" not in targets.columns:
            return targets.iloc[0:0]
        dates = pd.to_datetime(targets["match_date"], errors="coerce")
        if date_from:
            targets = targets[dates >= pd.Timestamp(date_from)]
            dates = pd.to_datetime(targets["match_date"], errors="coerce")
        if date_to:
            targets = targets[dates <= pd.Timestamp(date_to)]
    else:
        raise ValueError(f"Unknown prediction mode: {mode}")

    return targets


def predict_upcoming_matches(
    features_df: pd.DataFrame,
    model_dir: str | Path | None = None,
    season: int = SEASON,
    league: str = LEAGUE,
    competition: str = COMPETITION,
    category: str = CATEGORY,
) -> dict[str, Any]:
    matches: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    warnings: list[str] = []
    scorer_candidates = load_scorer_candidates()

    for idx, row in features_df.iterrows():
        try:
            home = str(row.get("home_team") or row.get("Home"))
            away = str(row.get("away_team") or row.get("Away"))
            match_date = row.get("match_date") or row.get("Date")
            result = predict_match(
                home_team=home,
                away_team=away,
                match_date=str(match_date) if pd.notna(match_date) else None,
                model_dir=model_dir,
                feature_row=row,
            )
            result["match_id"] = str(row.get("match_id") or result["match_id"])
            result["section"] = int(row.get("section")) if pd.notna(row.get("section")) else None
            result["scorer_candidates"] = {
                "home": scorer_candidates.get(home, []),
                "away": scorer_candidates.get(away, []),
            }
            matches.append(result)
        except Exception as exc:  # noqa: BLE001
            skipped.append({"row_index": int(idx), "reason": str(exc)})

    if not matches:
        warnings.append("予測対象が空のため latest_predictions.json は更新しません。")

    return {
        "last_updated": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds"),
        "season": season,
        "league": league,
        "competition": competition,
        "category": category,
        "matchweek": int(features_df["section"].dropna().astype(float).min()) if "section" in features_df.columns and not features_df.empty and not features_df["section"].dropna().empty else None,
        "model_version": "weather_removed_v1",
        "feature_policy": {"exclude_weather": True},
        "matches": matches,
        "skipped_matches": skipped,
        "warnings": warnings,
        "data_sources": {
            "features": "data/features/upcoming_features_2026.csv",
        },
    }


def write_predictions_safely(data: dict[str, Any], output_dir: str | Path = OUTPUT_DIR) -> dict[str, Any]:
    errors = validate_latest_predictions(data)
    if errors:
        return {"updated": False, "errors": errors}

    weather_columns = validate_no_weather_columns(list(data.keys()))
    if weather_columns:
        return {"updated": False, "errors": [f"Weather列が含まれています: {weather_columns}"]}

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    history_dir = out / "prediction_history"
    history_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = out / "latest_predictions.tmp.json"
    latest_path = out / "latest_predictions.json"
    csv_path = out / "latest_predictions.csv"
    updated_path = out / "last_updated.txt"
    timestamp = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("%Y%m%d_%H%M%S")
    history_path = history_dir / f"latest_predictions_{timestamp}.json"

    tmp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(tmp_path.read_text(encoding="utf-8"))
    tmp_path.replace(latest_path)
    shutil.copy2(latest_path, history_path)
    updated_path.write_text(str(data["last_updated"]) + "\n", encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["match_id", "date", "home_team", "away_team", "predicted_home", "predicted_away"],
        )
        writer.writeheader()
        for match in data["matches"]:
            writer.writerow(
                {
                    "match_id": match.get("match_id"),
                    "date": match.get("date"),
                    "home_team": match.get("home_team"),
                    "away_team": match.get("away_team"),
                    "predicted_home": match.get("predicted_score", {}).get("home"),
                    "predicted_away": match.get("predicted_score", {}).get("away"),
                }
            )

    return {
        "updated": True,
        "latest_path": str(latest_path),
        "csv_path": str(csv_path),
        "history_path": str(history_path),
    }
