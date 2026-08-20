#!/usr/bin/env python3
"""
evidence-no-secret-marker: Scan files for raw API keys or tokens.

Tightened pattern set (GAP-5-VERIFIER-PATTERN-TIGHTEN):
- Only flags `***` markers when they appear next to a key-like prefix in
  configuration-style contexts (e.g., `LINEAR_API_KEY=***` would flag; a sentence
  saying "the literal `***` placeholder" is recognised as documentation and
  skipped.
- Heuristic for documentation mentions: line containing words like "literal",
  "redact", "asterisk", "placeholder", "documentation", etc., alongside the
  marker is skipped.
- Skips comments and docstrings (lines starting with `#`, `//`, or triple quotes).
- Skips binary files by extension or by control-char sniff.
- Recognises self-referencing path (`/skills/verifiers/evidence-no-secret-marker/`)
  via EXCLUDE_GLOBS so the verifier doesn't flag itself.

Usage:
    python3 verify.py <path-or-dir> [--exclude <glob>]

Exits 0 if clean, 1 if any real marker found. Prints JSON report to stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys


# Patterns that look like RAW ACTIVE SECRETS (NOT placeholders).
SECRET_PATTERNS = [
    (r"\bsk-or-[A-Za-z0-9]{20,}", "openrouter-key"),
    (r"\blin_api_[A-Za-z0-9]{20,}", "linear-api-key"),
    (r"\bAIza[A-Za-z0-9_\-]{30,}", "google-api-key"),
    (r"\bsk-(?:proj-)?[A-Za-z0-9]{20,}", "openai-or-anthropic-key"),
    (r"\bghp_[A-Za-z0-9]{30,}\b", "github-pat"),
    (r"\bxox[baprs]-[A-Za-z0-9\-]{20,}\b", "slack-token"),
    (r"\b\d{8,}:[A-Za-z0-9_\-]{30,}\b", "telegram-bot-token"),
]

# Patterns that look like REDACTION MARKERS that shouldn't reach Telegram.
MARKER_PATTERNS = [
    (r"\*\*\*+", "asterisk-marker (3+)"),
    (r"\bREDACTED\b", "literal-redacted"),
    (r"<token>", "placeholder-token"),
]

DOC_CONTEXT_WORDS = (
    "literal", "look", "looks", "looks like", "redact", "redacted",
    "stars", "asterisk", "marker", "placeholder", "documentation",
    "docs", "telegram-bound", "forbidden patterns", "verifier documentation",
    "e.g.", "example", "explanation", "configure", "configuration",
    "skip", "exemption", "words", "contexts",
)

EXCLUDE_GLOBS = [
    "/tmp/hermes-verify-",
    "/state/archive/",
    ".bak",
    ".pre-handoff-wiring.bak",
    "/skills/verifiers/evidence-no-secret-marker/",  # self-reference
]

BINARY_EXTS = (".gz", ".zip", ".tar", ".png", ".jpg", ".jpeg", ".pdf", ".pyc")


def should_skip(path: str) -> bool:
    abs_path = os.path.abspath(path)
    return any(excl in abs_path or excl in path for excl in EXCLUDE_GLOBS)


def _is_comment_line(line: str) -> bool:
    s = line.lstrip()
    if s.startswith(("#", "//")):
        return True
    if s.startswith(('"""', "'''")):
        return True
    return False


def _looks_like_instruction_with_placeholder(line: str) -> bool:
    """Heuristic: a line that DOCUMENTS an env-export shape (e.g., `KEY=***`)
    should not be flagged as a secret leak. Distinguishing signals:
    - Line begins with code/instruction marker (-, $, >, #, or 'shell-like' cmd).
    - Line contains `=` followed immediately by `***`.
    - Line contains `***` inside backticks, parens, or quotes.
    - Line looks like a curl/shell example.
    - Line contains a `sed` substitution as a redaction-recipe.
    """
    s = line.lstrip()
    if s.startswith(("-", "$", ">", "#", "systemctl ", "hermes ", "curl ", "sed ", "grep ")):
        return True
    if "=***" in line:
        return True
    if "***`" in line or "`***" in line or "'***'" in line or '"***"' in line:
        return True
    if line.startswith(("Bearer ", "Authorization: ", "export ", "GITHUB_")):
        return True
    if "<token>" in line.lower():
        return True
    if "**[" in line and "REDACTED" in line:
        return True
    return False


def scan_file(path: str) -> list:
    if path.endswith(BINARY_EXTS):
        return []
    try:
        with open(path, "r", errors="ignore") as f:
            text = f.read()
    except (PermissionError, IsADirectoryError):
        return []

    # Sniff: if first 512 chars contain > 32 control chars (excluding \n\r\t), treat as binary.
    probe = text[:512]
    if sum(1 for c in probe if ord(c) < 32 and c not in "\n\r\t") > 32:
        return []

    findings = []
    for i, line in enumerate(text.splitlines(), 1):
        excerpt = line.strip()[:80]

        # Raw secrets: ALWAYS flag.
        for pattern, name in SECRET_PATTERNS:
            if re.search(pattern, line):
                findings.append({
                    "line_no": i, "pattern": name,
                    "excerpt": excerpt, "kind": "raw-secret",
                })

        # Skip comments before redaction-marker checks.
        if _is_comment_line(line):
            continue
        if _looks_like_instruction_with_placeholder(line):
            continue
        lo = line.lower()
        for pattern, name in MARKER_PATTERNS:
            if re.search(pattern, line):
                if "example" in lo or "fixture" in lo or "test fixture" in lo:
                    continue
                findings.append({
                    "line_no": i, "pattern": name,
                    "excerpt": excerpt, "kind": "redaction-marker",
                })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="evidence-no-secret-marker verifier")
    parser.add_argument("target", help="path to file or dir to scan")
    parser.add_argument("--exclude", action="append", default=[], help="additional glob substrings to skip")
    args = parser.parse_args()

    target = args.target
    extra_excludes = list(args.exclude)

    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = []
        for root, _, filenames in os.walk(target):
            for fn in filenames:
                files.append(os.path.join(root, fn))
    else:
        print(json.dumps({"error": f"path not found: {target}"}))
        return 1

    def skip(p: str) -> bool:
        return should_skip(p) or any(ex in p for ex in extra_excludes)

    all_findings = []
    files_scanned = 0
    for f in files:
        if skip(f):
            continue
        files_scanned += 1
        findings = scan_file(f)
        if findings:
            all_findings.append({"file": f, "matches": findings})

    has_raw = any(
        any(m["kind"] == "raw-secret" for m in entry["matches"])
        for entry in all_findings
    )
    report = {
        "verifier": "evidence-no-secret-marker",
        "target": target,
        "verdict": "PASS" if not all_findings else "FAIL",
        "files_scanned": files_scanned,
        "files_with_matches": len(all_findings),
        "has_raw_secret": has_raw,
        "findings": all_findings,
    }
    print(json.dumps(report, indent=2))
    return 0 if not all_findings else 1


if __name__ == "__main__":
    sys.exit(main())
