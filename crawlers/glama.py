#!/usr/bin/env python3
"""Crawler for Glama.ai MCP server registry.

Glama publishes a REST API at glama.ai/api/mcp/v1.
Discovery uses cursor-based pagination, download fetches server detail.

Incremental mode: uses index hash to detect changes in the listing.
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

logger = logging.getLogger("observatory.glama")

GLAMA_API = "https://glama.ai/api/mcp/v1"
PAGE_SIZE = 100  # Max supported by the API


class GlamaCrawler(BaseCrawler):
    registry_id = "glama"

    def __init__(self, conn, *, output_dir=None, rate_limit_ms=1000, shard=None, max_workers=4, crawl_mode="incremental"):
        super().__init__(conn, output_dir=output_dir, rate_limit_ms=rate_limit_ms, shard=shard, max_workers=max_workers, crawl_mode=crawl_mode)

    def discover(self) -> list[dict]:
        """Fetch all servers from Glama API with cursor-based pagination.

        Uses first/after pagination (GraphQL relay-style).
        Rate limit: 100 requests/second.
        """
        all_servers = []
        cursor = None

        while True:
            url = f"{GLAMA_API}/servers?first={PAGE_SIZE}"
            if cursor:
                url += f"&after={cursor}"

            try:
                self.rate_limiter.wait()
                resp = requests.get(url, timeout=30, headers={
                    "User-Agent": "AguaraObservatory/0.1 (https://github.com/garagon/aguara-observatory)",
                })
                resp.raise_for_status()
                data = resp.json()
            except Exception as e:
                logger.error("Glama API error: %s", e)
                break

            servers = data.get("servers", [])
            page_info = data.get("pageInfo", {})

            if not servers:
                break

            for server in servers:
                namespace = server.get("namespace", "")
                server_slug = server.get("slug", "")
                server_id = server.get("id", "")

                if not namespace:
                    continue

                # Build canonical slug: namespace_slug or just namespace
                if server_slug:
                    slug = f"{namespace}_{server_slug}"
                    qualified_name = f"{namespace}/{server_slug}"
                else:
                    slug = namespace
                    qualified_name = namespace

                all_servers.append({
                    "slug": slug,
                    "name": server.get("name", qualified_name),
                    "url": server.get("url", f"https://glama.ai/mcp/servers/{server_id}"),
                    "metadata": {
                        "glama_id": server_id,
                        "namespace": namespace,
                        "description": server.get("description", ""),
                        "attributes": server.get("attributes", []),
                        "repository_url": (server.get("repository") or {}).get("url", ""),
                    },
                    "qualified_name": qualified_name,
                })

            has_next = page_info.get("hasNextPage", False)
            cursor = page_info.get("endCursor")

            if not has_next or not cursor:
                break

            if len(all_servers) % 500 == 0:
                logger.info("Discovered %d servers so far...", len(all_servers))

        logger.info("Glama: discovered %d total servers", len(all_servers))
        return all_servers

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download server detail from Glama API.

        Fetches detail endpoint and GitHub README for full content.
        """
        skill_id = f"{self.registry_id}:{slug}"
        qualified_name = kwargs.get("qualified_name", slug.replace("_", "/", 1))
        metadata = kwargs.get("metadata", {})

        # Try to get detail from the API
        detail = self._fetch_detail(qualified_name)

        # Build content from detail + GitHub README
        content = self._build_content(detail, metadata, kwargs)

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

    def _fetch_detail(self, qualified_name: str) -> dict | None:
        """Fetch server detail from Glama API."""
        url = f"{GLAMA_API}/servers/{qualified_name}"
        try:
            self.rate_limiter.wait()
            resp = requests.get(url, timeout=20, headers={
                "User-Agent": "AguaraObservatory/0.1 (https://github.com/garagon/aguara-observatory)",
            })
            if resp.status_code == 404:
                return None
            if resp.status_code == 429:
                time.sleep(2)
                return None
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as e:
            logger.debug("Glama detail fetch failed for %s: %s", qualified_name, e)
            return None

    def _build_content(self, detail: dict | None, metadata: dict, kwargs: dict) -> str | None:
        """Build a Markdown document from Glama server detail + metadata."""
        name = kwargs.get("name", "")
        desc = metadata.get("description", "")

        parts = [f"# {name}\n"]

        # Use detail if available
        if detail:
            desc = detail.get("description", desc)
            tools = detail.get("tools") or []
            env_schema = detail.get("environmentVariablesJsonSchema")
            license_info = detail.get("spdxLicense")
            repo = detail.get("repository") or {}

            if desc:
                parts.append(f"{desc}\n")

            if repo.get("url"):
                parts.append(f"**Repository**: {repo['url']}\n")

            if license_info:
                parts.append(f"**License**: {license_info.get('name', 'Unknown')}\n")

            # Tool definitions — primary scan target
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

            # Environment variables — can reveal security concerns
            if env_schema and env_schema.get("properties"):
                parts.append("## Environment Variables\n")
                parts.append(f"```json\n{json.dumps(env_schema, indent=2)}\n```\n")
        else:
            # Fallback: use metadata only
            if desc:
                parts.append(f"{desc}\n")

            repo_url = metadata.get("repository_url", "")
            if repo_url:
                parts.append(f"**Repository**: {repo_url}\n")

        # Try GitHub README as supplementary content
        repo_url = metadata.get("repository_url", "")
        if not repo_url and detail:
            repo_url = (detail.get("repository") or {}).get("url", "")

        if repo_url and "github.com" in repo_url:
            readme = self._download_github_readme(repo_url)
            if readme:
                parts.append("\n## README\n")
                parts.append(readme)

        content = "\n".join(parts)
        return content if len(content) > 20 else None

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
    """CLI entrypoint for Glama crawler."""
    import argparse
    from pathlib import Path

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl Glama.ai registry")
    parser.add_argument("--output-dir", type=Path, help="Output directory")
    parser.add_argument("--mode", choices=["full", "incremental"], default="incremental", help="Crawl mode")
    parser.add_argument("--limit", type=int, default=0, help="Max servers to crawl (0=unlimited)")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = GlamaCrawler(conn, output_dir=args.output_dir, crawl_mode=args.mode)
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
