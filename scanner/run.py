#!/usr/bin/env python3
"""Run Aguara scanner on crawled skill files.

Ported from Aguara benchmark: run_aguara.py.
Changes: parameterized paths, downloads Aguara binary from GH Releases.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path

import requests

logger = logging.getLogger("observatory.scanner")

AGUARA_RELEASE_URL = "https://github.com/garagon/aguara/releases/latest/download"
DEFAULT_BINARY_DIR = Path("bin")


def get_aguara_binary(binary_dir: Path | None = None) -> Path:
    """Get or download the Aguara binary.

    Checks for:
    1. AGUARA_BIN env var (explicit path)
    2. Local binary in binary_dir
    3. Downloads from GitHub Releases
    """
    # Check env var first
    env_bin = os.environ.get("AGUARA_BIN")
    if env_bin:
        path = Path(env_bin)
        if path.exists():
            return path
        logger.warning("AGUARA_BIN=%s does not exist", env_bin)

    # Check local binary
    binary_dir = binary_dir or DEFAULT_BINARY_DIR
    binary_name = "aguara"
    if platform.system() == "Windows":
        binary_name = "aguara.exe"
    local_bin = binary_dir / binary_name
    if local_bin.exists():
        return local_bin

    # Download from GH Releases
    return download_aguara(binary_dir)


def download_aguara(binary_dir: Path) -> Path:
    """Download Aguara binary from GitHub Releases."""
    system = platform.system().lower()
    arch = platform.machine().lower()

    # Map to release asset naming
    os_map = {"linux": "linux", "darwin": "darwin"}
    arch_map = {"x86_64": "amd64", "amd64": "amd64", "arm64": "arm64", "aarch64": "arm64"}

    os_name = os_map.get(system)
    arch_name = arch_map.get(arch)
    if not os_name or not arch_name:
        raise RuntimeError(f"Unsupported platform: {system}/{arch}")

    asset_name = f"aguara-{os_name}-{arch_name}"
    url = f"{AGUARA_RELEASE_URL}/{asset_name}"

    logger.info("Downloading Aguara from %s", url)
    resp = requests.get(url, timeout=60, stream=True)
    resp.raise_for_status()

    binary_dir.mkdir(parents=True, exist_ok=True)
    dest = binary_dir / "aguara"
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)

    dest.chmod(0o755)
    logger.info("Aguara binary saved to %s", dest)
    return dest


def get_aguara_version(binary: Path) -> str:
    """Get Aguara version string."""
    try:
        result = subprocess.run(
            [str(binary), "version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return "unknown"


def run_scan(
    skills_dir: Path,
    binary: Path | None = None,
    timeout: int = 600,
) -> dict:
    """Run Aguara scan on a directory and return parsed JSON results.

    Args:
        skills_dir: Directory containing skill .md files
        binary: Path to Aguara binary (auto-detected if None)
        timeout: Scan timeout in seconds

    Returns:
        Parsed JSON scan result with 'findings', 'files_scanned', etc.
    """
    if binary is None:
        binary = get_aguara_binary()

    logger.info("Scanning %s with %s", skills_dir, binary)

    result = subprocess.run(
        [str(binary), "scan", str(skills_dir), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=timeout,
    )

    if result.returncode not in (0, 1):  # 1 = findings found
        raise RuntimeError(
            f"Aguara scan failed (exit {result.returncode}): {result.stderr}"
        )

    return json.loads(result.stdout)


def group_by_skill(scan_result: dict) -> dict[str, dict]:
    """Group findings by skill filename."""
    by_skill = {}
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}

    for finding in (scan_result.get("findings") or []):
        filepath = finding.get("file_path", "")
        fname = Path(filepath).name
        if fname not in by_skill:
            by_skill[fname] = {
                "filename": fname,
                "findings": [],
                "categories": set(),
                "max_severity": "INFO",
            }
        by_skill[fname]["findings"].append(finding)
        by_skill[fname]["categories"].add(finding.get("category", "unknown"))

    for fname, data in by_skill.items():
        data["categories"] = sorted(data["categories"])
        data["finding_count"] = len(data["findings"])
        max_sev = 0
        for f in data["findings"]:
            sev_str = f.get("severity", "INFO")
            if isinstance(sev_str, int):
                max_sev = max(max_sev, sev_str)
            else:
                max_sev = max(max_sev, severity_order.get(str(sev_str).upper(), 0))
        sev_names = {v: k for k, v in severity_order.items()}
        data["max_severity"] = sev_names.get(max_sev, "INFO")

    return by_skill


def main():
    """CLI entrypoint: run Aguara scan on a directory."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Aguara scanner")
    parser.add_argument("skills_dir", type=Path, help="Directory containing skill files")
    parser.add_argument("--binary", type=Path, help="Path to Aguara binary")
    parser.add_argument("--output", type=Path, help="Output JSON file")
    parser.add_argument("--timeout", type=int, default=600, help="Scan timeout (seconds)")
    args = parser.parse_args()

    from crawlers.utils import setup_logging
    setup_logging()

    scan_result = run_scan(args.skills_dir, binary=args.binary, timeout=args.timeout)

    by_skill = group_by_skill(scan_result)

    output = {
        "scan_meta": {k: v for k, v in scan_result.items() if k != "findings"},
        "by_skill": by_skill,
        "raw_findings": scan_result.get("findings", []),
    }

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, default=list) + "\n")
        logger.info("Results written to %s", args.output)
    else:
        print(json.dumps(output, indent=2, default=list))

    # Summary
    logger.info(
        "Scan complete: %d files, %d findings, %d skills with findings",
        scan_result.get("files_scanned", 0),
        len(scan_result.get("findings") or []),
        len(by_skill),
    )


if __name__ == "__main__":
    main()
