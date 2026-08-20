#!/usr/bin/env python3
"""
Hermes Session Handoff — cross-agent primitive.

Read, write, verify, and chain Hermes agent handoff files. Designed to work
identically for every Hermes profile that adopts the session-state-handoff
contract. Not tied to any single provider/model.

Run `python3 handoff.py --help` for subcommands. Imports nothing Hermes-specific
so the same script runs inside hermes, inside AGY, inside Claude/Codex CLIs,
inside cron no-agent scripts, and inside ad-hoc terminal commands.

Versioned alongside the JSON schema in templates/handoff.schema.json.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


SCHEMA_VERSION = "1.0.0"
SOURCE_PROFILE = "orchestrator"

# Default location under any Hermes profile. Override with --path.
# We resolve relative paths against this script's directory, NOT against $HOME,
# so a shell with a nested HOME (e.g. /home/ubuntu/.hermes/profiles/fred/home)
# still writes to the canonical hermes profile root.
_SCRIPT_DIR = Path(__file__).resolve().parent
_HERMES_ROOT = _SCRIPT_DIR.parent.parent.parent.parent.parent.parent  # 7 levels up to /home/ubuntu/.hermes

DEFAULT_HOT_PATH = str(_HERMES_ROOT / "profiles" / "<profile>" / "state" / "current.json")
DEFAULT_ARCHIVE_DIR = str(_HERMES_ROOT / "profiles" / "<profile>" / "state" / "archive" / "")


# ----------------------------- helpers ---------------------------------------

def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _expand(path: str) -> Path:
    """Expand ~ and environment vars; preserve absolute paths verbatim."""
    p = Path(os.path.expandvars(os.path.expanduser(path)))
    return p


def _resolve_profile_path(template: Optional[str], profile: str, default_template: Optional[str] = None) -> Path:
    """Resolve a template path. If template is None, use default_template (or fall back to DEFAULT_HOT_PATH)."""
    if template is None:
        template = default_template if default_template is not None else DEFAULT_HOT_PATH
    return _expand(template.replace("<profile>", profile))


def _load(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return None


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="handoff-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _validate_minimum(payload: dict[str, Any]) -> list[str]:
    """Lightweight contract check that does not require jsonschema."""
    problems: list[str] = []
    required_top = ["schema_version", "agent", "agent_profile", "written_at_utc", "session_id", "current_state"]
    for k in required_top:
        if k not in payload:
            problems.append(f"missing top-level field: {k}")
    if payload.get("schema_version") != SCHEMA_VERSION:
        problems.append(f"schema_version must be {SCHEMA_VERSION}, got {payload.get('schema_version')!r}")
    cs = payload.get("current_state") or {}
    if not cs.get("one_line"):
        problems.append("current_state.one_line is empty")
    energy = cs.get("energy_phase")
    allowed_energy = {"fresh", "in_sprint", "post_sprint_crash", "recovery", "idle", "blocked_on_human"}
    if energy not in allowed_energy:
        problems.append(f"current_state.energy_phase {energy!r} not in {sorted(allowed_energy)}")
    return problems


# ----------------------------- subcommands -----------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    hot = _resolve_profile_path(args.path, args.profile)
    hot.parent.mkdir(parents=True, exist_ok=True)
    archive = _resolve_profile_path(args.archive, args.profile, default_template=DEFAULT_ARCHIVE_DIR)
    archive.mkdir(parents=True, exist_ok=True)
    if hot.exists() and not args.force:
        print(f"handoff already exists at {hot}; use --force to overwrite")
        return 0
    seed = {
        "schema_version": SCHEMA_VERSION,
        "agent": args.agent,
        "agent_profile": args.profile,
        "session_id": "init",
        "written_at_utc": _now_utc(),
        "written_by": "manual_recovery",
        "current_state": {
            "one_line": f"{args.agent} ready. No prior handoff loaded.",
            "energy_phase": "fresh",
        },
        "executed_since_last_handoff": [],
        "in_flight": [],
        "pending_decisions_for_human": [],
        "next_action": {
            "title": "Wait for first user message from Michael."
        },
        "links_to_truth": {},
        "verification": {
            "verifier_result": "not_run",
            "scope": "ad_hoc_targeted",
        },
        "notes_for_next_self": [],
        "do_not_repeat": [],
    }
    _atomic_write(hot, seed)
    print(f"wrote seed handoff -> {hot}")
    return 0


def cmd_write(args: argparse.Namespace) -> int:
    hot = _resolve_profile_path(args.path, args.profile)
    archive = _resolve_profile_path(args.archive, args.profile, default_template=DEFAULT_ARCHIVE_DIR)

    payload_raw = sys.stdin.read() if args.from_stdin else args.json
    if not payload_raw or not payload_raw.strip():
        print("no payload supplied (use --from-stdin or --json)", file=sys.stderr)
        return 2
    try:
        payload = json.loads(payload_raw)
    except json.JSONDecodeError as e:
        print(f"invalid JSON: {e}", file=sys.stderr)
        return 2

    if not isinstance(payload, dict):
        print("payload must be a JSON object", file=sys.stderr)
        return 2

    payload.setdefault("schema_version", SCHEMA_VERSION)
    now = _now_utc()
    payload["written_at_utc"] = now
    payload.setdefault("written_by", "agent_turn" if args.from_stdin else "manual_recovery")
    # Stamp ts_utc on each executed entry so the daily_briefing filter can
    # distinguish "moved since last run" from older moved items.
    for entry in payload.get("executed_since_last_handoff", []) or []:
        if isinstance(entry, dict) and "ts_utc" not in entry:
            entry["ts_utc"] = now
    if args.agent:
        payload["agent"] = args.agent
    if args.profile:
        payload["agent_profile"] = args.profile
    if args.session_id:
        payload["session_id"] = args.session_id

    if args.patch:
        existing = _load(hot) or {}
        existing.update(payload)
        payload = existing

    problems = _validate_minimum(payload)
    if problems and not args.allow_minimum_fail:
        print("handoff contract errors:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        return 3

    if hot.exists():
        if archive is None:
            archive = _resolve_profile_path(None, args.profile)
        archive.mkdir(parents=True, exist_ok=True)
        prev = _load(hot) or {}
        prev_written = prev.get("written_at_utc", "unknown").replace(":", "-")
        prev_agent = prev.get("agent", "agent")
        target = archive / f"{prev_agent}-{prev_written}.json"
        try:
            shutil.copy2(hot, target)
            payload["previous_handoff"] = str(target)
        except OSError as e:
            print(f"warn: could not archive previous handoff: {e}", file=sys.stderr)

    _atomic_write(hot, payload)
    print(f"wrote handoff -> {hot}")
    if problems:
        print("warn: wrote with contract problems (allowed):", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
    return 0


def cmd_read(args: argparse.Namespace) -> int:
    hot = _resolve_profile_path(args.path, args.profile)
    data = _load(hot)
    if data is None:
        print(f"no handoff at {hot}", file=sys.stderr)
        return 1
    if args.one_line:
        print(data.get("current_state", {}).get("one_line", ""))
        return 0
    if args.next_action:
        na = data.get("next_action") or {}
        print(na.get("title", ""))
        return 0
    print(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


def cmd_clear(args: argparse.Namespace) -> int:
    hot = _resolve_profile_path(args.path, args.profile)
    if hot.exists():
        hot.unlink()
    print(f"removed {hot}")
    return 0


# ----------------------------- entrypoint ------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="handoff.py",
        description="Hermes session-state handoff primitive.",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    s_init = sub.add_parser("init", help="Seed an empty handoff file if absent")
    s_init.add_argument("--force", action="store_true", help="Overwrite an existing handoff")
    s_init.set_defaults(func=cmd_init)

    s_write = sub.add_parser("write", help="Write or patch the handoff (stdin JSON recommended)")
    src = s_write.add_mutually_exclusive_group(required=True)
    src.add_argument("--from-stdin", action="store_true", help="Read JSON payload from stdin")
    src.add_argument("--json", help="Inline JSON payload string")
    s_write.add_argument("--profile", default=None, help="Hermes profile name")
    s_write.add_argument("--agent", default=None, help="Short agent id")
    s_write.add_argument("--path", default=None, help="Override hot handoff path")
    s_write.add_argument("--archive", default=None, help="Override archive dir")
    s_write.add_argument("--session-id", default=None, help="Hermes session id that produced the write")
    s_write.add_argument("--patch", action="store_true", help="Merge into existing file instead of replacing")
    s_write.add_argument("--allow-minimum-fail", action="store_true", help="Write even if contract check fails")
    s_write.set_defaults(func=cmd_write)

    s_read = sub.add_parser("read", help="Read the handoff")
    s_read.add_argument("--profile", default=None, help="Hermes profile name")
    s_read.add_argument("--path", default=None, help="Override hot handoff path")
    s_read.add_argument("--one-line", action="store_true", help="Print only current_state.one_line")
    s_read.add_argument("--next-action", action="store_true", help="Print only next_action.title")
    s_read.set_defaults(func=cmd_read)

    s_clear = sub.add_parser("clear", help="Remove the hot handoff (keeps archive)")
    s_clear.add_argument("--profile", default=None, help="Hermes profile name")
    s_clear.add_argument("--path", default=None, help="Override hot handoff path")
    s_clear.set_defaults(func=cmd_clear)

    return p


def _resolve_globals(argv: list[str]) -> tuple[argparse.Namespace, list[str]]:
    """Pull --profile/--agent/--path/--archive from anywhere in argv and strip them
    before they reach the subparser (which only knows its own args)."""
    out = argparse.Namespace(profile="orchestrator", agent=None, path=None, archive=None)
    cleaned: list[str] = []
    i = 0
    while i < len(argv):
        tok = argv[i]
        if tok == "--profile" and i + 1 < len(argv):
            out.profile = argv[i + 1]; i += 2; continue
        if tok == "--agent" and i + 1 < len(argv):
            out.agent = argv[i + 1]; i += 2; continue
        if tok == "--path" and i + 1 < len(argv):
            out.path = argv[i + 1]; i += 2; continue
        if tok == "--archive" and i + 1 < len(argv):
            out.archive = argv[i + 1]; i += 2; continue
        cleaned.append(argv[i]); i += 1
    return out, cleaned


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    globals_ns, argv = _resolve_globals(argv)

    parser = build_parser()
    args = parser.parse_args(argv)
    args.profile = globals_ns.profile
    if globals_ns.agent is not None:
        args.agent = globals_ns.agent
    if globals_ns.path is not None:
        args.path = globals_ns.path
    if globals_ns.archive is not None:
        args.archive = globals_ns.archive
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
