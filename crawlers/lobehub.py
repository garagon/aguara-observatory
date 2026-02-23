#!/usr/bin/env python3
"""Crawler for LobeHub plugin marketplace.

LobeHub publishes a plugin index as a JSON file on GitHub.

Incremental mode: hashes the index JSON responses. If unchanged, skips entirely.
"""

from __future__ import annotations

import logging
import re

import requests

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash

logger = logging.getLogger("observatory.lobehub")

# LobeHub publishes indexes as JSON via CDN
LOBEHUB_PLUGINS_INDEX = "https://chat-plugins.lobehub.com/index.json"
LOBEHUB_AGENTS_INDEX = "https://chat-agents.lobehub.com/index.json"


class LobeHubCrawler(BaseCrawler):
    registry_id = "lobehub"

    def __init__(self, conn, *, output_dir=None, rate_limit_ms=500, shard=None, max_workers=1, crawl_mode="incremental"):
        super().__init__(conn, output_dir=output_dir, rate_limit_ms=rate_limit_ms, shard=shard, max_workers=max_workers, crawl_mode=crawl_mode)

    def discover(self) -> list[dict]:
        """Fetch all plugins/tools from LobeHub indexes.

        In incremental mode, hashes each index response. If unchanged from
        stored hash, skips that index entirely.
        """
        all_plugins = []

        for index_url, kind, items_key in [
            (LOBEHUB_PLUGINS_INDEX, "plugin", "plugins"),
            (LOBEHUB_AGENTS_INDEX, "agent", "agents"),
        ]:
            try:
                self.rate_limiter.wait()
                resp = requests.get(index_url, timeout=30)
                resp.raise_for_status()
            except Exception as e:
                logger.warning("Failed to fetch LobeHub %s index: %s", kind, e)
                continue

            # Incremental: check if index content changed
            if self.crawl_mode == "incremental":
                index_hash = content_hash(resp.text)
                stored_hash = self.get_state(f"index_hash:{kind}")
                if stored_hash and stored_hash == index_hash:
                    logger.info("LobeHub %s index unchanged (hash match) — skipping", kind)
                    continue
                self.set_state(f"index_hash:{kind}", index_hash)

            try:
                data = resp.json()
            except Exception as e:
                logger.warning("Failed to parse LobeHub %s index JSON: %s", kind, e)
                continue

            plugins = data.get(items_key, [])
            for plugin in plugins:
                identifier = plugin.get("identifier", "")
                if not identifier:
                    continue

                slug = f"{kind}_{identifier}"
                all_plugins.append({
                    "slug": slug,
                    "name": plugin.get("meta", {}).get("title", identifier),
                    "url": f"https://lobehub.com/{kind}s/{identifier}",
                    "metadata": {
                        "kind": kind,
                        "identifier": identifier,
                        "description": plugin.get("meta", {}).get("description", ""),
                        "author": plugin.get("author", ""),
                        "homepage": plugin.get("homepage", ""),
                        "manifest_url": plugin.get("manifest", ""),
                    },
                })

            logger.info("LobeHub %s index: %d entries", kind, len(plugins))

        return all_plugins

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download plugin manifest/README content."""
        skill_id = f"{self.registry_id}:{slug}"
        metadata = kwargs.get("metadata", {})

        content = None

        # Try to download the manifest JSON (contains tool definitions)
        manifest_url = metadata.get("manifest_url", "")
        if manifest_url:
            content = self._download_manifest(manifest_url)

        # Try GitHub README if homepage is GitHub
        if not content:
            homepage = metadata.get("homepage", "")
            if "github.com" in homepage:
                content = self._download_github_readme(homepage)

        # Fallback: synthesize content from metadata
        if not content:
            name = kwargs.get("name", slug)
            desc = metadata.get("description", "")
            if desc:
                content = f"# {name}\n\n{desc}\n"
            else:
                return CrawlResult(skill_id=skill_id, slug=slug, error="No content available")

        new_hash = content_hash(content)
        if not self.is_content_changed(skill_id, new_hash):
            return CrawlResult(skill_id=skill_id, slug=slug, skipped=True)

        return CrawlResult(
            skill_id=skill_id,
            slug=slug,
            name=kwargs.get("name"),
            url=kwargs.get("url"),
            content=content,
            content_hash=new_hash,
            content_size=len(content),
        )

    def _download_manifest(self, manifest_url: str) -> str | None:
        """Download and stringify a plugin manifest JSON."""
        try:
            self.rate_limiter.wait()
            resp = requests.get(manifest_url, timeout=15)
            if resp.status_code == 200:
                # Return the raw JSON as content for scanning
                return resp.text
        except requests.RequestException:
            pass
        return None

    def _download_github_readme(self, github_url: str) -> str | None:
        """Download README.md from a GitHub repo URL."""
        m = re.match(r"https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$", github_url)
        if not m:
            return None
        owner, repo = m.group(1), m.group(2)
        for branch in ("main", "master"):
            url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/README.md"
            try:
                self.rate_limiter.wait()
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    return resp.text
            except requests.RequestException:
                pass
        return None


def main():
    import argparse
    import json
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl LobeHub registry")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental", help="Crawl mode")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = LobeHubCrawler(conn, output_dir=args.output_dir, crawl_mode=args.mode)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
