# Cross-Profile Skill Adoption — Symlink Loop Case Study

Session: 2026-07-27, fred profile, session-state-handoff and proactive-execution-discipline adoption.

## What happened

The session was completing a class-level ask: "make sure all the current agents and all future agents get these skills." The implementation plan was correct in principle: pick a canonical source profile, run a single script that symlinks the skill into every other profile's `skills/<category>/` directory. The `prismatic-core-skill-distribution-ops` skill explicitly endorses the agent-neutral discovery layer pattern, and symlinks are how a single source of truth propagates edits everywhere.

The bug was a single missing line in the adoption helper: **the source profile was not excluded from the target list**.

## Exact sequence

The canonical source for both skills was `~/.hermes/profiles/orchestrator/skills/agent-operations/`. That directory contained the real skill files, including `SKILL.md`, `scripts/`, `references/`, and `templates/`.

`hermes profile list` filtered for running gateways returned seven profiles, including the orchestrator. The adoption helper iterated over that list. For each profile, the helper did:

```python
for name, src in SOURCE.items():
    dst = ao / name
    if dst.exists() or dst.is_symlink():
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        else:
            import shutil; shutil.rmtree(dst)
    os.symlink(src, dst)
```

When the helper reached `orchestrator`, the `dst` was the real canonical source directory (not a symlink, not a file). The `else` branch called `shutil.rmtree(dst)`, which succeeded and **deleted the canonical source**.

The next line, `os.symlink(src, dst)`, then created a symlink at `dst` pointing to `src` — which was the path just deleted. The symlink now resolves to itself, producing `Too many levels of symbolic links`. Every other profile's symlink that pointed at this canonical source (george, kai, ned, autobot, next-step — all symlinks installed earlier in the same loop iteration) was now broken.

## Live transcript of detection and recovery

```text
$ cat /home/ubuntu/.hermes/profiles/kai/skills/agent-operations/session-state-handoff/SKILL.md
cat: SKILL.md: Too many levels of symbolic links

$ ls -la /home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/
session-state-handoff -> /home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/session-state-handoff
proactive-execution-discipline -> /home/ubuntu/.hermes/profiles/orchestrator/skills/agent-operations/proactive-execution-discipline
```

The symlinks were pointing at themselves. The canonical source was gone.

## The corrected adoption helper

The right fix is at script construction time, not in a runtime check. The corrected pattern is:

```python
def adopt_one(source_profile: str, target: str, *skills) -> dict:
    """Adopt skills from source_profile into target's skills/<category>/."""
    # Hard-stop if target is the source. Never symlink a profile to itself.
    if target == source_profile:
        return {"target": target, "skipped": True, "reason": "target == source (self-adopt)"}
    src_root = Path(f"/home/ubuntu/.hermes/profiles/{source_profile}/skills/agent-operations")
    dst_root = Path(f"/home/ubuntu/.hermes/profiles/{target}/skills/agent-operations")
    installed = []
    for skill in skills:
        src = src_root / skill
        if not (src / "SKILL.md").exists():
            continue
        dst = dst_root / skill
        # Hard-stop check: never delete a non-symlink directory at dst.
        if dst.is_dir() and not dst.is_symlink():
            raise SystemExit(
                f"refusing to delete non-symlink directory at {dst}; "
                f"if {target} is the source, exclude it from the target list"
            )
        if dst.is_symlink() or dst.is_file():
            dst.unlink()
        dst_root.mkdir(parents=True, exist_ok=True)
        os.symlink(src, dst)
        installed.append(skill)
    return {"target": target, "installed": installed}


def adopt_all_running(source_profile: str, *skills) -> list[dict]:
    targets = discover_running_profiles()  # or your own enumeration
    targets = [t for t in targets if t != source_profile]  # exclude source
    return [adopt_one(source_profile, t, *skills) for t in targets]
```

Two layers of defense:

1. **Construction-time**: the source profile is filtered out of the target list before the loop starts.
2. **Runtime**: every `adopt_one` call checks `dst.is_dir() and not dst.is_symlink()` and raises `SystemExit` rather than deleting.

The runtime check is the load-bearing one. It catches the bug pattern even if a future caller forgets the construction-time filter — e.g. when the helper is called from a different context (CI, ad-hoc shell, another agent).

## Verifier (durable)

Run before any new cross-profile adoption:

```bash
python3 - <<'PY'
import os, subprocess
from pathlib import Path

# 1. Confirm the source is not in the target list.
SOURCE = "orchestrator"
TARGETS = ["autobot", "fred", "george", "kai", "ned", "next-step"]
assert SOURCE not in TARGETS, "SOURCE cannot be in TARGETS"

# 2. For each target, confirm the symlink resolves and is not a loop.
for t in TARGETS:
    ao = Path(f"/home/ubuntu/.hermes/profiles/{t}/skills/agent-operations")
    if not ao.exists():
        print(f"  {t}: NO agent-operations dir (skip)")
        continue
    for skill in ("session-state-handoff", "proactive-execution-discipline"):
        link = ao / skill
        if not link.is_symlink():
            print(f"  {t}/{skill}: not a symlink (FAIL)")
            continue
        target = os.readlink(str(link))
        # Resolve and ensure it exists and is not a loop.
        try:
            resolved = str(link.resolve(strict=True))
            print(f"  {t}/{skill} -> {target} (resolves to {resolved}) OK")
        except (OSError, RuntimeError) as e:
            print(f"  {t}/{skill} -> {target} BROKEN: {e}")
PY
```

Pass criterion: every target's symlink resolves to a real file, no loops.

## Recovery procedure when the bug has already fired

1. **Stop the script immediately.** Don't re-run it hoping the second time works.
2. **Find the loop.** `find ~/.hermes/profiles -type l | xargs -I {} sh -c 'readlink -f {} 2>/dev/null || echo LOOP:{}'` lists broken symlinks.
3. **Do not delete the symlinks blindly.** They are the only references to a source that no longer exists. The right action is to:
   - **Restore the source from authoritative copies.** The 2026-07-27 case used the conversation transcript (the original `write_file` content). In general, the source of last resort is whatever shipped the skill: the conversation, a git repo, a backup, or a hub-installed copy.
   - **Reconstruct the canonical source directory at the source profile's path** with the original files.
   - **Re-run the corrected adoption helper**, with the construction-time filter, the runtime check, AND the verifier.
4. **Run the verifier again after recovery.** Both `hermes skills list --profile <target>` and the filesystem resolve check must pass.
5. **Pin the case study.** The bug + the verifier + the recovery are durable knowledge; they belong in the umbrella skill and in the OKF.

## Why this case study is durable

- The bug pattern is generic: any symlink-based copy script that doesn't exclude its own source from its target list will produce this.
- The failure mode is silent at first — symlinks appear to install correctly, the agent sees "all skills enabled" — and only manifests later when something tries to read through the broken chain. The 2026-07-27 case was caught by a real CLI probe (`hermes skills list`) which had been showing the right number of skills but with truncated names that hid the breakage.
- The fix is two lines (construction-time filter, runtime check) and the verifier is a 15-line script. Both are worth the cost of any future cross-profile adoption.
- The same pattern bites any "distribute a single source to N targets via symlink" workflow, not just skills. Future-self reading this should generalize to: any time you iterate over a set and one of the iterations mutates a source that other iterations reference, explicitly exclude the source from the iteration set.

## Cross-references

- `prismatic-core-skill-distribution-ops` SKILL.md → "Cross-profile skill adoption: the source-profile trap" pitfall
- `hermes-agent` SKILL.md → general profile enumeration and skills-list quirks
- `references/hermes-gateway-stale-bash-spawn.md` → analogous pattern: an out-of-band process holds a lock that prevents the managed service from starting. Different mechanism, same shape (silent until a probe surfaces it).
