"""Tests for Pydantic models and scoring logic."""

from crawlers.models import (
    CrawlResult,
    Finding,
    Grade,
    Severity,
    SkillScore,
    score_to_grade,
    SEVERITY_SCORE_IMPACT,
)


def test_score_to_grade():
    assert score_to_grade(100) == Grade.A
    assert score_to_grade(95) == Grade.A
    assert score_to_grade(90) == Grade.A
    assert score_to_grade(89) == Grade.B
    assert score_to_grade(75) == Grade.B
    assert score_to_grade(74) == Grade.C
    assert score_to_grade(50) == Grade.C
    assert score_to_grade(49) == Grade.D
    assert score_to_grade(25) == Grade.D
    assert score_to_grade(24) == Grade.F
    assert score_to_grade(0) == Grade.F


def test_severity_score_impact():
    assert SEVERITY_SCORE_IMPACT[Severity.CRITICAL] == 25
    assert SEVERITY_SCORE_IMPACT[Severity.HIGH] == 15
    assert SEVERITY_SCORE_IMPACT[Severity.MEDIUM] == 8
    assert SEVERITY_SCORE_IMPACT[Severity.LOW] == 0
    assert SEVERITY_SCORE_IMPACT[Severity.INFO] == 0


def test_skill_make_id():
    from crawlers.models import Skill
    assert Skill.make_id("skills-sh", "foo_bar__baz") == "skills-sh:foo_bar__baz"


def test_crawl_result_skipped():
    result = CrawlResult(skill_id="reg:slug", slug="slug", skipped=True)
    assert result.skipped is True
    assert result.content is None


def test_finding_model():
    f = Finding(
        rule_id="PI-001",
        severity=Severity.HIGH,
        category="prompt-injection",
        line=42,
        matched_text="ignore previous",
    )
    assert f.severity == Severity.HIGH
    assert f.category == "prompt-injection"
