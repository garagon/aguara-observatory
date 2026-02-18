"""Tests for database operations."""

from crawlers.db import (
    create_scan,
    finish_scan,
    get_skill_hash,
    get_skills_by_registry,
    insert_findings,
    mark_skill_deleted,
    refresh_findings_latest,
    upsert_daily_stat,
    upsert_skill,
    upsert_skill_score,
    upsert_vendor_audit,
)
from crawlers.models import Finding, Grade, Severity, SkillScore, VendorAudit


def test_upsert_skill(db):
    skill_id = upsert_skill(db, "skills-sh", "test-slug", name="Test Skill")
    assert skill_id == "skills-sh:test-slug"

    # Verify it's in the DB
    row = db.execute("SELECT name FROM skills WHERE id = ?", (skill_id,)).fetchone()
    assert row[0] == "Test Skill"


def test_upsert_skill_update(db):
    upsert_skill(db, "skills-sh", "slug1", name="V1", content_hash="aaa")
    upsert_skill(db, "skills-sh", "slug1", name="V2", content_hash="bbb")

    row = db.execute("SELECT name, content_hash FROM skills WHERE id = ?", ("skills-sh:slug1",)).fetchone()
    assert row[0] == "V2"
    assert row[1] == "bbb"


def test_get_skill_hash(db):
    upsert_skill(db, "skills-sh", "slug1", content_hash="abc123")
    db.commit()
    assert get_skill_hash(db, "skills-sh:slug1") == "abc123"
    assert get_skill_hash(db, "nonexistent") is None


def test_mark_skill_deleted(db):
    upsert_skill(db, "skills-sh", "slug1")
    mark_skill_deleted(db, "skills-sh:slug1")
    db.commit()

    row = db.execute("SELECT deleted FROM skills WHERE id = ?", ("skills-sh:slug1",)).fetchone()
    assert row[0] == 1


def test_get_skills_by_registry(db):
    upsert_skill(db, "skills-sh", "a")
    upsert_skill(db, "skills-sh", "b")
    upsert_skill(db, "clawhub", "c")
    mark_skill_deleted(db, "skills-sh:b")
    db.commit()

    skills = get_skills_by_registry(db, "skills-sh")
    assert len(skills) == 1  # 'b' is deleted

    skills_all = get_skills_by_registry(db, "skills-sh", include_deleted=True)
    assert len(skills_all) == 2


def test_create_and_finish_scan(db):
    scan_id = create_scan(db, "skills-sh", "v0.2.0")
    assert scan_id > 0

    finish_scan(db, scan_id, skills_scanned=100, findings_count=42)
    row = db.execute("SELECT status, skills_scanned FROM scans WHERE id = ?", (scan_id,)).fetchone()
    assert row[0] == "completed"
    assert row[1] == 100


def test_insert_findings(db):
    upsert_skill(db, "skills-sh", "test")
    scan_id = create_scan(db, "skills-sh", "v0.2.0")

    findings = [
        Finding(rule_id="PI-001", severity=Severity.HIGH, category="prompt-injection"),
        Finding(rule_id="EX-002", severity=Severity.MEDIUM, category="exfiltration"),
    ]
    count = insert_findings(db, scan_id, "skills-sh:test", findings)
    assert count == 2

    rows = db.execute("SELECT COUNT(*) FROM findings WHERE scan_id = ?", (scan_id,)).fetchone()
    assert rows[0] == 2


def test_refresh_findings_latest(db):
    upsert_skill(db, "skills-sh", "test")
    scan_id = create_scan(db, "skills-sh", "v0.2.0")
    findings = [Finding(rule_id="PI-001", severity=Severity.HIGH, category="prompt-injection")]
    insert_findings(db, scan_id, "skills-sh:test", findings)

    refresh_findings_latest(db, "skills-sh:test", scan_id)
    row = db.execute("SELECT COUNT(*) FROM findings_latest WHERE skill_id = ?", ("skills-sh:test",)).fetchone()
    assert row[0] == 1

    # Refresh again with new scan should replace
    scan_id2 = create_scan(db, "skills-sh", "v0.2.1")
    new_findings = [
        Finding(rule_id="EX-001", severity=Severity.CRITICAL, category="exfiltration"),
    ]
    insert_findings(db, scan_id2, "skills-sh:test", new_findings)
    refresh_findings_latest(db, "skills-sh:test", scan_id2)

    row = db.execute("SELECT rule_id FROM findings_latest WHERE skill_id = ?", ("skills-sh:test",)).fetchone()
    assert row[0] == "EX-001"


def test_upsert_skill_score(db):
    upsert_skill(db, "skills-sh", "test")
    scan_id = create_scan(db, "skills-sh", "v0.2.0")

    score = SkillScore(
        skill_id="skills-sh:test",
        score=67,
        grade=Grade.C,
        finding_count=3,
        critical_count=0,
        high_count=1,
        medium_count=2,
        low_count=0,
    )
    upsert_skill_score(db, score, scan_id)

    row = db.execute("SELECT score, grade FROM skill_scores WHERE skill_id = ?", ("skills-sh:test",)).fetchone()
    assert row[0] == 67
    assert row[1] == "C"


def test_upsert_vendor_audit(db):
    upsert_skill(db, "skills-sh", "test")
    audit = VendorAudit(
        skill_id="skills-sh:test",
        vendor="agent-trust-hub",
        verdict="Fail",
        risk_level="High",
        alert_count=3,
        findings=[{"category": "PROMPT_INJECTION", "severity": "HIGH"}],
    )
    upsert_vendor_audit(db, audit)

    row = db.execute(
        "SELECT verdict, risk_level FROM vendor_audits WHERE skill_id = ? AND vendor = ?",
        ("skills-sh:test", "agent-trust-hub"),
    ).fetchone()
    assert row[0] == "Fail"
    assert row[1] == "High"


def test_upsert_daily_stat(db):
    upsert_daily_stat(db, "2026-01-15", "skills-sh", total_skills=5000, avg_score=72.3)
    row = db.execute(
        "SELECT total_skills, avg_score FROM daily_stats WHERE date = ? AND registry_id = ?",
        ("2026-01-15", "skills-sh"),
    ).fetchone()
    assert row[0] == 5000
    assert row[1] == 72.3
