from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run_prediction(mode: str) -> None:
    result = subprocess.run(
        [sys.executable, "scripts/run_prediction.py", "--mode", mode],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr or result.stdout


def test_next_section_writes_latest_predictions() -> None:
    run_prediction("next_section")
    path = Path("outputs/latest_predictions.json")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["matches"]
    assert data.get("warnings") == []
    assert data.get("skipped_matches") == []


def test_all_unplayed_writes_separate_predictions() -> None:
    run_prediction("all_unplayed")
    path = Path("outputs/all_unplayed_predictions.json")
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["matches"]
    assert data.get("warnings") == []
    assert data.get("skipped_matches") == []
