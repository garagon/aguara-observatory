"""Benchmark export and precision metrics for Aguara Watch findings.

Exports a stratified sample of ~500 findings from scan results, auto-labels
them using fp_analysis heuristics, and computes per-rule precision metrics.

Usage:
    python -m aggregator.benchmark [--data-dir data/] [--sample-size 500] [--export benchmark.json]
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path

from aggregator.fp_analysis import classify_finding

# Severity int→string mapping (Aguara JSON format)
SEVERITY_MAP = {0: "CRITICAL", 1: "HIGH", 2: "MEDIUM", 3: "LOW", 4: "INFO"}
SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

REGISTRIES = ["clawhub", "lobehub", "mcp-so", "skills-sh"]


@dataclass
class BenchmarkFinding:
    rule_id: str
    rule_name: str
    severity: str
    category: str
    file_path: str
    line: int
    matched_text: str
    context_type: str  # "documentation", "code_block", "execution", "unknown"
    registry: str
    score: int
    analyzer: str
    label: str  # "likely_tp", "likely_fp", "needs_review"
    label_reason: str


@dataclass
class RuleMetrics:
    rule_id: str
    severity: str
    category: str
    total: int = 0
    tp: int = 0
    fp: int = 0
    review: int = 0
    precision: float = 0.0
    fp_rate: float = 0.0


# ── Context detection ────────────────────────────────────────────────────────

DOC_HEADINGS = [
    "installation", "setup", "getting started", "prerequisites",
    "requirements", "usage", "quick start", "configuration",
    "how to use", "how to install", "examples", "demo",
]


def detect_context(finding: dict) -> str:
    """Classify the context around a finding as doc, code, or execution."""
    context_lines = finding.get("context", [])
    matched = (finding.get("matched_text") or "").lower()

    # Check surrounding lines for heading patterns
    for cl in context_lines:
        line = (cl.get("content") or "").strip().lower()
        if line.startswith("#"):
            heading = line.lstrip("#").strip()
            for keyword in DOC_HEADINGS:
                if keyword in heading:
                    return "documentation"

    # Check if inside a code block (``` markers in context)
    in_code_block = False
    for cl in context_lines:
        line = (cl.get("content") or "").strip()
        if line.startswith("```"):
            in_code_block = not in_code_block
        if cl.get("is_match") and in_code_block:
            return "code_block"

    # Check for execution indicators in the matched text
    exec_patterns = ["eval(", "exec(", "subprocess", "child_process", "shell=True", "| sh", "| bash"]
    for p in exec_patterns:
        if p in matched:
            return "execution"

    return "unknown"


# ── Loading ──────────────────────────────────────────────────────────────────

def load_findings(data_dir: Path) -> list[dict]:
    """Load all findings from scan-results JSON files."""
    all_findings = []
    for reg in REGISTRIES:
        path = data_dir / f"scan-results-{reg}.json"
        if not path.exists():
            continue
        with open(path) as f:
            data = json.load(f)
        for finding in data.get("raw_findings", []):
            finding["_registry"] = reg
            finding["_severity_str"] = SEVERITY_MAP.get(finding.get("severity", 4), "INFO")
            all_findings.append(finding)
    return all_findings


# ── Stratified sampling ──────────────────────────────────────────────────────

def stratified_sample(findings: list[dict], n: int, seed: int = 42) -> list[dict]:
    """Sample n findings stratified by severity and category."""
    rng = random.Random(seed)

    # Group by (severity, category)
    buckets: dict[tuple, list] = defaultdict(list)
    for f in findings:
        key = (f["_severity_str"], f.get("category", "unknown"))
        buckets[key].append(f)

    # Proportional allocation with minimum 1 per non-empty bucket
    total = len(findings)
    sampled = []

    for key, bucket in buckets.items():
        proportion = len(bucket) / total
        count = max(1, round(proportion * n))
        count = min(count, len(bucket))
        sampled.extend(rng.sample(bucket, count))

    # Trim or pad to target size
    if len(sampled) > n:
        sampled = rng.sample(sampled, n)
    elif len(sampled) < n:
        remaining = [f for f in findings if f not in sampled]
        extra = min(n - len(sampled), len(remaining))
        sampled.extend(rng.sample(remaining, extra))

    return sampled


# ── Benchmark creation ───────────────────────────────────────────────────────

def create_benchmark(findings: list[dict]) -> list[BenchmarkFinding]:
    """Create labeled benchmark findings with context detection."""
    benchmark = []
    for f in findings:
        severity = f["_severity_str"]
        rule_id = f.get("rule_id", "")
        matched_text = f.get("matched_text", "")

        cls = classify_finding(rule_id, severity, matched_text)
        ctx = detect_context(f)

        benchmark.append(BenchmarkFinding(
            rule_id=rule_id,
            rule_name=f.get("rule_name", ""),
            severity=severity,
            category=f.get("category", ""),
            file_path=f.get("file_path", ""),
            line=f.get("line", 0),
            matched_text=matched_text[:300],
            context_type=ctx,
            registry=f.get("_registry", ""),
            score=f.get("score", 0),
            analyzer=f.get("analyzer", ""),
            label=cls.label,
            label_reason=cls.reason,
        ))
    return benchmark


# ── Metrics ──────────────────────────────────────────────────────────────────

def compute_metrics(benchmark: list[BenchmarkFinding]) -> list[RuleMetrics]:
    """Compute per-rule precision metrics from the benchmark set."""
    by_rule: dict[str, RuleMetrics] = {}

    for b in benchmark:
        if b.rule_id not in by_rule:
            by_rule[b.rule_id] = RuleMetrics(
                rule_id=b.rule_id, severity=b.severity, category=b.category,
            )
        m = by_rule[b.rule_id]
        m.total += 1
        if b.label == "likely_tp":
            m.tp += 1
        elif b.label == "likely_fp":
            m.fp += 1
        else:
            m.review += 1

    for m in by_rule.values():
        classified = m.tp + m.fp
        if classified > 0:
            m.precision = round(m.tp / classified, 3)
            m.fp_rate = round(m.fp / classified, 3)

    return sorted(
        by_rule.values(),
        key=lambda m: (SEVERITY_ORDER.get(m.severity, 5), -m.total),
    )


# ── Output ───────────────────────────────────────────────────────────────────

def print_metrics(metrics: list[RuleMetrics], benchmark: list[BenchmarkFinding]) -> None:
    """Print metrics report to terminal."""
    total = len(benchmark)
    tp = sum(1 for b in benchmark if b.label == "likely_tp")
    fp = sum(1 for b in benchmark if b.label == "likely_fp")
    review = sum(1 for b in benchmark if b.label == "needs_review")

    print("=" * 80)
    print("AGUARA BENCHMARK — PER-RULE PRECISION METRICS")
    print("=" * 80)
    print(f"\nBenchmark size:  {total}")
    print(f"  Likely TP:     {tp} ({100*tp/total:.1f}%)")
    print(f"  Likely FP:     {fp} ({100*fp/total:.1f}%)")
    print(f"  Needs review:  {review} ({100*review/total:.1f}%)")

    # Context breakdown
    ctx_counts = defaultdict(int)
    for b in benchmark:
        ctx_counts[b.context_type] += 1
    print(f"\nContext distribution:")
    for ctx, cnt in sorted(ctx_counts.items(), key=lambda x: -x[1]):
        print(f"  {ctx:<16} {cnt:>5} ({100*cnt/total:.1f}%)")

    # Per-rule table
    print(f"\n{'─' * 80}")
    print(f"{'RULE':<28} {'SEV':<8} {'N':>5} {'TP':>5} {'FP':>5} {'REV':>5} {'PREC':>7} {'FP%':>7}")
    print(f"{'─' * 80}")

    current_sev = None
    for m in metrics:
        if m.severity != current_sev:
            current_sev = m.severity
            print(f"  {current_sev}")

        prec = f"{m.precision:.0%}" if (m.tp + m.fp) > 0 else "-"
        fpr = f"{m.fp_rate:.0%}" if (m.tp + m.fp) > 0 else "-"
        print(f"  {m.rule_id:<26} {m.severity:<8} {m.total:>5} {m.tp:>5} {m.fp:>5} {m.review:>5} {prec:>7} {fpr:>7}")

    # Worst precision rules
    bad_rules = [m for m in metrics if m.precision < 0.5 and m.total >= 3 and (m.tp + m.fp) > 0]
    if bad_rules:
        print(f"\n{'=' * 80}")
        print("RULES WITH <50% PRECISION (3+ samples)")
        print(f"{'=' * 80}")
        for m in sorted(bad_rules, key=lambda x: x.precision):
            print(f"  {m.rule_id:<28} precision={m.precision:.0%}  ({m.fp} FP / {m.tp + m.fp} classified)")


def export_benchmark(benchmark: list[BenchmarkFinding], metrics: list[RuleMetrics], path: str) -> None:
    """Export benchmark and metrics as JSON."""
    data = {
        "meta": {
            "total_findings": len(benchmark),
            "tp": sum(1 for b in benchmark if b.label == "likely_tp"),
            "fp": sum(1 for b in benchmark if b.label == "likely_fp"),
            "needs_review": sum(1 for b in benchmark if b.label == "needs_review"),
        },
        "findings": [asdict(b) for b in benchmark],
        "metrics": [asdict(m) for m in metrics],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"\nExported benchmark to {path}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Benchmark export and precision metrics")
    parser.add_argument("--data-dir", default="data/", help="Directory with scan-results-*.json")
    parser.add_argument("--sample-size", type=int, default=500, help="Number of findings to sample")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--export", help="Export benchmark JSON to file")
    parser.add_argument("--all", action="store_true", help="Analyze all findings (no sampling)")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        print(f"Error: {data_dir} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Loading findings from {data_dir}...")
    findings = load_findings(data_dir)
    print(f"Loaded {len(findings)} findings from {len(REGISTRIES)} registries")

    if args.all:
        sampled = findings
        print(f"Analyzing ALL {len(sampled)} findings")
    else:
        sampled = stratified_sample(findings, args.sample_size, seed=args.seed)
        print(f"Sampled {len(sampled)} findings (stratified by severity + category)")

    benchmark = create_benchmark(sampled)
    metrics = compute_metrics(benchmark)

    print_metrics(metrics, benchmark)

    if args.export:
        export_benchmark(benchmark, metrics, args.export)


if __name__ == "__main__":
    main()
