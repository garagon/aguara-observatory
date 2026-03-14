#!/usr/bin/env python3
"""Compute and update skill scores (A-F grades).

Scoring: Start at 100, -25 per CRITICAL, -15 per HIGH, -8 per MEDIUM, -3 per LOW.
Grade: A=90-100, B=75-89, C=50-74, D=25-49, F=0-24.

Findings with audit overrides (verdict='fp', confidence >= 0.8) are excluded
from score computation.
"""

from __future__ import annotations

import logging

from crawlers.db import upsert_skill_score
from crawlers.models import Severity, SkillScore, score_to_grade, SEVERITY_SCORE_IMPACT

logger = logging.getLogger("observatory.scores")

# Minimum confidence for an FP override to exclude a finding from scoring
FP_CONFIDENCE_THRESHOLD = 0.8


def recompute_all_scores(conn) -> dict:
    """Recompute scores for all skills based on findings_latest.

    Excludes findings that have been marked as false positives by the auditor
    (audit_overrides or audit_rule_overrides with verdict='fp' and high confidence).

    Uses batch SQL to avoid N+1 queries against remote Turso.
    Returns summary stats.
    """
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()

    # Subquery: findings NOT overridden as FP
    # Excludes findings that match:
    #   1. Per-skill audit_overrides with verdict='fp' and confidence >= threshold
    #   2. Rule-level audit_rule_overrides with verdict='fp' and confidence >= threshold
    conn.execute(
        f"""INSERT INTO skill_scores
              (skill_id, score, grade, finding_count,
               critical_count, high_count, medium_count, low_count,
               categories, last_scan_id, updated_at)
           SELECT
              s.id,
              MAX(0, 100
                - COALESCE(SUM(CASE WHEN fl.severity = 'CRITICAL' THEN 25 ELSE 0 END), 0)
                - COALESCE(SUM(CASE WHEN fl.severity = 'HIGH' THEN 15 ELSE 0 END), 0)
                - COALESCE(SUM(CASE WHEN fl.severity = 'MEDIUM' THEN 8 ELSE 0 END), 0)
              ) as score,
              CASE
                WHEN MAX(0, 100
                  - COALESCE(SUM(CASE WHEN fl.severity = 'CRITICAL' THEN 25 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'HIGH' THEN 15 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'MEDIUM' THEN 8 ELSE 0 END), 0)
                ) >= 90 THEN 'A'
                WHEN MAX(0, 100
                  - COALESCE(SUM(CASE WHEN fl.severity = 'CRITICAL' THEN 25 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'HIGH' THEN 15 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'MEDIUM' THEN 8 ELSE 0 END), 0)
                ) >= 75 THEN 'B'
                WHEN MAX(0, 100
                  - COALESCE(SUM(CASE WHEN fl.severity = 'CRITICAL' THEN 25 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'HIGH' THEN 15 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'MEDIUM' THEN 8 ELSE 0 END), 0)
                ) >= 50 THEN 'C'
                WHEN MAX(0, 100
                  - COALESCE(SUM(CASE WHEN fl.severity = 'CRITICAL' THEN 25 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'HIGH' THEN 15 ELSE 0 END), 0)
                  - COALESCE(SUM(CASE WHEN fl.severity = 'MEDIUM' THEN 8 ELSE 0 END), 0)
                ) >= 25 THEN 'D'
                ELSE 'F'
              END as grade,
              COALESCE(SUM(CASE WHEN fl.severity IS NOT NULL THEN 1 ELSE 0 END), 0) as finding_count,
              COALESCE(SUM(CASE WHEN fl.severity = 'CRITICAL' THEN 1 ELSE 0 END), 0) as critical_count,
              COALESCE(SUM(CASE WHEN fl.severity = 'HIGH' THEN 1 ELSE 0 END), 0) as high_count,
              COALESCE(SUM(CASE WHEN fl.severity = 'MEDIUM' THEN 1 ELSE 0 END), 0) as medium_count,
              COALESCE(SUM(CASE WHEN fl.severity = 'LOW' THEN 1 ELSE 0 END), 0) as low_count,
              COALESCE(GROUP_CONCAT(DISTINCT fl.category), '[]') as categories,
              MAX(fl.scan_id) as last_scan_id,
              ? as updated_at
           FROM skills s
           LEFT JOIN (
              SELECT f.* FROM findings_latest f
              WHERE NOT EXISTS (
                  SELECT 1 FROM audit_overrides ao
                  WHERE ao.skill_id = f.skill_id
                    AND ao.rule_id = f.rule_id
                    AND ao.verdict = 'fp'
                    AND ao.confidence >= {FP_CONFIDENCE_THRESHOLD}
              )
              AND NOT EXISTS (
                  SELECT 1 FROM audit_rule_overrides aro
                  WHERE aro.rule_id = f.rule_id
                    AND aro.verdict = 'fp'
                    AND aro.confidence >= {FP_CONFIDENCE_THRESHOLD}
              )
           ) fl ON s.id = fl.skill_id
           WHERE s.deleted = 0
           GROUP BY s.id
           ON CONFLICT(skill_id) DO UPDATE SET
              score = excluded.score,
              grade = excluded.grade,
              finding_count = excluded.finding_count,
              critical_count = excluded.critical_count,
              high_count = excluded.high_count,
              medium_count = excluded.medium_count,
              low_count = excluded.low_count,
              categories = excluded.categories,
              last_scan_id = excluded.last_scan_id,
              updated_at = excluded.updated_at""",
        (now,),
    )
    conn.commit()

    # Get summary
    grade_rows = conn.execute(
        "SELECT grade, COUNT(*) FROM skill_scores GROUP BY grade"
    ).fetchall()
    grade_dist = {g: c for g, c in grade_rows}
    updated = sum(grade_dist.values())

    # Count how many findings were excluded by overrides
    fp_excluded = conn.execute(f"""
        SELECT COUNT(*) FROM findings_latest f
        WHERE EXISTS (
            SELECT 1 FROM audit_overrides ao
            WHERE ao.skill_id = f.skill_id AND ao.rule_id = f.rule_id
            AND ao.verdict = 'fp' AND ao.confidence >= {FP_CONFIDENCE_THRESHOLD}
        )
        OR EXISTS (
            SELECT 1 FROM audit_rule_overrides aro
            WHERE aro.rule_id = f.rule_id
            AND aro.verdict = 'fp' AND aro.confidence >= {FP_CONFIDENCE_THRESHOLD}
        )
    """).fetchone()[0]

    logger.info(
        "Recomputed %d scores (excluded %d FP findings): A=%d B=%d C=%d D=%d F=%d",
        updated, fp_excluded,
        grade_dist.get("A", 0), grade_dist.get("B", 0), grade_dist.get("C", 0),
        grade_dist.get("D", 0), grade_dist.get("F", 0),
    )

    return {
        "updated": updated,
        "fp_excluded": fp_excluded,
        "grade_distribution": grade_dist,
    }


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
