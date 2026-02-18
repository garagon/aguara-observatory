#!/usr/bin/env python3
"""Vendor audit scraper for skills.sh security pages.

Ported from Aguara benchmark: scrape_audits.py.
Scrapes audit results from three vendors: Agent Trust Hub, Socket, Snyk.
Changes: writes to Turso DB instead of local JSON.
"""

from __future__ import annotations

import json
import logging
import re

import requests
from bs4 import BeautifulSoup

from crawlers.db import upsert_vendor_audit
from crawlers.models import VendorAudit
from crawlers.utils import RateLimiter

logger = logging.getLogger("observatory.vendor_audits")

VENDORS = ["agent-trust-hub", "socket", "snyk"]
BASE_URL = "https://skills.sh"
RATE_LIMIT_MS = 500
HEADERS = {"User-Agent": "AguaraObservatory/0.1"}


def fetch_page(url: str, rate_limiter: RateLimiter) -> str | None:
    """Fetch a page, return HTML text or None."""
    rate_limiter.wait()
    try:
        resp = requests.get(url, timeout=15, headers=HEADERS)
        if resp.status_code == 200:
            return resp.text
        return None
    except requests.RequestException:
        return None


# --- Vendor Parsers (ported directly from scrape_audits.py) ---

def parse_agent_trust_hub(html: str) -> dict:
    """Parse Gen Agent Trust Hub audit page."""
    result = {
        "vendor": "agent-trust-hub",
        "verdict": None,
        "risk_level": None,
        "findings": [],
    }

    text = html

    verdict_match = re.search(r"\b(Pass|Fail)\b", text)
    if verdict_match:
        result["verdict"] = verdict_match.group(1)

    risk_match = re.search(r"\b(Safe|Low|Med(?:ium)?|High|Critical)\b", text, re.IGNORECASE)
    if risk_match:
        result["risk_level"] = risk_match.group(1)

    categories = [
        "REMOTE_CODE_EXECUTION", "COMMAND_EXECUTION", "EXTERNAL_DOWNLOADS",
        "DATA_EXFILTRATION", "PROMPT_INJECTION", "INDIRECT_PROMPT_INJECTION",
        "CREDENTIALS_UNSAFE", "DYNAMIC_EXECUTION", "NO_CODE",
    ]
    for cat in categories:
        pattern = rf'{cat}[^"]*?(?:(?:CRITICAL|HIGH|MEDIUM|MED|LOW|INFO))'
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            for m in matches:
                sev_match = re.search(r"(CRITICAL|HIGH|MEDIUM|MED|LOW|INFO)", m, re.IGNORECASE)
                sev = sev_match.group(1).upper() if sev_match else "UNKNOWN"
                if sev == "MED":
                    sev = "MEDIUM"
                result["findings"].append({"category": cat, "severity": sev})
        elif cat in text:
            result["findings"].append({"category": cat, "severity": "UNKNOWN"})

    # Parse structured JSON data from RSC payloads
    json_blocks = re.findall(r'\{[^{}]*"category"[^{}]*\}', text)
    for block in json_blocks:
        try:
            data = json.loads(block)
            if "category" in data and "severity" in data:
                cat = data["category"].upper().replace(" ", "_")
                sev = data["severity"].upper()
                if {"category": cat, "severity": sev} not in result["findings"]:
                    result["findings"].append({"category": cat, "severity": sev})
        except json.JSONDecodeError:
            pass

    return result


def parse_socket(html: str) -> dict:
    """Parse Socket audit page."""
    result = {
        "vendor": "socket",
        "verdict": None,
        "alert_count": 0,
        "alerts": [],
    }

    text = html

    alert_match = re.search(r"(\d+)\s+alert", text, re.IGNORECASE)
    if alert_match:
        result["alert_count"] = int(alert_match.group(1))

    codes = {
        "SC006": "third-party script install",
        "CI003": "backtick command substitution",
        "CI009": "natural language download instruction",
    }
    for code, desc in codes.items():
        if code in text:
            result["alerts"].append({"code": code, "description": desc})

    socket_cats = ["Malware", "Obfuscated File", "Security Concerns", "Suspicious Patterns"]
    for cat in socket_cats:
        if cat.lower() in text.lower():
            result["alerts"].append({"category": cat})

    conf_match = re.search(r"[Cc]onfidence[:\s]*(\d+)%", text)
    if conf_match:
        result["confidence_pct"] = int(conf_match.group(1))
    sev_match = re.search(r"[Ss]everity[:\s]*(\d+)%", text)
    if sev_match:
        result["severity_pct"] = int(sev_match.group(1))

    if result["alert_count"] == 0 and not result["alerts"]:
        result["verdict"] = "clean"
    else:
        result["verdict"] = "alerts"

    return result


def parse_snyk(html: str) -> dict:
    """Parse Snyk audit page."""
    result = {
        "vendor": "snyk",
        "risk_score": None,
        "risk_level": None,
        "findings": [],
    }

    text = html

    score_match = re.search(r"[Rr]isk\s*[Ss]core[:\s]*([01]?\.\d+)", text)
    if score_match:
        result["risk_score"] = float(score_match.group(1))

    risk_match = re.search(r"\b(Low|Med(?:ium)?|High|Critical)\b", text, re.IGNORECASE)
    if risk_match:
        result["risk_level"] = risk_match.group(1)

    snyk_codes = {
        "W007": {"name": "Insecure Credential Handling", "severity": "HIGH"},
        "W009": {"name": "Direct Money Access Capability", "severity": "MEDIUM"},
        "W011": {"name": "Third-Party Content Exposure", "severity": "MEDIUM"},
        "W012": {"name": "Unverifiable External Dependency", "severity": "MEDIUM"},
    }
    for code, info in snyk_codes.items():
        if code in text:
            result["findings"].append({
                "code": code,
                "name": info["name"],
                "severity": info["severity"],
            })

    return result


# --- Main scraping logic ---

def scrape_skill_audits(
    org: str,
    repo: str,
    skill: str,
    rate_limiter: RateLimiter,
) -> dict[str, dict]:
    """Scrape all vendor audits for a single skill."""
    results = {}

    for vendor in VENDORS:
        url = f"{BASE_URL}/{org}/{repo}/{skill}/security/{vendor}"
        html = fetch_page(url, rate_limiter)

        if not html:
            results[vendor] = {"vendor": vendor, "status": "not_found"}
            continue

        if vendor == "agent-trust-hub":
            results[vendor] = parse_agent_trust_hub(html)
        elif vendor == "socket":
            results[vendor] = parse_socket(html)
        elif vendor == "snyk":
            results[vendor] = parse_snyk(html)

        results[vendor]["url"] = url

    return results


def scrape_and_store(conn, skill_id: str, org: str, repo: str, skill: str) -> dict:
    """Scrape vendor audits for a skill and store in DB."""
    rate_limiter = RateLimiter(RATE_LIMIT_MS)
    results = scrape_skill_audits(org, repo, skill, rate_limiter)

    for vendor, data in results.items():
        if data.get("status") == "not_found":
            continue

        audit = VendorAudit(
            skill_id=skill_id,
            vendor=vendor,
            verdict=data.get("verdict"),
            risk_level=data.get("risk_level"),
            risk_score=data.get("risk_score"),
            alert_count=data.get("alert_count", 0),
            findings=data.get("findings", data.get("alerts", [])),
            raw_data=data,
        )
        upsert_vendor_audit(conn, audit)

    return results


def main():
    """CLI entrypoint: scrape vendor audits for all skills-sh skills in DB."""
    import argparse

    from crawlers.db import connect, init_schema, get_skills_by_registry
    from crawlers.utils import setup_logging

    parser = argparse.ArgumentParser(description="Scrape vendor audits")
    parser.add_argument("--registry", default="skills-sh", help="Registry to scrape audits for")
    parser.add_argument("--limit", type=int, default=0, help="Max skills to scrape (0=all)")
    args = parser.parse_args()

    setup_logging()
    conn = connect()
    init_schema(conn)

    skills = get_skills_by_registry(conn, args.registry)
    logger.info("Found %d skills in %s", len(skills), args.registry)

    if args.limit > 0:
        skills = skills[:args.limit]

    scraped = 0
    failed = 0

    for i, (skill_id, slug, _) in enumerate(skills, 1):
        # Parse org/repo/skill from slug (format: org_repo__skill)
        parts = re.match(r"^(.+?)_(.+?)__(.+)$", slug)
        if not parts:
            continue

        org, repo, skill = parts.group(1), parts.group(2), parts.group(3)

        try:
            scrape_and_store(conn, skill_id, org, repo, skill)
            scraped += 1
        except Exception as e:
            logger.warning("Failed to scrape audits for %s: %s", skill_id, e)
            failed += 1

        if i % 50 == 0:
            conn.commit()
            logger.info("Progress: %d/%d (scraped=%d, failed=%d)", i, len(skills), scraped, failed)

    conn.commit()
    logger.info("Done: scraped=%d, failed=%d", scraped, failed)


if __name__ == "__main__":
    main()
