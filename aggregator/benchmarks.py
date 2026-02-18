#!/usr/bin/env python3
"""Benchmark comparison: Aguara vs vendor audits.

Ported from Aguara benchmark: compare.py.
Reads from Turso DB instead of local JSON files.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict

logger = logging.getLogger("observatory.benchmarks")

# Category mapping: Aguara category -> vendor categories
AGUARA_TO_VENDORS = {
    "prompt-injection": {
        "agent-trust-hub": ["PROMPT_INJECTION", "INDIRECT_PROMPT_INJECTION"],
        "socket": [],
        "snyk": [],
    },
    "exfiltration": {
        "agent-trust-hub": ["DATA_EXFILTRATION"],
        "socket": [],
        "snyk": [],
    },
    "credential-leak": {
        "agent-trust-hub": ["CREDENTIALS_UNSAFE"],
        "socket": [],
        "snyk": ["W007"],
    },
    "supply-chain": {
        "agent-trust-hub": [],
        "socket": ["SC006", "CI003", "CI009"],
        "snyk": ["W012"],
    },
    "external-download": {
        "agent-trust-hub": ["EXTERNAL_DOWNLOADS"],
        "socket": ["SC006"],
        "snyk": ["W011", "W012"],
    },
    "command-execution": {
        "agent-trust-hub": ["COMMAND_EXECUTION", "REMOTE_CODE_EXECUTION"],
        "socket": [],
        "snyk": [],
    },
    "indirect-injection": {
        "agent-trust-hub": ["INDIRECT_PROMPT_INJECTION"],
        "socket": [],
        "snyk": [],
    },
    "third-party-content": {
        "agent-trust-hub": [],
        "socket": [],
        "snyk": ["W011", "W012"],
    },
    "unicode-attack": {
        "agent-trust-hub": [],
        "socket": ["Obfuscated File"],
        "snyk": [],
    },
    "mcp-config": {
        "agent-trust-hub": ["COMMAND_EXECUTION"],
        "socket": ["SC006"],
        "snyk": ["W011"],
    },
    "rug-pull": {"agent-trust-hub": [], "socket": [], "snyk": []},
    "toxic-flow": {"agent-trust-hub": [], "socket": [], "snyk": []},
}

# Reverse mapping
VENDOR_TO_AGUARA = defaultdict(set)
for _aguara_cat, _vendor_map in AGUARA_TO_VENDORS.items():
    for _vendor, _codes in _vendor_map.items():
        for _code in _codes:
            VENDOR_TO_AGUARA[(_vendor, _code)].add(_aguara_cat)

SOCKET_NOISE = {"Security Concerns", "Suspicious Patterns"}
ATH_IGNORE = {"NO_CODE"}


def get_vendor_flags_from_db(conn, skill_id: str) -> set[tuple[str, str]]:
    """Extract vendor flags for a skill from DB."""
    flags = set()

    rows = conn.execute(
        "SELECT vendor, findings, raw_data FROM vendor_audits WHERE skill_id = ?",
        (skill_id,),
    ).fetchall()

    for vendor, findings_json, raw_json in rows:
        findings = json.loads(findings_json) if findings_json else []

        if vendor == "agent-trust-hub":
            for f in findings:
                cat = f.get("category", "")
                if cat and cat not in ATH_IGNORE:
                    flags.add(("agent-trust-hub", cat))

        elif vendor == "socket":
            for f in findings:
                code = f.get("code", "")
                cat = f.get("category", "")
                if code:
                    flags.add(("socket", code))
                if cat and cat not in SOCKET_NOISE:
                    flags.add(("socket", cat))

        elif vendor == "snyk":
            for f in findings:
                code = f.get("code", "")
                if code:
                    flags.add(("snyk", code))

    return flags


def get_aguara_categories_from_db(conn, skill_id: str) -> set[str]:
    """Get Aguara finding categories for a skill from latest findings."""
    rows = conn.execute(
        "SELECT DISTINCT category FROM findings_latest WHERE skill_id = ?",
        (skill_id,),
    ).fetchall()
    return {row[0] for row in rows}


def classify_skill(aguara_cats: set[str], vendor_flags: set[tuple[str, str]]) -> dict:
    """Classify TP/FP/FN/TN per category."""
    classification = {}

    for aguara_cat in AGUARA_TO_VENDORS:
        aguara_found = aguara_cat in aguara_cats
        vendor_found = False
        matched = []

        for vendor, codes in AGUARA_TO_VENDORS[aguara_cat].items():
            for code in codes:
                if (vendor, code) in vendor_flags:
                    vendor_found = True
                    matched.append(f"{vendor}:{code}")

        if aguara_found and vendor_found:
            classification[aguara_cat] = {"result": "TP", "vendor_match": matched}
        elif aguara_found and not vendor_found:
            classification[aguara_cat] = {"result": "FP"}
        elif not aguara_found and vendor_found:
            classification[aguara_cat] = {"result": "FN", "vendor_match": matched}
        else:
            classification[aguara_cat] = {"result": "TN"}

    return classification


def compute_metrics(comparisons: dict) -> dict:
    """Compute precision, recall, F1 per category and overall."""
    per_cat = {}

    for cat in AGUARA_TO_VENDORS:
        tp = fp = fn = tn = 0
        for data in comparisons.values():
            result = data["classification"].get(cat, {}).get("result", "TN")
            if result == "TP":
                tp += 1
            elif result == "FP":
                fp += 1
            elif result == "FN":
                fn += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 1.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 1.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

        per_cat[cat] = {
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }

    total_tp = sum(m["tp"] for m in per_cat.values())
    total_fp = sum(m["fp"] for m in per_cat.values())
    total_fn = sum(m["fn"] for m in per_cat.values())
    total_tn = sum(m["tn"] for m in per_cat.values())

    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 1.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 1.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0

    return {
        "per_category": per_cat,
        "overall": {
            "tp": total_tp, "fp": total_fp, "fn": total_fn, "tn": total_tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        },
    }


def run_benchmark(conn) -> dict:
    """Run full benchmark comparison from DB data.

    Returns dict with comparisons, metrics, and summary.
    """
    # Get all skills-sh skills that have vendor audits
    skills_with_audits = conn.execute(
        """SELECT DISTINCT va.skill_id FROM vendor_audits va
           JOIN skills s ON va.skill_id = s.id
           WHERE s.deleted = 0"""
    ).fetchall()

    comparisons = {}
    for (skill_id,) in skills_with_audits:
        vendor_flags = get_vendor_flags_from_db(conn, skill_id)
        aguara_cats = get_aguara_categories_from_db(conn, skill_id)
        classification = classify_skill(aguara_cats, vendor_flags)

        comparisons[skill_id] = {
            "aguara_categories": sorted(aguara_cats),
            "vendor_flags": sorted(f"{v}:{c}" for v, c in vendor_flags),
            "classification": classification,
        }

    # Also include skills with Aguara findings but no audits
    skills_with_findings = conn.execute(
        """SELECT DISTINCT fl.skill_id FROM findings_latest fl
           JOIN skills s ON fl.skill_id = s.id
           WHERE s.deleted = 0"""
    ).fetchall()

    for (skill_id,) in skills_with_findings:
        if skill_id not in comparisons:
            aguara_cats = get_aguara_categories_from_db(conn, skill_id)
            classification = classify_skill(aguara_cats, set())
            comparisons[skill_id] = {
                "aguara_categories": sorted(aguara_cats),
                "vendor_flags": [],
                "classification": classification,
                "no_audit_data": True,
            }

    metrics = compute_metrics(comparisons)
    logger.info(
        "Benchmark: %d skills, P=%.2f%% R=%.2f%% F1=%.2f%%",
        len(comparisons),
        metrics["overall"]["precision"] * 100,
        metrics["overall"]["recall"] * 100,
        metrics["overall"]["f1"] * 100,
    )

    return {
        "skills_compared": len(comparisons),
        "metrics": metrics,
        "comparisons": comparisons,
    }


def main():
    from crawlers.db import connect, init_schema
    from crawlers.utils import setup_logging

    setup_logging()
    conn = connect()
    init_schema(conn)

    result = run_benchmark(conn)
    print(json.dumps({"metrics": result["metrics"], "skills_compared": result["skills_compared"]}, indent=2))


if __name__ == "__main__":
    main()
