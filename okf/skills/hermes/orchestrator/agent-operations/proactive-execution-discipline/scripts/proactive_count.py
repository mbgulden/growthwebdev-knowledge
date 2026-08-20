#!/usr/bin/env python3
"""
Hermes Proactive-Execution-Discipline — weekly counter.

Records one entry per agent turn into state/proactive-count.json with shape:
  {
    "week_starting_utc": "YYYY-MM-DD",
    "turns": [{ts_utc, did, category, was_asked_for}, ...]
  }

Subcommands:
  record   — append one entry (stdin JSON)
  report   — print the weekly ratio + breakdown
  roll     — rotate to a new week if week has changed
  verify   — run an ad-hoc check that the JSON is valid + counts are consistent

Usage:
  python3 proactive_count.py record --profile orchestrator --agent fred \
      --did "wired handoff files for kai" --category infrastructure --was-asked-for false

  python3 proactive_count.py report --profile orchestrator

  python3 proactive_count.py roll --profile orchestrator
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


SCHEMA_VERSION = "1.0.0"


def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _monday_of_week() -> str:
    today = _dt.date.today()
    monday = today - _dt.timedelta(days=today.weekday())
    return monday.isoformat()


def _state_path(profile: str, override_path: Optional[str] = None) -> Path:
    if override_path:
        return Path(override_path)
    return Path(f"/home/ubuntu/.hermes/profiles/{profile}/state/proactive-count.json")


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": SCHEMA_VERSION, "week_starting_utc": _monday_of_week(), "turns": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="proactive-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp): os.unlink(tmp)
        raise


def cmd_record(args: argparse.Namespace) -> int:
    path = _state_path(args.profile, args.state_path)
    data = _load(path)
    current_week = _monday_of_week()
    if data.get("week_starting_utc") != current_week:
        data = {"schema_version": SCHEMA_VERSION, "week_starting_utc": current_week, "turns": []}
    entry = {
        "ts_utc": _now_utc(),
        "did": args.did,
        "category": args.category,
        "was_asked_for": bool(args.was_asked_for),
    }
    data["turns"].append(entry)
    _atomic_write(path, data)
    print(json.dumps({"status": "recorded", "path": str(path), "entry": entry}, indent=2))
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    path = _state_path(args.profile, args.state_path)
    data = _load(path)
    turns = data.get("turns", [])
    total = len(turns)
    asked = sum(1 for t in turns if t.get("was_asked_for"))
    not_asked = total - asked
    ratio = (not_asked / total) if total else 0.0
    by_category: dict[str, dict[str, int]] = {}
    for t in turns:
        cat = t.get("category", "uncategorized")
        s = by_category.setdefault(cat, {"total": 0, "asked": 0, "not_asked": 0})
        s["total"] += 1
        if t.get("was_asked_for"): s["asked"] += 1
        else: s["not_asked"] += 1
    out = {
        "profile": args.profile,
        "week_starting_utc": data.get("week_starting_utc"),
        "total_turns": total,
        "asked_for_count": asked,
        "executed_without_asking_count": not_asked,
        "ratio_executed_without_asking": round(ratio, 3),
        "health_threshold": 0.70,
        "by_category": by_category,
        "verdict": "HEALTHY" if ratio >= 0.70 else ("REGRESSING" if ratio >= 0.50 else "FAILING"),
    }
    print(json.dumps(out, indent=2))
    return 0


def cmd_roll(args: argparse.Namespace) -> int:
    path = _state_path(args.profile, args.state_path)
    data = _load(path)
    current_week = _monday_of_week()
    if data.get("week_starting_utc") == current_week:
        print(f"already on week {current_week}; nothing to roll")
        return 0
    archive_dir = path.parent / "archive"
    archive_dir.mkdir(exist_ok=True)
    archive_name = f"proactive-count-{data.get('week_starting_utc', 'unknown')}.json"
    import shutil
    if path.exists():
        shutil.copy2(path, archive_dir / archive_name)
    new_data = {"schema_version": SCHEMA_VERSION, "week_starting_utc": current_week, "turns": []}
    _atomic_write(path, new_data)
    print(f"rolled: archived {archive_name}, started week {current_week}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    path = _state_path(args.profile, args.state_path)
    if not path.exists():
        print(f"no counter at {path}; nothing to verify")
        return 0
    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: invalid JSON: {e}")
        return 1
    required = ["schema_version", "week_starting_utc", "turns"]
    for k in required:
        if k not in data:
            print(f"FAIL: missing top-level field {k}")
            return 1
    turns = data["turns"]
    for i, t in enumerate(turns):
        for k in ("ts_utc", "did", "category", "was_asked_for"):
            if k not in t:
                print(f"FAIL: turn[{i}] missing {k}")
                return 1
        if not isinstance(t["was_asked_for"], bool):
            print(f"FAIL: turn[{i}].was_asked_for must be bool, got {type(t['was_asked_for']).__name__}")
            return 1
    print(f"PASS: {path} — {len(turns)} turn(s), schema_version={data['schema_version']}")
    return 0


def _resolve_globals(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Pull --profile from anywhere in argv AND strip it (with its value) from argv."""
    out = argparse.Namespace(profile="orchestrator")
    cleaned: list[str] = []
    i = 0
    while i < len(argv):
        if argv[i] == "--profile" and i + 1 < len(argv):
            out.profile = argv[i + 1]
            i += 2
            continue
        cleaned.append(argv[i])
        i += 1
    return out, cleaned


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    globals_ns, argv = _resolve_globals(argv)

    p = argparse.ArgumentParser(prog="proactive_count.py", description="Hermes proactive-execution discipline counter.")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_record = sub.add_parser("record", help="Record one bounded move the agent just executed")
    s_record.add_argument("--did", required=True, help="What the agent did")
    s_record.add_argument("--category", required=True)
    s_record.add_argument("--was-asked-for", type=lambda v: v.lower() in {"true","1","yes","y"}, default=False)
    s_record.add_argument("--state-path", default=None, help="Override the counter file path (for testing)")
    s_record.set_defaults(func=cmd_record)

    s_report = sub.add_parser("report", help="Print the weekly ratio + breakdown")
    s_report.add_argument("--state-path", default=None, help="Override the counter file path (for testing)")
    s_report.set_defaults(func=cmd_report)

    s_roll = sub.add_parser("roll", help="Rotate to a new week (archives current)")
    s_roll.add_argument("--state-path", default=None, help="Override the counter file path (for testing)")
    s_roll.set_defaults(func=cmd_roll)

    s_verify = sub.add_parser("verify", help="Verify the counter JSON is valid + consistent")
    s_verify.add_argument("--state-path", default=None, help="Override the counter file path (for testing)")
    s_verify.set_defaults(func=cmd_verify)

    args = p.parse_args(argv)
    args.profile = globals_ns.profile
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
