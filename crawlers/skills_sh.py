#!/usr/bin/env python3
"""Crawler for skills.sh registry.

Ported from Aguara benchmark scripts: discover.py + download_skills.py.
Changes from original:
  - No skill limit (crawls ALL skills)
  - Shard support (A-F, G-L, M-R, S-Z) for parallel GH Actions
  - Writes to Turso DB instead of local JSON manifest
  - Incremental via content SHA-256 hash
"""

from __future__ import annotations

import json
import logging
import re
import subprocess
import time
from pathlib import Path
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler
from crawlers.models import CrawlResult
from crawlers.utils import content_hash, shard_matches

logger = logging.getLogger("observatory.skills_sh")

SITEMAP_URL = "https://skills.sh/sitemap.xml"
RAW_BASE = "https://raw.githubusercontent.com"
GH_API_RATE_LIMIT_MS = 200
RAW_RATE_LIMIT_MS = 100


class SkillsShCrawler(BaseCrawler):
    registry_id = "skills-sh"

    def __init__(self, conn, *, output_dir=None, rate_limit_ms=500, shard=None):
        super().__init__(conn, output_dir=output_dir, rate_limit_ms=rate_limit_ms, shard=shard)
        self._repo_trees: dict[str, dict | None] = {}  # cache

    # --- Discovery ---

    def discover(self) -> list[dict]:
        """Fetch sitemap and parse all skill URLs."""
        logger.info("Fetching sitemap from %s", SITEMAP_URL)
        resp = requests.get(SITEMAP_URL, timeout=30, headers={
            "User-Agent": "AguaraObservatory/0.1"
        })
        resp.raise_for_status()
        logger.info("Sitemap size: %d bytes", len(resp.text))

        skills = self._parse_sitemap(resp.text)
        logger.info("Parsed %d skill URLs from sitemap", len(skills))

        # Apply shard filter
        if self.shard:
            skills = [s for s in skills if shard_matches(s["slug"], self.shard)]
            logger.info("After shard filter (%s): %d skills", self.shard, len(skills))

        return skills

    def _parse_sitemap(self, xml_text: str) -> list[dict]:
        """Parse sitemap XML, extract skill entries."""
        root = ElementTree.fromstring(xml_text)
        ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        skills = []
        seen = set()

        for loc in root.findall(".//sm:loc", ns):
            url = loc.text.strip() if loc.text else ""
            m = re.match(r"https://skills\.sh/([^/]+)/([^/]+)/([^/]+)/?$", url)
            if not m:
                continue
            org, repo, skill = m.group(1), m.group(2), m.group(3)
            if skill == "security":
                continue
            key = (org, repo, skill)
            if key in seen:
                continue
            seen.add(key)

            slug = f"{org}_{repo}__{skill}"
            skills.append({
                "slug": slug,
                "name": skill,
                "url": url,
                "metadata": {"org": org, "repo": repo, "skill": skill},
            })

        return skills

    # --- Download ---

    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download SKILL.md content via GitHub raw or skills.sh scrape."""
        metadata = kwargs.get("metadata", {})
        org = metadata.get("org", "")
        repo = metadata.get("repo", "")
        skill = metadata.get("skill", "")
        url = kwargs.get("url", "")

        if not org or not repo:
            return CrawlResult(
                skill_id=f"{self.registry_id}:{slug}",
                slug=slug,
                error="Missing org/repo metadata",
            )

        skill_id = f"{self.registry_id}:{slug}"

        content = None
        method = None

        # Method 1: GitHub tree + raw download
        tree = self._get_repo_tree(org, repo)
        if tree:
            path = self._find_skill_path(tree, skill)
            if path:
                content = self._download_raw(org, repo, path)
                if content:
                    method = f"raw:{path}"
                time.sleep(RAW_RATE_LIMIT_MS / 1000)

        # Method 2: Try common paths directly
        if not content:
            for try_path in [
                f"skills/{skill}/SKILL.md",
                f"{skill}/SKILL.md",
                "SKILL.md",
            ]:
                content = self._download_raw(org, repo, try_path)
                if content:
                    method = f"raw-guess:{try_path}"
                    break
                time.sleep(RAW_RATE_LIMIT_MS / 1000)

        # Method 3: Scrape skills.sh page
        if not content and url:
            content = self._scrape_skills_sh(url)
            if content:
                method = "scrape"
            time.sleep(RAW_RATE_LIMIT_MS / 1000)

        if not content:
            return CrawlResult(skill_id=skill_id, slug=slug, error="All download methods failed")

        # Check if content changed
        new_hash = content_hash(content)
        if not self.is_content_changed(skill_id, new_hash):
            return CrawlResult(skill_id=skill_id, slug=slug, skipped=True)

        return CrawlResult(
            skill_id=skill_id,
            slug=slug,
            name=skill,
            url=url,
            content=content,
            content_hash=new_hash,
            content_size=len(content),
            metadata={"method": method, "org": org, "repo": repo},
        )

    # --- GitHub helpers ---

    def _get_repo_tree(self, org: str, repo: str) -> dict | None:
        """Get file tree for a repo (cached per repo)."""
        key = f"{org}/{repo}"
        if key in self._repo_trees:
            return self._repo_trees[key]

        tree = self._gh_api_tree(org, repo)
        self._repo_trees[key] = tree
        time.sleep(GH_API_RATE_LIMIT_MS / 1000)
        return tree

    def _gh_api_tree(self, org: str, repo: str) -> dict | None:
        """Call GitHub API via gh CLI for repo tree."""
        for branch in ("main", "master"):
            data = self._gh_api(f"repos/{org}/{repo}/git/trees/{branch}?recursive=1")
            if data and "tree" in data:
                return {
                    item["path"]: item["sha"]
                    for item in data["tree"]
                    if item["type"] == "blob" and item["path"].lower().endswith(".md")
                }
        return None

    @staticmethod
    def _gh_api(endpoint: str) -> dict | None:
        """Call GitHub API via gh CLI."""
        try:
            result = subprocess.run(
                ["gh", "api", endpoint],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
            pass
        return None

    @staticmethod
    def _find_skill_path(tree: dict, skill: str) -> str | None:
        """Find SKILL.md path in repo tree."""
        candidates = [
            f"skills/{skill}/SKILL.md",
            f"skills/{skill}/skill.md",
            f"{skill}/SKILL.md",
            f"{skill}/skill.md",
            "SKILL.md",
        ]
        for c in candidates:
            if c in tree:
                return c

        for path in tree:
            parts = path.lower().split("/")
            if skill.lower() in parts and parts[-1] in ("skill.md",):
                return path

        return None

    @staticmethod
    def _download_raw(org: str, repo: str, path: str) -> str | None:
        """Download raw file from GitHub."""
        for branch in ("main", "master"):
            url = f"{RAW_BASE}/{org}/{repo}/{branch}/{path}"
            try:
                resp = requests.get(url, timeout=15)
                if resp.status_code == 200:
                    return resp.text
            except requests.RequestException:
                pass
        return None

    @staticmethod
    def _scrape_skills_sh(url: str) -> str | None:
        """Fallback: scrape skill content from skills.sh page."""
        if not url:
            return None
        try:
            resp = requests.get(url, timeout=15, headers={
                "User-Agent": "AguaraObservatory/0.1"
            })
            if resp.status_code != 200:
                return None
            soup = BeautifulSoup(resp.text, "lxml")
            main = soup.find("main") or soup.find("article") or soup.find("div", class_="prose")
            if main:
                return main.get_text(separator="\n", strip=True)
        except Exception:
            pass
        return None


def main():
    """CLI entrypoint for skills.sh crawler."""
    import argparse
    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Crawl skills.sh registry")
    parser.add_argument("--shard", help="Letter range shard (e.g. A-F)")
    parser.add_argument("--output-dir", type=Path, help="Output directory for skill files")
    parser.add_argument("--rate-limit", type=int, default=500, help="Rate limit in ms")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    crawler = SkillsShCrawler(
        conn,
        output_dir=args.output_dir,
        rate_limit_ms=args.rate_limit,
        shard=args.shard,
    )
    stats = crawler.crawl()
    conn.commit()
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
