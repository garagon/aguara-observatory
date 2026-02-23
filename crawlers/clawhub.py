#!/usr/bin/env python3
"""Crawler for ClawHub registry.

Ported from Aguara benchmark: download_clawhub.py.
Changes from original:
  - No skill limit (crawls ALL skills)
  - Incremental via sort=updated + content hash
  - Writes to Turso DB
  - Incremental mode: watermark updatedAt + ETag HEAD pre-check
"""

from __future__ import annotations

import io
import logging
import time
import zipfile

import requests

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash

logger = logging.getLogger("observatory.clawhub")

CLAWHUB_API = "https://clawhub.ai/api/v1"
DOWNLOAD_RATE_LIMIT_MS = 3100  # 20 downloads/min limit


class ClawHubCrawler(BaseCrawler):
    registry_id = "clawhub"

    def __init__(self, conn, *, output_dir=None, rate_limit_ms=3100, shard=None, max_workers=1, crawl_mode="incremental"):
        super().__init__(conn, output_dir=output_dir, rate_limit_ms=rate_limit_ms, shard=shard, max_workers=max_workers, crawl_mode=crawl_mode)

    def discover(self) -> list[dict]:
        """Fetch all skills from ClawHub API with pagination.

        In incremental mode, stops paginating when reaching skills older than last_crawl_at.
        """
        all_skills = []
        cursor = None
        last_updated_at = None  # stored as str(epoch_ms) from API

        if self.crawl_mode == "incremental":
            raw = self.get_state("last_updated_at")
            if raw:
                try:
                    last_updated_at = int(raw)
                    logger.info("Incremental mode: watermark last_updated_at=%s", last_updated_at)
                except ValueError:
                    logger.warning("Invalid watermark '%s', ignoring", raw)
                    last_updated_at = None

        while True:
            url = f"{CLAWHUB_API}/skills?limit=200&sort=updated"
            if cursor:
                url += f"&cursor={cursor}"

            try:
                resp = requests.get(url, timeout=30)
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error("ClawHub API error: %s", e)
                break

            items = data.get("items", [])
            if not items:
                break

            stop_paginating = False
            for item in items:
                slug = item.get("slug", "")
                if not slug:
                    continue

                raw_updated = item.get("updatedAt")

                # In incremental mode, stop when we reach skills older than watermark
                # updatedAt is epoch ms (int) from the API
                if last_updated_at and raw_updated is not None and int(raw_updated) <= last_updated_at:
                    logger.info("Reached watermark at %s, stopping pagination (%d skills so far)", raw_updated, len(all_skills))
                    stop_paginating = True
                    break

                all_skills.append({
                    "slug": slug,
                    "name": item.get("name", slug),
                    "url": f"https://clawhub.ai/skills/{slug}",
                    "metadata": {
                        k: item.get(k)
                        for k in ("description", "author", "version", "updatedAt")
                        if item.get(k)
                    },
                })

            if stop_paginating:
                break

            cursor = data.get("nextCursor")
            if not cursor:
                break

            time.sleep(0.3)
            logger.info("Discovered %d skills so far...", len(all_skills))

        # Update watermark to the newest updatedAt seen (first item, since sorted desc)
        if all_skills and all_skills[0].get("metadata", {}).get("updatedAt"):
            newest = str(all_skills[0]["metadata"]["updatedAt"])
            self.set_state("last_updated_at", newest)
            logger.info("Updated watermark last_updated_at=%s", newest)
        elif not all_skills and not last_updated_at:
            # First run with no skills found — store current epoch ms as fallback
            import time as _time
            self.set_state("last_updated_at", str(int(_time.time() * 1000)))

        return all_skills

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download a skill zip from ClawHub and extract SKILL.md.

        In incremental mode, does a HEAD request first to check ETag before
        downloading the full ZIP.
        """
        skill_id = f"{self.registry_id}:{slug}"
        url = f"{CLAWHUB_API}/download?slug={slug}&tag=latest"

        # Incremental: HEAD pre-check with ETag
        if self.crawl_mode == "incremental":
            stored_etag = self.get_state(f"etag:{slug}")
            if stored_etag:
                try:
                    head_resp = requests.head(url, timeout=15)
                    if head_resp.status_code == 200:
                        remote_etag = head_resp.headers.get("ETag", "")
                        if remote_etag and remote_etag == stored_etag:
                            return CrawlResult(skill_id=skill_id, slug=slug, skipped=True)
                except requests.RequestException:
                    pass  # Fall through to full download

        for attempt in range(3):
            self.rate_limiter.wait()
            try:
                resp = requests.get(url, timeout=30)
                if resp.status_code == 410:
                    return CrawlResult(skill_id=skill_id, slug=slug, error="soft-deleted (410)")
                if resp.status_code == 429:
                    wait = 10 * (attempt + 1)
                    logger.warning("ClawHub 429 for %s, backing off %ds", slug, wait)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == 2:
                    return CrawlResult(skill_id=skill_id, slug=slug, error=str(e))
                time.sleep(5)
        else:
            return CrawlResult(skill_id=skill_id, slug=slug, error="429 after retries")

        # Store ETag for future incremental runs
        etag = resp.headers.get("ETag", "")
        if etag:
            self.set_state(f"etag:{slug}", etag)

        # Extract SKILL.md from zip
        try:
            with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
                for name in zf.namelist():
                    if name.upper().endswith("SKILL.MD"):
                        content_bytes = zf.read(name)
                        content_text = content_bytes.decode("utf-8", errors="replace")

                        new_hash = content_hash(content_text)
                        if not self.is_content_changed(skill_id, new_hash):
                            return CrawlResult(skill_id=skill_id, slug=slug, skipped=True)

                        return CrawlResult(
                            skill_id=skill_id,
                            slug=slug,
                            name=kwargs.get("name", slug),
                            url=kwargs.get("url"),
                            content=content_text,
                            content_hash=new_hash,
                            content_size=len(content_text),
                        )
        except zipfile.BadZipFile:
            return CrawlResult(skill_id=skill_id, slug=slug, error="Bad zip file")

        return CrawlResult(skill_id=skill_id, slug=slug, error="No SKILL.md in zip")


def main():
    """CLI entrypoint for ClawHub crawler."""
    import argparse
    import json
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl ClawHub registry")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental", help="Crawl mode")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = ClawHubCrawler(conn, output_dir=args.output_dir, crawl_mode=args.mode)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
