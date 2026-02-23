"""Tests for crawl_state and crawl_runs DB functions."""

import pytest

from crawlers.db import (
    get_crawl_state,
    set_crawl_state,
    create_crawl_run,
    finish_crawl_run,
)


class TestCrawlState:
    def test_get_missing_key(self, db):
        """get_crawl_state returns None for a key that doesn't exist."""
        assert get_crawl_state(db, "clawhub", "nonexistent") is None

    def test_roundtrip(self, db):
        """set then get returns the same value."""
        set_crawl_state(db, "clawhub", "last_crawl_at", "2025-01-01T00:00:00Z")
        db.commit()
        assert get_crawl_state(db, "clawhub", "last_crawl_at") == "2025-01-01T00:00:00Z"

    def test_upsert_overwrites(self, db):
        """set_crawl_state overwrites existing value."""
        set_crawl_state(db, "clawhub", "etag:foo", "abc123")
        db.commit()
        set_crawl_state(db, "clawhub", "etag:foo", "def456")
        db.commit()
        assert get_crawl_state(db, "clawhub", "etag:foo") == "def456"

    def test_different_registries_independent(self, db):
        """Same key for different registries stores independently."""
        set_crawl_state(db, "clawhub", "last_crawl_at", "2025-01-01")
        set_crawl_state(db, "skills-sh", "last_crawl_at", "2025-06-01")
        db.commit()
        assert get_crawl_state(db, "clawhub", "last_crawl_at") == "2025-01-01"
        assert get_crawl_state(db, "skills-sh", "last_crawl_at") == "2025-06-01"

    def test_multiple_keys_per_registry(self, db):
        """A registry can store multiple state keys."""
        set_crawl_state(db, "mcp-so", "etag:server1", "aaa")
        set_crawl_state(db, "mcp-so", "etag:server2", "bbb")
        set_crawl_state(db, "mcp-so", "last_crawl_at", "2025-03-15")
        db.commit()
        assert get_crawl_state(db, "mcp-so", "etag:server1") == "aaa"
        assert get_crawl_state(db, "mcp-so", "etag:server2") == "bbb"
        assert get_crawl_state(db, "mcp-so", "last_crawl_at") == "2025-03-15"


class TestCrawlRuns:
    def test_create_and_finish(self, db):
        """Create a crawl run, finish it, verify it's stored."""
        run_id = create_crawl_run(db, "clawhub", "incremental")
        assert run_id > 0

        finish_crawl_run(
            db, run_id,
            duration_s=42.5,
            discovered=100,
            downloaded=10,
            skipped=85,
            failed=5,
            changed_files=10,
            status="completed",
        )

        row = db.execute("SELECT * FROM crawl_runs WHERE id = ?", (run_id,)).fetchone()
        assert row is not None
        # Check key fields by index (id, registry_id, mode, started, finished, duration, ...)
        assert row[1] == "clawhub"       # registry_id
        assert row[2] == "incremental"   # mode
        assert row[5] == 42.5            # duration_s
        assert row[6] == 100             # discovered
        assert row[7] == 10              # downloaded
        assert row[8] == 85              # skipped
        assert row[9] == 5               # failed
        assert row[10] == 10             # changed_files
        assert row[11] == "completed"    # status

    def test_create_failed_run(self, db):
        """A crawl run that fails records the error."""
        run_id = create_crawl_run(db, "skills-sh", "full")
        finish_crawl_run(
            db, run_id,
            duration_s=1.0,
            status="failed",
            error="Connection timeout",
        )
        row = db.execute("SELECT status, error FROM crawl_runs WHERE id = ?", (run_id,)).fetchone()
        assert row[0] == "failed"
        assert row[1] == "Connection timeout"

    def test_multiple_runs(self, db):
        """Multiple runs for the same registry are independent."""
        id1 = create_crawl_run(db, "clawhub", "full")
        id2 = create_crawl_run(db, "clawhub", "incremental")
        assert id1 != id2

        finish_crawl_run(db, id1, duration_s=100, discovered=500, status="completed")
        finish_crawl_run(db, id2, duration_s=5, discovered=10, status="completed")

        rows = db.execute(
            "SELECT id, mode, duration_s, discovered FROM crawl_runs WHERE registry_id = ? ORDER BY id",
            ("clawhub",),
        ).fetchall()
        assert len(rows) == 2
        assert rows[0][1] == "full"
        assert rows[0][2] == 100
        assert rows[1][1] == "incremental"
        assert rows[1][2] == 5
