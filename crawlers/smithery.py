#!/usr/bin/env python3
"""Crawler for Smithery.ai MCP server registry.

Smithery publishes a public REST API at registry.smithery.ai.
Discovery uses paginated listing, download fetches server detail (tools, description).

Incremental mode: stores the most recent createdAt timestamp as a watermark
and stops pagination when reaching previously-seen servers.
"""

from __future__ import annotations

import json
import logging
import re
import time

import requests

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash

logger = logging.getLogger("observatory.smithery")

SMITHERY_API = "https://registry.smithery.ai"
PAGE_SIZE = 50  # API returns empty pages above 50


class SmitheryCrawler(BaseCrawler):
    registry_id = "smithery"

    def __init__(self, conn, *, output_dir=None, rate_limit_ms=500, shard=None, max_workers=4, crawl_mode="incremental"):
        super().__init__(conn, output_dir=output_dir, rate_limit_ms=rate_limit_ms, shard=shard, max_workers=max_workers, crawl_mode=crawl_mode)

    def discover(self) -> list[dict]:
        """Fetch all servers from Smithery API with page-based pagination.

        In incremental mode, stores the newest createdAt as a watermark and
        stops when reaching servers older than the watermark.
        """
        all_servers = []
        watermark = None

        if self.crawl_mode == "incremental":
            raw = self.get_state("last_created_at")
            if raw:
                watermark = raw
                logger.info("Incremental mode: watermark last_created_at=%s", watermark)

        page = 1
        total_pages = None
        newest_created_at = None

        while True:
            url = f"{SMITHERY_API}/servers?page={page}&pageSize={PAGE_SIZE}"

            try:
                self.rate_limiter.wait()
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "AguaraObservatory/0.1 (https://github.com/garagon/aguara-observatory)",
                })
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error("Smithery API error on page %d: %s", page, e)
                break

            servers = data.get("servers", [])
            pagination = data.get("pagination", {})

            if total_pages is None:
                total_pages = pagination.get("totalPages", 1)
                total_count = pagination.get("totalCount", 0)
                logger.info("Smithery: %d total servers, %d pages", total_count, total_pages)

            if not servers:
                break

            stop_paginating = False
            for server in servers:
                qualified_name = server.get("qualifiedName", "")
                if not qualified_name:
                    continue

                created_at = server.get("createdAt", "")

                # Track the newest createdAt for watermark update
                if newest_created_at is None and created_at:
                    newest_created_at = created_at

                # In incremental mode, stop at watermark
                if watermark and created_at and created_at <= watermark:
                    logger.info(
                        "Reached watermark at %s, stopping pagination (%d servers so far)",
                        created_at, len(all_servers),
                    )
                    stop_paginating = True
                    break

                # Use qualifiedName as slug (e.g. "upstash/context7-mcp" or "exa")
                slug = qualified_name.replace("/", "_")

                all_servers.append({
                    "slug": slug,
                    "name": server.get("displayName", qualified_name),
                    "url": server.get("homepage", f"https://smithery.ai/server/{qualified_name}"),
                    "metadata": {
                        k: server.get(k)
                        for k in ("description", "namespace", "verified", "useCount", "remote", "createdAt")
                        if server.get(k) is not None
                    },
                    "qualified_name": qualified_name,
                })

            if stop_paginating:
                break

            page += 1
            if total_pages and page > total_pages:
                break

            logger.info("Discovered %d servers so far (page %d/%s)...", len(all_servers), page - 1, total_pages)

        # Update watermark
        if newest_created_at:
            self.set_state("last_created_at", newest_created_at)
            logger.info("Updated watermark last_created_at=%s", newest_created_at)

        return all_servers

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download server detail from Smithery API.

        Fetches the detail endpoint which includes tools, connections, and description.
        Synthesizes a Markdown document for Aguara to scan.
        """
        skill_id = f"{self.registry_id}:{slug}"
        qualified_name = kwargs.get("qualified_name", slug.replace("_", "/", 1))

        detail_url = f"{SMITHERY_API}/servers/{qualified_name}"

        try:
            self.rate_limiter.wait()
            resp = requests.get(detail_url, timeout=20, headers={
                "User-Agent": "AguaraObservatory/0.1 (https://github.com/garagon/aguara-observatory)",
            })
            if resp.status_code == 404:
                return CrawlResult(skill_id=skill_id, slug=slug, error="not found (404)")
            if resp.status_code == 429:
                time.sleep(5)
                return CrawlResult(skill_id=skill_id, slug=slug, error="rate limited (429)")
            resp.raise_for_status()
            detail = resp.json()
        except requests.RequestException as e:
            return CrawlResult(skill_id=skill_id, slug=slug, error=str(e))

        # Synthesize scannable content from API detail
        content = self._build_content(detail, kwargs)

        if not content:
            return CrawlResult(skill_id=skill_id, slug=slug, error="No content available")

        new_hash = content_hash(content)
        if not self.is_content_changed(skill_id, new_hash):
            return CrawlResult(skill_id=skill_id, slug=slug, skipped=True)

        return CrawlResult(
            skill_id=skill_id,
            slug=slug,
            name=kwargs.get("name", slug),
            url=kwargs.get("url"),
            content=content,
            content_hash=new_hash,
            content_size=len(content),
        )

    @staticmethod
    def _build_content(detail: dict, kwargs: dict) -> str | None:
        """Build a Markdown document from Smithery server detail."""
        name = detail.get("displayName") or kwargs.get("name", "")
        desc = detail.get("description", "")
        tools = detail.get("tools") or []
        connections = detail.get("connections") or []
        security = detail.get("security")

        parts = [f"# {name}\n"]

        if desc:
            parts.append(f"{desc}\n")

        # Include tool definitions — this is the primary scan target
        if tools:
            parts.append("## Tools\n")
            for tool in tools:
                tool_name = tool.get("name", "unknown")
                tool_desc = tool.get("description", "")
                parts.append(f"### {tool_name}\n")
                if tool_desc:
                    parts.append(f"{tool_desc}\n")
                input_schema = tool.get("inputSchema")
                if input_schema:
                    parts.append(f"```json\n{json.dumps(input_schema, indent=2)}\n```\n")

        # Include connection/deployment info
        if connections:
            parts.append("## Connections\n")
            for conn_info in connections:
                conn_type = conn_info.get("type", "unknown")
                deploy_url = conn_info.get("deploymentUrl", "")
                parts.append(f"- **{conn_type}**: {deploy_url}\n")
                config_schema = conn_info.get("configSchema")
                if config_schema and config_schema.get("properties"):
                    parts.append(f"```json\n{json.dumps(config_schema, indent=2)}\n```\n")

        # Include security metadata if present
        if security:
            parts.append("## Security\n")
            parts.append(f"```json\n{json.dumps(security, indent=2)}\n```\n")

        content = "\n".join(parts)
        return content if len(content) > 20 else None


def main():
    """CLI entrypoint for Smithery crawler."""
    import argparse
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl Smithery.ai registry")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental", help="Crawl mode")
    parser.add_argument("--limit", type=int, default=0, help="Max servers to crawl (0=unlimited)")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = SmitheryCrawler(conn, output_dir=args.output_dir, crawl_mode=args.mode)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
