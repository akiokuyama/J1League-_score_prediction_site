from __future__ import annotations

from pathlib import Path


def test_streamlit_does_not_display_model_metrics() -> None:
    app_text = Path("app/streamlit_app.py").read_text(encoding="utf-8")

    forbidden = [
        "load_model_metrics",
        "model_metrics",
        "勝敗Accuracy",
        "Home MAE",
        "Away MAE",
        "スコア完全的中率",
    ]
    for pattern in forbidden:
        assert pattern not in app_text
