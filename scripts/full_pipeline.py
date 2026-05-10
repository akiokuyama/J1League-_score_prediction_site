"""Run the Week3 update, feature generation, and prediction pipeline."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "soccer_score_app_matplotlib"))
os.environ.setdefault("LOKY_MAX_CPU_COUNT", "1")


def run_step(args: list[str]) -> int:
    print("[RUN]", " ".join(args), flush=True)
    result = subprocess.run(args, cwd=PROJECT_ROOT, check=False)
    return int(result.returncode)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Week3フルパイプライン")
    parser.add_argument("--season", type=int, default=2026)
    parser.add_argument("--category", default="100yj1")
    parser.add_argument("--mode", default="next_section")
    parser.add_argument("--use-cache", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    update_cmd = [sys.executable, "scripts/update_2026_data.py"]
    if args.use_cache:
        update_cmd.append("--use-cache")
    steps = [
        update_cmd,
        [sys.executable, "scripts/make_upcoming_features.py", "--season", str(args.season), "--category", args.category],
        [sys.executable, "scripts/run_prediction.py", "--mode", args.mode],
    ]
    final_code = 0
    for step in steps:
        code = run_step(step)
        if code != 0:
            final_code = code
            break
    return final_code


if __name__ == "__main__":
    sys.exit(main())
