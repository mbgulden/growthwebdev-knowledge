"""Ad-hoc verifier for weekly journal rollups.

Self-contained — every import it uses is included. Run via:
    python3 /path/to/weekly_rollup_verify.py <journals_root> <YYYY-Www>

Exits 0 on success, 1 on any failure. Prints concrete checks so the cron
final response can quote them verbatim.

Checks:
  1. New rollup file exists and is readable.
  2. Word count is under the prompt's limit (default 400; override with WEEKLY_WORD_LIMIT env).
  3. All 6 required sections are present (Decisions / Shipped / Blocked /
     By the Numbers / Looking Ahead / Maintenance Notes) — matched on the
     plain markdown heading text (### Decisions Made), independent of any
     emoji prefix.
  4. At least 7 unique daily source citations of the form YYYY/MM/DD.md.
  5. latest-weekly.md is a relative symlink pointing at weekly/<YYYY-Www>.md.
  6. The previous week's file is byte-identical to a hash captured in
     /tmp/weekly_rollup_prev.sha256 if that baseline file exists. To create
     the baseline on the first run, invoke the script with --snapshot-prev.

This script is intentionally ad-hoc verification, not a canonical suite.
Label outputs "ad-hoc verification passed", never "tests passed".
"""

from __future__ import annotations

import hashlib
import os
import re
import sys
from pathlib import Path

REQUIRED_HEADINGS = [
    "Decisions Made",
    "Shipped",
    "Blocked / In Flight",
    "By the Numbers",
    "Looking Ahead",
    "Maintenance Notes",
]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str]) -> int:
    if len(argv) not in (2, 3):
        print(
            "usage: weekly_rollup_verify.py <journals_root> <YYYY-Www> [--snapshot-prev]",
            file=sys.stderr,
        )
        return 2

    snapshot_prev = len(argv) == 3 and argv[2] == "--snapshot-prev"
    root = Path(argv[0]).expanduser().resolve()
    iso = argv[1]
    weekly_dir = root / "weekly"
    new_file = weekly_dir / f"{iso}.md"
    latest = root / "latest-weekly.md"
    baseline = Path("/tmp/weekly_rollup_prev.sha256")

    failures: list[str] = []

    # 1. New file exists and is readable.
    if not new_file.is_file():
        failures.append(f"missing rollup file: {new_file}")
        print("\n".join(failures))
        return 1
    text = new_file.read_text(encoding="utf-8")
    print(f"OK  file readable: {new_file}")

    # 2. Word count vs. limit.
    limit = int(os.environ.get("WEEKLY_WORD_LIMIT", "400"))
    words = len(text.split())
    if words > limit:
        failures.append(f"word count {words} exceeds limit {limit}")
    else:
        print(f"OK  word count: {words} <= {limit}")

    # 3. Required sections — match on the markdown heading text only.
    section_markers = [f"### {h}" for h in REQUIRED_HEADINGS]
    missing_sections = [s for s in section_markers if s not in text]
    if missing_sections:
        failures.append(f"missing sections: {missing_sections}")
    else:
        print(f"OK  all {len(section_markers)} required sections present")

    # 4. Source citations.
    cites = set(re.findall(r"\d{4}/\d{2}/\d{2}\.md", text))
    if len(cites) < 7:
        failures.append(f"only {len(cites)} unique daily source citations, expected >= 7")
    else:
        print(f"OK  {len(cites)} unique daily source citations")

    # 5. latest-weekly.md symlink target.
    if not latest.is_symlink():
        failures.append(f"{latest} is not a symlink")
    else:
        target = os.readlink(str(latest))
        expected = f"weekly/{iso}.md"
        if target != expected:
            failures.append(f"{latest} -> {target!r}, expected {expected!r}")
        else:
            print(f"OK  latest-weekly.md -> {target}")

    # 6. Previous-week preservation (only meaningful if a baseline exists).
    weeks = sorted(p.stem for p in weekly_dir.glob("*.md"))
    weeks_before = [w for w in weeks if w < iso]
    prev_file = weekly_dir / f"{weeks_before[-1]}.md" if weeks_before else None

    if snapshot_prev:
        if prev_file and prev_file.is_file():
            baseline.write_text(sha256(prev_file) + "\n", encoding="utf-8")
            print(f"OK  baseline created for {prev_file.name}")
        else:
            print("INFO no previous weekly to baseline")
        return 0

    if baseline.is_file() and prev_file and prev_file.is_file():
        expected_sha = baseline.read_text(encoding="utf-8").strip()
        actual_sha = sha256(prev_file)
        if expected_sha != actual_sha:
            failures.append(
                f"{prev_file.name} was modified — "
                f"expected sha {expected_sha[:12]}..., got {actual_sha[:12]}..."
            )
        else:
            print(f"OK  {prev_file.name} unchanged (sha {actual_sha[:12]}...)")
    else:
        print("INFO no previous-week baseline; skipping byte-identical check")

    if failures:
        print("\nFAILURES:", file=sys.stderr)
        for f in failures:
            print(f"  - {f}", file=sys.stderr)
        return 1

    print("\nad-hoc verification passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
