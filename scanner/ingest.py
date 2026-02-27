#!/usr/bin/env python3
"""Ingest Aguara scan results into Turso database.

Reads JSON scan output and writes findings, scores, and latest findings.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

from crawlers.db import (
    connect,
    create_scan,
    finish_scan,
    get_skills_by_registry,
    init_schema,
    insert_findings,
    refresh_findings_latest,
    upsert_skill_score,
)
from crawlers.models import Finding, Severity, SkillScore, score_to_grade, SEVERITY_SCORE_IMPACT

logger = logging.getLogger("observatory.ingest")

# Aguara outputs severity as int: 4=CRITICAL, 3=HIGH, 2=MEDIUM, 1=LOW, 0=INFO
SEVERITY_INT_MAP = {
    4: Severity.CRITICAL,
    3: Severity.HIGH,
    2: Severity.MEDIUM,
    1: Severity.LOW,
    0: Severity.INFO,
}

# Map registry to filename patterns
REGISTRY_SLUG_PATTERNS = {
    "skills-sh": re.compile(r"^(.+?)_(.+?)__(.+)\.md$"),  # org_repo__skill.md
    "clawhub": re.compile(r"^(.+)\.md$"),                   # slug.md
    "mcp-registry": re.compile(r"^(.+)\.md$"),
    "mcp-so": re.compile(r"^(.+)\.md$"),
    "lobehub": re.compile(r"^(.+)\.md$"),
    "smithery": re.compile(r"^(.+)\.md$"),
    "glama": re.compile(r"^(.+)\.md$"),
}


def filename_to_skill_id(filename: str, registry_id: str) -> str | None:
    """Convert a filename to a skill_id for a given registry."""
    name = filename.removesuffix(".md")
    return f"{registry_id}:{name}"


def parse_finding(raw: dict) -> Finding:
    """Parse a raw Aguara JSON finding into a Finding model."""
    raw_sev = raw.get("severity", "INFO")
    if isinstance(raw_sev, int):
        severity = SEVERITY_INT_MAP.get(raw_sev, Severity.INFO)
    else:
        try:
            severity = Severity(str(raw_sev).upper())
        except ValueError:
            severity = Severity.INFO

    return Finding(
        rule_id=raw.get("rule_id", "unknown"),
        severity=severity,
        category=raw.get("category", "unknown"),
        subcategory=raw.get("subcategory"),
        line=raw.get("line"),
        matched_text=raw.get("matched_text", ""),
        message=raw.get("message", ""),
    )


def compute_score(findings: list[Finding]) -> SkillScore:
    """Compute a skill score (0-100) and grade (A-F) from findings."""
    score = 100
    critical = high = medium = low = 0
    categories = set()

    for f in findings:
        impact = SEVERITY_SCORE_IMPACT.get(f.severity, 0)
        score -= impact
        categories.add(f.category)

        if f.severity == Severity.CRITICAL:
            critical += 1
        elif f.severity == Severity.HIGH:
            high += 1
        elif f.severity == Severity.MEDIUM:
            medium += 1
        elif f.severity == Severity.LOW:
            low += 1

    score = max(0, score)
    grade = score_to_grade(score)

    return SkillScore(
        skill_id="",  # filled by caller
        score=score,
        grade=grade,
        finding_count=len(findings),
        critical_count=critical,
        high_count=high,
        medium_count=medium,
        low_count=low,
        categories=sorted(categories),
    )


def ingest_scan_results(
    conn,
    scan_result: dict,
    registry_id: str,
    aguara_version: str = "unknown",
    delta: bool = False,
) -> int:
    """Ingest a full scan result into the database.

    Args:
        conn: Database connection
        scan_result: Raw Aguara JSON scan output
        registry_id: Which registry these skills belong to
        aguara_version: Version of Aguara used
        delta: If True, only score skills present in this scan (incremental mode)

    Returns:
        Scan ID
    """
    scan_id = create_scan(conn, registry_id, aguara_version)
    logger.info("Created scan #%d for registry=%s", scan_id, registry_id)

    # Build known skill IDs for this registry
    known_skills = {
        row[1]: row[0]  # slug -> skill_id
        for row in get_skills_by_registry(conn, registry_id)
    }

    # Group findings by file
    by_file: dict[str, list[dict]] = {}
    raw_findings = scan_result.get("findings") or scan_result.get("raw_findings") or []
    for finding in raw_findings:
        filepath = finding.get("file_path", "")
        fname = Path(filepath).name
        by_file.setdefault(fname, []).append(finding)

    total_findings = 0
    skills_scanned = 0

    for fname, raw_findings in by_file.items():
        skill_id = filename_to_skill_id(fname, registry_id)
        if not skill_id:
            continue

        # Verify this skill exists in DB
        slug = skill_id.split(":", 1)[1] if ":" in skill_id else skill_id
        if slug not in known_skills:
            logger.debug("Skipping unknown skill: %s", skill_id)
            continue

        skill_id = known_skills[slug]

        # Parse findings
        findings = [parse_finding(raw) for raw in raw_findings]

        # Insert findings
        count = insert_findings(conn, scan_id, skill_id, findings)
        total_findings += count

        # Refresh latest findings
        refresh_findings_latest(conn, skill_id, scan_id)

        # Compute and store score
        skill_score = compute_score(findings)
        skill_score.skill_id = skill_id
        upsert_skill_score(conn, skill_score, scan_id)

        skills_scanned += 1

    # Score clean skills — ONLY in full scan mode.
    # In delta mode, we only scanned a subset of files, so we must NOT
    # overwrite scores for skills that weren't in this scan.
    if not delta:
        scanned_slugs = set()
        for fname in by_file:
            slug = fname.removesuffix(".md")
            scanned_slugs.add(slug)

        for slug, skill_id in known_skills.items():
            if slug in scanned_slugs:
                continue  # Already scored above
            clean_score = SkillScore(
                skill_id=skill_id,
                score=100,
                grade=score_to_grade(100),
                finding_count=0,
            )
            upsert_skill_score(conn, clean_score, scan_id)
            skills_scanned += 1

    finish_scan(
        conn,
        scan_id,
        skills_scanned=skills_scanned,
        findings_count=total_findings,
        status="completed",
    )
    conn.commit()

    logger.info(
        "Scan #%d complete: %d skills, %d findings ingested",
        scan_id, skills_scanned, total_findings,
    )
    return scan_id


def build_delta_dir(data_dir: Path, manifest_path: Path, delta_dir: Path) -> int:
    """Create a delta directory with symlinks to only changed files.

    Reads .changed_files.txt manifest and symlinks those files from data_dir
    into delta_dir. Returns count of files linked.
    """
    if not manifest_path.exists():
        return 0

    delta_dir.mkdir(parents=True, exist_ok=True)
    count = 0
    for line in manifest_path.read_text().splitlines():
        fname = line.strip()
        if not fname:
            continue
        src = data_dir / fname
        dst = delta_dir / fname
        if src.exists():
            dst.symlink_to(src.resolve())
            count += 1
    return count


def main():
    """CLI entrypoint: ingest scan results from JSON file."""
    import argparse

    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Ingest Aguara scan results into DB")
    parser.add_argument("results_file", type=Path, help="Aguara JSON results file")
    parser.add_argument("--registry", required=True, help="Registry ID")
    parser.add_argument("--aguara-version", default="unknown", help="Aguara version")
    parser.add_argument("--delta", action="store_true",
                        help="Delta mode: only ingest results, preserve existing scores for unchanged skills")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    scan_result = json.loads(args.results_file.read_text())
    scan_id = ingest_scan_results(
        conn, scan_result, args.registry, args.aguara_version, delta=args.delta,
    )
    print(f"Ingested scan #{scan_id} (delta={args.delta})")


if __name__ == "__main__":
    main()
