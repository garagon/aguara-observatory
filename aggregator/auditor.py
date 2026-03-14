"""Automated auditor: classifies findings and writes audit_overrides to DB.

Runs fp_analysis heuristics against findings_latest and persists verdicts
so that score computation can exclude confirmed false positives.

Usage:
    python -m aggregator.auditor [--min-confidence 0.8] [--dry-run]
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import sys

from aggregator.fp_analysis import classify_finding
from crawlers.db import (
    connect,
    init_schema,
    upsert_audit_override,
    upsert_rule_override,
)

logger = logging.getLogger("observatory.auditor")

# Confidence mapping: how much we trust each heuristic label
LABEL_CONFIDENCE = {
    "likely_fp": 0.85,
    "likely_tp": 0.85,
    "needs_review": 0.4,
}

# Reasons with very high confidence (manually validated patterns)
HIGH_CONFIDENCE_REASONS = {
    # FP patterns that are almost always correct
    "low_severity_informational",
    "pip_install_doc",
    "doc_install_pattern",
    "env_var_http_verb_name",
    "mcp_tool_description",
    "example_domain",
    "example_url",
    "doc_link_pattern",
    "doc_table_fragment",
    "localhost_dev_port",
    "credential_template",
    "isolated_flag_in_docs",
    "eval_exec_partial_match",
    "path_setup_instruction",
    "github_download",
    "crontab_reference",
    "install_fragment",
    "script_reference",
    # TP patterns that are almost always correct
    "curl_pipe_shell",
    "cloud_metadata_access",
    "reverse_shell",
    "ssrf_pattern",
    "prompt_injection_pattern",
    "chained_shell_execution",
    "prompt_injection_medium",
    "supply_chain_medium",
    "supply_chain_pattern",
}

# Override: bump confidence for validated patterns
REASON_CONFIDENCE_OVERRIDE = {r: 0.95 for r in HIGH_CONFIDENCE_REASONS}


def _text_hash(text: str | None) -> str:
    """SHA-256 hash of matched_text for dedup."""
    content = (text or "").strip()
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def run_auditor(
    conn,
    *,
    min_confidence: float = 0.8,
    dry_run: bool = False,
    batch_size: int = 5000,
) -> dict:
    """Classify all findings and write audit overrides.

    Returns summary stats dict.
    """
    cursor = conn.execute("""
        SELECT fl.id, fl.skill_id, fl.rule_id, fl.severity, fl.matched_text
        FROM findings_latest fl
        ORDER BY fl.skill_id, fl.rule_id
    """)

    stats = {"total": 0, "fp": 0, "tp": 0, "review": 0, "written": 0, "skipped": 0}
    batch_count = 0

    while True:
        rows = cursor.fetchmany(batch_size)
        if not rows:
            break

        for row in rows:
            finding_id, skill_id, rule_id, severity, matched_text = row
            stats["total"] += 1

            cls = classify_finding(rule_id, severity, matched_text)

            if cls.label == "likely_fp":
                stats["fp"] += 1
                verdict = "fp"
            elif cls.label == "likely_tp":
                stats["tp"] += 1
                verdict = "tp"
            else:
                stats["review"] += 1
                verdict = None  # Don't write needs_review as overrides

            if verdict is None:
                stats["skipped"] += 1
                continue

            confidence = REASON_CONFIDENCE_OVERRIDE.get(
                cls.reason, LABEL_CONFIDENCE.get(cls.label, 0.5)
            )

            if confidence < min_confidence:
                stats["skipped"] += 1
                continue

            if not dry_run:
                upsert_audit_override(
                    conn,
                    skill_id=skill_id,
                    rule_id=rule_id,
                    verdict=verdict,
                    reason=cls.reason,
                    auditor="heuristic",
                    confidence=confidence,
                    matched_text_hash=_text_hash(matched_text),
                )
                stats["written"] += 1
            else:
                stats["written"] += 1

        batch_count += 1
        if batch_count % 10 == 0 and not dry_run:
            conn.commit()
            logger.info("Progress: %d findings processed", stats["total"])

    if not dry_run:
        conn.commit()

    return stats


def main():
    parser = argparse.ArgumentParser(description="Run automated FP/TP auditor")
    parser.add_argument(
        "--min-confidence", type=float, default=0.8,
        help="Minimum confidence to write an override (default: 0.8)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Classify but don't write to DB",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    conn = connect()
    init_schema(conn)

    logger.info("Running auditor (min_confidence=%.2f, dry_run=%s)", args.min_confidence, args.dry_run)
    stats = run_auditor(conn, min_confidence=args.min_confidence, dry_run=args.dry_run)

    print(f"\nAuditor complete:")
    print(f"  Total findings:  {stats['total']:,}")
    print(f"  Likely FP:       {stats['fp']:,}")
    print(f"  Likely TP:       {stats['tp']:,}")
    print(f"  Needs review:    {stats['review']:,}")
    print(f"  Overrides written: {stats['written']:,}")
    print(f"  Skipped (low confidence): {stats['skipped']:,}")

    if args.dry_run:
        print("\n  (dry run — no changes written)")

    conn.close()


if __name__ == "__main__":
    main()
