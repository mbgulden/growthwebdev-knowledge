#!/usr/bin/env python3
"""
Combined write-and-rewire helper.

Wraps `handoff.py write` with an immediate `wire_cold_start.py wire` for the
same profile. Use this on the hot path (end-of-turn). Falls back to writing
without rewiring if the wire script is missing or fails (handoff stays valid;
the greeting just goes stale until the next wire run).

Idempotent. Safe to call multiple times per turn.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


HAND = "/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py"
WIRE = "/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/wire_cold_start.py"


def write_and_wire(profile: str, agent: str, session_id: str, payload: dict, *, rewire: bool = True) -> dict:
    out: dict = {"profile": profile, "agent": agent, "steps": {}}
    r = subprocess.run(
        ["python3", HAND, "write", "--from-stdin",
         "--profile", profile, "--agent", agent,
         "--session-id", session_id],
        input=json.dumps(payload), capture_output=True, text=True, timeout=15,
    )
    out["steps"]["handoff_write"] = {"rc": r.returncode, "stdout": r.stdout.strip()[:200], "stderr": r.stderr.strip()[:200]}
    if r.returncode != 0:
        out["handoff_ok"] = False
        return out
    out["handoff_ok"] = True

    if rewire:
        if not Path(WIRE).exists():
            out["steps"]["rewire"] = {"rc": -1, "stderr": "wire_cold_start.py not found at canonical path"}
            out["rewire_ok"] = False
            return out
        rw = subprocess.run(
            ["python3", WIRE, "wire", "--profile", profile],
            capture_output=True, text=True, timeout=15,
        )
        out["steps"]["rewire"] = {"rc": rw.returncode, "stdout": rw.stdout.strip()[:200], "stderr": rw.stderr.strip()[:200]}
        out["rewire_ok"] = rw.returncode == 0
    else:
        out["rewire_ok"] = None

    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="write_and_wire.py")
    p.add_argument("--profile", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--session-id", default="manual")
    p.add_argument("--no-rewire", action="store_true", help="Skip the prefill rewire after writing")
    args = p.parse_args(argv)

    raw = sys.stdin.read()
    if not raw.strip():
        print("no payload on stdin", file=sys.stderr)
        return 2
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"invalid JSON: {e}", file=sys.stderr)
        return 2

    result = write_and_wire(args.profile, args.agent, args.session_id, payload, rewire=not args.no_rewire)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("handoff_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
