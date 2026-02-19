#!/usr/bin/env python3
"""Resume downloads for skills that were discovered but not yet downloaded.

Usage:
    python -m crawlers.resume_downloads --registry clawhub [--rate-limit-ms 3000] [--max-workers 1]
"""

from __future__ import annotations

import argparse
import json
import logging
import time

from crawlers.db import connect, init_schema, upsert_skill
from crawlers.utils import setup_logging

logger = logging.getLogger("observatory.resume")


def resume_registry(conn, registry_id: str, rate_limit_ms: int = 3000, max_workers: int = 1) -> dict:
    """Download pending skills for a registry."""
    # Get skills without content_hash
    rows = conn.execute(
        """SELECT slug, name, url, metadata FROM skills
           WHERE registry_id = ? AND deleted = 0 AND content_hash IS NULL
           ORDER BY slug""",
        (registry_id,),
    ).fetchall()

    if not rows:
        logger.info("[%s] No pending downloads", registry_id)
        return {"pending": 0, "downloaded": 0, "failed": 0, "skipped": 0}

    logger.info("[%s] Resuming %d pending downloads (rate=%dms)", registry_id, len(rows), rate_limit_ms)

    # Build skill_info list
    skills = []
    for slug, name, url, metadata_json in rows:
        info = {"slug": slug, "name": name, "url": url}
        if metadata_json:
            try:
                info["metadata"] = json.loads(metadata_json)
            except (json.JSONDecodeError, TypeError):
                pass
        skills.append(info)

    # Import the right crawler
    if registry_id == "clawhub":
        from crawlers.clawhub import ClawHubCrawler
        crawler = ClawHubCrawler(conn, rate_limit_ms=rate_limit_ms, max_workers=max_workers)
    elif registry_id == "mcp-so":
        from crawlers.mcp_so import McpSoCrawler
        crawler = McpSoCrawler(conn, rate_limit_ms=rate_limit_ms, max_workers=max_workers)
    elif registry_id == "skills-sh":
        from crawlers.skills_sh import SkillsShCrawler
        crawler = SkillsShCrawler(conn, rate_limit_ms=rate_limit_ms, max_workers=max_workers)
    elif registry_id == "mcp-registry":
        from crawlers.pulsemcp_scraper import PulseMCPScraper
        crawler = PulseMCPScraper(conn, rate_limit_ms=rate_limit_ms, max_workers=max_workers)
    else:
        logger.error("Unknown registry: %s", registry_id)
        return {"error": f"Unknown registry: {registry_id}"}

    crawler.stats["discovered"] = len(skills)

    # Download only (skip discover phase)
    if max_workers > 1:
        crawler._crawl_concurrent(skills)
    else:
        crawler._crawl_sequential(skills)

    conn.commit()

    stats = {
        "pending": len(skills),
        "downloaded": crawler.stats["downloaded"],
        "failed": crawler.stats["failed"],
        "skipped": crawler.stats["skipped"],
    }
    logger.info("[%s] Resume complete: %s", registry_id, stats)
    return stats


def main():
    parser = argparse.ArgumentParser(description="Resume pending downloads")
    parser.add_argument("--registry", required=True, help="Registry ID")
    parser.add_argument("--rate-limit-ms", type=int, default=3000, help="Rate limit in ms")
    parser.add_argument("--max-workers", type=int, default=1, help="Concurrent workers")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    stats = resume_registry(conn, args.registry, args.rate_limit_ms, args.max_workers)
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
