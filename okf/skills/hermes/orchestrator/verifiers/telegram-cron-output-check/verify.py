#!/usr/bin/env python3
"""
telegram-cron-output-check: Scan Telegram-bound cron scripts for forbidden stdout patterns.

Detects:
  - Recap paragraphs (multi-line output that prints even when nothing is active)
  - Header-only outputs (date + counts but no action)
  - All-clear / green-pulse markers in stdout
  - Debug scaffolding (e.g. Alert sent to Telegram, AGY exit code)
  - Recurring tagged prefixes (TAG markers that should go to stderr)

Usage:
    python3 verify.py <path-or-dir>

Exits 0 if clean, 1 if any violation found.
"""

import sys
import re
import os


# Patterns that should not appear in stdout for Telegram-bound cron scripts.
# Heuristic - false positives possible; treat as candidates for review.
FORBIDDEN_PATTERNS = [
    (r"print\([^)]*(?:^|\s)I will\s", "I will narrative (subject=I)"),
    (r"print\([^)]*(?:^|\s)I am going to\s", "I am going to narrative"),
    (r"print\([^)]*Let me\s", "Let me narrative"),
    (r"print\([^)]*AGY exit\b", "AGY exit scaffolding"),
    (r"print\([^)]*Alert sent to Telegram", "Alert sent to Telegram (use stderr)"),
    (r"print\([^)]*Telegram send failed", "Telegram send failed (use stderr)"),
    (r"print\([^)]*\[SILENT\]", "SILENT marker (use exit silent)"),
    (r"print\([^)]*\[OK\]", "OK / all-clear marker"),
    (r"print\([^)]*All hostnames locked", "All-clear phrasing (use silent)"),
    (r"print\([^)]*Top stale\b", "Top stale recap section"),
    (r"print\([^)]*Sample.*next_action", "Sample recap section"),
    (r"print\([^)]*GitHub activity sample", "GitHub activity recap section"),
    (r"print\([^)]*Projects scanned\b", "Projects scanned recap line"),
    (r"print\([^,)]*\[NIGHTLY-BACKLOG\]", "tagged prefix NIGHTLY-BACKLOG"),
    (r"print\([^,)]*\[CONSULTING-PIPELINE\]", "tagged prefix CONSULTING-PIPELINE"),
    (r"print\([^)]*Cross-Project Sync", "Cross-Project Sync header (recap)"),
]


def is_stderr(line):
    return "file=sys.stderr" in line or "file=sys" in line


def scan_file(path):
    # Skip broken symlinks or directories.
    if os.path.islink(path) and not os.path.exists(path):
        return []
    if not os.path.isfile(path):
        return []
    findings = []
    try:
        with open(path, "r", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if is_stderr(line):
                    continue
                for pattern, name in FORBIDDEN_PATTERNS:
                    if re.search(pattern, line):
                        findings.append({
                            "line_no": i,
                            "pattern": name,
                            "excerpt": line.strip()[:100],
                        })
    except (PermissionError, IsADirectoryError, UnicodeDecodeError):
        pass
    return findings


def main():
    if len(sys.argv) != 2:
        print("usage: verify.py <path-or-dir>")
        sys.exit(2)

    target = sys.argv[1]
    if os.path.isfile(target):
        files = [target]
    elif os.path.isdir(target):
        files = []
        for root, _, filenames in os.walk(target):
            for fn in filenames:
                if fn.endswith((".py", ".sh")):
                    files.append(os.path.join(root, fn))
    else:
        print(f"path not found: {target}")
        sys.exit(1)

    all_findings = []
    for f in files:
        # Skip self (this verifier)
        if "telegram-cron-output-check" in f:
            continue
        findings = scan_file(f)
        if findings:
            all_findings.append({"file": f, "matches": findings})

    if not all_findings:
        print("PASS: no forbidden stdout patterns found")
        sys.exit(0)

    print(f"FAIL: {len(all_findings)} files have forbidden stdout patterns:")
    for entry in all_findings:
        print(f"  {entry['file']}")
        for m in entry["matches"][:5]:
            print(f"    line {m['line_no']}: {m['pattern']}")
            print(f"      {m['excerpt']}")
    sys.exit(1)


if __name__ == "__main__":
    main()
