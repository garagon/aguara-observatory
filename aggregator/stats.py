#!/usr/bin/env python3
"""Compute per-registry daily statistics and store in daily_stats table."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from crawlers.db import upsert_daily_stat

logger = logging.getLogger("observatory.stats")


def compute_daily_stats(conn, date: str | None = None) -> dict:
    """Compute stats for all registries for a given date.

    Args:
        conn: Database connection
        date: Date string (YYYY-MM-DD). Defaults to today.

    Returns:
        Dict of {registry_id: stats_dict}
    """
    if date is None:
        date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    registries = conn.execute("SELECT id FROM registries").fetchall()
    all_stats = {}

    for (registry_id,) in registries:
        stats = _compute_registry_stats(conn, registry_id, date)
        all_stats[registry_id] = stats

        upsert_daily_stat(conn, date, registry_id, **stats)
        logger.info("[%s] %s: %d skills, %d findings, avg score %.1f",
                    date, registry_id, stats["total_skills"],
                    stats["total_findings"], stats["avg_score"])

    conn.commit()
    return all_stats


def _compute_registry_stats(conn, registry_id: str, date: str) -> dict:
    """Compute stats for a single registry."""
    # Total skills (not deleted)
    row = conn.execute(
        "SELECT COUNT(*) FROM skills WHERE registry_id = ? AND deleted = 0",
        (registry_id,),
    ).fetchone()
    total_skills = row[0] if row else 0

    # Skills scanned (have a score)
    row = conn.execute(
        """SELECT COUNT(*) FROM skill_scores ss
           JOIN skills s ON ss.skill_id = s.id
           WHERE s.registry_id = ? AND s.deleted = 0""",
        (registry_id,),
    ).fetchone()
    skills_scanned = row[0] if row else 0

    # Finding counts by severity from latest findings
    severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    rows = conn.execute(
        """SELECT fl.severity, COUNT(*) FROM findings_latest fl
           JOIN skills s ON fl.skill_id = s.id
           WHERE s.registry_id = ? AND s.deleted = 0
           GROUP BY fl.severity""",
        (registry_id,),
    ).fetchall()
    for sev, count in rows:
        if sev in severity_counts:
            severity_counts[sev] = count

    total_findings = sum(severity_counts.values())

    # Average score
    row = conn.execute(
        """SELECT AVG(ss.score) FROM skill_scores ss
           JOIN skills s ON ss.skill_id = s.id
           WHERE s.registry_id = ? AND s.deleted = 0""",
        (registry_id,),
    ).fetchone()
    avg_score = row[0] if row and row[0] is not None else 100.0

    # Grade distribution
    grade_counts = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
    rows = conn.execute(
        """SELECT ss.grade, COUNT(*) FROM skill_scores ss
           JOIN skills s ON ss.skill_id = s.id
           WHERE s.registry_id = ? AND s.deleted = 0
           GROUP BY ss.grade""",
        (registry_id,),
    ).fetchall()
    for grade, count in rows:
        if grade in grade_counts:
            grade_counts[grade] = count

    # New skills today
    row = conn.execute(
        "SELECT COUNT(*) FROM skills WHERE registry_id = ? AND DATE(first_seen) = ?",
        (registry_id, date),
    ).fetchone()
    new_skills = row[0] if row else 0

    # Deleted skills today
    row = conn.execute(
        "SELECT COUNT(*) FROM skills WHERE registry_id = ? AND deleted = 1 AND DATE(last_seen) = ?",
        (registry_id, date),
    ).fetchone()
    deleted_skills = row[0] if row else 0

    return {
        "total_skills": total_skills,
        "skills_scanned": skills_scanned,
        "total_findings": total_findings,
        "critical_count": severity_counts["CRITICAL"],
        "high_count": severity_counts["HIGH"],
        "medium_count": severity_counts["MEDIUM"],
        "low_count": severity_counts["LOW"],
        "avg_score": round(avg_score, 1),
        "grade_a_count": grade_counts["A"],
        "grade_b_count": grade_counts["B"],
        "grade_c_count": grade_counts["C"],
        "grade_d_count": grade_counts["D"],
        "grade_f_count": grade_counts["F"],
        "new_skills": new_skills,
        "deleted_skills": deleted_skills,
    }


def main():
    import argparse

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Compute daily stats")
    parser.add_argument("--date", help="Date (YYYY-MM-DD), defaults to today")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    stats = compute_daily_stats(conn, args.date)
    import json
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
