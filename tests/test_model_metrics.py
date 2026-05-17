from __future__ import annotations

from src.evaluation.model_metrics import build_model_metrics


def test_build_model_metrics() -> None:
    metrics = build_model_metrics(
        {
            "season": 2026,
            "league": "J1",
            "matches": [
                {
                    "matchweek": 1,
                    "predicted_score": {"home": 1, "away": 0},
                    "actual_score": {"home": 1, "away": 0},
                },
                {
                    "matchweek": 2,
                    "predicted_score": {"home": 0, "away": 1},
                    "actual_score": {"home": 2, "away": 1},
                },
            ],
        }
    )

    assert metrics["evaluated_matches"] == 2
    assert metrics["sample_size"] == 2
    assert metrics["score_exact_match_rate"] == 0.5
    assert metrics["home_goal_mae"] == 1.0
    assert metrics["metrics"]["final_score_exact_match_rate"] == 0.5
    assert metrics["metrics"]["home_mae"] == 1.0
    assert metrics["metrics"]["away_mae"] == 0.0
    assert metrics["metrics"]["result_accuracy"] == 0.5


def test_model_metrics_output_schema() -> None:
    data = build_model_metrics({"season": 2026, "league": "J1", "matches": []})

    assert data["evaluated_matches"] >= 0
    assert data["sample_size"] >= 0
    for key in ["result_accuracy", "score_exact_match_rate", "home_goal_mae", "away_goal_mae", "period"]:
        assert key in data
    for key in ["final_score_exact_match_rate", "home_mae", "away_mae", "result_accuracy"]:
        assert key in data["metrics"]
