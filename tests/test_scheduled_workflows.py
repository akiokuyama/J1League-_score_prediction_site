from pathlib import Path


def read_workflow(name: str) -> str:
    return Path(".github/workflows", name).read_text(encoding="utf-8")


def test_results_after_matches_workflow_is_results_only() -> None:
    text = read_workflow("update_results_after_matches.yml")

    assert "name: Update Results After Matches" in text
    assert "workflow_dispatch:" in text
    assert 'cron: "0 22 * * 0"' in text
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in text
    assert "python -m compileall app src scripts" in text
    assert "python -m pytest" in text
    assert "python scripts/update_2026_data.py --season 2026 --category 100yj1 --scope results" in text
    assert "python scripts/build_past_prediction_results.py" in text
    assert "python scripts/validate_past_prediction_results.py" in text
    assert "full_pipeline.py --season 2026 --category 100yj1 --mode next_section" not in text
    assert "run_prediction.py --mode all_unplayed" not in text
    assert "outputs/latest_predictions.json \\" not in text
    assert "outputs/all_unplayed_predictions.json \\" not in text
    assert "outputs/prediction_history \\" not in text
    assert "Data/features \\" not in text
    assert "data/features" not in text
    assert "build_model_metrics.py" not in text
    assert "git add outputs/local" not in text


def test_scheduled_prediction_workflow_updates_predictions() -> None:
    text = read_workflow("update_predictions_scheduled.yml")

    assert "name: Update Predictions Scheduled" in text
    assert "workflow_dispatch:" in text
    assert 'cron: "0 12 * * 4"' in text
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in text
    assert "python -m compileall app src scripts" in text
    assert "python -m pytest" in text
    assert "python scripts/full_pipeline.py --season 2026 --category 100yj1 --mode next_section" in text
    assert "python scripts/run_prediction.py --mode all_unplayed" in text
    assert "python scripts/build_past_prediction_results.py" in text
    assert "python scripts/validate_prediction_outputs.py" in text
    assert "python scripts/validate_past_prediction_results.py" in text
    assert "build_model_metrics.py" not in text
    assert "git add outputs/local" not in text
    assert "outputs/local/model_metrics.json must not be generated in Actions" in text


def test_manual_workflow_remains_manual_only() -> None:
    text = read_workflow("update_predictions_manual.yml")

    assert "name: Manual Prediction Update" in text
    assert "workflow_dispatch:" in text
    assert "schedule:" not in text
    assert "FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true" in text
    assert "python scripts/build_model_metrics.py" not in text
    assert "python scripts/validate_prediction_outputs.py" in text
    assert "python scripts/validate_past_prediction_results.py" in text
    assert "git add outputs/local" not in text
