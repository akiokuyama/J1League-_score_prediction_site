"""Build a 2026 Special point-in-time training dataset from saved feature snapshots."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.scraping import safe_write_csv
from src.features.snapshots import SNAPSHOT_DIR, load_feature_snapshots


TARGET_COLUMNS = ["Score", "Home_Goals", "Away_Goals", "Goal_Diff", "Match_Result"]
KNOWN_TBD_VALUES = {"", "nan", "none", "tbd", "未定"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "保存済みの節別特徴量スナップショットと試合結果を結合し、"
            "シーズン終了後の再学習用データセットを作成します。"
        )
    )
    parser.add_argument("--season", type=int, default=2026)
    parser.add_argument("--season-key", default="2026_special", help="保存用のシーズン識別子")
    parser.add_argument("--season-label", default="2026 Special", help="レポート表示用のシーズン名")
    parser.add_argument("--season-name", default="2026_Special", help="学習データのSeason列に保存する値")
    parser.add_argument("--reference-dataset", default="Data/ML_dataset.csv")
    parser.add_argument("--matches", default="Data/processed/matches_2026_clean.csv")
    parser.add_argument("--fallback-features", default="Data/features/match_features_2026.csv")
    parser.add_argument("--snapshot-dir", default="Data/features/snapshots")
    parser.add_argument("--output", default="Data/features/training_dataset_2026_special_point_in_time.csv")
    parser.add_argument(
        "--combined-output",
        default="Data/features/training_dataset_with_2026_special_point_in_time.csv",
        help="reference dataset に2026 Special point-in-time行を追加した再学習用CSV",
    )
    parser.add_argument("--source-output", default="Data/features/training_dataset_2026_special_point_in_time_sources.csv")
    parser.add_argument("--report-output", default="Data/features/training_dataset_2026_special_point_in_time_report.json")
    return parser.parse_args()


def _resolve(path: str | Path) -> Path:
    target = Path(path)
    return target if target.is_absolute() else PROJECT_ROOT / target


def _is_known_team(value: Any) -> bool:
    return str(value).strip().lower() not in KNOWN_TBD_VALUES


def _match_result(home_goals: int, away_goals: int) -> int:
    if home_goals > away_goals:
        return 1
    if home_goals < away_goals:
        return -1
    return 0


def _actual_targets(match: pd.Series) -> dict[str, Any]:
    home_goals = int(match["home_score"])
    away_goals = int(match["away_score"])
    return {
        "Score": f"{home_goals}-{away_goals}",
        "Home_Goals": home_goals,
        "Away_Goals": away_goals,
        "Goal_Diff": home_goals - away_goals,
        "Match_Result": _match_result(home_goals, away_goals),
    }


def _snapshot_date_key(value: Any) -> str:
    text = str(value)
    return text[:8] if len(text) >= 8 else ""


def _match_date_key(value: Any) -> str:
    return str(value).replace("-", "")[:8]


def _latest_snapshot_for_match(snapshots: pd.DataFrame, match: pd.Series) -> pd.Series | None:
    if snapshots.empty or "match_id" not in snapshots.columns:
        return None
    match_id = str(match["match_id"])
    candidates = snapshots[snapshots["match_id"].astype(str) == match_id].copy()
    if candidates.empty:
        return None
    match_date = _match_date_key(match["match_date"])
    if "feature_as_of" in candidates.columns and match_date:
        candidates["_snapshot_date"] = candidates["feature_as_of"].map(_snapshot_date_key)
        allowed = candidates[candidates["_snapshot_date"] <= match_date]
        if not allowed.empty:
            candidates = allowed
    sort_col = "feature_as_of" if "feature_as_of" in candidates.columns else "match_id"
    return candidates.sort_values(sort_col).iloc[-1]


def _row_from_source(source: pd.Series, reference_columns: list[str], targets: dict[str, Any]) -> dict[str, Any]:
    row = {col: source[col] if col in source.index else None for col in reference_columns}
    for col, value in targets.items():
        if col in row:
            row[col] = value
    if "Weather" in row and pd.isna(row["Weather"]):
        row["Weather"] = "Unknown"
    return row


def build_point_in_time_training_dataset(
    *,
    season: int,
    reference_dataset: str | Path,
    matches_path: str | Path,
    fallback_features_path: str | Path,
    snapshot_dir: str | Path,
    season_key: str = "2026_special",
    season_label: str = "2026 Special",
    season_name: str = "2026_Special",
) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    reference = pd.read_csv(_resolve(reference_dataset))
    reference_columns = reference.columns.tolist()
    matches = pd.read_csv(_resolve(matches_path))
    fallback = pd.read_csv(_resolve(fallback_features_path))
    snapshots = load_feature_snapshots(_resolve(snapshot_dir), season_key=season_key)

    finished = matches[
        (matches["season"].astype(int) == int(season))
        & (matches["status"].astype(str) == "finished")
        & matches["home_score"].notna()
        & matches["away_score"].notna()
        & matches["home_team"].map(_is_known_team)
        & matches["away_team"].map(_is_known_team)
    ].copy()

    fallback_by_match = {
        str(row["match_id"]): row
        for _, row in fallback.dropna(subset=["match_id"]).iterrows()
        if "match_id" in fallback.columns
    }

    rows: list[dict[str, Any]] = []
    source_rows: list[dict[str, Any]] = []
    skipped: list[str] = []
    for _, match in finished.sort_values(["match_date", "kickoff_time", "match_id"]).iterrows():
        match_id = str(match["match_id"])
        targets = _actual_targets(match)
        snapshot = _latest_snapshot_for_match(snapshots, match)
        if snapshot is not None:
            row = _row_from_source(snapshot, reference_columns, targets)
            if "Season" in row:
                row["Season"] = season_name
            rows.append(row)
            source_rows.append(
                {
                    "match_id": match_id,
                    "section": int(match["section"]),
                    "match_date": match["match_date"],
                    "feature_source": "snapshot",
                    "feature_as_of": snapshot.get("feature_as_of"),
                    "feature_snapshot_path": snapshot.get("feature_snapshot_path"),
                    "fallback_reason": "",
                }
            )
            continue

        fallback_row = fallback_by_match.get(match_id)
        if fallback_row is not None:
            row = _row_from_source(fallback_row, reference_columns, targets)
            if "Season" in row:
                row["Season"] = season_name
            rows.append(row)
            source_rows.append(
                {
                    "match_id": match_id,
                    "section": int(match["section"]),
                    "match_date": match["match_date"],
                    "feature_source": "fallback_rebuilt",
                    "feature_as_of": "",
                    "feature_snapshot_path": "",
                    "fallback_reason": "no_point_in_time_snapshot",
                }
            )
            continue

        skipped.append(match_id)

    dataset = pd.DataFrame(rows, columns=reference_columns)
    source_frame = pd.DataFrame(source_rows)
    report = {
        "season": int(season),
        "season_key": season_key,
        "season_label": season_label,
        "season_name": season_name,
        "finished_matches": int(len(finished)),
        "training_rows": int(len(dataset)),
        "snapshot_rows": int((source_frame["feature_source"] == "snapshot").sum()) if not source_frame.empty else 0,
        "fallback_rows": int((source_frame["feature_source"] == "fallback_rebuilt").sum()) if not source_frame.empty else 0,
        "skipped_rows": int(len(skipped)),
        "skipped_match_ids": skipped,
        "reference_columns": int(len(reference_columns)),
        "snapshot_files": int(len(list(Path(_resolve(snapshot_dir)).glob(f"upcoming_features_{season_key}_asof_*.csv"))) if _resolve(snapshot_dir).exists() else 0),
    }
    return dataset, source_frame, report


def main() -> int:
    args = parse_args()
    dataset, sources, report = build_point_in_time_training_dataset(
        season=args.season,
        reference_dataset=args.reference_dataset,
        matches_path=args.matches,
        fallback_features_path=args.fallback_features,
        snapshot_dir=args.snapshot_dir,
        season_key=args.season_key,
        season_label=args.season_label,
        season_name=args.season_name,
    )
    safe_write_csv(dataset, _resolve(args.output))
    reference = pd.read_csv(_resolve(args.reference_dataset))
    combined = pd.concat([reference, dataset], ignore_index=True, sort=False)
    safe_write_csv(combined, _resolve(args.combined_output))
    safe_write_csv(sources, _resolve(args.source_output))
    report["combined_rows"] = int(len(combined))
    report["combined_output"] = args.combined_output
    report_path = _resolve(args.report_output)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": args.output,
                "combined_output": args.combined_output,
                "source_output": args.source_output,
                "report": report,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
