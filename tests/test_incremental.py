"""Tests for incremental crawling behavior."""

import pytest
from unittest.mock import patch, MagicMock

from crawlers.db import set_crawl_state, get_crawl_state, upsert_skill
from crawlers.clawhub import ClawHubCrawler
from crawlers.lobehub import LobeHubCrawler


class TestClawHubIncremental:
    def test_watermark_stops_pagination(self, db):
        """In incremental mode, discover() stops when reaching skills older than watermark."""
        # Set a watermark (epoch ms)
        set_crawl_state(db, "clawhub", "last_updated_at", "1717200000000")  # 2024-06-01
        db.commit()

        # Mock API response with items sorted by updatedAt desc (epoch ms)
        api_response = {
            "items": [
                {"slug": "new-skill", "name": "New", "updatedAt": 1718496000000},  # 2024-06-16
                {"slug": "old-skill", "name": "Old", "updatedAt": 1714521600000},  # 2024-05-01
            ],
            "nextCursor": "cursor123",
        }

        crawler = ClawHubCrawler(db, crawl_mode="incremental")

        with patch("crawlers.clawhub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = api_response
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            skills = crawler.discover()

        # Should only return the skill newer than watermark
        assert len(skills) == 1
        assert skills[0]["slug"] == "new-skill"

    def test_full_mode_ignores_watermark(self, db):
        """In full mode, discover() ignores the watermark."""
        set_crawl_state(db, "clawhub", "last_updated_at", "1717200000000")
        db.commit()

        api_response = {
            "items": [
                {"slug": "new-skill", "name": "New", "updatedAt": 1718496000000},
                {"slug": "old-skill", "name": "Old", "updatedAt": 1714521600000},
            ],
        }

        crawler = ClawHubCrawler(db, crawl_mode="full")

        with patch("crawlers.clawhub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = api_response
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            skills = crawler.discover()

        # Should return both skills
        assert len(skills) == 2

    def test_watermark_updated_after_discover(self, db):
        """After discover(), the watermark should be updated."""
        crawler = ClawHubCrawler(db, crawl_mode="incremental")

        api_response = {"items": [{"slug": "s1", "name": "S1", "updatedAt": 1718496000000}]}

        with patch("crawlers.clawhub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = api_response
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            crawler.discover()

        # Watermark should be set to the updatedAt of the newest item
        wm = get_crawl_state(db, "clawhub", "last_updated_at")
        assert wm == "1718496000000"


class TestLobeHubIncremental:
    def test_index_hash_skip(self, db):
        """In incremental mode, LobeHub skips index if hash matches."""
        index_body = '{"plugins": [{"identifier": "p1", "meta": {"title": "P1"}}]}'

        # Store the hash of the index
        from crawlers.utils import content_hash
        stored = content_hash(index_body)
        set_crawl_state(db, "lobehub", "index_hash:plugin", stored)
        db.commit()

        crawler = LobeHubCrawler(db, crawl_mode="incremental")

        with patch("crawlers.lobehub.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.text = index_body
            mock_resp.json.return_value = {"plugins": [{"identifier": "p1", "meta": {"title": "P1"}}]}
            mock_resp.raise_for_status = MagicMock()
            mock_get.return_value = mock_resp

            skills = crawler.discover()

        # Both indexes return same hash → both skipped → empty
        assert len(skills) == 0


class TestManifest:
    def test_changed_slugs_tracked(self, db, tmp_path):
        """Base crawler tracks changed slugs when content is saved."""
        from crawlers.models import CrawlResult

        # Create a minimal concrete crawler for testing
        class FakeCrawler(ClawHubCrawler):
            registry_id = "clawhub"

            def discover(self):
                return [{"slug": "test-skill", "name": "Test"}]

            def download(self, slug, **kwargs):
                return CrawlResult(
                    skill_id=f"clawhub:{slug}",
                    slug=slug,
                    content="# Test\nHello",
                    content_hash="abc123",
                    content_size=12,
                )

        crawler = FakeCrawler(db, output_dir=tmp_path, crawl_mode="incremental")
        crawler.crawl()

        assert "test-skill" in crawler.changed_slugs
        manifest = tmp_path / ".changed_files.txt"
        assert manifest.exists()
        assert "test-skill.md" in manifest.read_text()
