"""Shared utilities for crawlers."""

from __future__ import annotations

import hashlib
import json
import logging
import time
from pathlib import Path

import requests

logger = logging.getLogger("observatory")

# Default rate limit: 500ms between requests
DEFAULT_RATE_LIMIT_MS = 500


class RateLimiter:
    """Simple rate limiter based on minimum delay between calls."""

    def __init__(self, delay_ms: int = DEFAULT_RATE_LIMIT_MS):
        self.delay_s = delay_ms / 1000.0
        self._last_call = 0.0

    def wait(self):
        now = time.monotonic()
        elapsed = now - self._last_call
        if elapsed < self.delay_s:
            time.sleep(self.delay_s - elapsed)
        self._last_call = time.monotonic()


def content_hash(content: str | bytes) -> str:
    """SHA-256 hash of content."""
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def fetch_url(
    url: str,
    *,
    timeout: int = 30,
    rate_limiter: RateLimiter | None = None,
    headers: dict | None = None,
) -> requests.Response:
    """Fetch a URL with optional rate limiting."""
    if rate_limiter:
        rate_limiter.wait()
    default_headers = {
        "User-Agent": "AguaraObservatory/0.1 (https://github.com/garagon/aguara-observatory)"
    }
    if headers:
        default_headers.update(headers)
    resp = requests.get(url, timeout=timeout, headers=default_headers)
    resp.raise_for_status()
    return resp


def save_json(path: Path, data) -> None:
    """Save data as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False) + "\n")


def load_json(path: Path):
    """Load JSON from file, returns None if not found."""
    if not path.exists():
        return None
    return json.loads(path.read_text())


def setup_logging(level: int = logging.INFO) -> None:
    """Configure logging for observatory scripts."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def shard_matches(slug: str, shard: str) -> bool:
    """Check if a slug belongs to a letter-range shard (e.g. 'A-F')."""
    if not shard or not slug:
        return True
    parts = shard.upper().split("-")
    if len(parts) != 2:
        return True
    start, end = parts
    first_char = slug[0].upper()
    return start <= first_char <= end
