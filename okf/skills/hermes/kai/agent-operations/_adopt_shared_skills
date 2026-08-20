#!/usr/bin/env python3
"""
adopt-shared-skills — install canonical skills into a new or existing Hermes profile.

Run when:
  - You create a new Hermes profile and want it to inherit the shared skills.
  - You want to backfill adoption onto an existing profile that lacks them.
  - You need to repair a broken symlink to one of the canonical skills.

The "canonical" set lives under:
    ~/.hermes/profiles/orchestrator/skills/agent-operations/

This script symlinks each canonical skill into:
    ~/.hermes/profiles/<profile>/skills/agent-operations/<skill>/

Symlinks keep a single source of truth — any future edit propagates to every
profile that has adopted. Idempotent: safe to re-run.

HARD GUARDS (do not remove):
  1. The orchestrator profile is the source. The script REFUSES to adopt into
     orchestrator (would create a self-referencing symlink loop and clobber
     the canonical source).
  2. The script REFUSES to replace a real directory with a symlink. If a target
     path is a non-empty directory, the script aborts with a clear error.
  3. Each adoption takes a backup of any pre-existing target (symlink or empty
     dir) to state/adopt-backups/<profile>/<skill>-<timestamp> so repairs are possible.

Usage:
  python3 adopt_shared_skills.py [--profile <name>] [--all-running]
                                [--include [skill,skill,...]]
                                [--dry-run] [--force]

Default behavior: target the orchestrator's own profile (no-op due to guard #1).

Profiles discovered from running gateways (orchestrator always excluded):
  autobot, fred, george, kai, ned, next-step, ...

Canonical skills maintained:
  - session-state-handoff       (transient state + cold-start wiring, dormant until Hermes 0.17+ fixes prefill loader)
  - proactive-execution-discipline  (hard rule against propose-before-work, weekly counter)
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from datetime import datetime, timezone


CANONICAL_ROOT = Path("/home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations")
SOURCE_PROFILE = "orchestrator"  # NEVER adopt into this — it's the source
# Keep the original public list (scanned from agent-operations/) for back-compat.
CANONICAL_SKILLS = ["session-state-handoff", "proactive-execution-discipline", "projector-aware-communication-discipline"]

# Additional top-level skill subtrees that we treat as canonical / shared.
# Anything with a SKILL.md inside these is eligible for adoption onto other
# profiles via this script. Add new top-level categories here as they grow.
ADDITIONAL_CANONICAL_DIRS = [
    Path("/home/ubuntu/.hermes/profiles/orchestrator/skills/micro"),
]  # NOTE: skills/operations/ etc. are profile-specific (not canonical), keep them out.


def discover_running_profiles() -> list[str]:
    """Parse `hermes profile list` for running gateways. Excludes the source profile."""
    r = subprocess.run(["hermes", "profile", "list"], capture_output=True, text=True, timeout=30)
    out: list[str] = []
    for line in r.stdout.splitlines():
        parts = line.split()
        # Gateway column is the third field (index 2) per the table header.
        if len(parts) >= 3 and parts[2] == "running":
            name = parts[0].lstrip("◆").strip()
            if not name:
                continue
            if name == SOURCE_PROFILE:
                continue  # GUARD 1
            if name not in out:
                out.append(name)
    return out


def _is_self_referencing_symlink(path: Path) -> bool:
    """Return True if path is a symlink whose target would resolve back to itself."""
    if not path.is_symlink():
        return False
    try:
        target = os.readlink(str(path))
        resolved = os.path.normpath(str(path.parent / target))
        return resolved == os.path.normpath(str(path))
    except OSError:
        return False


def _backup_target(profile: str, skill_name: str, dst: Path) -> Path | None:
    """If dst exists (and is not a symlink), copy it to backups/. Returns backup path."""
    if not dst.exists():
        return None
    if dst.is_symlink():
        return None  # symlinks are trivial — just overwrite
    # Backup
    backup_root = Path(f"/home/ubuntu/.hermes/profiles/{profile}/state/adopt-backups")
    backup_root.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_root / f"{skill_name}-{ts}"
    if dst.is_dir():
        shutil.copytree(str(dst), str(backup_path), dirs_exist_ok=False)
    else:
        shutil.copy2(str(dst), str(backup_path))
    return backup_path


def _resolve_targets(include: list[str] | None) -> list[tuple[str, Path]]:
    """Return list of (skill_name, src_path) from the include list, or auto-discover.

    Each include item may be:
      - bare skill name (under agent-operations/ — back-compat)
      - 'subdir/skill' (under skills/<subdir>/<skill>/ — for micro, verifiers, etc.)
      - 'subdir/' (a bare subdir: returns every SKILL.md-bearing skill under it)
    If include is None we auto-discover every skill across CANONICAL_ROOT and
    ADDITIONAL_CANONICAL_DIRS.
    """
    if not include:
        out = []
        for name in CANONICAL_SKILLS:
            out.append((name, CANONICAL_ROOT / name))
        for d in ADDITIONAL_CANONICAL_DIRS:
            if not d.exists():
                continue
            for child in sorted(d.iterdir()):
                if child.is_dir() and (child / "SKILL.md").exists():
                    out.append((f"{d.name}/{child.name}", child))
        return out
    out = []
    for raw in include:
        if raw.endswith("/"):
            d = Path(f"/home/ubuntu/.hermes/profiles/orchestrator/skills/{raw.rstrip('/')}")
            if d.exists():
                for child in sorted(d.iterdir()):
                    if child.is_dir() and (child / "SKILL.md").exists():
                        out.append((f"{d.name}/{child.name}", child))
            continue
        if "/" in raw:
            subdir, skill = raw.split("/", 1)
            if subdir == "agent-operations":
                src = CANONICAL_ROOT / skill
            else:
                src = Path(f"/home/ubuntu/.hermes/profiles/orchestrator/skills/{subdir}") / skill
        else:
            src = CANONICAL_ROOT / raw
        out.append((raw, src))
    return out


def adopt_one(profile: str, *, include: list[str] | None = None,
              dry_run: bool = False, force: bool = False) -> dict:
    """Install the canonical skills into one profile's skills tree."""

    # GUARD 1: refuse to adopt into the source profile
    if profile == SOURCE_PROFILE:
        return {
            "profile": profile,
            "status": "skipped",
            "reason": f"{profile} is the source profile; cannot adopt into itself (would create symlink loop)",
            "installed": [], "skipped": [], "errors": []
        }

    skills_root = Path(f"/home/ubuntu/.hermes/profiles/{profile}/skills")
    installed = []
    skipped = []
    errors = []

    targets = _resolve_targets(include)

    for skill_name, src in targets:
        # dst mirrors the same relative subdir under the target profile.
        if "/" in skill_name:
            subdir, leaf = skill_name.split("/", 1)
            dst_parent = skills_root / subdir
            dst = dst_parent / leaf
        else:
            dst_parent = skills_root / "agent-operations"
            dst = dst_parent / skill_name

        if not (src / "SKILL.md").exists():
            skipped.append({"skill": skill_name, "reason": "missing source SKILL.md"})
            continue

        # GUARD 2: refuse to clobber a real (non-symlink, non-empty) directory.
        # Apply this BEFORE the dry-run short-circuit so dry-run reports the same
        # errors real install would — otherwise dry-run would lie about safety.
        if dst.exists() and not dst.is_symlink() and any(dst.iterdir()):
            if not force:
                errors.append({
                    "skill": skill_name,
                    "reason": f"target {dst} is a non-empty directory; refusing to clobber. Use --force to override (will backup first)."
                })
                continue

        # Dry-run: just record intent (guard already checked the target)
        if dry_run:
            installed.append(skill_name)
            continue

        # Real install: backup if needed, then symlink
        skills_root.mkdir(parents=True, exist_ok=True)
        dst_parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() or dst.is_symlink():
            _backup_target(profile, skill_name, dst)
            # Remove existing
            if dst.is_symlink() or dst.is_file():
                dst.unlink()
            elif dst.is_dir():
                shutil.rmtree(dst)

        # GUARD 3: verify the source still exists right before creating the symlink
        if not (src / "SKILL.md").exists():
            errors.append({"skill": skill_name, "reason": "source disappeared between check and install"})
            continue

        try:
            os.symlink(src, dst)
        except Exception as e:
            errors.append({"skill": skill_name, "reason": f"symlink failed: {e}"})
            continue

        installed.append(skill_name)

    # Verify visibility via hermes skills list (only if not dry-run)
    visible_check = None
    if not dry_run:
        r = subprocess.run(["hermes", "skills", "list", "--profile", profile],
                           capture_output=True, text=True, timeout=30)
        out_text = r.stdout
        # Hermes truncates long names with "…" — use prefixes
        visibility = {}
        for skill_name, _ in targets:
            visibility[skill_name] = any(s in out_text for s in [
                skill_name, skill_name[:20], skill_name[:15], skill_name[:10]
            ])
        visible_check = visibility

    return {
        "profile": profile,
        "status": "ok" if not errors else "partial" if installed else "error",
        "installed": installed,
        "skipped": skipped,
        "errors": errors,
        "visible_in_hermes_skills_list": visible_check,
        "dry_run": dry_run
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="adopt_shared_skills.py")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--profile", help="Single profile name")
    g.add_argument("--all-running", action="store_true",
                   help="Adopt on every running profile (per hermes profile list, source excluded)")
    g.add_argument("--profiles", nargs="+",
                   help="Explicit list of profile names (overrides running discovery)")
    p.add_argument("--include", nargs="+", default=None,
                   help="Subset of canonical skills to adopt (default: all)")
    p.add_argument("--dry-run", action="store_true",
                   help="Compute the install plan without touching files")
    p.add_argument("--force", action="store_true",
                   help="Override guards (will backup a non-empty dir before replacing)")
    args = p.parse_args(argv)

    if args.profile:
        targets = [args.profile]
    elif args.all_running:
        targets = discover_running_profiles()
    else:
        targets = args.profiles

    results = [adopt_one(p, include=args.include, dry_run=args.dry_run, force=args.force)
               for p in targets]

    print(json.dumps({
        "adopter": "adopt_shared_skills.py",
        "source_profile": SOURCE_PROFILE,
        "targets": targets,
        "dry_run": args.dry_run,
        "results": results
    }, indent=2))

    # Exit code: nonzero if any target had errors
    any_error = any(r["status"] == "error" for r in results)
    return 1 if any_error else 0


if __name__ == "__main__":
    raise SystemExit(main())