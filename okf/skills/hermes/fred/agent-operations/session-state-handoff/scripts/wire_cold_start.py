#!/usr/bin/env python3
"""
Hermes Session Handoff — cold-start wiring (Pattern A).

Generates a per-profile `prefill_messages_file` JSON whose contents are derived
from the active handoff, then points the profile's config.yaml at that file.

Why this exists:
- Pattern A (per-profile config) is the provider-agnostic-enough cold-start hook
  on Hermes versions where plugin hooks are documented but not invoked (#2817).
- `prefill_messages_file` is the only supported mechanism that runs on every
  LLM call without depending on a custom plugin path.

Idempotent. Safe to re-run after any handoff write.

Usage:
    python3 wire_cold_start.py wire --profile kai
    python3 wire_cold_start.py wire --all
    python3 wire_cold_start.py status --profile kai
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any, Optional


HAND = "/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff/scripts/handoff.py"
SOURCE_PROFILE = "orchestrator"

# First-reply requirement: makes the cold-start greeting include handoff fields
# (one_line, next_action, in_flight, pending_decisions) instead of just acknowledging.
# (2026-07-27 finding: gentle wording is required; MANDATORY backfires.)
FIRST_REPLY_REQUIREMENT = (
    " FIRST-REPLY REQUIREMENT: surface current_state.one_line, next_action.title, "
    "every entry in in_flight[], and every question in pending_decisions_for_human[] "
    "before anything else. The session handoff is THIS file (state/current.json); "
    "do not confuse it with project-registry.json or any other source."
)


def _now_utc() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _prefill_path(profile: str) -> Path:
    return Path(f"/home/ubuntu/.hermes/profiles/{profile}/state/prefill_messages.json")


def _config_path(profile: str) -> Path:
    return Path(f"/home/ubuntu/.hermes/profiles/{profile}/config.yaml")


def _handoff_one_line(profile: str) -> tuple[str, dict[str, Any] | None]:
    r = subprocess.run(
        ["python3", HAND, "read", "--profile", profile],
        capture_output=True, text=True, timeout=10,
    )
    if r.returncode != 0:
        return "", None
    try:
        data = json.loads(r.stdout)
    except json.JSONDecodeError:
        return "", None
    return (data.get("current_state", {}).get("one_line") or ""), data


def _build_prefill_messages(one_line: str, profile: str) -> list[dict[str, str]]:
    if not one_line:
        return []
    return [
        {
            "role": "system",
            "content": (
                f"[session-handoff for profile '{profile}'] "
                f"The previous session left this greeting for the user: \"{one_line}\". "
                "Open the next turn by acknowledging it briefly (one sentence), "
                "then ask for the next instruction. Do not invent context beyond "
                "what is in this handoff."
            ) + FIRST_REPLY_REQUIREMENT,
        },
        {
            "role": "user",
            "content": "(resume from previous session — see system reminder above)",
        },
    ]


def _atomic_write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="prefill-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _read_yaml(path: Path) -> dict[str, Any]:
    import yaml
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _atomic_write_yaml(path: Path, data: dict[str, Any]) -> None:
    import yaml
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix="config-", suffix=".yaml", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, sort_keys=False, allow_unicode=True, default_flow_style=False)
        # back up the original once
        if not Path(str(path) + ".pre-handoff-wiring.bak").exists() and path.exists():
            shutil.copy2(path, str(path) + ".pre-handoff-wiring.bak")
        os.replace(tmp, path)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def wire_profile(profile: str, *, dry_run: bool = False) -> dict[str, Any]:
    one_line, _ = _handoff_one_line(profile)
    prefill = _prefill_path(profile)
    config = _config_path(profile)
    messages = _build_prefill_messages(one_line, profile)

    out: dict[str, Any] = {
        "profile": profile,
        "one_line": one_line,
        "prefill_path": str(prefill),
        "config_path": str(config),
        "messages_count": len(messages),
        "dry_run": dry_run,
    }
    if not one_line:
        out["status"] = "skipped-no-handoff"
        return out
    if not config.exists():
        out["status"] = "skipped-no-config-yaml"
        return out

    if not dry_run:
        _atomic_write_json(prefill, messages)
        cfg = _read_yaml(config)
        cfg["prefill_messages_file"] = str(prefill)
        _atomic_write_yaml(config, cfg)

    out["status"] = "wired"
    out["messages_preview"] = messages[0]["content"][:200] if messages else ""
    return out


def status_profile(profile: str) -> dict[str, Any]:
    prefill = _prefill_path(profile)
    config = _config_path(profile)
    out: dict[str, Any] = {
        "profile": profile,
        "prefill_path": str(prefill),
        "prefill_exists": prefill.exists(),
        "config_path": str(config),
        "config_exists": config.exists(),
    }
    if prefill.exists():
        try:
            data = json.loads(prefill.read_text())
            out["messages_count"] = len(data)
            if data:
                out["first_message_role"] = data[0].get("role")
                out["first_message_preview"] = data[0].get("content", "")[:140]
        except Exception as e:
            out["prefill_parse_error"] = str(e)
    if config.exists():
        cfg = _read_yaml(config)
        out["config_prefill_setting"] = cfg.get("prefill_messages_file", "<missing>")
    return out


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="wire_cold_start.py", description="Wire handoff -> prefill_messages_file (Pattern A).")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_wire = sub.add_parser("wire", help="Generate prefill JSON and update config.yaml for one or all profiles")
    g = s_wire.add_mutually_exclusive_group(required=True)
    g.add_argument("--profile", help="Single profile name (NOT the source profile orchestrator)")
    g.add_argument("--all", action="store_true", help="Wire the default set of profiles")
    g.add_argument("--profiles", nargs="+", help="Explicit list of profile names")
    s_wire.add_argument("--dry-run", action="store_true", help="Compute what would be written without touching files")
    s_wire.set_defaults(func=lambda a: cmd_wire(a))

    s_status = sub.add_parser("status", help="Show current prefill wiring for one or all profiles")
    g2 = s_status.add_mutually_exclusive_group(required=True)
    g2.add_argument("--profile", help="Single profile name")
    g2.add_argument("--all", action="store_true", help="Status the default set of profiles")
    g2.add_argument("--profiles", nargs="+", help="Explicit list of profile names")
    s_status.set_defaults(func=lambda a: cmd_status(a))

    return p


def _resolve_profiles(args: argparse.Namespace) -> list[str]:
    if getattr(args, "all", False):
        # Default: every running profile except the source.
        return _discover_running_excluding_source()
    if getattr(args, "profile", None):
        return [args.profile]
    return list(args.profiles or [])


def _discover_running_excluding_source() -> list[str]:
    r = subprocess.run(["hermes", "profile", "list"], capture_output=True, text=True, timeout=30)
    out = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "running":
            name = parts[0].lstrip("◆").strip()
            if not name or name == SOURCE_PROFILE: continue
            if name not in out: out.append(name)
    return out


def cmd_wire(args: argparse.Namespace) -> int:
    profiles = _resolve_profiles(args)
    results = [wire_profile(p, dry_run=args.dry_run) for p in profiles]
    print(json.dumps({"action": "wire", "results": results}, indent=2, ensure_ascii=False))
    failures = sum(1 for r in results if r.get("status") not in ("wired", "skipped-no-handoff", "skipped-no-config-yaml"))
    return 0 if failures == 0 else 1


def cmd_status(args: argparse.Namespace) -> int:
    profiles = _resolve_profiles(args)
    results = [status_profile(p) for p in profiles]
    print(json.dumps({"action": "status", "results": results}, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
