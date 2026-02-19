#!/usr/bin/env python3
"""Export static JSON API files and CSV datasets from Turso.

Generates files for web/public/api/v1/ to be served as static API.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from aggregator.benchmarks import run_benchmark
from aggregator.trends import compute_weekly_trends

logger = logging.getLogger("observatory.export")

DEFAULT_OUTPUT_DIR = Path("web/public/api/v1")
DATASETS_DIR = Path("web/public/datasets")


def export_all(conn, output_dir: Path | None = None, datasets_dir: Path | None = None) -> dict:
    """Export all static JSON API files and CSV datasets.

    Returns summary of files generated.
    """
    output_dir = output_dir or DEFAULT_OUTPUT_DIR
    datasets_dir = datasets_dir or DATASETS_DIR
    output_dir.mkdir(parents=True, exist_ok=True)
    datasets_dir.mkdir(parents=True, exist_ok=True)

    files = {}

    # /api/v1/stats.json — Global stats
    stats = _export_global_stats(conn, output_dir)
    files["stats.json"] = stats

    # /api/v1/registries.json — Registry list with stats
    registries = _export_registries(conn, output_dir)
    files["registries.json"] = len(registries)

    # /api/v1/registries/{id}/stats.json — Per-registry stats
    for reg in registries:
        _export_registry_stats(conn, output_dir, reg["id"])
    files["registry_stats"] = len(registries)

    # /api/v1/categories.json — Finding counts by category
    _export_categories(conn, output_dir)
    files["categories.json"] = True

    # /api/v1/categories/{category}.json — Skills per category
    cat_count = _export_category_skills(conn, output_dir)
    files["category_pages"] = cat_count

    # /api/v1/grades/{grade}.json — Skills per grade
    grade_count = _export_grade_skills(conn, output_dir)
    files["grade_pages"] = grade_count

    # /api/v1/trends/weekly.json
    _export_weekly_trends(conn, output_dir)
    files["trends/weekly.json"] = True

    # /api/v1/benchmarks/vendors.json
    _export_benchmarks(conn, output_dir)
    files["benchmarks/vendors.json"] = True

    # /api/v1/feed/recent.json — Recent critical findings
    _export_recent_feed(conn, output_dir)
    files["feed/recent.json"] = True

    # /api/v1/skills/{registry}/{slug}.json — Individual skill reports
    skill_count = _export_skill_reports(conn, output_dir)
    files["skill_reports"] = skill_count

    # /api/v1/registries/{id}/skills.json — Per-registry skill list
    for reg in registries:
        _export_registry_skills(conn, output_dir, reg["id"])
    files["registry_skills"] = len(registries)

    # /api/v1/search-index.json — Skill search index
    _export_search_index(conn, output_dir)
    files["search-index.json"] = True

    # /api/v1/datasets/manifest.json
    _export_datasets_manifest(conn, datasets_dir, output_dir)
    files["datasets/manifest.json"] = True

    # CSV datasets
    _export_csv_datasets(conn, datasets_dir)
    files["csv_datasets"] = True

    logger.info("Export complete: %s", files)
    return files


def _write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str, ensure_ascii=False) + "\n")


def _export_global_stats(conn, output_dir: Path) -> dict:
    """Generate /api/v1/stats.json."""
    stats = {}

    row = conn.execute("SELECT COUNT(*) FROM skills WHERE deleted = 0").fetchone()
    stats["total_skills"] = row[0]

    row = conn.execute("SELECT COUNT(*) FROM skill_scores").fetchone()
    stats["skills_scanned"] = row[0]

    row = conn.execute("SELECT COUNT(*) FROM findings_latest WHERE severity != 'LOW'").fetchone()
    stats["total_findings"] = row[0]
    row = conn.execute("SELECT COUNT(*) FROM findings_latest").fetchone()
    stats["total_findings_all"] = row[0]

    row = conn.execute("SELECT AVG(score) FROM skill_scores").fetchone()
    stats["avg_score"] = round(row[0], 1) if row[0] else 100.0

    row = conn.execute("SELECT COUNT(*) FROM registries").fetchone()
    stats["registries_count"] = row[0]

    # Grade distribution
    grade_rows = conn.execute(
        "SELECT grade, COUNT(*) FROM skill_scores GROUP BY grade"
    ).fetchall()
    stats["grade_distribution"] = {g: c for g, c in grade_rows}

    # Severity distribution
    sev_rows = conn.execute(
        "SELECT severity, COUNT(*) FROM findings_latest GROUP BY severity"
    ).fetchall()
    stats["severity_distribution"] = {s: c for s, c in sev_rows}

    stats["generated_at"] = datetime.now(timezone.utc).isoformat()

    _write_json(output_dir / "stats.json", stats)
    return stats


def _export_registries(conn, output_dir: Path) -> list[dict]:
    """Generate /api/v1/registries.json."""
    rows = conn.execute("SELECT id, name, url, description FROM registries").fetchall()
    registries = []

    for reg_id, name, url, desc in rows:
        # Get skill count
        count_row = conn.execute(
            "SELECT COUNT(*) FROM skills WHERE registry_id = ? AND deleted = 0",
            (reg_id,),
        ).fetchone()

        # Get avg score
        score_row = conn.execute(
            """SELECT AVG(ss.score) FROM skill_scores ss
               JOIN skills s ON ss.skill_id = s.id
               WHERE s.registry_id = ? AND s.deleted = 0""",
            (reg_id,),
        ).fetchone()

        registries.append({
            "id": reg_id,
            "name": name,
            "url": url,
            "description": desc,
            "skill_count": count_row[0],
            "avg_score": round(score_row[0], 1) if score_row[0] else 100.0,
        })

    _write_json(output_dir / "registries.json", registries)
    return registries


def _export_registry_stats(conn, output_dir: Path, registry_id: str) -> None:
    """Generate /api/v1/registries/{id}/stats.json."""
    # Latest daily stats
    row = conn.execute(
        "SELECT * FROM daily_stats WHERE registry_id = ? ORDER BY date DESC LIMIT 1",
        (registry_id,),
    ).fetchone()

    if not row:
        return

    cols = [desc[0] for desc in conn.execute("SELECT * FROM daily_stats LIMIT 0").description]
    stats = dict(zip(cols, row))

    _write_json(output_dir / "registries" / registry_id / "stats.json", stats)


def _export_categories(conn, output_dir: Path) -> None:
    """Generate /api/v1/categories.json (excludes LOW/INFO findings)."""
    rows = conn.execute(
        "SELECT category, COUNT(*) as count FROM findings_latest WHERE severity NOT IN ('LOW', 'INFO') GROUP BY category ORDER BY count DESC"
    ).fetchall()

    categories = [{"category": cat, "count": count} for cat, count in rows]
    _write_json(output_dir / "categories.json", categories)


def _export_category_skills(conn, output_dir: Path) -> int:
    """Generate /api/v1/categories/{category}.json — skills list per category."""
    cats = conn.execute(
        "SELECT DISTINCT category FROM findings_latest WHERE severity NOT IN ('LOW', 'INFO')"
    ).fetchall()

    count = 0
    for (category,) in cats:
        rows = conn.execute(
            """SELECT DISTINCT s.id, s.slug, s.name, s.registry_id,
                      COALESCE(ss.score, 100) as score,
                      COALESCE(ss.grade, 'A') as grade,
                      COALESCE(ss.finding_count, 0) as finding_count,
                      COALESCE(ss.critical_count, 0) as critical_count,
                      COALESCE(ss.high_count, 0) as high_count
               FROM findings_latest fl
               JOIN skills s ON fl.skill_id = s.id
               LEFT JOIN skill_scores ss ON s.id = ss.skill_id
               WHERE fl.category = ? AND fl.severity NOT IN ('LOW', 'INFO') AND s.deleted = 0
               ORDER BY COALESCE(ss.score, 100) ASC""",
            (category,),
        ).fetchall()

        skills = []
        for skill_id, slug, name, reg_id, score, grade, fc, cc, hc in rows:
            skills.append({
                "skill_id": skill_id,
                "slug": slug,
                "name": name or slug,
                "registry_id": reg_id,
                "score": score,
                "grade": grade,
                "finding_count": fc,
                "critical_count": cc,
                "high_count": hc,
            })

        _write_json(output_dir / "categories" / f"{category}.json", {
            "category": category,
            "skill_count": len(skills),
            "skills": skills,
        })
        count += 1

    return count


def _export_grade_skills(conn, output_dir: Path) -> int:
    """Generate /api/v1/grades/{grade}.json — skills list per grade."""
    grades = conn.execute(
        "SELECT DISTINCT grade FROM skill_scores"
    ).fetchall()

    count = 0
    for (grade,) in grades:
        rows = conn.execute(
            """SELECT ss.skill_id, s.slug, s.name, s.registry_id,
                      ss.score, ss.grade, ss.finding_count,
                      ss.critical_count, ss.high_count
               FROM skill_scores ss
               JOIN skills s ON ss.skill_id = s.id
               WHERE ss.grade = ? AND s.deleted = 0
               ORDER BY ss.score ASC""",
            (grade,),
        ).fetchall()

        skills = []
        for skill_id, slug, name, reg_id, score, g, fc, cc, hc in rows:
            skills.append({
                "skill_id": skill_id,
                "slug": slug,
                "name": name or slug,
                "registry_id": reg_id,
                "score": score,
                "grade": g,
                "finding_count": fc,
                "critical_count": cc,
                "high_count": hc,
            })

        _write_json(output_dir / "grades" / f"{grade}.json", {
            "grade": grade,
            "skill_count": len(skills),
            "skills": skills,
        })
        count += 1

    return count


def _export_weekly_trends(conn, output_dir: Path) -> None:
    """Generate /api/v1/trends/weekly.json."""
    trends = compute_weekly_trends(conn, weeks=52)
    _write_json(output_dir / "trends" / "weekly.json", trends)


def _export_benchmarks(conn, output_dir: Path) -> None:
    """Generate /api/v1/benchmarks/vendors.json."""
    result = run_benchmark(conn)
    # Only export metrics, not full comparisons (too large)
    _write_json(output_dir / "benchmarks" / "vendors.json", {
        "skills_compared": result["skills_compared"],
        "metrics": result["metrics"],
    })


def _export_recent_feed(conn, output_dir: Path, limit: int = 50) -> None:
    """Generate /api/v1/feed/recent.json — recent critical/high findings."""
    rows = conn.execute(
        """SELECT fl.skill_id, fl.rule_id, fl.severity, fl.category,
                  fl.message, fl.updated_at, s.name, s.registry_id
           FROM findings_latest fl
           JOIN skills s ON fl.skill_id = s.id
           WHERE fl.severity IN ('CRITICAL', 'HIGH')
           ORDER BY fl.updated_at DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()

    feed = []
    for row in rows:
        skill_id = row[0]
        registry_id = row[7]
        slug = skill_id.removeprefix(f"{registry_id}:")
        feed.append({
            "skill_id": skill_id,
            "slug": slug,
            "rule_id": row[1],
            "severity": row[2],
            "category": row[3],
            "message": row[4],
            "updated_at": row[5],
            "skill_name": row[6],
            "registry_id": registry_id,
        })

    _write_json(output_dir / "feed" / "recent.json", feed)


def _export_skill_reports(conn, output_dir: Path) -> int:
    """Generate /api/v1/skills/{registry}/{slug}.json for ALL skills (not just those with findings)."""
    rows = conn.execute(
        """SELECT s.id, s.registry_id, s.slug, s.name, s.url,
                  s.first_seen, s.last_seen, s.metadata
           FROM skills s
           WHERE s.deleted = 0"""
    ).fetchall()

    count = 0
    for skill_id, registry_id, slug, name, url, first_seen, last_seen, metadata_json in rows:
        # Get findings (may be empty for clean skills)
        finding_rows = conn.execute(
            """SELECT rule_id, severity, category, subcategory, line,
                      matched_text, message
               FROM findings_latest WHERE skill_id = ?""",
            (skill_id,),
        ).fetchall()

        # Get score
        score_row = conn.execute(
            "SELECT score, grade FROM skill_scores WHERE skill_id = ?",
            (skill_id,),
        ).fetchone()

        # Extract description from metadata
        description = None
        if metadata_json:
            try:
                meta = json.loads(metadata_json)
                description = meta.get("description")
            except (json.JSONDecodeError, TypeError):
                pass

        report = {
            "skill_id": skill_id,
            "registry_id": registry_id,
            "slug": slug,
            "name": name,
            "url": url,
            "description": description,
            "first_seen": first_seen,
            "last_seen": last_seen,
            "score": score_row[0] if score_row else 100,
            "grade": score_row[1] if score_row else "A",
            "findings": [
                {
                    "rule_id": r[0],
                    "severity": r[1],
                    "category": r[2],
                    "subcategory": r[3],
                    "line": r[4],
                    "matched_text": r[5],
                    "message": r[6],
                }
                for r in finding_rows
            ],
        }

        safe_slug = slug.replace("/", "_").replace(":", "_")
        _write_json(output_dir / "skills" / registry_id / f"{safe_slug}.json", report)
        count += 1

    return count


def _export_registry_skills(conn, output_dir: Path, registry_id: str) -> None:
    """Generate /api/v1/registries/{id}/skills.json — list of skills with scores."""
    rows = conn.execute(
        """SELECT s.id, s.slug, s.name,
                  COALESCE(ss.score, 100) as score,
                  COALESCE(ss.grade, 'A') as grade,
                  COALESCE(ss.finding_count, 0) as finding_count,
                  COALESCE(ss.critical_count, 0) as critical_count,
                  COALESCE(ss.high_count, 0) as high_count
           FROM skills s
           LEFT JOIN skill_scores ss ON s.id = ss.skill_id
           WHERE s.registry_id = ? AND s.deleted = 0
           ORDER BY COALESCE(ss.score, 100) ASC""",
        (registry_id,),
    ).fetchall()

    skills = []
    for skill_id, slug, name, score, grade, fc, cc, hc in rows:
        skills.append({
            "skill_id": skill_id,
            "slug": slug,
            "name": name or slug,
            "score": score,
            "grade": grade,
            "finding_count": fc,
            "critical_count": cc,
            "high_count": hc,
        })

    _write_json(output_dir / "registries" / registry_id / "skills.json", skills)


def _export_search_index(conn, output_dir: Path) -> None:
    """Generate /api/v1/search-index.json — lightweight skill index for client-side search."""
    rows = conn.execute(
        """SELECT s.slug, s.name, s.registry_id,
                  COALESCE(ss.score, 100) as score,
                  COALESCE(ss.grade, 'A') as grade,
                  COALESCE(ss.finding_count, 0) as finding_count
           FROM skills s
           LEFT JOIN skill_scores ss ON s.id = ss.skill_id
           WHERE s.deleted = 0
           ORDER BY s.registry_id, s.slug"""
    ).fetchall()

    index = []
    for slug, name, registry_id, score, grade, fc in rows:
        index.append({
            "slug": slug,
            "name": name or slug,
            "registry": registry_id,
            "score": score,
            "grade": grade,
            "findings": fc,
        })

    _write_json(output_dir / "search-index.json", index)


def _export_datasets_manifest(conn, datasets_dir: Path, output_dir: Path) -> None:
    """Generate /api/v1/datasets/manifest.json with download links."""
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "datasets": [
            {
                "name": "findings",
                "description": "All latest findings across registries",
                "format": "csv",
                "path": "/datasets/findings.csv",
            },
            {
                "name": "scores",
                "description": "Skill scores and grades",
                "format": "csv",
                "path": "/datasets/scores.csv",
            },
            {
                "name": "skills",
                "description": "All discovered skills metadata",
                "format": "csv",
                "path": "/datasets/skills.csv",
            },
        ],
    }
    _write_json(output_dir / "datasets" / "manifest.json", manifest)


def _export_csv_datasets(conn, datasets_dir: Path) -> None:
    """Export CSV datasets for bulk download."""
    # Findings CSV
    rows = conn.execute(
        """SELECT fl.skill_id, s.registry_id, s.slug, fl.rule_id,
                  fl.severity, fl.category, fl.message
           FROM findings_latest fl
           JOIN skills s ON fl.skill_id = s.id
           ORDER BY fl.severity, s.registry_id"""
    ).fetchall()

    _write_csv(
        datasets_dir / "findings.csv",
        ["skill_id", "registry_id", "slug", "rule_id", "severity", "category", "message"],
        rows,
    )

    # Scores CSV
    rows = conn.execute(
        """SELECT ss.skill_id, s.registry_id, s.slug, s.name,
                  ss.score, ss.grade, ss.finding_count,
                  ss.critical_count, ss.high_count, ss.medium_count, ss.low_count
           FROM skill_scores ss
           JOIN skills s ON ss.skill_id = s.id
           ORDER BY ss.score"""
    ).fetchall()

    _write_csv(
        datasets_dir / "scores.csv",
        ["skill_id", "registry_id", "slug", "name", "score", "grade",
         "finding_count", "critical_count", "high_count", "medium_count", "low_count"],
        rows,
    )

    # Skills CSV
    rows = conn.execute(
        """SELECT id, registry_id, slug, name, url, content_hash,
                  content_size, first_seen, last_seen, deleted
           FROM skills ORDER BY registry_id, slug"""
    ).fetchall()

    _write_csv(
        datasets_dir / "skills.csv",
        ["id", "registry_id", "slug", "name", "url", "content_hash",
         "content_size", "first_seen", "last_seen", "deleted"],
        rows,
    )


def _write_csv(path: Path, headers: list[str], rows: list[tuple]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(headers)
    writer.writerows(rows)
    path.write_text(buf.getvalue())


def main():
    import argparse

    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Export static API + datasets")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--datasets-dir", type=Path, default=DATASETS_DIR)
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    files = export_all(conn, args.output_dir, args.datasets_dir)
    print(json.dumps(files, indent=2, default=str))


if __name__ == "__main__":
    main()
