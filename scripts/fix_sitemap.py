#!/usr/bin/env python3
"""Generate a proper flat sitemap.xml with SEO metadata from Astro's sitemap-0.xml.

Usage:
    python scripts/fix_sitemap.py --pre   # Before build: copy existing to public/
    python scripts/fix_sitemap.py         # After build: regenerate from fresh sitemap-0.xml
"""

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "web" / "dist"
PUBLIC = ROOT / "web" / "public"
TODAY = date.today().isoformat()

# Priority and changefreq by URL pattern
RULES = [
    (r"^https://watch\.aguarascan\.com/$", "1.0", "daily"),
    (r"/registries/$", "0.9", "daily"),
    (r"/registries/[^/]+/$", "0.8", "daily"),
    (r"/categories/$", "0.8", "daily"),
    (r"/categories/[^/]+/$", "0.7", "weekly"),
    (r"/grades/[^/]+/$", "0.7", "weekly"),
    (r"/trends/$", "0.8", "daily"),
    (r"/datasets/$", "0.7", "weekly"),
    (r"/benchmarks/$", "0.7", "weekly"),
    (r"/about/$", "0.5", "monthly"),
    (r"/skills/", "0.6", "weekly"),
]

DEFAULT_PRIORITY = "0.5"
DEFAULT_FREQ = "weekly"


def classify(url: str):
    for pattern, prio, freq in RULES:
        if re.search(pattern, url):
            return prio, freq
    return DEFAULT_PRIORITY, DEFAULT_FREQ


def generate(urls: list[str], out: Path):
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]

    for url in urls:
        prio, freq = classify(url)
        lines.append("  <url>")
        lines.append(f"    <loc>{url}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{prio}</priority>")
        lines.append("  </url>")

    lines.append("</urlset>")
    out.write_text("\n".join(lines) + "\n")
    print(f"Generated {out.name}: {len(urls)} URLs, lastmod={TODAY}")


def main():
    pre_build = "--pre" in sys.argv

    src = DIST / "sitemap-0.xml"
    if not src.exists():
        if pre_build:
            # Pre-build: use existing public/sitemap.xml if available, skip otherwise
            existing = PUBLIC / "sitemap.xml"
            if existing.exists():
                print(f"Pre-build: {existing.name} already exists, keeping it")
            else:
                print("Pre-build: no sitemap-0.xml yet, skipping")
            return
        print(f"ERROR: {src} not found", file=sys.stderr)
        sys.exit(1)

    raw = src.read_text()
    urls = re.findall(r"<loc>([^<]+)</loc>", raw)

    if not urls:
        print("ERROR: no URLs found in sitemap-0.xml", file=sys.stderr)
        sys.exit(1)

    if pre_build:
        # Write to public/ so Astro copies it to dist/
        generate(urls, PUBLIC / "sitemap.xml")
    else:
        # Write to dist/ directly (post-build refresh)
        generate(urls, DIST / "sitemap.xml")


if __name__ == "__main__":
    main()
