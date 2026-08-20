---
type: Reference
title: "Adoption-loop bug recovery — what not to do when installing canonical skills into a profile"
description: "Worked example of the 2026-07-27 incident where adopt_shared_skills.py clobbered its own canonical source. Captures the bug class, the recovery procedure, and the hardened guards that prevent recurrence. Read before writing or modifying any 'install X everywhere' script."
tags: [reference, adoption, symlink-loop, canonical-source, recovery, guard]
timestamp: 2026-07-29T03:45:00Z
last_verified: 2026-07-29
verified_by: fred
status: incident-report
---

# Adoption-loop bug recovery — 2026-07-27

## What happened

The session was asked to "make sure all the current agents and all future agents get these skills." I built `_adopt_shared_skills.py` and ran it with `--all-running` to install the canonical `session-state-handoff` and `proactive-execution-discipline` skills onto every running Hermes profile via symlinks to the orchestrator source.

The adopter's `discover_running_profiles()` correctly enumerated 7 profiles. The loop installed symlinks on 5 of them. But then the loop **also tried to adopt into the orchestrator profile** — which is the canonical source. The code did:

```python
os.symlink(src, dst)   # dst = orchestrator/skills/agent-operations/session-state-handoff
                          # src = orchestrator/skills/agent-operations/session-state-handoff
```

`os.symlink` doesn't check whether `dst` is inside `src`. The result: a symlink at `orchestrator/skills/agent-operations/session-state-handoff` that points to itself. Every subsequent `readlink` or `ls` of that path triggers a symlink loop, and every other profile's symlink (which pointed at the now-self-referencing source) became a broken target.

**The canonical source was destroyed from the perspective of every other profile's symlink, even though the file content was still technically there.** I had to rebuild both skills from conversation memory.

## Why this happened (root cause)

Three things went wrong simultaneously:

1. **The adopter did not exclude the source profile from the target list.** `discover_running_profiles()` returned all running profiles, including orchestrator. The loop iterated over all of them.
2. **The adopter had no guard against replacing a non-empty directory with a symlink.** A non-empty target directory is usually a sign that someone has real content there; replacing it with a symlink is destructive.
3. **I didn't run `--dry-run` first on a fresh setup.** The dry-run was added later as a hard requirement, but the original `adopt --all-running` ran real install immediately.

## The recovery (what I did)

1. **Stopped and told Michael honestly.** Surfaced the bug, the blast radius (every profile), and the recovery options. **Did not silently attempt a fix that could make it worse.**
2. **Asked for permission to rebuild.** "Do you want me to (1) rebuild ... or (2) stop and let you review?"
3. **Rebuilt from conversation memory.** I had the full text of every `write_file` call I made during the session. The rebuild wasn't perfect (a few bugs re-emerged: argparse parents re-defaulting user flags; `_dt.datetime.timezone.utc` typo) but each was caught in re-verification.
4. **Hardened the adopter.** Three hard guards added:
   - **Refuses to adopt into the source profile.** `if profile == SOURCE_PROFILE: skip with reason "is the source profile; cannot adopt into itself"`. The default for `--all-running` excludes orchestrator.
   - **Refuses to clobber a non-empty directory with a symlink.** `if dst.exists() and not dst.is_symlink() and any(dst.iterdir()): error unless --force`. A backup is taken first when `--force` is used.
   - **Dry-run is the default for any non-trivial change.** `--dry-run` is the documented "try this first" path for every subcommand.

## The five durable lessons (for any future-skill-writer)

1. **An "install X everywhere" script must exclude its own source.** A canonical source is **never** a valid target for its own install. Bake this into the loop, not into a runtime check.
2. **An installer must refuse to replace a real (non-symlink) directory with a symlink unless `--force` is passed.** Real content is a signal. Take a backup first.
3. **Dry-run is the default, not an opt-in.** First time a script runs against a real filesystem, it should print a plan, not mutate. The mutation is the second run.
4. **If an install fails, the post-mortem question is "what guard was missing?" not "what was the user's input?"** The script's job is to defend against bad input, not to trust the input.
5. **Recovery from a real bug requires honest reporting and explicit permission, not silent rebuilding.** If I had rebuilt without asking, I would have hidden the bug from the only person who needed to know about it.

## Cross-references

- `~/.hermes/profiles/orchestrator/state/pins/PIN-2026-07-27-SESSION-COMPLETE-MOVING-TO-GAP-2.md` — the session's pin trail
- `okf/reports/2026-07-27-agent-harness-discipline-session.md` — full session report
- `~/.hermes/profiles/orchestrator/skills/agent-operations/_adopt_shared_skills.py` — the canonical adopter with the three hard guards

## Verification

Run `python3 _adopt_shared_skills.py --profile orchestrator --dry-run`. The expected output: `status: skipped, reason: "orchestrator is the source profile; cannot adopt into itself"`. If the adopter accepts orchestrator as a target, the guard has regressed — fix it before any further adoption runs.
