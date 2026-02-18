#!/usr/bin/env python3
"""Crawler for PulseMCP registry (www.pulsemcp.com).

PulseMCP has a public API for listing MCP servers.
"""

from __future__ import annotations

import logging

import requests

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash

logger = logging.getLogger("observatory.mcp_registry")

PULSEMCP_API = "https://api.pulsemcp.com/v0beta1"


class PulseMCPCrawler(BaseCrawler):
    registry_id = "mcp-registry"

    def discover(self) -> list[dict]:
        """Fetch all MCP servers from PulseMCP API."""
        all_servers = []
        offset = 0
        limit = 100

        while True:
            url = f"{PULSEMCP_API}/servers?count_per_page={limit}&offset={offset}"
            try:
                self.rate_limiter.wait()
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "AguaraObservatory/0.1"
                })
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error("PulseMCP API error at offset %d: %s", offset, e)
                break

            servers = data.get("servers", [])
            if not servers:
                break

            for server in servers:
                name = server.get("name", "")
                slug = self._make_slug(name, server.get("url", ""))
                if not slug:
                    continue

                all_servers.append({
                    "slug": slug,
                    "name": name,
                    "url": server.get("url", ""),
                    "metadata": {
                        k: server.get(k)
                        for k in ("description", "github_url", "category",
                                  "author", "created_at", "updated_at")
                        if server.get(k)
                    },
                })

            if len(servers) < limit:
                break
            offset += limit
            logger.info("Discovered %d servers so far...", len(all_servers))

        return all_servers

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download MCP server README/description from GitHub."""
        skill_id = f"{self.registry_id}:{slug}"
        metadata = kwargs.get("metadata", {})
        github_url = metadata.get("github_url", "")

        # Try to get README from GitHub
        content = None
        if github_url:
            content = self._download_github_readme(github_url)

        # Fallback: use description as content
        if not content:
            desc = metadata.get("description", "")
            name = kwargs.get("name", slug)
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

    def _download_github_readme(self, github_url: str) -> str | None:
        """Download README.md from a GitHub repo."""
        # Extract owner/repo from GitHub URL
        import re
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

    @staticmethod
    def _make_slug(name: str, url: str) -> str:
        """Create a URL-safe slug from server name."""
        import re
        # Prefer GitHub-style org/repo slug
        m = re.match(r"https?://github\.com/([^/]+)/([^/]+)", url)
        if m:
            return f"{m.group(1)}_{m.group(2)}".lower()
        # Fallback: slugify name
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", name).strip("-").lower()
        return slug or "unknown"


def main():
    import argparse
    import json
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl PulseMCP registry")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = PulseMCPCrawler(conn, output_dir=args.output_dir)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
