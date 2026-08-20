#!/usr/bin/env python3
"""
verifier-coverage: Track % of artifacts that shipped with a pre-written verifier.

Usage:
    python3 verifier_coverage.py record --artifact <path> [--verifier <path>] [--verifier-first]
    python3 verifier_coverage.py report
    python3 verifier_coverage.py verify

Exit codes:
    record: 0 always
    report: 0 if pre_written_pct >= 70, 1 otherwise
    verify: 0 if counter file is well-formed
"""

import sys
import json
import os
import datetime
import re

COUNTER_PATH = os.path.expanduser("~/.hermes/profiles/orchestrator/state/verifier-coverage.json")
TARGET_PCT = 70.0


def week_key(ts: datetime.datetime) -> str:
    """ISO week key like 2026-W31."""
    iso = ts.isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def load_counter() -> dict:
    if not os.path.exists(COUNTER_PATH):
        return {"schema_version": "1.0.0", "weeks": {}}
    with open(COUNTER_PATH) as f:
        return json.load(f)


def save_counter(c: dict):
    os.makedirs(os.path.dirname(COUNTER_PATH), exist_ok=True)
    with open(COUNTER_PATH, "w") as f:
        json.dump(c, f, indent=2)


def cmd_record():
    args = sys.argv[2:]
    artifact = None
    verifier = None
    verifier_first = False
    i = 0
    while i < len(args):
        if args[i] == "--artifact":
            artifact = args[i + 1]
            i += 2
        elif args[i] == "--verifier":
            verifier = args[i + 1]
            i += 2
        elif args[i] == "--verifier-first":
            verifier_first = True
            i += 1
        else:
            i += 1

    if not artifact:
        print(json.dumps({"error": "--artifact required"}))
        sys.exit(2)

    c = load_counter()
    now = datetime.datetime.now(datetime.timezone.utc)
    wk = week_key(now)

    if wk not in c["weeks"]:
        c["weeks"][wk] = {"artifacts": [], "pre_written": 0, "total": 0}

    entry = {
        "ts_utc": now.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
        "artifact_path": artifact,
        "verifier_path": verifier,
        "verifier_written_first": verifier_first,
    }
    c["weeks"][wk]["artifacts"].append(entry)
    c["weeks"][wk]["total"] += 1
    if verifier:
        c["weeks"][wk]["pre_written"] += 1

    save_counter(c)
    print(json.dumps({"recorded": entry, "week": wk}, indent=2))
    sys.exit(0)


def cmd_report():
    c = load_counter()
    if not c.get("weeks"):
        print(json.dumps({"verdict": "NO_DATA", "note": "no artifacts recorded yet"}))
        sys.exit(0)

    out = {}
    overall_total = 0
    overall_pre = 0
    for wk, w in sorted(c["weeks"].items()):
        pct = (w["pre_written"] / w["total"] * 100) if w["total"] else 0
        out[wk] = {
            "total": w["total"],
            "pre_written": w["pre_written"],
            "pre_written_pct": round(pct, 1),
        }
        overall_total += w["total"]
        overall_pre += w["pre_written"]

    overall_pct = (overall_pre / overall_total * 100) if overall_total else 0
    verdict = "HEALTHY" if overall_pct >= TARGET_PCT else "REGRESSING"

    report = {
        "verifier": "verifier-coverage",
        "target_pct": TARGET_PCT,
        "overall": {
            "total": overall_total,
            "pre_written": overall_pre,
            "pre_written_pct": round(overall_pct, 1),
        },
        "weeks": out,
        "verdict": verdict,
    }
    print(json.dumps(report, indent=2))
    sys.exit(0 if verdict == "HEALTHY" else 1)


def cmd_verify():
    if not os.path.exists(COUNTER_PATH):
        print(json.dumps({"verdict": "PASS", "note": "counter file does not exist yet (no records)"}))
        sys.exit(0)
    try:
        c = load_counter()
        assert "schema_version" in c
        assert "weeks" in c
        print(json.dumps({"verdict": "PASS", "weeks_recorded": len(c["weeks"])}))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"verdict": "FAIL", "error": str(e)}))
        sys.exit(1)


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "usage: verifier_coverage.py {record|report|verify}"}))
        sys.exit(2)
    cmd = sys.argv[1]
    if cmd == "record":
        cmd_record()
    elif cmd == "report":
        cmd_report()
    elif cmd == "verify":
        cmd_verify()
    else:
        print(json.dumps({"error": f"unknown command: {cmd}"}))
        sys.exit(2)


if __name__ == "__main__":
    main()
