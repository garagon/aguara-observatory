"""Base crawler interface for Aguara Observatory."""

from __future__ import annotations

import logging
import threading
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        max_workers: int = 1,
    ):
        self.conn = conn
        self.output_dir = output_dir or Path(f"data/{self.registry_id}")
        self.rate_limiter = RateLimiter(rate_limit_ms)
        self.shard = shard
        self.max_workers = max_workers
        self.stats = {"discovered": 0, "downloaded": 0, "skipped": 0, "failed": 0}
        self._db_lock = threading.Lock()

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
        logger.info("[%s] Starting crawl (shard=%s, workers=%d)", self.registry_id, self.shard, self.max_workers)

        # Phase 1: Discover
        skills = self.discover()
        self.stats["discovered"] = len(skills)
        logger.info("[%s] Discovered %d skills", self.registry_id, len(skills))

        # Phase 2a: Register all skills in DB (serial, fast)
        for skill_info in skills:
            upsert_skill(
                self.conn,
                self.registry_id,
                skill_info["slug"],
                name=skill_info.get("name"),
                url=skill_info.get("url"),
                metadata=skill_info.get("metadata"),
            )
        self.conn.commit()

        # Phase 2b: Download (concurrent or sequential)
        if self.max_workers > 1:
            self._crawl_concurrent(skills)
        else:
            self._crawl_sequential(skills)

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

    def _crawl_sequential(self, skills: list[dict]) -> None:
        """Download skills sequentially (original behavior)."""
        for i, skill_info in enumerate(skills, 1):
            slug = skill_info["slug"]
            if i % 100 == 0:
                logger.info("[%s] Progress: %d/%d", self.registry_id, i, len(skills))

            self._download_and_process(skill_info)

    def _crawl_concurrent(self, skills: list[dict]) -> None:
        """Download skills concurrently using ThreadPoolExecutor."""
        total = len(skills)
        completed = 0

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(self._download_one, skill_info): skill_info
                for skill_info in skills
            }

            for future in as_completed(futures):
                completed += 1
                if completed % 200 == 0:
                    logger.info("[%s] Progress: %d/%d (dl=%d skip=%d fail=%d)",
                                self.registry_id, completed, total,
                                self.stats["downloaded"], self.stats["skipped"], self.stats["failed"])

                skill_info = futures[future]
                try:
                    result = future.result()
                except Exception as e:
                    logger.warning("[%s] Failed %s: %s", self.registry_id, skill_info["slug"], e)
                    self.stats["failed"] += 1
                    continue

                # Process result (DB writes + file saves) under lock
                self._process_result(skill_info["slug"], result)

                # Commit periodically to avoid holding transactions too long
                if completed % 500 == 0:
                    with self._db_lock:
                        self.conn.commit()

    def _download_one(self, skill_info: dict) -> CrawlResult:
        """Download a single skill (thread-safe, no DB access)."""
        slug = skill_info["slug"]
        kwargs = {k: v for k, v in skill_info.items() if k != "slug"}
        return self.download(slug, **kwargs)

    def _process_result(self, slug: str, result: CrawlResult) -> None:
        """Process a download result: update DB and save file."""
        if result.skipped:
            self.stats["skipped"] += 1
            return

        if result.error:
            logger.warning("[%s] Error for %s: %s", self.registry_id, slug, result.error)
            self.stats["failed"] += 1
            return

        with self._db_lock:
            if result.content_hash:
                upsert_skill(
                    self.conn,
                    self.registry_id,
                    slug,
                    content_hash=result.content_hash,
                    content_size=result.content_size,
                )

        if result.content:
            self._save_content(slug, result.content)

        self.stats["downloaded"] += 1

    def _download_and_process(self, skill_info: dict) -> None:
        """Download and process a single skill (sequential mode)."""
        slug = skill_info["slug"]
        try:
            result = self._download_one(skill_info)
        except Exception as e:
            logger.warning("[%s] Failed to download %s: %s", self.registry_id, slug, e)
            self.stats["failed"] += 1
            return
        self._process_result(slug, result)

    def _save_content(self, slug: str, content: str) -> None:
        """Save skill content to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        safe_name = slug.replace("/", "_").replace(":", "_")
        filepath = self.output_dir / f"{safe_name}.md"
        filepath.write_text(content, encoding="utf-8")

    def is_content_changed(self, skill_id: str, new_hash: str) -> bool:
        """Check if content has changed since last crawl."""
        with self._db_lock:
            old_hash = get_skill_hash(self.conn, skill_id)
        return old_hash != new_hash
