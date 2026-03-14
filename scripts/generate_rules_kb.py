#!/usr/bin/env python3
"""Generate the rule knowledge base JSON for the web frontend.

Reads scan results to extract rule metadata, then merges
hand-written remediation and FP guidance.

Output: web/public/api/v1/rules.json
"""

import json
import glob
from pathlib import Path

SCAN_GLOBS = ["data/scan-results-*.json", "data/*-results.json"]
OUTPUT = Path("web/public/api/v1/rules.json")
SEV_MAP = {4: "CRITICAL", 3: "HIGH", 2: "MEDIUM", 1: "LOW", 0: "INFO"}


def main():
    # Step 1: Extract rule metadata from scan results
    rules = {}
    for pattern in SCAN_GLOBS:
        for fpath in glob.glob(pattern):
            try:
                data = json.loads(Path(fpath).read_text())
                for f in (data.get("findings") or data.get("raw_findings") or []):
                    rid = f.get("rule_id", "")
                    if rid and rid not in rules:
                        rules[rid] = {
                            "name": f.get("rule_name", ""),
                            "description": f.get("description", ""),
                            "category": f.get("category", ""),
                            "severity": SEV_MAP.get(f.get("severity", 0), "INFO"),
                            "analyzer": f.get("analyzer", "pattern"),
                        }
            except Exception:
                pass

    # Step 2: Load remediation from companion file
    rem_path = Path("scripts/rules_remediation.json")
    if rem_path.exists():
        rem = json.loads(rem_path.read_text())
        for rid, r in rules.items():
            if rid in rem:
                r["remediation"] = rem[rid].get("remediation", "")
                r["fp_hint"] = rem[rid].get("fp_hint", "")
            else:
                r["remediation"] = f"Review this {r['severity'].lower()}-severity finding."
                r["fp_hint"] = "Review the matched text in context."
    else:
        for r in rules.values():
            r["remediation"] = f"Review this {r['severity'].lower()}-severity finding."
            r["fp_hint"] = "Review the matched text in context."

    # Step 3: Write output
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(rules, indent=2, ensure_ascii=False) + "\n")
    print(f"Written {len(rules)} rules to {OUTPUT}")


if __name__ == "__main__":
    main()
