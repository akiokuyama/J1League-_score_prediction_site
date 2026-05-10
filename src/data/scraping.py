"""Shared scraping utilities with cache and safe writes."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd
import requests
from bs4 import BeautifulSoup

from src.config import HTML_CACHE_DIR


USER_AGENT = "SoccerScoreApp/0.1 (+https://openai.com; educational data collection)"


@dataclass(frozen=True)
class FetchResult:
    url: str
    html: str
    cache_path: Path
    from_cache: bool


def cache_path_for_url(url: str, cache_dir: str | Path = HTML_CACHE_DIR) -> Path:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:20]
    return Path(cache_dir) / f"{digest}.html"


def fetch_html(
    url: str,
    *,
    use_cache: bool = False,
    cache_dir: str | Path = HTML_CACHE_DIR,
    retries: int = 3,
    delay_seconds: float = 1.0,
    timeout: int = 20,
) -> FetchResult:
    cache_path = cache_path_for_url(url, cache_dir)
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    if use_cache and cache_path.exists():
        return FetchResult(url=url, html=cache_path.read_text(encoding="utf-8"), cache_path=cache_path, from_cache=True)

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers={"User-Agent": USER_AGENT},
                timeout=timeout,
            )
            response.raise_for_status()
            response.encoding = response.apparent_encoding or response.encoding
            cache_path.write_text(response.text, encoding="utf-8")
            if delay_seconds > 0:
                time.sleep(delay_seconds * (attempt + 1))
            return FetchResult(url=url, html=response.text, cache_path=cache_path, from_cache=False)
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            time.sleep(delay_seconds * (2**attempt))

    raise RuntimeError(f"HTML取得に失敗しました: {url}: {last_error}")


def soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def safe_write_csv(df: pd.DataFrame, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    df.to_csv(tmp, index=False)
    tmp.replace(target)


def empty_frame(columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(columns=columns)


def write_json(path: str | Path, data: dict[str, Any]) -> None:
    import json

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(target)

