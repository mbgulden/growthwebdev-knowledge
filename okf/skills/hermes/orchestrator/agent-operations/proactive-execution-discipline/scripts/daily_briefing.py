#!/usr/bin/env python3
"""
Hermes Proactive-Execution-Discipline — daily briefing shape.

Renders the briefing shape from SKILL.md:
  - Moved since <last_contact>
  - Blocked
  - Executed without asking

Sources moved/blocked/executed counts from the handoff and the proactive counter.

Usage:
  python3 daily_briefing.py --profile orchestrator [--json] [--save-last-run]
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


HAND = "/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py"
COUNT = "/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline/scripts/proactive_count.py"


def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _read_handoff(profile: str) -> dict[str, Any] | None:
    r = subprocess.run(["python3", HAND, "read", "--profile", profile],
                       capture_output=True, text=True, timeout=10)
    if r.returncode != 0: return None
    try: return json.loads(r.stdout)
    except json.JSONDecodeError: return None


def _read_counter(profile: str) -> dict[str, Any]:
    r = subprocess.run(["python3", COUNT, "report", "--profile", profile],
                       capture_output=True, text=True, timeout=10)
    if r.returncode != 0:
        return {"total_turns": 0, "asked_for_count": 0, "executed_without_asking_count": 0, "by_category": {}}
    try: return json.loads(r.stdout)
    except json.JSONDecodeError: return {}


def _last_briefing_path(profile: str) -> Path:
    return Path(f"/home/ubuntu/.hermes/profiles/{profile}/state/briefing-last-run.json")


def _load_last_briefing_ts(profile: str) -> str | None:
    p = _last_briefing_path(profile)
    if not p.exists(): return None
    try:
        return json.loads(p.read_text()).get("last_run_utc")
    except json.JSONDecodeError:
        return None


def _save_last_briefing_ts(profile: str, ts_utc: str) -> None:
    p = _last_briefing_path(profile)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="briefing-", suffix=".json", dir=str(p.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump({"last_run_utc": ts_utc, "profile": profile}, fh, indent=2)
        os.replace(tmp, p)
    except Exception:
        if os.path.exists(tmp): os.unlink(tmp)
        raise


def _filter_executed_since(entries: list[dict], since_ts: str | None) -> list[dict]:
    if not since_ts: return entries
    out = []
    for e in entries:
        ts = e.get("ts_utc", "")
        if not ts or ts >= since_ts: out.append(e)
    return out


def render(profile: str, since_ts: Optional[str] = None) -> dict[str, Any]:
    handoff = _read_handoff(profile) or {}
    counter = _read_counter(profile)
    executed_all = counter.get("executed_without_asking_count", 0)
    asked = counter.get("asked_for_count", 0)
    total = counter.get("total_turns", 0)
    by_cat = counter.get("by_category", {})

    moved = handoff.get("executed_since_last_handoff", []) or []
    in_flight = handoff.get("in_flight", []) or []
    pending = handoff.get("pending_decisions_for_human", []) or []

    if since_ts:
        moved = _filter_executed_since(moved, since_ts)

    blocked: list[dict[str, Any]] = []
    for item in in_flight:
        if item.get("status") in ("blocked", "awaiting_human", "paused"):
            blocked.append(item)

    moved_lines = [
        f"- {e.get("what","?")} [{e.get("kind","?")}] ref={e.get("ref","-")}"
        for e in moved
    ] or ["- (nothing moved since last contact)"]
    blocked_lines = [
        f"- {b.get("id_or_title","?")} (status={b.get("status","?")}, owner={b.get("owner","-")})"
        for b in blocked
    ] or ["- (nothing blocked)"]
    executed_lines = [
        f"- {total} bounded moves logged this week ({executed_all} not explicitly requested, {asked} were)",
        f"- by category: {json.dumps(by_cat)}" if by_cat else "- by category: (no data)",
    ]

    summary = {
        "profile": profile,
        "generated_utc": _now_utc(),
        "since": since_ts,
        "moved": moved,
        "blocked": blocked,
        "pending_decisions": pending,
        "executed_without_asking_count": executed_all,
        "asked_for_count": asked,
        "total_turns_logged": total,
        "by_category": by_cat,
    }
    summary["markdown"] = (
        f"# Daily briefing — {profile}\n\n"
        f"_Generated: {summary["generated_utc"]} · Since: {since_ts or "first run"}_\n\n"
        f"## Moved since last contact\n"
        + "\n".join(moved_lines) + "\n\n"
        f"## Blocked\n"
        + "\n".join(blocked_lines) + "\n\n"
        f"## Executed without asking\n"
        + "\n".join(executed_lines) + "\n\n"
        f"## Pending decisions for human\n"
        + ("\n".join(f"- {p.get("question","?")} (urgency={p.get("urgency","?")})" for p in pending) if pending else "- (none)")
    )
    return summary


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="daily_briefing.py")
    p.add_argument("--profile", default="orchestrator")
    p.add_argument("--last-contact-ts", default=None)
    p.add_argument("--since-window", default="12 hours ago")
    p.add_argument("--json", action="store_true")
    p.add_argument("--save-last-run", action="store_true")
    args = p.parse_args(argv)

    profile = args.profile
    since = args.last_contact_ts
    if since is None:
        since = _load_last_briefing_ts(profile)
    if since is None:
        try:
            n_hours = int(args.since_window.split()[0])
            since = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=n_hours)).isoformat(timespec="seconds")
        except Exception:
            since = None

    summary = render(profile, since)

    if args.json:
        out = {k: v for k, v in summary.items() if k != "markdown"}
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(summary["markdown"])

    if args.save_last_run:
        _save_last_briefing_ts(profile, summary["generated_utc"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
