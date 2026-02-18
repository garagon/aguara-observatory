#!/usr/bin/env python3
"""Compute weekly and monthly trend data from daily_stats."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

logger = logging.getLogger("observatory.trends")


def compute_weekly_trends(conn, weeks: int = 52) -> list[dict]:
    """Compute weekly aggregated trends.

    Returns list of weekly data points, most recent first.
    Each point includes per-registry stats and overall totals.
    """
    end_date = datetime.now(timezone.utc).date()
    trends = []

    for week_offset in range(weeks):
        week_end = end_date - timedelta(days=week_offset * 7)
        week_start = week_end - timedelta(days=6)

        week_data = {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "registries": {},
            "totals": {
                "total_skills": 0,
                "total_findings": 0,
                "critical_count": 0,
                "high_count": 0,
                "avg_score": 0.0,
                "new_skills": 0,
            },
        }

        # Get the latest daily_stats entry within this week for each registry
        rows = conn.execute(
            """SELECT registry_id,
                      MAX(total_skills) as total_skills,
                      MAX(skills_scanned) as skills_scanned,
                      MAX(total_findings) as total_findings,
                      MAX(critical_count) as critical_count,
                      MAX(high_count) as high_count,
                      MAX(medium_count) as medium_count,
                      MAX(low_count) as low_count,
                      AVG(avg_score) as avg_score,
                      SUM(new_skills) as new_skills,
                      SUM(deleted_skills) as deleted_skills
               FROM daily_stats
               WHERE date BETWEEN ? AND ?
               GROUP BY registry_id""",
            (week_start.isoformat(), week_end.isoformat()),
        ).fetchall()

        score_count = 0
        score_sum = 0.0

        for row in rows:
            registry_stats = {
                "total_skills": row[1] or 0,
                "skills_scanned": row[2] or 0,
                "total_findings": row[3] or 0,
                "critical_count": row[4] or 0,
                "high_count": row[5] or 0,
                "medium_count": row[6] or 0,
                "low_count": row[7] or 0,
                "avg_score": round(row[8] or 100.0, 1),
                "new_skills": row[9] or 0,
                "deleted_skills": row[10] or 0,
            }
            week_data["registries"][row[0]] = registry_stats

            week_data["totals"]["total_skills"] += registry_stats["total_skills"]
            week_data["totals"]["total_findings"] += registry_stats["total_findings"]
            week_data["totals"]["critical_count"] += registry_stats["critical_count"]
            week_data["totals"]["high_count"] += registry_stats["high_count"]
            week_data["totals"]["new_skills"] += registry_stats["new_skills"]

            if registry_stats["avg_score"] > 0:
                score_sum += registry_stats["avg_score"]
                score_count += 1

        if score_count > 0:
            week_data["totals"]["avg_score"] = round(score_sum / score_count, 1)

        # Only include weeks with data
        if rows:
            trends.append(week_data)

    return trends


def compute_monthly_trends(conn, months: int = 12) -> list[dict]:
    """Compute monthly aggregated trends."""
    end_date = datetime.now(timezone.utc).date()
    trends = []

    for month_offset in range(months):
        # Calculate month boundaries
        year = end_date.year - (end_date.month - 1 - month_offset) // 12
        month = (end_date.month - 1 - month_offset) % 12 + 1
        month_start = f"{year:04d}-{month:02d}-01"

        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1
        month_end = f"{next_year:04d}-{next_month:02d}-01"

        rows = conn.execute(
            """SELECT registry_id,
                      MAX(total_skills) as total_skills,
                      MAX(total_findings) as total_findings,
                      AVG(avg_score) as avg_score,
                      SUM(new_skills) as new_skills
               FROM daily_stats
               WHERE date >= ? AND date < ?
               GROUP BY registry_id""",
            (month_start, month_end),
        ).fetchall()

        if rows:
            month_data = {
                "month": f"{year:04d}-{month:02d}",
                "registries": {},
                "totals": {"total_skills": 0, "total_findings": 0, "avg_score": 0.0},
            }

            score_sum = 0.0
            score_count = 0

            for row in rows:
                month_data["registries"][row[0]] = {
                    "total_skills": row[1] or 0,
                    "total_findings": row[2] or 0,
                    "avg_score": round(row[3] or 100.0, 1),
                    "new_skills": row[4] or 0,
                }
                month_data["totals"]["total_skills"] += row[1] or 0
                month_data["totals"]["total_findings"] += row[2] or 0
                if row[3]:
                    score_sum += row[3]
                    score_count += 1

            if score_count > 0:
                month_data["totals"]["avg_score"] = round(score_sum / score_count, 1)

            trends.append(month_data)

    return trends


def main():
    import argparse
    import json

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Compute trends")
    parser.add_argument("--weeks", type=int, default=52, help="Number of weeks for weekly trends")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    weekly = compute_weekly_trends(conn, args.weeks)
    monthly = compute_monthly_trends(conn)

    print(json.dumps({"weekly": weekly, "monthly": monthly}, indent=2))


if __name__ == "__main__":
    main()
