#!/usr/bin/env python3
"""Scraper for PulseMCP (www.pulsemcp.com) server directory.

Scrapes the public HTML pages since the API requires auth.
206 pages, 42 servers per page, ~8,600 total.
"""

from __future__ import annotations

import logging
import re
import time

import requests
from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash

logger = logging.getLogger("observatory.pulsemcp")

PULSEMCP_URL = "https://www.pulsemcp.com"


class PulseMCPScraper(BaseCrawler):
    registry_id = "mcp-registry"

    def __init__(self, conn, *, output_dir=None, rate_limit_ms=1500, shard=None, max_workers=1):
        super().__init__(conn, output_dir=output_dir, rate_limit_ms=rate_limit_ms, shard=shard, max_workers=max_workers)

    def discover(self) -> list[dict]:
        """Scrape all server listings from paginated HTML pages."""
        all_servers = []
        page = 1

        while True:
            self.rate_limiter.wait()
            url = f"{PULSEMCP_URL}/servers?page={page}&sort=alphabetical-asc"
            try:
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "AguaraObservatory/0.1 (+https://github.com/garagon/aguara-observatory)",
                })
                resp.raise_for_status()
            except Exception as e:
                logger.error("PulseMCP page %d error: %s", page, e)
                break

            servers = self._parse_listing_page(resp.text)
            if not servers:
                break

            all_servers.extend(servers)

            if page % 10 == 0:
                logger.info("Discovered %d servers (page %d)...", len(all_servers), page)

            page += 1

            # Safety: max 250 pages
            if page > 250:
                break

        return all_servers

    def _parse_listing_page(self, html: str) -> list[dict]:
        """Parse a single listing page and extract server info."""
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", attrs={"data-test-id": re.compile(r"^mcp-server-grid-card")})
        servers = []

        for card in cards:
            link = card.find("a", href=re.compile(r"^/servers/"))
            if not link:
                continue

            slug = link["href"].replace("/servers/", "").strip("/")
            if not slug:
                continue

            title_el = card.find("h3")
            author_el = card.find("p", class_=re.compile(r"text-14.*text-gray"))
            desc_el = card.find("p", class_=re.compile(r"text-15.*text-pulse"))

            name = title_el.text.strip() if title_el else slug
            author = author_el.text.strip() if author_el else None
            description = desc_el.text.strip() if desc_el else None

            metadata = {}
            if author:
                metadata["author"] = author
            if description:
                metadata["description"] = description

            servers.append({
                "slug": slug,
                "name": name,
                "url": f"{PULSEMCP_URL}/servers/{slug}",
                "metadata": metadata,
            })

        return servers

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download server detail page and extract description as content."""
        skill_id = f"{self.registry_id}:{slug}"
        url = f"{PULSEMCP_URL}/servers/{slug}"

        self.rate_limiter.wait()
        try:
            resp = requests.get(url, timeout=30, headers={
                "User-Agent": "AguaraObservatory/0.1 (+https://github.com/garagon/aguara-observatory)",
            })
            if resp.status_code == 404:
                return CrawlResult(skill_id=skill_id, slug=slug, error="404 not found")
            resp.raise_for_status()
        except requests.RequestException as e:
            return CrawlResult(skill_id=skill_id, slug=slug, error=str(e))

        # Parse detail page for full description
        content = self._parse_detail_page(resp.text, kwargs.get("name", slug))
        if not content:
            # Fallback: build content from metadata
            desc = (kwargs.get("metadata") or {}).get("description", "")
            name = kwargs.get("name", slug)
            if desc:
                content = f"# {name}\n\n{desc}\n"
            else:
                return CrawlResult(skill_id=skill_id, slug=slug, error="No content")

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

    def _parse_detail_page(self, html: str, fallback_name: str = "") -> str | None:
        """Extract meaningful content from a server detail page."""
        soup = BeautifulSoup(html, "html.parser")

        parts = []

        # Title
        title = soup.find("h1")
        if title:
            parts.append(f"# {title.text.strip()}")
        elif fallback_name:
            parts.append(f"# {fallback_name}")

        # Description sections
        for section in soup.find_all("div", class_=re.compile(r"prose|description|readme|content")):
            text = section.get_text(separator="\n", strip=True)
            if text and len(text) > 20:
                parts.append(text)

        # Tool/capability listings
        for heading in soup.find_all(["h2", "h3"]):
            heading_text = heading.text.strip()
            if any(kw in heading_text.lower() for kw in ("tool", "capabilit", "feature", "what")):
                # Get sibling content
                sibling = heading.find_next_sibling()
                if sibling:
                    text = sibling.get_text(separator="\n", strip=True)
                    if text:
                        parts.append(f"## {heading_text}\n{text}")

        if not parts:
            return None

        return "\n\n".join(parts) + "\n"


def main():
    import argparse
    import json
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Scrape PulseMCP registry")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    parser.add_argument("--max-workers", type=int, default=3, help="Concurrent workers")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = PulseMCPScraper(conn, output_dir=args.output_dir, max_workers=args.max_workers)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
