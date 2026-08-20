#!/usr/bin/env python3
"""
AOT staging-vs-production structural diff.

Pulls both pages, computes the 5 structural signals (byte size, img dedup,
bg-image count, heading order diff, section ordering), and prints a report
suitable for pasting into a user-facing audit message.

Usage:
    python3 aot-staging-vs-prod-diff.py \\
        --prod-url https://activeoahutours.com/ \\
        --staging-url https://content-astro-homepage.active-oahu-tours-mirror.pages.dev/

Or pass already-downloaded HTML files:
    python3 aot-staging-vs-prod-diff.py \\
        --prod-html /tmp/prod.html \\
        --staging-html /tmp/staging.html

Exits 0 always — this is a diagnostic, not a pass/fail check.
"""

import argparse
import hashlib
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def img_urls(html: str) -> list[str]:
    return sorted(set(re.findall(r'<img[^>]*src="([^"]+)"', html)))


def bg_urls(html: str) -> list[str]:
    """Unique background-image URLs (skips the wrapping url() syntax)."""
    raw = re.findall(r"background-image\s*:\s*url\(['\"]?([^'\")]+)['\"]?\)", html)
    # Strip leading slash differences so /wp-content/... and wp-content/... match
    return sorted(set(raw))


def img_url_counts(html: str) -> Counter:
    return Counter(re.findall(r'<img[^>]*src="([^"]+)"', html))


def headings(html: str, level: int) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(rf'<h{level}[^>]*?>([^<]+)</h{level}>', html)]


def all_headings(html: str) -> list[str]:
    h = []
    for lvl in (1, 2, 3):
        h.extend(headings(html, lvl))
    return [t for t in h if t]


def print_table(rows: list[tuple[str, str, str, str]]) -> None:
    name_w = max(len(r[0]) for r in rows)
    a_w = max(len(r[1]) for r in rows)
    b_w = max(len(r[2]) for r in rows)
    for label, a, b, delta in rows:
        print(f"  {label:<{name_w}}  {a:>{a_w}}  {b:>{b_w}}  {delta}")
    print()


def diff(label: str, prod_set: set, stage_set: set, prefix: str = "") -> None:
    missing = sorted(prod_set - stage_set)
    extra = sorted(stage_set - prod_set)
    print(f"=== {label} ===")
    if missing:
        print(f"  IN PROD NOT IN STAGING ({len(missing)}):")
        for x in missing:
            print(f"    - {prefix}{x}")
    if extra:
        print(f"  IN STAGING NOT IN PROD ({len(extra)}):")
        for x in extra:
            print(f"    + {prefix}{x}")
    if not missing and not extra:
        print("  (no diff)")
    print()


def report(prod: str, stage: str, prod_url: str, stage_url: str) -> None:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"AOT STAGING-VS-PRODUCTION STRUCTURAL DIFF")
    print(f"Generated: {now}")
    print(f"  PROD:    {prod_url}  ({len(prod):,} bytes, sha256={hashlib.sha256(prod.encode()).hexdigest()[:16]})")
    print(f"  STAGING: {stage_url}  ({len(stage):,} bytes, sha256={hashlib.sha256(stage.encode()).hexdigest()[:16]})")
    print()

    # Signal 1: top-line counts
    prod_imgs = img_urls(prod)
    stage_imgs = img_urls(stage)
    prod_bgs = bg_urls(prod)
    stage_bgs = bg_urls(stage)
    prod_h = all_headings(prod)
    stage_h = all_headings(stage)

    print("=== TOP-LINE COUNTS ===")
    print_table([
        ("HTML bytes", f"{len(prod):,}", f"{len(stage):,}", f"{len(stage) - len(prod):+,}"),
        ("Unique <img> URLs", str(len(prod_imgs)), str(len(stage_imgs)), str(len(stage_imgs) - len(prod_imgs))),
        ("background-image URLs", str(len(prod_bgs)), str(len(stage_bgs)), str(len(stage_bgs) - len(prod_bgs))),
        ("h1 / h2 / h3",
            f"{len(headings(prod, 1))} / {len(headings(prod, 2))} / {len(headings(prod, 3))}",
            f"{len(headings(stage, 1))} / {len(headings(stage, 2))} / {len(headings(stage, 3))}",
            ""),
    ])

    # Signal 2: image dedup
    print("=== DUPLICATE IMAGES ON STAGING (none on prod is the goal) ===")
    stage_counts = img_url_counts(stage)
    prod_counts = img_url_counts(prod)
    dupes = [(img, c) for img, c in stage_counts.items() if c > 1]
    prod_dupes = [(img, c) for img, c in prod_counts.items() if c > 1]
    if dupes:
        for img, c in dupes:
            print(f"  STAGING {c}x: {img}")
    else:
        print("  (none on staging)")
    if prod_dupes:
        print("  ⚠ Production itself has duplicates (rare — flag this):")
        for img, c in prod_dupes:
            print(f"    PROD {c}x: {img}")
    print()

    # Signal 3: image URL diff
    diff("IMAGE URL DIFF", set(prod_imgs), set(stage_imgs))

    # Signal 4: bg-image URL diff
    diff("BACKGROUND-IMAGE URL DIFF", set(prod_bgs), set(stage_bgs))

    # Signal 5: heading diff
    diff("HEADING DIFF (h1 + h2 + h3, dedup)", set(prod_h), set(stage_h))

    # Section ordering: show first appearance of common markers
    common = set(prod_h) & set(stage_h)
    print("=== SECTION ORDER (first-appearance index for shared headings) ===")
    print(f"  {'Heading':<60} {'PROD':>6} {'STAGING':>8}")
    for h in sorted(common, key=lambda x: prod_h.index(x)):
        p_idx = prod_h.index(h)
        s_idx = stage_h.index(h)
        marker = "  ⚠" if p_idx != s_idx else ""
        print(f"  {h[:58]:<60} {p_idx:>6} {s_idx:>8}{marker}")
    print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--prod-url")
    parser.add_argument("--staging-url")
    parser.add_argument("--prod-html")
    parser.add_argument("--staging-html")
    args = parser.parse_args()

    if args.prod_html and args.staging_html:
        with open(args.prod_html) as f:
            prod = f.read()
        with open(args.staging_html) as f:
            stage = f.read()
        prod_url = f"file://{args.prod_html}"
        stage_url = f"file://{args.staging_html}"
    elif args.prod_url and args.staging_url:
        prod = fetch(args.prod_url)
        stage = fetch(args.staging_url)
        prod_url = args.prod_url
        stage_url = args.staging_url
    else:
        print("Provide either --prod-url + --staging-url OR --prod-html + --staging-html", file=sys.stderr)
        return 2

    report(prod, stage, prod_url, stage_url)
    return 0


if __name__ == "__main__":
    sys.exit(main())