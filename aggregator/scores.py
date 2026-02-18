#!/usr/bin/env python3
"""Compute and update skill scores (A-F grades).

Scoring: Start at 100, -25 per CRITICAL, -15 per HIGH, -8 per MEDIUM, -3 per LOW.
Grade: A=90-100, B=75-89, C=50-74, D=25-49, F=0-24.
"""

from __future__ import annotations

import logging

from crawlers.db import upsert_skill_score
from crawlers.models import Severity, SkillScore, score_to_grade, SEVERITY_SCORE_IMPACT

logger = logging.getLogger("observatory.scores")


def recompute_all_scores(conn) -> dict:
    """Recompute scores for all skills based on findings_latest.

    Returns summary stats.
    """
    # Get all skills with their latest findings
    rows = conn.execute(
        """SELECT s.id, fl.severity, fl.category
           FROM skills s
           LEFT JOIN findings_latest fl ON s.id = fl.skill_id
           WHERE s.deleted = 0
           ORDER BY s.id"""
    ).fetchall()

    # Group findings by skill
    skill_findings: dict[str, list[tuple[str, str]]] = {}
    for skill_id, severity, category in rows:
        if skill_id not in skill_findings:
            skill_findings[skill_id] = []
        if severity:
            skill_findings[skill_id].append((severity, category))

    updated = 0
    grade_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}

    for skill_id, findings in skill_findings.items():
        score = 100
        critical = high = medium = low = 0
        categories = set()

        for severity, category in findings:
            try:
                sev = Severity(severity)
            except ValueError:
                continue

            score -= SEVERITY_SCORE_IMPACT.get(sev, 0)
            categories.add(category)

            if sev == Severity.CRITICAL:
                critical += 1
            elif sev == Severity.HIGH:
                high += 1
            elif sev == Severity.MEDIUM:
                medium += 1
            elif sev == Severity.LOW:
                low += 1

        score = max(0, score)
        grade = score_to_grade(score)

        skill_score = SkillScore(
            skill_id=skill_id,
            score=score,
            grade=grade,
            finding_count=len(findings),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            categories=sorted(categories),
        )

        # Get latest scan_id for this skill
        row = conn.execute(
            "SELECT scan_id FROM findings_latest WHERE skill_id = ? LIMIT 1",
            (skill_id,),
        ).fetchone()
        scan_id = row[0] if row else None

        upsert_skill_score(conn, skill_score, scan_id)
        grade_dist[grade.value] += 1
        updated += 1

    conn.commit()
    logger.info(
        "Recomputed %d scores: A=%d B=%d C=%d D=%d F=%d",
        updated,
        grade_dist["A"], grade_dist["B"], grade_dist["C"],
        grade_dist["D"], grade_dist["F"],
    )

    return {"updated": updated, "grade_distribution": grade_dist}


def main():
    import json

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    setup_logging()
    conn = connect()
    init_schema(conn)

    result = recompute_all_scores(conn)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
