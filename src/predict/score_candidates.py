"""Score candidate generation for match prediction."""

from __future__ import annotations

import math
from typing import Any


def _poisson_pmf(k: int, lam: float) -> float:
    lam = max(float(lam), 0.05)
    return math.exp(-lam) * (lam**k) / math.factorial(k)


def _normal_pdf(value: float, mean: float, sigma: float) -> float:
    sigma = max(float(sigma), 1e-6)
    z = (float(value) - float(mean)) / sigma
    return math.exp(-0.5 * z * z) / (sigma * math.sqrt(2 * math.pi))


def _result_key(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home_win"
    if home_goals == away_goals:
        return "draw"
    return "away_win"


def generate_score_candidates(
    expected_home_goals: float,
    expected_away_goals: float,
    result_probabilities: dict[str, float],
    predicted_goal_diff: float,
    max_goals: int = 5,
    top_n: int = 5,
    diff_sigma: float = 1.0,
) -> list[dict[str, Any]]:
    """Return the top N score candidates by combined model score."""

    if max_goals < 0:
        raise ValueError("max_goals must be 0 or greater.")
    if top_n <= 0:
        raise ValueError("top_n must be greater than 0.")

    home_lambda = max(float(expected_home_goals), 0.05)
    away_lambda = max(float(expected_away_goals), 0.05)
    candidates: list[dict[str, Any]] = []

    for home_goals in range(max_goals + 1):
        for away_goals in range(max_goals + 1):
            poisson_probability = _poisson_pmf(home_goals, home_lambda) * _poisson_pmf(
                away_goals, away_lambda
            )
            result_weight = float(result_probabilities.get(_result_key(home_goals, away_goals), 0.0))
            diff_weight = _normal_pdf(
                home_goals - away_goals,
                mean=float(predicted_goal_diff),
                sigma=diff_sigma,
            )
            combined_score = poisson_probability * result_weight * diff_weight
            candidates.append(
                {
                    "score": f"{home_goals}-{away_goals}",
                    "home_goals": int(home_goals),
                    "away_goals": int(away_goals),
                    "probability": 0.0,
                    "poisson_probability": float(poisson_probability),
                    "combined_score": float(combined_score),
                }
            )

    candidates.sort(key=lambda item: item["combined_score"], reverse=True)
    top_candidates = candidates[:top_n]
    total_score = sum(float(item["combined_score"]) for item in top_candidates)
    if total_score > 0:
        for item in top_candidates:
            item["probability"] = float(item["combined_score"] / total_score)

    return top_candidates
