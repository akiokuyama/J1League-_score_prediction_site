from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from scripts.build_point_in_time_training_dataset import build_point_in_time_training_dataset
from src.features.snapshots import save_upcoming_feature_snapshot


def test_save_upcoming_feature_snapshot(tmp_path: Path) -> None:
    features = pd.DataFrame(
        [
            {
                "match_id": "m1",
                "Season": 2026,
                "Section": 18,
                "Home": "home",
                "Away": "away",
            }
        ]
    )
    sources = pd.DataFrame([{"match_id": "actual_schedule", "Season": "actual_schedule"}])

    paths = save_upcoming_feature_snapshot(
        features,
        sources=sources,
        snapshot_dir=tmp_path,
        created_at=datetime(2026, 5, 24, 12, 0, 0),
    )

    assert paths.features.exists()
    assert paths.sources is not None and paths.sources.exists()
    assert paths.metadata.exists()
    assert paths.features.name == "upcoming_features_2026_special_asof_20260524_120000.csv"
    saved = pd.read_csv(paths.features)
    assert saved.loc[0, "feature_as_of"] == "20260524_120000"
    assert saved.loc[0, "season_key"] == "2026_special"
    assert saved.loc[0, "feature_snapshot_source"] == "weekly_prediction_snapshot"


def test_build_point_in_time_training_dataset_uses_snapshot_then_fallback(tmp_path: Path) -> None:
    reference = pd.DataFrame(
        columns=[
            "Season",
            "Section",
            "Date",
            "Home",
            "Score",
            "Away",
            "Weather",
            "Home_Goals",
            "Away_Goals",
            "Goal_Diff",
            "Match_Result",
            "Home_Current_Rank",
        ]
    )
    reference_path = tmp_path / "ML_dataset.csv"
    reference.to_csv(reference_path, index=False)

    matches = pd.DataFrame(
        [
            {
                "season": 2026,
                "section": 1,
                "match_date": "2026-02-06",
                "kickoff_time": "19:00",
                "home_team": "a",
                "away_team": "b",
                "home_score": 2,
                "away_score": 1,
                "status": "finished",
                "match_id": "m1",
            },
            {
                "season": 2026,
                "section": 18,
                "match_date": "2026-05-30",
                "kickoff_time": "14:00",
                "home_team": "c",
                "away_team": "d",
                "home_score": 0,
                "away_score": 0,
                "status": "finished",
                "match_id": "m2",
            },
        ]
    )
    matches_path = tmp_path / "matches.csv"
    matches.to_csv(matches_path, index=False)

    fallback = pd.DataFrame(
        [
            {
                "match_id": "m1",
                "Season": 2026,
                "Section": 1,
                "Date": "2026-02-06",
                "Home": "a",
                "Score": "0-0",
                "Away": "b",
                "Home_Goals": 0,
                "Away_Goals": 0,
                "Goal_Diff": 0,
                "Match_Result": 0,
                "Home_Current_Rank": 9,
            }
        ]
    )
    fallback_path = tmp_path / "fallback.csv"
    fallback.to_csv(fallback_path, index=False)

    save_upcoming_feature_snapshot(
        pd.DataFrame(
            [
                {
                    "match_id": "m2",
                    "Season": 2026,
                    "Section": 18,
                    "Date": "2026-05-30",
                    "Home": "c",
                    "Score": "0-0",
                    "Away": "d",
                    "Home_Goals": 0,
                    "Away_Goals": 0,
                    "Goal_Diff": 0,
                    "Match_Result": 0,
                    "Home_Current_Rank": 3,
                }
            ]
        ),
        snapshot_dir=tmp_path / "snapshots",
        created_at=datetime(2026, 5, 24, 12, 0, 0),
    )

    dataset, sources, report = build_point_in_time_training_dataset(
        season=2026,
        reference_dataset=reference_path,
        matches_path=matches_path,
        fallback_features_path=fallback_path,
        snapshot_dir=tmp_path / "snapshots",
    )

    assert len(dataset) == 2
    assert report["snapshot_rows"] == 1
    assert report["fallback_rows"] == 1
    assert report["season_key"] == "2026_special"
    assert report["season_label"] == "2026 Special"
    assert sources["feature_source"].tolist() == ["fallback_rebuilt", "snapshot"]
    assert dataset["Season"].tolist() == ["2026_Special", "2026_Special"]
    assert dataset["Score"].tolist() == ["2-1", "0-0"]
    assert dataset["Match_Result"].tolist() == [1, 0]
    assert dataset["Home_Current_Rank"].tolist() == [9, 3]
