"""Update 2026 data sources without overwriting existing legacy data."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.scrape_football_lab_team import scrape_football_lab_team_2026
from src.data.scrape_formations import scrape_formations_2026
from src.data.scrape_market_values import scrape_market_values_2026
from src.data.scrape_matches import scrape_matches_2026
from src.data.scrape_player_stats import scrape_player_stats_2026
from src.data.scrape_standings import scrape_standings_2026
from src.data.scrape_team_stats import scrape_team_stats_2026
from src.data.scraping import write_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="2026年データを更新します")
    parser.add_argument("--use-cache", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    report: dict[str, object] = {
        "updated_at": datetime.now(ZoneInfo("Asia/Tokyo")).isoformat(timespec="seconds"),
        "use_cache": args.use_cache,
        "sources": {},
    }

    steps = [
        ("matches", lambda: scrape_matches_2026(use_cache=args.use_cache)),
        ("standings", lambda: scrape_standings_2026(use_cache=args.use_cache)),
        ("team_stats", lambda: scrape_team_stats_2026(use_cache=args.use_cache)),
        ("market_values", lambda: scrape_market_values_2026(use_cache=args.use_cache)),
        ("football_lab", lambda: scrape_football_lab_team_2026(use_cache=args.use_cache)),
        ("formations", lambda: scrape_formations_2026(use_cache=args.use_cache)),
        ("player_stats", lambda: scrape_player_stats_2026(use_cache=args.use_cache)),
    ]

    for name, fn in steps:
        try:
            _, info = fn()
            report["sources"][name] = info
            print(f"[INFO] {name}: {json.dumps(info, ensure_ascii=False)}")
        except Exception as exc:  # noqa: BLE001
            report["sources"][name] = {"warnings": [str(exc)]}
            print(f"[WARN] {name}: {exc}")

    report_path = PROJECT_ROOT / "data" / "processed" / "update_2026_report.json"
    write_json(report_path, report)
    print(f"[OK] データ更新レポート: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

