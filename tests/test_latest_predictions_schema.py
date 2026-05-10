from __future__ import annotations

import json
from pathlib import Path


def test_latest_predictions_schema() -> None:
    path = Path("outputs/latest_predictions.json")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))

    for key in ["last_updated", "season", "league", "matches"]:
        assert key in data

    assert data.get("warnings") == []
    assert data.get("skipped_matches") == []
    assert data["matches"]

    required_match_keys = [
        "predicted_score",
        "expected_goals",
        "result_probabilities",
        "score_candidates",
        "scorer_candidates",
    ]
    for match in data["matches"]:
        for key in required_match_keys:
            assert key in match
        assert "home" in match["scorer_candidates"]
        assert "away" in match["scorer_candidates"]
        assert match["scorer_candidates"]["home"]
        assert match["scorer_candidates"]["away"]
