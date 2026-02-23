"""Turso/libSQL database client for Aguara Observatory."""

from __future__ import annotations

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import libsql_experimental as libsql

from crawlers.models import CrawlResult, Finding, Severity, SkillScore, VendorAudit

logger = logging.getLogger("observatory.db")

SCHEMA_DIR = Path(__file__).parent.parent / "schemas"

# Hrana/Turso errors that indicate a stale stream requiring reconnect.
_RETRIABLE_ERRORS = ("stream not found", "stream expired", "connection", "hrana")

_MAX_RETRIES = 3
_RETRY_BACKOFF = 1.0  # seconds, doubles each attempt


def _raw_connect(url: str, auth_token: str) -> libsql.Connection:
    if url.startswith("libsql://"):
        return libsql.connect(url, auth_token=auth_token)
    return libsql.connect(url)


class ResilientConnection:
    """Wrapper around libsql.Connection with automatic reconnect on stream errors."""

    def __init__(self, url: str, auth_token: str):
        self._url = url
        self._auth_token = auth_token
        self._conn = _raw_connect(url, auth_token)

    def _reconnect(self) -> None:
        logger.warning("Reconnecting to Turso (%s)", self._url)
        self._conn = _raw_connect(self._url, self._auth_token)

    def _is_retriable(self, exc: Exception) -> bool:
        msg = str(exc).lower()
        return any(err in msg for err in _RETRIABLE_ERRORS)

    def execute(self, sql, params=()):
        for attempt in range(_MAX_RETRIES):
            try:
                return self._conn.execute(sql, params)
            except Exception as exc:
                if not self._is_retriable(exc) or attempt == _MAX_RETRIES - 1:
                    raise
                wait = _RETRY_BACKOFF * (2 ** attempt)
                logger.warning("DB execute failed (attempt %d/%d): %s — retrying in %.1fs",
                               attempt + 1, _MAX_RETRIES, exc, wait)
                time.sleep(wait)
                self._reconnect()
        raise RuntimeError("unreachable")

    def commit(self):
        for attempt in range(_MAX_RETRIES):
            try:
                return self._conn.commit()
            except Exception as exc:
                if not self._is_retriable(exc) or attempt == _MAX_RETRIES - 1:
                    raise
                wait = _RETRY_BACKOFF * (2 ** attempt)
                logger.warning("DB commit failed (attempt %d/%d): %s — retrying in %.1fs",
                               attempt + 1, _MAX_RETRIES, exc, wait)
                time.sleep(wait)
                self._reconnect()
        raise RuntimeError("unreachable")

    def close(self):
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def connect(
    url: str | None = None,
    auth_token: str | None = None,
) -> ResilientConnection:
    """Connect to Turso or local SQLite with automatic reconnect.

    Environment variables:
        TURSO_DATABASE_URL: Turso database URL (libsql://...)
        TURSO_AUTH_TOKEN: Turso auth token

    For local dev, set TURSO_DATABASE_URL to a local file path or ":memory:".
    """
    url = url or os.environ.get("TURSO_DATABASE_URL", "file:observatory.db")
    auth_token = auth_token or os.environ.get("TURSO_AUTH_TOKEN", "")
    return ResilientConnection(url, auth_token)


def init_schema(conn: libsql.Connection) -> None:
    """Run all schema SQL files in order."""
    schema_files = sorted(SCHEMA_DIR.glob("*.sql"))
    for schema_file in schema_files:
        logger.info("Applying schema: %s", schema_file.name)
        sql = schema_file.read_text()
        # Execute each statement separately (SQLite doesn't support multi-statement)
        for statement in sql.split(";"):
            statement = statement.strip()
            if statement:
                conn.execute(statement)
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --- Skills ---

def upsert_skill(
    conn: libsql.Connection,
    registry_id: str,
    slug: str,
    *,
    name: str | None = None,
    url: str | None = None,
    content_hash: str | None = None,
    content_size: int = 0,
    metadata: dict | None = None,
) -> str:
    """Insert or update a skill. Returns the skill ID."""
    skill_id = f"{registry_id}:{slug}"
    now = _now()
    meta_json = json.dumps(metadata) if metadata else None

    conn.execute(
        """
        INSERT INTO skills (id, registry_id, slug, name, url, content_hash, content_size,
                           first_seen, last_seen, metadata)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = COALESCE(excluded.name, skills.name),
            url = COALESCE(excluded.url, skills.url),
            content_hash = COALESCE(excluded.content_hash, skills.content_hash),
            content_size = CASE WHEN excluded.content_size > 0 THEN excluded.content_size ELSE skills.content_size END,
            last_seen = excluded.last_seen,
            metadata = COALESCE(excluded.metadata, skills.metadata),
            deleted = 0
        """,
        (skill_id, registry_id, slug, name, url, content_hash, content_size, now, now, meta_json),
    )
    return skill_id


def get_skill_hash(conn: libsql.Connection, skill_id: str) -> str | None:
    """Get the current content hash for a skill."""
    row = conn.execute(
        "SELECT content_hash FROM skills WHERE id = ?", (skill_id,)
    ).fetchone()
    return row[0] if row else None


def mark_skill_deleted(conn: libsql.Connection, skill_id: str) -> None:
    """Mark a skill as deleted (soft delete)."""
    conn.execute(
        "UPDATE skills SET deleted = 1, last_seen = ? WHERE id = ?",
        (_now(), skill_id),
    )


def get_skills_by_registry(
    conn: libsql.Connection,
    registry_id: str,
    *,
    include_deleted: bool = False,
) -> list[tuple]:
    """Get all skills for a registry."""
    if include_deleted:
        return conn.execute(
            "SELECT id, slug, content_hash FROM skills WHERE registry_id = ?",
            (registry_id,),
        ).fetchall()
    return conn.execute(
        "SELECT id, slug, content_hash FROM skills WHERE registry_id = ? AND deleted = 0",
        (registry_id,),
    ).fetchall()


# --- Scans ---

def create_scan(
    conn: libsql.Connection,
    registry_id: str,
    aguara_version: str,
) -> int:
    """Create a new scan record. Returns scan ID."""
    cursor = conn.execute(
        """
        INSERT INTO scans (registry_id, aguara_version, status)
        VALUES (?, ?, 'running')
        """,
        (registry_id, aguara_version),
    )
    conn.commit()
    return cursor.lastrowid


def finish_scan(
    conn: libsql.Connection,
    scan_id: int,
    *,
    skills_scanned: int = 0,
    findings_count: int = 0,
    status: str = "completed",
    error: str | None = None,
) -> None:
    """Mark a scan as completed or failed."""
    conn.execute(
        """
        UPDATE scans SET finished_at = ?, skills_scanned = ?,
            findings_count = ?, status = ?, error = ?
        WHERE id = ?
        """,
        (_now(), skills_scanned, findings_count, status, error, scan_id),
    )
    conn.commit()


# --- Findings ---

def insert_findings(
    conn: libsql.Connection,
    scan_id: int,
    skill_id: str,
    findings: list[Finding],
) -> int:
    """Insert findings for a skill from a scan. Returns count inserted."""
    for f in findings:
        from crawlers.models import SEVERITY_SCORE_IMPACT
        impact = SEVERITY_SCORE_IMPACT.get(f.severity, 0)
        conn.execute(
            """
            INSERT INTO findings (scan_id, skill_id, rule_id, severity, category,
                                 subcategory, line, matched_text, message, score_impact)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (scan_id, skill_id, f.rule_id, f.severity.value, f.category,
             f.subcategory, f.line, f.matched_text, f.message, impact),
        )
    return len(findings)


def refresh_findings_latest(conn: libsql.Connection, skill_id: str, scan_id: int) -> None:
    """Replace latest findings for a skill with findings from a new scan."""
    conn.execute("DELETE FROM findings_latest WHERE skill_id = ?", (skill_id,))
    conn.execute(
        """
        INSERT INTO findings_latest (skill_id, scan_id, rule_id, severity, category,
                                    subcategory, line, matched_text, message, score_impact)
        SELECT skill_id, scan_id, rule_id, severity, category,
               subcategory, line, matched_text, message, score_impact
        FROM findings WHERE skill_id = ? AND scan_id = ?
        """,
        (skill_id, scan_id),
    )


# --- Scores ---

def upsert_skill_score(conn: libsql.Connection, score: SkillScore, scan_id: int) -> None:
    """Insert or update a skill score."""
    conn.execute(
        """
        INSERT INTO skill_scores (skill_id, score, grade, finding_count,
            critical_count, high_count, medium_count, low_count, categories,
            last_scan_id, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(skill_id) DO UPDATE SET
            score = excluded.score, grade = excluded.grade,
            finding_count = excluded.finding_count,
            critical_count = excluded.critical_count,
            high_count = excluded.high_count,
            medium_count = excluded.medium_count,
            low_count = excluded.low_count,
            categories = excluded.categories,
            last_scan_id = excluded.last_scan_id,
            updated_at = excluded.updated_at
        """,
        (score.skill_id, score.score, score.grade.value, score.finding_count,
         score.critical_count, score.high_count, score.medium_count, score.low_count,
         json.dumps(score.categories), scan_id, _now()),
    )


# --- Vendor Audits ---

def upsert_vendor_audit(conn: libsql.Connection, audit: VendorAudit) -> None:
    """Insert or update a vendor audit result."""
    conn.execute(
        """
        INSERT INTO vendor_audits (skill_id, vendor, verdict, risk_level, risk_score,
            alert_count, findings, raw_data, scraped_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(skill_id, vendor) DO UPDATE SET
            verdict = excluded.verdict, risk_level = excluded.risk_level,
            risk_score = excluded.risk_score, alert_count = excluded.alert_count,
            findings = excluded.findings, raw_data = excluded.raw_data,
            scraped_at = excluded.scraped_at
        """,
        (audit.skill_id, audit.vendor, audit.verdict, audit.risk_level,
         audit.risk_score, audit.alert_count,
         json.dumps(audit.findings), json.dumps(audit.raw_data) if audit.raw_data else None,
         _now()),
    )


# --- Daily Stats ---

def upsert_daily_stat(conn: libsql.Connection, date: str, registry_id: str, **kwargs) -> None:
    """Insert or update daily stats."""
    cols = ["date", "registry_id"] + list(kwargs.keys())
    placeholders = ", ".join(["?"] * len(cols))
    updates = ", ".join(f"{k} = excluded.{k}" for k in kwargs)
    values = tuple([date, registry_id] + list(kwargs.values()))

    conn.execute(
        f"""
        INSERT INTO daily_stats ({", ".join(cols)})
        VALUES ({placeholders})
        ON CONFLICT(date, registry_id) DO UPDATE SET {updates}
        """,
        values,
    )


# --- Crawl State (incremental watermarks) ---

def get_crawl_state(conn: libsql.Connection, registry_id: str, key: str) -> str | None:
    """Read a crawl state value. Returns None if not set."""
    row = conn.execute(
        "SELECT value FROM crawl_state WHERE registry_id = ? AND key = ?",
        (registry_id, key),
    ).fetchone()
    return row[0] if row else None


def set_crawl_state(conn: libsql.Connection, registry_id: str, key: str, value: str) -> None:
    """Write a crawl state value (upsert)."""
    conn.execute(
        """
        INSERT INTO crawl_state (registry_id, key, value, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(registry_id, key) DO UPDATE SET
            value = excluded.value,
            updated_at = excluded.updated_at
        """,
        (registry_id, key, value, _now()),
    )


# --- Crawl Runs (observability) ---

def create_crawl_run(conn: libsql.Connection, registry_id: str, mode: str = "full") -> int:
    """Create a new crawl run record. Returns run ID."""
    cursor = conn.execute(
        "INSERT INTO crawl_runs (registry_id, mode) VALUES (?, ?)",
        (registry_id, mode),
    )
    conn.commit()
    return cursor.lastrowid


def finish_crawl_run(
    conn: libsql.Connection,
    run_id: int,
    *,
    duration_s: float = 0,
    discovered: int = 0,
    downloaded: int = 0,
    skipped: int = 0,
    failed: int = 0,
    changed_files: int = 0,
    status: str = "completed",
    error: str | None = None,
) -> None:
    """Mark a crawl run as completed or failed."""
    conn.execute(
        """
        UPDATE crawl_runs SET finished_at = ?, duration_s = ?,
            discovered = ?, downloaded = ?, skipped = ?, failed = ?,
            changed_files = ?, status = ?, error = ?
        WHERE id = ?
        """,
        (_now(), duration_s, discovered, downloaded, skipped, failed,
         changed_files, status, error, run_id),
    )
    conn.commit()
