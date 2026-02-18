#!/usr/bin/env python3
"""Crawler for mcp.so MCP server directory.

mcp.so is an HTML-based directory. We scrape server listings and their
detail pages to extract README/description content.
"""

from __future__ import annotations

import logging
import re

import requests
from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash, shard_matches

logger = logging.getLogger("observatory.mcp_so")

MCP_SO_BASE = "https://mcp.so"


class McpSoCrawler(BaseCrawler):
    registry_id = "mcp-so"

    def discover(self) -> list[dict]:
        """Discover MCP servers from mcp.so listing pages."""
        all_servers = []
        page = 1

        while True:
            url = f"{MCP_SO_BASE}/servers?page={page}"
            try:
                self.rate_limiter.wait()
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "AguaraObservatory/0.1"
                })
                if resp.status_code != 200:
                    break
            except requests.RequestException as e:
                logger.error("mcp.so request error at page %d: %s", page, e)
                break

            soup = BeautifulSoup(resp.text, "lxml")
            cards = soup.select("a[href^='/server/']")

            if not cards:
                break

            seen_this_page = set()
            for card in cards:
                href = card.get("href", "")
                slug = href.removeprefix("/server/").strip("/")
                if not slug or slug in seen_this_page:
                    continue
                seen_this_page.add(slug)

                # Apply shard filter
                if self.shard and not shard_matches(slug, self.shard):
                    continue

                name = card.get_text(strip=True) or slug
                all_servers.append({
                    "slug": slug,
                    "name": name,
                    "url": f"{MCP_SO_BASE}/server/{slug}",
                })

            logger.info("Page %d: found %d servers (total: %d)", page, len(seen_this_page), len(all_servers))
            page += 1

            # Safety: stop if we've gone too many pages
            if page > 500:
                logger.warning("Stopping at page %d (safety limit)", page)
                break

        return all_servers

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download server detail page from mcp.so and extract content."""
        skill_id = f"{self.registry_id}:{slug}"
        url = kwargs.get("url", f"{MCP_SO_BASE}/server/{slug}")

        self.rate_limiter.wait()
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "AguaraObservatory/0.1"
            })
            if resp.status_code != 200:
                return CrawlResult(skill_id=skill_id, slug=slug, error=f"HTTP {resp.status_code}")
        except requests.RequestException as e:
            return CrawlResult(skill_id=skill_id, slug=slug, error=str(e))

        # Extract content from detail page
        content = self._extract_content(resp.text, kwargs.get("name", slug))
        if not content:
            return CrawlResult(skill_id=skill_id, slug=slug, error="No content extracted")

        new_hash = content_hash(content)
        if not self.is_content_changed(skill_id, new_hash):
            return CrawlResult(skill_id=skill_id, slug=slug, skipped=True)

        # Try to find GitHub URL for metadata
        github_url = self._extract_github_url(resp.text)

        return CrawlResult(
            skill_id=skill_id,
            slug=slug,
            name=kwargs.get("name"),
            url=url,
            content=content,
            content_hash=new_hash,
            content_size=len(content),
            metadata={"github_url": github_url} if github_url else None,
        )

    @staticmethod
    def _extract_content(html: str, name: str) -> str | None:
        """Extract server description/README from detail page."""
        soup = BeautifulSoup(html, "lxml")

        # Look for main content area (README rendered)
        content_area = (
            soup.find("div", class_=re.compile(r"readme|content|description|prose", re.I))
            or soup.find("article")
            or soup.find("main")
        )

        if content_area:
            text = content_area.get_text(separator="\n", strip=True)
            if len(text) > 50:
                return text

        # Fallback: get meta description + any structured data
        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc = meta_desc.get("content", "") if meta_desc else ""
        if desc:
            return f"# {name}\n\n{desc}\n"

        return None

    @staticmethod
    def _extract_github_url(html: str) -> str | None:
        """Extract GitHub repo URL from page."""
        m = re.search(r'href="(https://github\.com/[^/]+/[^/"]+)"', html)
        return m.group(1) if m else None


def main():
    import argparse
    import json
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl mcp.so registry")
    parser.add_argument("--shard", help="Letter range shard (e.g. A-M)")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = McpSoCrawler(conn, output_dir=args.output_dir, shard=args.shard)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
