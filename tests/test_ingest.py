"""Tests for scan result ingestion."""

from crawlers.db import get_skills_by_registry, upsert_skill
from scanner.ingest import compute_score, filename_to_skill_id, parse_finding
from crawlers.models import Grade, Severity


def test_filename_to_skill_id():
    assert filename_to_skill_id("org_repo__skill.md", "skills-sh") == "skills-sh:org_repo__skill"
    assert filename_to_skill_id("my-tool.md", "clawhub") == "clawhub:my-tool"


def test_parse_finding():
    raw = {
        "rule_id": "PI-001",
        "severity": "HIGH",
        "category": "prompt-injection",
        "line": 10,
        "matched_text": "ignore previous instructions",
        "message": "Possible prompt injection",
    }
    f = parse_finding(raw)
    assert f.rule_id == "PI-001"
    assert f.severity == Severity.HIGH
    assert f.line == 10


def test_parse_finding_numeric_severity():
    """Aguara outputs severity as int: 4=CRITICAL, 3=HIGH, etc."""
    raw = {"rule_id": "S-1", "severity": 4, "category": "supply-chain"}
    f = parse_finding(raw)
    assert f.severity == Severity.CRITICAL

    raw2 = {"rule_id": "S-2", "severity": 2, "category": "test"}
    f2 = parse_finding(raw2)
    assert f2.severity == Severity.MEDIUM


def test_parse_finding_invalid_severity():
    raw = {"rule_id": "X-1", "severity": "BOGUS", "category": "unknown"}
    f = parse_finding(raw)
    assert f.severity == Severity.INFO  # fallback


def test_compute_score_clean():
    score = compute_score([])
    assert score.score == 100
    assert score.grade == Grade.A
    assert score.finding_count == 0


def test_compute_score_with_findings():
    findings = [
        parse_finding({"rule_id": "PI-001", "severity": "CRITICAL", "category": "prompt-injection"}),
        parse_finding({"rule_id": "EX-001", "severity": "HIGH", "category": "exfiltration"}),
        parse_finding({"rule_id": "CL-001", "severity": "MEDIUM", "category": "credential-leak"}),
    ]
    score = compute_score(findings)
    # 100 - 25 (CRITICAL) - 15 (HIGH) - 8 (MEDIUM) = 52
    assert score.score == 52
    assert score.grade == Grade.C
    assert score.critical_count == 1
    assert score.high_count == 1
    assert score.medium_count == 1


def test_compute_score_minimum_zero():
    # Enough findings to push below zero
    findings = [
        parse_finding({"rule_id": f"PI-{i}", "severity": "CRITICAL", "category": "prompt-injection"})
        for i in range(10)
    ]
    score = compute_score(findings)
    assert score.score == 0
    assert score.grade == Grade.F
