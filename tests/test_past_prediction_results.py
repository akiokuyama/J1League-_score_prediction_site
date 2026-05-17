from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.evaluation.past_predictions import build_past_prediction_results


def _write_history(history_dir: Path, match_id: str = "m-1", predicted_score: dict | None = None) -> None:
    history_dir.mkdir(exist_ok=True)
    history_file = history_dir / "latest_predictions_20260517_120000.json"
    history_file.write_text(
        json.dumps(
            {
                "matches": [
                    {
                        "match_id": match_id,
                        "section": 3,
                        "home_team": "aaa",
                        "away_team": "bbb",
                        "predicted_score": predicted_score or {"home": 1, "away": 0},
                        "result_probabilities": {"home_win": 0.5, "draw": 0.3, "away_win": 0.2},
                        "score_candidates": [{"score": "1-0", "probability": 0.2}],
                    }
                ]
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def test_build_past_prediction_results_joins_finished_actual_scores(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    _write_history(history_dir)
    matches_path = tmp_path / "matches.csv"
    pd.DataFrame(
        [
            {
                "match_id": "m-1",
                "section": 3,
                "match_date": "2026-05-01",
                "kickoff_time": "19:00",
                "home_team": "aaa",
                "away_team": "bbb",
                "home_score": 2,
                "away_score": 1,
                "stadium": "Test Stadium",
                "status": "finished",
            },
            {
                "match_id": "m-2",
                "section": 3,
                "home_score": None,
                "away_score": None,
                "status": "unplayed",
            },
        ]
    ).to_csv(matches_path, index=False)

    data = build_past_prediction_results(history_dir=history_dir, matches_path=matches_path)

    assert len(data["matches"]) == 1
    match = data["matches"][0]
    assert match["match_id"] == "m-1"
    assert match["actual_score"] == {"home": 2, "away": 1}
    assert match["predicted_score"] == {"home": 1, "away": 0}
    assert match["predicted_result"] == "home_win"
    assert match["actual_result"] == "home_win"
    assert match["is_result_correct"] is True
    assert match["is_score_correct"] is False
    assert data["diagnostics"]["match_id_matched"] == 1
    assert data["diagnostics"]["evaluation_target_matches"] == 1


def test_build_past_prediction_results_excludes_unplayed_match(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    _write_history(history_dir)
    matches_path = tmp_path / "matches.csv"
    pd.DataFrame(
        [
            {
                "match_id": "m-1",
                "section": 3,
                "home_score": None,
                "away_score": None,
                "status": "unplayed",
            }
        ]
    ).to_csv(matches_path, index=False)

    data = build_past_prediction_results(history_dir=history_dir, matches_path=matches_path)

    assert data["matches"] == []
    assert data["diagnostics"]["match_id_matched"] == 1
    assert data["diagnostics"]["matched_but_unplayed"] == 1
    assert data["diagnostics"]["matched_but_missing_score"] == 1
    assert data["diagnostics"]["evaluation_target_matches"] == 0


def test_build_past_prediction_results_excludes_finished_match_with_missing_score(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    _write_history(history_dir)
    matches_path = tmp_path / "matches.csv"
    pd.DataFrame(
        [
            {
                "match_id": "m-1",
                "section": 3,
                "home_score": 1,
                "away_score": None,
                "status": "finished",
            }
        ]
    ).to_csv(matches_path, index=False)

    data = build_past_prediction_results(history_dir=history_dir, matches_path=matches_path)

    assert data["matches"] == []
    assert data["diagnostics"]["finished_matched"] == 1
    assert data["diagnostics"]["matched_but_missing_score"] == 1
    assert data["diagnostics"]["evaluation_target_matches"] == 0


def test_build_past_prediction_results_counts_unmatched_prediction(tmp_path: Path) -> None:
    history_dir = tmp_path / "history"
    _write_history(history_dir, match_id="missing")
    matches_path = tmp_path / "matches.csv"
    pd.DataFrame(
        [
            {
                "match_id": "m-1",
                "section": 3,
                "home_score": 1,
                "away_score": 0,
                "status": "finished",
            }
        ]
    ).to_csv(matches_path, index=False)

    data = build_past_prediction_results(history_dir=history_dir, matches_path=matches_path)

    assert data["matches"] == []
    assert data["diagnostics"]["match_id_matched"] == 0
    assert data["diagnostics"]["unmatched_prediction_matches"] == 1
