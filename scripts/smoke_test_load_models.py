"""Smoke test for loading trained models and running one sample prediction."""

from __future__ import annotations

import os
import sys
import tempfile
import warnings
from pathlib import Path
from typing import Iterable

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "soccer_score_app_matplotlib"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")
warnings.filterwarnings(
    "ignore",
    message="Could not find the number of physical cores.*",
    category=UserWarning,
)

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.load_model import ModelBundle, load_models


DATASET_CANDIDATES = (
    Path("Data/ML_dataset.csv"),
    Path("data/ML_dataset.csv"),
    Path("Data/ml_dataset.csv"),
    Path("data/ml_dataset.csv"),
)

DROP_COLS = [
    "Season",
    "Section",
    "Date",
    "Score",
    "Home",
    "Away",
    "Stadium",
    "Home_Goals",
    "Away_Goals",
    "Goal_Diff",
    "Match_Result",
]

CAT_COLS = [
    "Weather",
    "Backline_Matchup",
    "Home_Formation",
    "Away_Formation",
]

SAMPLE_CONTEXT_COLS = ["Season", "Section", "Date", "Home", "Away", "Score"]


def find_dataset(candidates: Iterable[Path] = DATASET_CANDIDATES) -> Path:
    for candidate in candidates:
        path = PROJECT_ROOT / candidate
        if path.is_file():
            return path

    csv_files = sorted(PROJECT_ROOT.glob("**/*.csv"))
    discovered = "\n".join(f"  - {path.relative_to(PROJECT_ROOT)}" for path in csv_files[:30])
    raise FileNotFoundError(
        "ML_dataset.csv was not found. CSV files discovered:\n"
        f"{discovered or '  (none)'}"
    )


def build_feature_frame(df: pd.DataFrame, feature_names: list[str]) -> pd.DataFrame:
    drop_cols = [col for col in DROP_COLS if col in df.columns]
    cat_cols = [col for col in CAT_COLS if col in df.columns and col not in drop_cols]

    X = df.drop(columns=drop_cols, errors="ignore")
    X = pd.get_dummies(X, columns=cat_cols, dummy_na=False)

    missing_from_dataset = [col for col in feature_names if col not in X.columns]
    extra_in_dataset = [col for col in X.columns if col not in feature_names]

    if missing_from_dataset:
        print(f"[WARN] 学習時特徴量にあるが現在データにない列: {len(missing_from_dataset)}")
        print(f"       {missing_from_dataset[:20]}")
    if extra_in_dataset:
        print(f"[WARN] 現在データにあるが学習時特徴量にない列: {len(extra_in_dataset)}")
        print(f"       {extra_in_dataset[:20]}")

    X = X.reindex(columns=feature_names, fill_value=0)
    return X


def run_prediction(bundle: ModelBundle, X_sample: pd.DataFrame) -> dict[str, object]:
    goals = bundle.step1_goals.predict(X_sample)[0]
    result_probabilities = bundle.step2_clf.predict_proba(X_sample)[0]
    result_classes = list(getattr(bundle.step2_clf, "classes_", []))
    goal_diff = bundle.step2_diff.predict(X_sample)[0]

    return {
        "expected_goals_home": float(goals[0]),
        "expected_goals_away": float(goals[1]),
        "result_classes": [int(value) for value in result_classes],
        "result_probabilities": [float(value) for value in result_probabilities],
        "predicted_goal_diff": float(goal_diff),
    }


def to_python_scalar(value: object) -> object:
    if hasattr(value, "item"):
        return value.item()
    return value


def main() -> int:
    try:
        bundle = load_models()
        print(f"[OK] model_dir: {bundle.model_dir}")
        print("[OK] モデル読み込み成功")
        print(f"[INFO] feature count: {len(bundle.feature_names)}")

        dataset_path = find_dataset()
        df = pd.read_csv(dataset_path)
        print(f"[OK] dataset: {dataset_path}")
        print(f"[OK] ML_dataset 読み込み成功: shape={df.shape}")

        X = build_feature_frame(df, bundle.feature_names)
        sample = df.tail(1)
        X_sample = X.tail(1)

        sample_context = {
            col: to_python_scalar(sample.iloc[0][col])
            for col in SAMPLE_CONTEXT_COLS
            if col in sample.columns
        }
        print("\n[INFO] sample match:")
        print(sample_context)

        prediction = run_prediction(bundle, X_sample)
        print("\n[OK] 予測テスト成功")
        for key, value in prediction.items():
            print(f"  {key}: {value}")
        return 0
    except Exception as exc:
        print(f"[ERROR] smoke test failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
