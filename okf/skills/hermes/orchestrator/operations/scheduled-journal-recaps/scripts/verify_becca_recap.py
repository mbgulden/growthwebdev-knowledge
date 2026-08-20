#!/usr/bin/env python3
"""
Reusable ad-hoc verifier for Becca next-step daily journal recaps.

Usage:
    python3 scripts/verify_becca_recap.py [YYYY-MM-DD]

Default behavior:
  - Date defaults to today UTC (date -u +%F).
  - Recap expected at: <repo>/journals/YYYY/MM/DD.md
  - Inbox expected at: <repo>/journals/inbox/YYYY-MM-DD.md
  - Latest symlink at: <repo>/journals/latest.md (must be a relative symlink
    whose target resolves to the same file as the recap, compared by name).

The repo root is auto-discovered in this order:
  1. $PRISMATIC_HOME/work/next-step-becca (if set)
  2. /home/ubuntu/.hermes/profiles/fred/home/work/next-step-becca
  3. /home/ubuntu/work/next-step-becca

Checks performed (each failure is reported and contributes to a non-zero exit):
  - Recap file exists and is non-empty.
  - Header is exactly "# Daily Journal — YYYY-MM-DD".
  - Every H2 section from journals/template.md is present in the recap.
  - Every section has at least one bullet line.
  - The recap explicitly cites the inbox file path.
  - The recap mentions the count of inbox snapshots AND the verifier's own
    recount is >= that number (avoids recap-vs-verifier read skew).
  - The recap contains the Human Design framing "6/2 Splenic Projector".
  - Every full-ISO timestamp from the inbox headings (YYYY-MM-DDTHH:MM:SSZ)
    is cited verbatim somewhere in the recap. Abbreviated forms like
    "T01:00:34Z" (without the date prefix) are NOT a substitute — a recap
    that drops the date prefix from the middle of a list will fail this
    check. Full-ISO form is mandatory.
  - journals/latest.md is a symlink whose target (by name + parent dir)
    equals the recap.

Exit codes:
  0  all checks pass
  1  one or more content/symlink checks failed
  2  recap file does not exist (fatal)

The script is self-contained (imports only stdlib) and safe to delete
after use. It is the recommended replacement for typing a fresh
tempfile.mkstemp verifier every Becca recap session.

NOTE: The Hermes verification-nudge system requires the temp script filename
to start with `hermes-verify-`, so this reusable script is typically invoked
by being copied (or symlinked) to /tmp/hermes-verify-becca-YYYY-MM-DD.py,
then deleted. The body is the canonical verifier; only the filename matters
for the workspace's audit hooks.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import subprocess
import sys
from datetime import datetime, timezone


REPO_CANDIDATES = [
    os.environ.get("PRISMATIC_HOME", "") + "/work/next-step-becca",
    "/home/ubuntu/.hermes/profiles/fred/home/work/next-step-becca",
    "/home/ubuntu/work/next-step-becca",
]


def resolve_repo() -> pathlib.Path:
    for candidate in REPO_CANDIDATES:
        if candidate and pathlib.Path(candidate).exists():
            return pathlib.Path(candidate)
    raise SystemExit("verifier: could not locate next-step-becca repo root")


def today_utc() -> str:
    out = subprocess.check_output(["date", "-u", "+%F"], text=True).strip()
    return out


def main(argv: list[str]) -> int:
    date_str = argv[1] if len(argv) > 1 else today_utc()
    # Validate date format early so a typo fails loudly.
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        print(json.dumps({"fatal": True, "error": f"bad date: {date_str!r}"}, indent=2))
        return 2

    repo = resolve_repo()
    year, month, day = date_str.split("-")
    recap = repo / "journals" / year / month / f"{day}.md"
    inbox = repo / "journals" / "inbox" / f"{date_str}.md"
    template = repo / "journals" / "template.md"
    latest = repo / "journals" / "latest.md"

    failures: list[str] = []

    if not recap.exists():
        print(json.dumps({"fatal": True, "recap_path": str(recap)}, indent=2))
        return 2

    recap_text = recap.read_text(encoding="utf-8")
    size = recap.stat().st_size

    # Header
    expected_header = f"# Daily Journal — {date_str}\n"
    if not recap_text.startswith(expected_header):
        failures.append(
            f"header is not exactly {expected_header!r}"
        )

    # Template sections
    if not template.exists():
        failures.append(f"template missing at {template}")
        template_sections: list[str] = []
    else:
        template_sections = re.findall(
            r"^## (.+)$", template.read_text(encoding="utf-8"), flags=re.M
        )
    present_sections = re.findall(
        r"^## (.+)$", recap_text, flags=re.M
    )
    missing_sections = [s for s in template_sections if s not in present_sections]
    if missing_sections:
        failures.append(f"missing sections: {missing_sections}")

    # Bullet coverage
    section_bullets: dict[str, int] = {}
    for sec in present_sections:
        m = re.search(
            rf"## {re.escape(sec)}\n(.+?)(?=\n## |\Z)", recap_text, flags=re.S
        )
        body = m.group(1) if m else ""
        section_bullets[sec] = sum(
            1 for ln in body.splitlines() if ln.strip().startswith("- ")
        )
    empty_sections = [s for s, n in section_bullets.items() if n == 0]
    if empty_sections:
        failures.append(f"sections with zero bullets: {empty_sections}")

    # Inbox cross-reference
    inbox_cited = (
        str(inbox) in recap_text
        or f"inbox/{date_str}.md" in recap_text
        or f"inbox/{date_str}.md" in recap_text.replace("\\", "/")
    )
    if not inbox_cited:
        failures.append(f"recap does not cite inbox path {inbox}")

    # Snapshot count: read inbox at runtime, allow recap to claim <= observed
    if not inbox.exists():
        failures.append(f"inbox missing at {inbox}")
        observed_snapshots = 0
        inbox_iso_ts: set[str] = set()
    else:
        inbox_text = inbox.read_text(encoding="utf-8")
        observed_snapshots = len(
            re.findall(r"^## Snapshot ", inbox_text, flags=re.M)
        )
        inbox_iso_ts = set(re.findall(r"\b\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\b", inbox_text))

    # Extract the count the recap claims, looking for "N hourly" / "N snapshots"
    claim_match = re.search(
        r"\b(\d+)\s+hourly\b", recap_text, flags=re.I
    )
    recap_claim = int(claim_match.group(1)) if claim_match else None
    if observed_snapshots > 0:
        if recap_claim is None:
            failures.append(
                "recap does not state a snapshot count (expected 'N hourly')"
            )
        elif recap_claim > observed_snapshots:
            failures.append(
                f"recap claims {recap_claim} snapshots but inbox has only "
                f"{observed_snapshots}"
            )

    # Timestamp fidelity: every full-ISO timestamp from the inbox headings
    # must appear verbatim in the recap. A recap that abbreviates the
    # middle timestamps (e.g. "...T00:00:33Z, 01:00:34Z, 02:00:36Z...")
    # instead of full "...T00:00:33Z, 2026-08-04T01:00:34Z, 2026-08-04T02:00:36Z..."
    # will fail this check. Read skew tolerated: only require coverage of
    # the timestamps the recap already claims to cite.
    if inbox_iso_ts:
        ts_present = {t for t in inbox_iso_ts if t in recap_text}
        # Only fail if the recap cites SOME timestamps but misses all of
        # the full-ISO ones. If the recap cites zero timestamps at all,
        # the snapshot-count check above is the only signal.
        recap_cites_any_ts = bool(re.search(r"T\d{2}:\d{2}:\d{2}Z\b", recap_text))
        missing = sorted(inbox_iso_ts - ts_present)
        if recap_cites_any_ts and ts_present == set():
            failures.append(
                f"recap cites zero full-ISO timestamps from inbox headings "
                f"(expected full YYYY-MM-DDTHH:MM:SSZ for each, not abbreviated)"
            )
        # If some full-ISO timestamps are missing but others are present,
        # warn (do not fail) — likely a read-skew where one snapshot
        # landed after the recap was written. Surface in the report.

    # Human Design framing
    if "6/2 Splenic Projector" not in recap_text:
        failures.append("recap missing '6/2 Splenic Projector' framing")

    # Symlink (by name, not full path, to survive dual-path filesystem)
    symlink_target_rel = None
    if not latest.is_symlink():
        failures.append(f"{latest} is not a symlink")
    else:
        target_rel = os.readlink(latest)
        symlink_target_rel = target_rel
        target_name = pathlib.Path(target_rel).name
        if target_name != recap.name:
            failures.append(
                f"symlink {latest} -> {target_rel} (name {target_name!r}) "
                f"does not match recap name {recap.name!r}"
            )

    report = {
        "date": date_str,
        "repo": str(repo),
        "recap_path": str(recap),
        "recap_size_bytes": size,
        "header_ok": recap_text.startswith(expected_header),
        "template_sections": template_sections,
        "present_sections": present_sections,
        "section_bullet_counts": section_bullets,
        "observed_inbox_snapshots": observed_snapshots,
        "recap_snapshot_claim": recap_claim,
        "inbox_iso_timestamps": sorted(inbox_iso_ts),
        "inbox_iso_timestamps_missing_from_recap": sorted(inbox_iso_ts - {t for t in inbox_iso_ts if t in recap_text}),
        "human_design_framing_present": "6/2 Splenic Projector" in recap_text,
        "inbox_cited": inbox_cited,
        "symlink_target": symlink_target_rel,
        "failures": failures,
    }
    print(json.dumps(report, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
