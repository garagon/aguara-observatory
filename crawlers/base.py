"""Base crawler interface for Aguara Observatory."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path

import libsql_experimental as libsql

from crawlers.db import upsert_skill, get_skill_hash
from crawlers.models import CrawlResult
from crawlers.utils import RateLimiter, content_hash

logger = logging.getLogger("observatory.crawler")


class BaseCrawler(ABC):
    """Base class for registry crawlers.

    Subclasses must implement:
        - registry_id: str property
        - discover(): list discovered skill slugs
        - download(slug): download a single skill's content
    """

    def __init__(
        self,
        conn: libsql.Connection,
        *,
        output_dir: Path | None = None,
        rate_limit_ms: int = 500,
        shard: str | None = None,
    ):
        self.conn = conn
        self.output_dir = output_dir or Path(f"data/{self.registry_id}")
        self.rate_limiter = RateLimiter(rate_limit_ms)
        self.shard = shard
        self.stats = {"discovered": 0, "downloaded": 0, "skipped": 0, "failed": 0}

    @property
    @abstractmethod
    def registry_id(self) -> str:
        """Registry identifier (e.g. 'skills-sh')."""
        ...

    @abstractmethod
    def discover(self) -> list[dict]:
        """Discover all skills in the registry.

        Returns list of dicts with at least 'slug' key.
        May also include 'name', 'url', 'metadata'.
        """
        ...

    @abstractmethod
    def download(self, slug: str, **kwargs) -> CrawlResult:
        """Download content for a single skill.

        Returns CrawlResult with content, hash, etc.
        """
        ...

    def crawl(self) -> dict:
        """Run full crawl: discover → download (incremental).

        Returns stats dict.
        """
        logger.info("[%s] Starting crawl (shard=%s)", self.registry_id, self.shard)

        # Phase 1: Discover
        skills = self.discover()
        self.stats["discovered"] = len(skills)
        logger.info("[%s] Discovered %d skills", self.registry_id, len(skills))

        # Phase 2: Download (incremental)
        for i, skill_info in enumerate(skills, 1):
            slug = skill_info["slug"]
            skill_id = f"{self.registry_id}:{slug}"

            if i % 100 == 0:
                logger.info("[%s] Progress: %d/%d", self.registry_id, i, len(skills))

            # Register the skill in DB (upsert)
            upsert_skill(
                self.conn,
                self.registry_id,
                slug,
                name=skill_info.get("name"),
                url=skill_info.get("url"),
                metadata=skill_info.get("metadata"),
            )

            # Check if content changed
            try:
                kwargs = {k: v for k, v in skill_info.items() if k != "slug"}
                result = self.download(slug, **kwargs)
            except Exception as e:
                logger.warning("[%s] Failed to download %s: %s", self.registry_id, slug, e)
                self.stats["failed"] += 1
                continue

            if result.skipped:
                self.stats["skipped"] += 1
                continue

            if result.error:
                logger.warning("[%s] Error for %s: %s", self.registry_id, slug, result.error)
                self.stats["failed"] += 1
                continue

            # Update skill with content hash
            if result.content_hash:
                upsert_skill(
                    self.conn,
                    self.registry_id,
                    slug,
                    content_hash=result.content_hash,
                    content_size=result.content_size,
                )

            # Save content to disk for scanning
            if result.content:
                self._save_content(slug, result.content)

            self.stats["downloaded"] += 1

        self.conn.commit()
        logger.info(
            "[%s] Crawl complete: %d discovered, %d downloaded, %d skipped, %d failed",
            self.registry_id,
            self.stats["discovered"],
            self.stats["downloaded"],
            self.stats["skipped"],
            self.stats["failed"],
        )
        return self.stats

    def _save_content(self, slug: str, content: str) -> None:
        """Save skill content to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = slug.replace("/", "_").replace(":", "_")
        filepath = self.output_dir / f"{safe_name}.md"
        filepath.write_text(content, encoding="utf-8")

    def is_content_changed(self, skill_id: str, new_hash: str) -> bool:
        """Check if content has changed since last crawl."""
        old_hash = get_skill_hash(self.conn, skill_id)
        return old_hash != new_hash
