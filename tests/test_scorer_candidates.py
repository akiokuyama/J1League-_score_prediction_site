from __future__ import annotations

import pandas as pd

from src.predict.scorer_candidates import build_team_scorer_candidates, calculate_goal_propensity_score


def test_calculate_goal_propensity_score() -> None:
    score = calculate_goal_propensity_score(
        {
            "goal_point_90": 1.0,
            "shoot_point_90": 2.0,
            "cbp_attack_90": 3.0,
            "played_games": 3,
            "position": "FW",
        }
    )
    assert score == 3.12


def test_calculate_goal_propensity_score_applies_low_appearance_penalty() -> None:
    score = calculate_goal_propensity_score(
        {
            "goal_point_90": 1.0,
            "shoot_point_90": 0.0,
            "cbp_attack_90": 0.0,
            "played_games": 2,
            "position": "MF",
        }
    )
    assert score == 0.1


def test_build_team_scorer_candidates_returns_top_five() -> None:
    df = pd.DataFrame(
        [
            {"team": "aaa", "player": "A", "position": "FW", "goals": 1, "assists": 0, "cbp_90": 0.1, "played_games": 3},
            {"team": "aaa", "player": "B", "position": "MF", "goals": 3, "assists": 1, "cbp_90": 0.2, "played_games": 4},
            {"team": "aaa", "player": "C", "position": "FW", "goals": 2, "assists": 4, "cbp_90": 0.3, "played_games": 5},
            {"team": "aaa", "player": "D", "position": "DF", "goals": 0, "assists": 0, "cbp_90": 0.4, "played_games": 6},
            {"team": "aaa", "player": "E", "position": "FW", "goals": 1, "assists": 2, "cbp_90": 0.5, "played_games": 7},
            {"team": "aaa", "player": "F", "position": "FW", "goals": 0, "assists": 1, "cbp_90": 0.6, "played_games": 8},
            {"team": "bbb", "player": "G", "position": "FW", "goals": 4, "assists": 0, "cbp_90": 0.0, "played_games": 9},
        ]
    )

    candidates = build_team_scorer_candidates(df, top_n=5)

    assert len(candidates["aaa"]) == 5
    assert candidates["aaa"][0]["rank"] == 1
    assert candidates["aaa"][0]["player"] == "C"
    assert candidates["bbb"][0]["player"] == "G"
    assert "scorer_score" in candidates["aaa"][0]
    assert "probability" in candidates["aaa"][0]
