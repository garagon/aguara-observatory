#!/usr/bin/env python3
"""Compare old vs new Aguara scan results across registries.

Loads baseline (pre-upgrade) and new scan results, computes:
- Total findings delta per registry and overall
- New rules appearing, rules removed
- Severity distribution changes
- Per-rule deltas (findings added/removed)
- Estimated FP impact using heuristic classifier from fp_analysis

Usage:
    python scripts/compare_scans.py
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Add project root to path for aggregator imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from aggregator.fp_analysis import classify_finding

REGISTRIES = ["skills-sh", "clawhub", "mcp-so", "lobehub", "mcp-registry"]
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
BASELINE_DIR = DATA_DIR / "baseline-pre-upgrade"

SEV_MAP = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "INFO",
           "CRITICAL": "CRITICAL", "HIGH": "HIGH", "MEDIUM": "MEDIUM",
           "LOW": "LOW", "INFO": "INFO"}


def normalize_severity(finding: dict) -> str:
    """Convert numeric or string severity to string label."""
    return SEV_MAP.get(finding.get("severity", "INFO"), "INFO")


def load_findings(path: Path) -> list[dict]:
    """Load findings from a scan result JSON file."""
    if not path.exists():
        return []
    data = json.loads(path.read_text())
    # Handle both raw aguara output and scanner/run.py wrapped output
    if "raw_findings" in data:
        return data["raw_findings"] or []
    return data.get("findings") or []


def fingerprint(f: dict) -> str:
    """Create a stable fingerprint for a finding to track additions/removals."""
    file_path = Path(f.get("file_path", "")).name
    rule = f.get("rule_id", "")
    line = f.get("line", 0)
    return f"{file_path}|{rule}|{line}"


def classify_findings(findings: list[dict]) -> dict:
    """Classify all findings using heuristic FP analysis."""
    counts = {"likely_tp": 0, "likely_fp": 0, "needs_review": 0}
    for f in findings:
        cls = classify_finding(
            f.get("rule_id", ""),
            normalize_severity(f),
            f.get("matched_text", ""),
        )
        counts[cls.label] += 1
    return counts


def severity_dist(findings: list[dict]) -> Counter:
    return Counter(normalize_severity(f) for f in findings)


def rule_dist(findings: list[dict]) -> Counter:
    return Counter(f.get("rule_id", "UNKNOWN") for f in findings)


def category_dist(findings: list[dict]) -> Counter:
    return Counter(f.get("category", "unknown") for f in findings)


def main():
    print("=" * 80)
    print("AGUARA SCAN COMPARISON: BASELINE vs NEW BUILD")
    print("=" * 80)

    total_old = 0
    total_new = 0
    all_old_findings = []
    all_new_findings = []

    registry_rows = []

    for reg in REGISTRIES:
        old_path = BASELINE_DIR / f"scan-results-{reg}.json"
        new_path = DATA_DIR / f"scan-results-new-{reg}.json"

        old_findings = load_findings(old_path)
        new_findings = load_findings(new_path)

        all_old_findings.extend(old_findings)
        all_new_findings.extend(new_findings)

        delta = len(new_findings) - len(old_findings)
        pct = (delta / len(old_findings) * 100) if old_findings else 0

        registry_rows.append({
            "registry": reg,
            "old": len(old_findings),
            "new": len(new_findings),
            "delta": delta,
            "pct": pct,
        })

        total_old += len(old_findings)
        total_new += len(new_findings)

    # Registry summary table
    print(f"\n{'REGISTRY':<20} {'OLD':>8} {'NEW':>8} {'DELTA':>8} {'CHANGE':>8}")
    print("-" * 56)
    for r in registry_rows:
        sign = "+" if r["delta"] >= 0 else ""
        print(f"{r['registry']:<20} {r['old']:>8,} {r['new']:>8,} {sign}{r['delta']:>7,} {r['pct']:>+7.1f}%")
    print("-" * 56)
    total_delta = total_new - total_old
    total_pct = (total_delta / total_old * 100) if total_old else 0
    sign = "+" if total_delta >= 0 else ""
    print(f"{'TOTAL':<20} {total_old:>8,} {total_new:>8,} {sign}{total_delta:>7,} {total_pct:>+7.1f}%")

    # Severity distribution comparison
    print(f"\n{'=' * 80}")
    print("SEVERITY DISTRIBUTION")
    print(f"{'=' * 80}")
    old_sev = severity_dist(all_old_findings)
    new_sev = severity_dist(all_new_findings)
    all_sevs = sorted(set(list(old_sev.keys()) + list(new_sev.keys())),
                      key=lambda s: {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}.get(s, 5))
    print(f"\n{'SEVERITY':<12} {'OLD':>8} {'NEW':>8} {'DELTA':>8}")
    print("-" * 40)
    for sev in all_sevs:
        o = old_sev.get(sev, 0)
        n = new_sev.get(sev, 0)
        d = n - o
        sign = "+" if d >= 0 else ""
        print(f"{sev:<12} {o:>8,} {n:>8,} {sign}{d:>7,}")

    # Category distribution comparison
    print(f"\n{'=' * 80}")
    print("CATEGORY DISTRIBUTION")
    print(f"{'=' * 80}")
    old_cat = category_dist(all_old_findings)
    new_cat = category_dist(all_new_findings)
    all_cats = sorted(set(list(old_cat.keys()) + list(new_cat.keys())))
    print(f"\n{'CATEGORY':<35} {'OLD':>7} {'NEW':>7} {'DELTA':>7}")
    print("-" * 60)
    for cat in all_cats:
        o = old_cat.get(cat, 0)
        n = new_cat.get(cat, 0)
        d = n - o
        if d != 0:
            sign = "+" if d >= 0 else ""
            print(f"{cat:<35} {o:>7,} {n:>7,} {sign}{d:>6,}")

    # Per-rule delta (top movers)
    print(f"\n{'=' * 80}")
    print("TOP RULE CHANGES (by absolute delta)")
    print(f"{'=' * 80}")
    old_rules = rule_dist(all_old_findings)
    new_rules = rule_dist(all_new_findings)
    all_rule_ids = sorted(set(list(old_rules.keys()) + list(new_rules.keys())))
    rule_deltas = []
    for rid in all_rule_ids:
        o = old_rules.get(rid, 0)
        n = new_rules.get(rid, 0)
        d = n - o
        if d != 0:
            rule_deltas.append((rid, o, n, d))

    rule_deltas.sort(key=lambda x: abs(x[3]), reverse=True)

    # New rules
    new_rule_ids = [rd for rd in rule_deltas if rd[1] == 0 and rd[2] > 0]
    if new_rule_ids:
        print(f"\n  NEW RULES (not in baseline):")
        for rid, o, n, d in new_rule_ids:
            print(f"    {rid:<30} +{n} findings")

    # Removed rules
    removed_rule_ids = [rd for rd in rule_deltas if rd[2] == 0 and rd[1] > 0]
    if removed_rule_ids:
        print(f"\n  REMOVED RULES (no longer firing):")
        for rid, o, n, d in removed_rule_ids:
            print(f"    {rid:<30} -{o} findings")

    # Changed rules
    changed = [rd for rd in rule_deltas if rd[1] > 0 and rd[2] > 0]
    if changed:
        print(f"\n  CHANGED RULES (top 20 by delta):")
        print(f"  {'RULE':<30} {'OLD':>7} {'NEW':>7} {'DELTA':>7}")
        print(f"  {'-' * 55}")
        for rid, o, n, d in changed[:20]:
            sign = "+" if d >= 0 else ""
            print(f"  {rid:<30} {o:>7,} {n:>7,} {sign}{d:>6,}")

    # FP Analysis comparison
    print(f"\n{'=' * 80}")
    print("FALSE POSITIVE ANALYSIS (heuristic)")
    print(f"{'=' * 80}")

    old_fp = classify_findings(all_old_findings)
    new_fp = classify_findings(all_new_findings)

    print(f"\n{'CLASSIFICATION':<18} {'OLD':>8} {'OLD%':>7} {'NEW':>8} {'NEW%':>7} {'DELTA':>8}")
    print("-" * 60)
    for label in ["likely_tp", "likely_fp", "needs_review"]:
        o = old_fp[label]
        n = new_fp[label]
        o_pct = (o / total_old * 100) if total_old else 0
        n_pct = (n / total_new * 100) if total_new else 0
        d = n - o
        sign = "+" if d >= 0 else ""
        print(f"{label:<18} {o:>8,} {o_pct:>6.1f}% {n:>8,} {n_pct:>6.1f}% {sign}{d:>7,}")

    # FP rate by severity (new scan)
    print(f"\n  FP RATE BY SEVERITY (new scan):")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        sev_findings = [f for f in all_new_findings if normalize_severity(f) == sev]
        if not sev_findings:
            continue
        sev_cls = classify_findings(sev_findings)
        fp_rate = sev_cls["likely_fp"] / len(sev_findings) * 100
        tp_rate = sev_cls["likely_tp"] / len(sev_findings) * 100
        print(f"    {sev:<10} {len(sev_findings):>6} findings  TP={tp_rate:>5.1f}%  FP={fp_rate:>5.1f}%  Review={100-tp_rate-fp_rate:>5.1f}%")

    # Net quality assessment
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    old_tp_rate = (old_fp["likely_tp"] / total_old * 100) if total_old else 0
    new_tp_rate = (new_fp["likely_tp"] / total_new * 100) if total_new else 0
    old_fp_rate = (old_fp["likely_fp"] / total_old * 100) if total_old else 0
    new_fp_rate = (new_fp["likely_fp"] / total_new * 100) if total_new else 0

    print(f"\n  Findings:     {total_old:,} -> {total_new:,} ({total_delta:+,})")
    print(f"  TP rate:      {old_tp_rate:.1f}% -> {new_tp_rate:.1f}% ({new_tp_rate - old_tp_rate:+.1f}pp)")
    print(f"  FP rate:      {old_fp_rate:.1f}% -> {new_fp_rate:.1f}% ({new_fp_rate - old_fp_rate:+.1f}pp)")
    print(f"  New rules:    {len(new_rule_ids)}")
    print(f"  Removed rules: {len(removed_rule_ids)}")

    if new_fp_rate < old_fp_rate:
        print(f"\n  >> FP rate IMPROVED by {old_fp_rate - new_fp_rate:.1f} percentage points")
    elif new_fp_rate > old_fp_rate:
        print(f"\n  >> FP rate INCREASED by {new_fp_rate - old_fp_rate:.1f} percentage points")
    else:
        print(f"\n  >> FP rate unchanged")

    if new_tp_rate > old_tp_rate:
        print(f"  >> TP rate IMPROVED by {new_tp_rate - old_tp_rate:.1f} percentage points")


if __name__ == "__main__":
    main()
