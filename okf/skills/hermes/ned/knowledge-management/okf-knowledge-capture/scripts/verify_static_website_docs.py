#!/usr/bin/env python3
"""Ad-hoc verifier for small static marketing-site/documentation repos.

Usage:
  python3 verify_static_website_docs.py /path/to/repo \
    --changed README.md docs/content-checklist.md docs/trust-lead-content-inventory.md \
    --domain sentinelitad.com

This is intentionally generic enough to copy into /tmp/hermes-verify-* for
session-specific runs. Report results as ad-hoc verification, not suite green.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
import xml.etree.ElementTree as ET


class Parser(HTMLParser):
    pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", type=Path)
    parser.add_argument("--changed", nargs="*", default=[])
    parser.add_argument("--domain", default="")
    parser.add_argument("--port", type=int, default=8799)
    args = parser.parse_args()

    root = args.repo.resolve()
    failures: list[str] = []

    public_files = [
        "public/index.html",
        "public/privacy.html",
        "public/terms.html",
        "public/thanks.html",
        "public/robots.txt",
        "public/sitemap.xml",
        "public/CNAME",
    ]
    docs = ["README.md", *args.changed, *public_files]
    for rel in sorted(set(docs)):
        p = root / rel
        if not p.exists():
            failures.append(f"missing: {rel}")
        elif p.stat().st_size == 0:
            failures.append(f"empty: {rel}")

    # Parse public artifacts when present.
    for rel in ["public/index.html", "public/privacy.html", "public/terms.html", "public/thanks.html"]:
        p = root / rel
        if p.exists():
            try:
                Parser().feed(p.read_text(encoding="utf-8"))
            except Exception as exc:  # noqa: BLE001 - verifier should report all parse failures
                failures.append(f"HTML parse failed {rel}: {exc}")
    sitemap = root / "public/sitemap.xml"
    if sitemap.exists():
        try:
            ET.parse(sitemap)
        except Exception as exc:  # noqa: BLE001
            failures.append(f"sitemap XML parse failed: {exc}")

    if args.domain:
        cname = root / "public/CNAME"
        robots = root / "public/robots.txt"
        if cname.exists() and cname.read_text(encoding="utf-8").strip() != args.domain:
            failures.append(f"CNAME is not {args.domain}")
        if robots.exists() and args.domain not in robots.read_text(encoding="utf-8"):
            failures.append(f"robots.txt does not mention {args.domain}")

    # Smoke-test local static serving.
    proc = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(args.port), "--bind", "127.0.0.1", "--directory", str(root / "public")],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1)
        for path in ["/", "/privacy.html", "/terms.html", "/thanks.html", "/robots.txt", "/sitemap.xml"]:
            try:
                with urllib.request.urlopen(f"http://127.0.0.1:{args.port}{path}", timeout=5) as resp:
                    if resp.status != 200:
                        failures.append(f"local HTTP {path}: {resp.status}")
            except Exception as exc:  # noqa: BLE001
                failures.append(f"local HTTP {path}: {exc}")
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()

    diff = subprocess.run(["git", "diff", "--check"], cwd=root, text=True, capture_output=True)
    if diff.returncode != 0:
        failures.append("git diff --check failed: " + (diff.stdout + diff.stderr).strip())

    if failures:
        print("RESULT: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("RESULT: PASS")
    print("Covered: required docs/public files, HTML/XML parse, CNAME/robots, local HTTP 200 smoke, git diff --check.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
