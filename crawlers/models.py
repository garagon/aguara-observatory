"""Pydantic models for Aguara Observatory."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Registry(BaseModel):
    id: str
    name: str
    url: str
    description: str | None = None


class Skill(BaseModel):
    id: str  # {registry}:{slug}
    registry_id: str
    slug: str
    name: str | None = None
    url: str | None = None
    content_hash: str | None = None
    content_size: int = 0
    first_seen: datetime = Field(default_factory=datetime.utcnow)
    last_seen: datetime = Field(default_factory=datetime.utcnow)
    last_scanned: datetime | None = None
    deleted: bool = False
    metadata: dict[str, Any] | None = None

    @staticmethod
    def make_id(registry_id: str, slug: str) -> str:
        return f"{registry_id}:{slug}"


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


SEVERITY_SCORE_IMPACT = {
    Severity.CRITICAL: 25,
    Severity.HIGH: 15,
    Severity.MEDIUM: 8,
    Severity.LOW: 0,   # Informational — stored but doesn't affect score
    Severity.INFO: 0,
}


class Grade(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"


def score_to_grade(score: int) -> Grade:
    if score >= 90:
        return Grade.A
    if score >= 75:
        return Grade.B
    if score >= 50:
        return Grade.C
    if score >= 25:
        return Grade.D
    return Grade.F


class Finding(BaseModel):
    rule_id: str
    severity: Severity
    category: str
    subcategory: str | None = None
    line: int | None = None
    matched_text: str | None = None
    message: str | None = None


class ScanResult(BaseModel):
    skill_id: str
    findings: list[Finding] = []
    max_severity: Severity | None = None
    finding_count: int = 0
    categories: list[str] = []


class SkillScore(BaseModel):
    skill_id: str
    score: int = 100
    grade: Grade = Grade.A
    finding_count: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    categories: list[str] = []


class VendorAudit(BaseModel):
    skill_id: str
    vendor: str
    verdict: str | None = None
    risk_level: str | None = None
    risk_score: float | None = None
    alert_count: int = 0
    findings: list[dict[str, Any]] = []
    raw_data: dict[str, Any] | None = None


class DailyStat(BaseModel):
    date: str  # YYYY-MM-DD
    registry_id: str
    total_skills: int = 0
    skills_scanned: int = 0
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0
    medium_count: int = 0
    low_count: int = 0
    avg_score: float = 100.0
    grade_a_count: int = 0
    grade_b_count: int = 0
    grade_c_count: int = 0
    grade_d_count: int = 0
    grade_f_count: int = 0
    new_skills: int = 0
    deleted_skills: int = 0


class CrawlResult(BaseModel):
    """Result from a single skill crawl."""
    skill_id: str
    slug: str
    name: str | None = None
    url: str | None = None
    content: str | None = None
    content_hash: str | None = None
    content_size: int = 0
    metadata: dict[str, Any] | None = None
    error: str | None = None
    skipped: bool = False  # True if content unchanged (same hash)
