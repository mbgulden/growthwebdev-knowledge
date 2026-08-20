# Adoption pitfalls — lessons from the 2026-07-29 self-referencing-symlink bug

The skill ships `_adopt_shared_skills.py` which installs the canonical skills into every running profile's `skills/agent-operations/` directory via symlinks. This reference captures the failure modes that bit us on 2026-07-29 and the hard guards that prevent recurrence. Future-self (or any agent adopting the same pattern for a different "install X everywhere" script) should read this before writing or auditing such a script.

## The bug that cost the session 2026-07-29

The first adoption loop included the source profile (`orchestrator`) in the target list. The sequence:

1. Loop enumerates running profiles, including orchestrator.
2. For `orchestrator`:
   - Loop reads the canonical directory: `skills/agent-operations/session-state-handoff/` (real, with SKILL.md).
   - Loop sees a "non-empty target" at `skills/agent-operations/session-state-handoff/`.
   - Without a guard, the loop removes the canonical directory and replaces it with `os.symlink(<self>, <self>)` — a self-referencing symlink.
3. For all other profiles:
   - Loop tries to symlink at `skills/agent-operations/session-state-handoff -> /home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff`.
   - The target now resolves to a self-referencing symlink, which is itself broken.
4. Result: both the canonical source AND all 6 adoption symlinks are broken. Pins, OKF docs, and the skill's own example payloads all point at paths that no longer exist.

**Recovery took the rest of the session:** rebuild both skills from the conversation transcript, harden the script, re-adopt with the hardened script, verify 7/7.

## Hard guards (current implementation)

The hardened script has four guards. All four are non-negotiable. Patching any of them is a regression.

### Guard 1 — Exclude the source profile

```python
SOURCE_PROFILE = "orchestrator"

def discover_running_profiles() -> list[str]:
    r = subprocess.run(["hermes", "profile", "list"], ...)
    out = []
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 3 and parts[2] == "running":
            name = parts[0].lstrip("◆").strip()
            if not name or name == SOURCE_PROFILE:
                continue
            if name not in out:
                out.append(name)
    return out
```

The source profile is excluded from the running-profiles discovery, AND from any `--profile` argument. There's no "I know the source is in the list, but treat it specially" exception. The source is never a target.

### Guard 2 — Refuse non-empty directories without `--force`

```python
if dst.exists() and not dst.is_symlink() and any(dst.iterdir()):
    if not force:
        errors.append({
            "skill": skill_name,
            "reason": f"target {dst} is a non-empty directory; refusing to clobber. ..."
        })
        continue
```

**This guard fires BEFORE the dry-run short-circuit.** A first version of the script had the dry-run check first, which made dry-run lie about safety (it would report "ok" for non-empty targets that real install would refuse). The order matters.

### Guard 3 — Backup before replace

```python
def _backup_target(profile: str, skill_name: str, dst: Path) -> Path | None:
    if not dst.exists():
        return None
    if dst.is_symlink():
        return None
    backup_root = Path(f"/home/ubuntu/.hermes/profiles/{profile}/state/adopt-backups")
    backup_root.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = backup_root / f"{skill_name}-{ts}"
    if dst.is_dir():
        shutil.copytree(str(dst), str(backup_path), dirs_exist_ok=False)
    else:
        shutil.copy2(str(dst), str(backup_path))
    return backup_path
```

Backups go to `state/adopt-backups/<profile>/<skill>-<timestamp>/`. The timestamp is UTC. The backup is a copy (not a symlink, not a hardlink) so it survives even if the symlink replacement misbehaves.

### Guard 4 — Source-still-exists check

```python
if not (src / "SKILL.md").exists():
    errors.append({"skill": skill_name, "reason": "source disappeared between check and install"})
    continue
```

This is a TOCTOU defense: between the time we checked the source and the time we made the symlink, the source could have been removed (by another process, by a parallel adoption, by anything). If it's gone, we abort rather than create a broken symlink.

## The adopter is not hermetic — that's a limitation

The script's target path is hardcoded:

```python
def _state_path(profile: str, override_path: Optional[str] = None) -> Path:
    if override_path:
        return Path(override_path)
    return Path(f"/home/ubuntu/.hermes/profiles/{profile}/state/proactive-count.json")
```

Wait, that's the counter. The adopter's target base is hardcoded at `Path(f"/home/ubuntu/.hermes/profiles/{profile}/skills/agent-operations/")`. **It does NOT respect HERMES_HOME for the target path.** That means:

- You cannot adopt into a profile on a host with a non-default HERMES_HOME.
- A test that tries to use `--state-path /tmp/foo` for the target will fail because the target is computed at a fixed absolute path.

This is a real limitation. **The fix is a follow-up:** parameterize the target base the same way the source is parameterized. Until that lands, the script can only adopt into profiles whose root is at the canonical `/home/ubuntu/.hermes/profiles/<name>/` path. If your test needs a hermetic target, use a real profile name (not a tmp path) and clean up after.

## Testing the adopter

The verifier recipe that exercises every guard is at the bottom of `cold-start-integration.md`. The high-level steps:

1. **Compile check** — `python3 -m py_compile _adopt_shared_skills.py` exits 0.
2. **Source-profile skip** — `adopt_shared_skills.py --profile orchestrator --dry-run` returns a result with `status: "skipped"` and `reason: "...source profile..."`.
3. **Non-empty-dir refusal** — create a real profile directory (NOT a tmpdir — the script doesn't honor HERMES_HOME for the target), populate with `SKILL.md`, run `--dry-run`, confirm `errors` contains 2 entries (one per skill) with `"refusing to clobber"`, and confirm the pre-existing `SKILL.md` content is unchanged.
4. **Visibility check** — after a real install, `hermes skills list --profile <name>` shows both skills.

Step 3 is the one that bit us: a tmpdir-based test passed silently because the script's target path is at the canonical location, not at the tmpdir. **Always use a real profile name for adopter tests.** Clean up the test profile afterward with `shutil.rmtree`.

## Pin a still-open item

The adopter doesn't respect `HERMES_HOME` for the target path. Pin as a follow-up so future-self knows to either (a) fix the script to parameterize the target, or (b) document the limitation in the script's docstring.
