"""Heuristic false-positive analysis for Aguara Watch findings.

Classifies each finding as likely-TP, likely-FP, or needs-review based on
matched_text patterns and rule context. Outputs a per-rule report.

Usage:
    python -m aggregator.fp_analysis [--db observatory.db] [--export fp_report.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

# ─── Heuristic classifiers ────────────────────────────────────────────────────

# Documentation install patterns: almost always FP in skill descriptions
DOC_INSTALL_RE = re.compile(
    r"(pip|pip3)\s+install\s+"
    r"|npm\s+install\s+"
    r"|npx\s+"
    r"|go\s+install\s+"
    r"|cargo\s+install\s+"
    r"|gem\s+install\s+"
    r"|brew\s+install\s+"
    r"|apt(-get)?\s+install\s+"
    r"|yum\s+install\s+"
    r"|pacman\s+-S\s+"
    r"|docker\s+pull\s+",
    re.IGNORECASE,
)

# Env var names that contain HTTP verbs but aren't exfiltration
ENV_VAR_HTTP_VERB_RE = re.compile(
    r"process\.env\.(SEND|POST|GET|PUT|DELETE|NEXT_PUBLIC_POST|NEXT_PUBLIC_GET)"
    r"|os\.environ\[?[\"'](POST|GET|SEND|PUT|DELETE)",
    re.IGNORECASE,
)

# Standard MCP config showing "command": "npx" (not an attack, just unpinned)
MCP_NPX_CONFIG_RE = re.compile(
    r'"command"\s*:\s*"npx"'
    r"|claude\s+mcp\s+add\s+.*npx",
    re.IGNORECASE,
)

# Known legitimate domains in curl/download patterns
SAFE_DOMAINS = [
    "bun.sh", "deno.land", "ollama.com", "nodejs.org", "rustup.rs",
    "get.docker.com", "raw.githubusercontent.com", "cli.github.com",
    "install.python-poetry.org", "pyenv.run", "brew.sh",
    "sdk.cloud.google.com", "cli.inference.sh", "browser-use.com",
    "mise.jdx.dev", "proto.moonrepo.app",
]
SAFE_DOMAIN_RE = re.compile(
    "|".join(re.escape(d) for d in SAFE_DOMAINS),
    re.IGNORECASE,
)

# Shell script execution in documentation context
SCRIPT_EXEC_RE = re.compile(
    r"\./[\w./-]+\.sh"
    r"|bash\s+[\w./-]+\.sh"
    r"|sh\s+[\w./-]+\.sh",
    re.IGNORECASE,
)

# MCP tool descriptions that look like capability docs, not cross-tool leakage
MCP_TOOL_DOC_RE = re.compile(
    r"(get|fetch|read|list|search)\s+.*\+\s*(post|send|write|create|update)"
    r"|get\s+(an?\s+)?(api|csrf|auth)\s+(key|token)"
    r"|scope:\s+"
    r"|available\s+in\s+all"
    r"|request\s+all\s+permissions",
    re.IGNORECASE,
)

# Self-modifying patterns that are actually skill workflows
SKILL_WORKFLOW_RE = re.compile(
    r"(promote|append|update|add)\s+.*\s+(to|in)\s+(CLAUDE\.md|\.claude/)"
    r"|write\s+to\s+CLAUDE\.md",
    re.IGNORECASE,
)

# Subprocess/eval in code examples
CODE_EXAMPLE_RE = re.compile(
    r"subprocess\.(run|call|Popen)\("
    r"|shell\s*=\s*True"
    r"|eval\s*\(",
    re.IGNORECASE,
)


@dataclass
class Classification:
    label: str  # "likely_fp", "likely_tp", "needs_review"
    reason: str


@dataclass
class RuleReport:
    rule_id: str
    severity: str
    total: int = 0
    likely_tp: int = 0
    likely_fp: int = 0
    needs_review: int = 0
    fp_reasons: dict = field(default_factory=lambda: defaultdict(int))
    tp_reasons: dict = field(default_factory=lambda: defaultdict(int))
    samples_fp: list = field(default_factory=list)
    samples_tp: list = field(default_factory=list)
    samples_review: list = field(default_factory=list)


def classify_finding(rule_id: str, severity: str, matched_text: str) -> Classification:
    """Apply heuristic rules to classify a finding."""
    text = matched_text or ""
    text_lower = text.lower().strip()

    # ── LOW severity rules: almost all informational ──
    if severity == "LOW":
        # EXTDL_009: pip install
        if rule_id == "EXTDL_009" and "pip" in text_lower and "install" in text_lower:
            return Classification("likely_fp", "pip_install_doc")

        # CMDEXEC_013: shell script execution
        if rule_id == "CMDEXEC_013" and SCRIPT_EXEC_RE.search(text):
            return Classification("likely_fp", "script_reference")

        # Generic doc install patterns
        if DOC_INSTALL_RE.search(text):
            return Classification("likely_fp", "doc_install_pattern")

        # Most LOW findings are informational by design
        return Classification("likely_fp", "low_severity_informational")

    # ── EXFIL_007: env var with HTTP verb name ──
    if rule_id == "EXFIL_007" and ENV_VAR_HTTP_VERB_RE.search(text):
        return Classification("likely_fp", "env_var_http_verb_name")

    # ── MCPCFG_001: npx without version pin ──
    if rule_id == "MCPCFG_001" and MCP_NPX_CONFIG_RE.search(text):
        return Classification("needs_review", "npx_no_pin_real_but_noisy")

    # ── MCP_007/009/010: tool documentation patterns ──
    if rule_id in ("MCP_007", "MCP_009", "MCP_010") and MCP_TOOL_DOC_RE.search(text):
        return Classification("likely_fp", "mcp_tool_description")

    # ── PROMPT_INJECTION_016: skill writing to CLAUDE.md ──
    if rule_id == "PROMPT_INJECTION_016" and SKILL_WORKFLOW_RE.search(text):
        return Classification("needs_review", "skill_workflow_claude_md")

    # ── Download rules with known-safe domains ──
    if rule_id in ("EXTDL_013", "SUPPLY_003", "EXTDL_007") and SAFE_DOMAIN_RE.search(text):
        return Classification("needs_review", "known_domain_but_curl_pipe_sh")

    # ── CRITICAL findings: default to likely_tp ──
    if severity == "CRITICAL":
        # curl | sh is always a real concern even with known domains
        if "| sh" in text_lower or "| bash" in text_lower:
            return Classification("likely_tp", "curl_pipe_shell")
        if "metadata" in text_lower or "169.254.169.254" in text_lower:
            return Classification("likely_tp", "cloud_metadata_access")
        if "reverse" in text_lower and "shell" in text_lower:
            return Classification("likely_tp", "reverse_shell")
        return Classification("likely_tp", "critical_default")

    # ── HIGH findings: context-dependent ──
    if severity == "HIGH":
        # Code patterns that could be docs or real
        if CODE_EXAMPLE_RE.search(text) and len(text) < 30:
            return Classification("needs_review", "short_code_pattern")
        # SSRF patterns are almost always TP
        if rule_id.startswith("SSRF_"):
            return Classification("likely_tp", "ssrf_pattern")
        # Prompt injection patterns
        if rule_id.startswith("PROMPT_INJECTION_"):
            return Classification("likely_tp", "prompt_injection_pattern")
        # NLP findings have built-in context analysis
        if rule_id.startswith("NLP_"):
            return Classification("likely_tp", "nlp_contextual_detection")
        # Supply chain
        if rule_id.startswith("SUPPLY_"):
            return Classification("likely_tp", "supply_chain_pattern")
        # Default HIGH
        return Classification("needs_review", "high_needs_context")

    # ── MEDIUM findings: mostly needs review ──
    if severity == "MEDIUM":
        if DOC_INSTALL_RE.search(text):
            return Classification("likely_fp", "doc_install_pattern")
        return Classification("needs_review", "medium_needs_context")

    return Classification("needs_review", "unclassified")


def analyze(db_path: str) -> dict:
    """Run heuristic analysis on all findings."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT fl.rule_id, fl.severity, fl.matched_text, fl.message,
               s.name as skill_name, s.slug as skill_slug
        FROM findings_latest fl
        JOIN skills s ON fl.skill_id = s.id
        ORDER BY fl.rule_id, fl.severity
    """)

    reports: dict[str, RuleReport] = {}

    for row in cursor.fetchall():
        rule_id = row["rule_id"]
        severity = row["severity"]
        matched_text = row["matched_text"] or ""

        key = f"{rule_id}|{severity}"
        if key not in reports:
            reports[key] = RuleReport(rule_id=rule_id, severity=severity)

        report = reports[key]
        report.total += 1

        cls = classify_finding(rule_id, severity, matched_text)

        sample = {
            "skill": row["skill_slug"] or row["skill_name"],
            "matched": matched_text[:120],
            "reason": cls.reason,
        }

        if cls.label == "likely_fp":
            report.likely_fp += 1
            report.fp_reasons[cls.reason] += 1
            if len(report.samples_fp) < 3:
                report.samples_fp.append(sample)
        elif cls.label == "likely_tp":
            report.likely_tp += 1
            report.tp_reasons[cls.reason] += 1
            if len(report.samples_tp) < 3:
                report.samples_tp.append(sample)
        else:
            report.needs_review += 1
            if len(report.samples_review) < 3:
                report.samples_review.append(sample)

    conn.close()
    return reports


def print_report(reports: dict[str, RuleReport]) -> None:
    """Print human-readable analysis report."""
    # Sort by severity order, then by total desc
    sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

    sorted_reports = sorted(
        reports.values(),
        key=lambda r: (sev_order.get(r.severity, 5), -r.total),
    )

    total_findings = sum(r.total for r in sorted_reports)
    total_fp = sum(r.likely_fp for r in sorted_reports)
    total_tp = sum(r.likely_tp for r in sorted_reports)
    total_review = sum(r.needs_review for r in sorted_reports)

    print("=" * 78)
    print("AGUARA WATCH — HEURISTIC FALSE-POSITIVE ANALYSIS")
    print("=" * 78)
    print(f"\nTotal findings:  {total_findings:,}")
    print(f"  Likely TP:     {total_tp:,} ({100*total_tp/total_findings:.1f}%)")
    print(f"  Likely FP:     {total_fp:,} ({100*total_fp/total_findings:.1f}%)")
    print(f"  Needs review:  {total_review:,} ({100*total_review/total_findings:.1f}%)")

    # Summary by severity
    print(f"\n{'─' * 78}")
    print(f"{'SEVERITY':<10} {'TOTAL':>7} {'TP':>7} {'FP':>7} {'REVIEW':>7} {'FP%':>7}")
    print(f"{'─' * 78}")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        sev_reports = [r for r in sorted_reports if r.severity == sev]
        t = sum(r.total for r in sev_reports)
        tp = sum(r.likely_tp for r in sev_reports)
        fp = sum(r.likely_fp for r in sev_reports)
        rv = sum(r.needs_review for r in sev_reports)
        fp_pct = f"{100*fp/t:.0f}%" if t > 0 else "—"
        print(f"{sev:<10} {t:>7,} {tp:>7,} {fp:>7,} {rv:>7,} {fp_pct:>7}")

    # Detail by rule
    print(f"\n{'=' * 78}")
    print("DETAIL BY RULE")
    print(f"{'=' * 78}")

    current_sev = None
    for r in sorted_reports:
        if r.severity != current_sev:
            current_sev = r.severity
            print(f"\n{'─' * 78}")
            print(f"  {current_sev}")
            print(f"{'─' * 78}")

        fp_pct = f"{100*r.likely_fp/r.total:.0f}%" if r.total > 0 else "—"
        bar_tp = "█" * min(r.likely_tp, 50)
        bar_fp = "░" * min(r.likely_fp, 50)

        print(f"\n  {r.rule_id:<28} total={r.total:<5} TP={r.likely_tp:<5} FP={r.likely_fp:<5} review={r.needs_review:<5} FP%={fp_pct}")

        if r.fp_reasons:
            top_reasons = sorted(r.fp_reasons.items(), key=lambda x: -x[1])[:3]
            for reason, cnt in top_reasons:
                print(f"    FP: {reason} ({cnt})")
        if r.tp_reasons:
            top_reasons = sorted(r.tp_reasons.items(), key=lambda x: -x[1])[:3]
            for reason, cnt in top_reasons:
                print(f"    TP: {reason} ({cnt})")

        # Show samples for needs_review (most actionable)
        if r.samples_review:
            print(f"    Review samples:")
            for s in r.samples_review[:2]:
                matched = s["matched"].replace("\n", " ")[:80]
                print(f"      [{s['skill'][:30]}] {matched}")

    # Actionable recommendations
    print(f"\n{'=' * 78}")
    print("RECOMMENDATIONS")
    print(f"{'=' * 78}")

    # Rules with >80% FP rate and significant volume
    fp_rules = [
        r for r in sorted_reports
        if r.total >= 10 and r.likely_fp / r.total > 0.8
    ]
    if fp_rules:
        print("\n  Rules to downgrade or add exclude patterns (>80% FP, 10+ findings):")
        for r in sorted(fp_rules, key=lambda x: -x.total):
            print(f"    {r.rule_id} ({r.severity}): {r.likely_fp}/{r.total} FP ({100*r.likely_fp/r.total:.0f}%)")

    # Rules needing manual review
    review_rules = [
        r for r in sorted_reports
        if r.needs_review >= 10 and r.severity in ("CRITICAL", "HIGH")
    ]
    if review_rules:
        print("\n  High-severity rules needing manual review (10+ findings):")
        for r in sorted(review_rules, key=lambda x: -x.needs_review):
            print(f"    {r.rule_id} ({r.severity}): {r.needs_review} to review")


def export_json(reports: dict[str, RuleReport], path: str) -> None:
    """Export analysis results as JSON."""
    data = {}
    for key, r in reports.items():
        data[key] = {
            "rule_id": r.rule_id,
            "severity": r.severity,
            "total": r.total,
            "likely_tp": r.likely_tp,
            "likely_fp": r.likely_fp,
            "needs_review": r.needs_review,
            "fp_rate": round(r.likely_fp / r.total, 3) if r.total > 0 else 0,
            "fp_reasons": dict(r.fp_reasons),
            "tp_reasons": dict(r.tp_reasons),
            "samples_fp": r.samples_fp,
            "samples_tp": r.samples_tp,
            "samples_review": r.samples_review,
        }

    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nExported to {path}")


def main():
    parser = argparse.ArgumentParser(description="Heuristic FP analysis for Aguara Watch")
    parser.add_argument("--db", default="observatory.db", help="Path to observatory.db")
    parser.add_argument("--export", help="Export JSON report to file")
    args = parser.parse_args()

    db_path = args.db
    if not Path(db_path).exists():
        print(f"Error: {db_path} not found", file=sys.stderr)
        sys.exit(1)

    reports = analyze(db_path)
    print_report(reports)

    if args.export:
        export_json(reports, args.export)


if __name__ == "__main__":
    main()
