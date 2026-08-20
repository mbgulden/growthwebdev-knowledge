#!/usr/bin/env python3
"""
okf-section-check: Verify OKF documents have valid frontmatter and a sensible
section set for their type.

Tightened pattern set (GAP-5-VERIFIER-PATTERN-TIGHTEN):
- Frontmatter fields are type-different for OKF (project-registry uses
  type/title/description/tags/timestamp/status) vs CK scripts (uses
  name/description only). Frontmatter completeness is checked AGAINST the
  doc's own type, not a fixed list.
- Section requirements vary by OKF type: a `standard` requires Purpose/What
  this standard defines/Adoption status/Honest lessons/Related work. A `report`
  requires different sections. The verifier learns this from the frontmatter's
  `type:` field; if `type` is missing, falls back to standard requirements.

Usage:
    python3 verify.py <path-to-okf-file>

Exits 0 if all type-appropriate checks pass, 1 otherwise. Prints JSON report.
"""

from __future__ import annotations

import sys
import json
import re
import os


# Type-specific required section *fragments* (case-insensitive substring match
# against headings). A heading matches if any fragment appears in the heading.
TYPE_REQUIRED_SECTIONS: dict[str, list[str]] = {
    "standard": [
        "purpose",
        "what this standard",
        "adoption",
        "honest lessons",
        "related work",
    ],
    # Real OKF reports use "TL;DR" or "Summary" at top; "What landed" / "What
    # got built" / "What built" / "Skills shipped" / "Adoption" for what's
    # produced; "Deferred" / "Pinned" / "Open" for what wasn't; "Honest" for
    # lessons. Match by a generous heuristic.
    "report": [
        "tl;dr",  # executive summary at top
        "what got built",
        "honest",
        "future",
    ],
    "how-to": [
        "purpose",
        "procedure",
        "verification",
    ],
}

# Universal frontmatter fields every OKF doc has.
UNIVERSAL_FRONTMATTER = ["type", "title", "description", "status"]

# Type-specific extras.
TYPE_EXTRA_FRONTMATTER: dict[str, list[str]] = {
    "standard": ["tags", "timestamp"],
    "report": ["timestamp", "tags"],
    "how-to": ["timestamp"],
}


def parse_frontmatter(content: str) -> tuple[dict, bool]:
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}, False
    out = {}
    for line in m.group(1).split("\n"):
        if ":" in line and not line.startswith((" ", "\t")):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out, True


def _doc_type(fm: dict) -> str:
    t = (fm.get("type") or "").lower().strip()
    if t in TYPE_REQUIRED_SECTIONS:
        return t
    return "standard"  # safe default


def check_frontmatter(content: str) -> dict:
    fm, ok = parse_frontmatter(content)
    if not ok:
        return {"ok": False, "missing": UNIVERSAL_FRONTMATTER, "type": "unknown", "has_status_current": False}
    doc_type = _doc_type(fm)
    required = set(UNIVERSAL_FRONTMATTER + TYPE_EXTRA_FRONTMATTER.get(doc_type, []))
    missing = [f for f in required if f not in fm]
    return {
        "ok": not missing,
        "missing": missing,
        "type": doc_type,
        "has_status_current": fm.get("status", "") in ("current", "active", "shipped", "drafted", "in-progress"),
        "detected_type": doc_type,
    }


def check_sections(content: str, doc_type: str) -> dict:
    headings = []
    for line in content.split("\n"):
        if line.startswith("## "):
            headings.append(line[3:].strip())
    required = TYPE_REQUIRED_SECTIONS.get(doc_type, TYPE_REQUIRED_SECTIONS["standard"])
    found = []
    missing = []
    for req in required:
        if any(req.lower() in h.lower() for h in headings):
            found.append(req)
        else:
            missing.append(req)
    return {"ok": not missing, "found": found, "missing": missing, "headings_total": len(headings)}


def check_links(content: str, base_path: str) -> dict:
    md_links = re.findall(r"\]\(([^)]+\.md)\)", content)
    broken = []
    for link in md_links:
        target = os.path.join(os.path.dirname(base_path), link)
        try:
            if not os.path.exists(target):
                broken.append(link)
        except OSError:
            broken.append(link)
    return {"ok": not broken, "total": len(md_links), "broken": broken}


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "usage: verify.py <okf-file>"}))
        return 2
    path = sys.argv[1]
    if not os.path.exists(path):
        print(json.dumps({"error": f"file not found: {path}"}))
        return 1
    with open(path) as f:
        content = f.read()
    fm = check_frontmatter(content)
    sections = check_sections(content, fm["detected_type"])
    links = check_links(content, path)
    all_ok = fm["ok"] and fm["has_status_current"] and sections["ok"] and links["ok"]
    report = {
        "verifier": "okf-section-check",
        "path": path,
        "verdict": "PASS" if all_ok else "FAIL",
        "frontmatter": fm,
        "sections": sections,
        "links": links,
    }
    print(json.dumps(report, indent=2))
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
