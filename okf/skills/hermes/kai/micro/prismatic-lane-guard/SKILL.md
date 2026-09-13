---
name: prismatic-lane-guard
description: Use when a push is blocked by the Prismatic lane guard.
version: 1
author: kai
license: MIT
metadata:
  hermes:
    tags: [prismatic, git-hooks, governance, lanes, okf]
    related_skills: [okf-mcp-hub, active-oahu-operations]
---

# Prismatic Lane Guard (pre-push)

## When to Use
- A `git push` in a Prismatic-managed repo fails with a guard/lane error (or fails
  silently and a branch is found stuck unpushed).
- You are about to change per-agent lane ownership in `PRISMATIC_ENGINE.yaml`.
- An auto-regen or bulk commit is sitting unpushed and you need to find out why.
- A user questions whether the lane mechanism is still in use — verify enforcement
  before answering.

Prismatic-managed repos carry a git `pre-push` guard that validates every pushed path
against per-agent lane ownership in `PRISMATIC_ENGINE.yaml`. A block here is policy
enforcement, not a git permission error — the push error may not name the real cause,
so diagnose before guessing. Class of task: diagnosing guard blocks, unit-testing
lane logic, and landing access fixes through governance.

## Mechanism
- Hook: `.git/hooks/pre-push` (real, not a `*.sample`) delegating to a backing
  script at the repo root (e.g. `scripts/prismatic-pre-push-hook.py`).
- Config: `PRISMATIC_ENGINE.yaml` at the repo ROOT — note: outside every content lane
  (this causes the bootstrap self-block, see Pitfalls).
- Lanes: per-agent owner entries; path matching is by **prefix/derivation**, not
  literal string.
- Dual-repo: each managed repo (e.g. the OKF knowledge hub and the AOT mirror) has
  its **own independent** yaml + hook. Census both before claiming a governance fix
  is complete — and verify each repo actually contains the blocked path before
  touching its config (a repo without the path needs no change).

## Diagnostic workflow
1. Confirm the hook is installed: `ls .git/hooks/ | grep -v sample`; also check
   `git config core.hooksPath`.
2. Find the backing script: `grep -rl PRISMATIC_ENGINE --include=*.py .`
3. Read lanes for **all** agents by parsing the yaml with PyYAML — do not grep for
   path literals (see Pitfall 1).
4. Unit-test the hook's own functions against the real config before changing
   anything — import the hyphenated file via `importlib.util.spec_from_file_location`
   and resolve the blocked path for each agent. This is the only way to get a
   deterministic BLOCK/ALLOW verdict (recipe in
   `references/gro-4988-investigation-2026-09-13.md`).
5. Corroborate with historical evidence: blocked auto-regen commits, PR addenda,
   `.prismatic/locks.json` / `.antigravity/swarm_locks.json`.
6. Check the bootstrap self-block (Pitfall 3) **before** proposing a fix — it
   determines who is even allowed to land the fix.

## Pitfalls
1. **Literal grep false negative.** `grep "okf/skills" PRISMATIC_ENGINE.yaml` can
   return exit 1 even when a lane matches, because matching is
   prefix/derivation-based. A grep miss is not evidence a lane is absent — parse the
   yaml and test with the hook's own resolution functions.
2. **Two configs, two repos.** Fixing only one repo's yaml leaves the other still
   blocking. Both must be censused; report which needed changes and which did not.
3. **Bootstrap self-block.** The config file sits at repo root, outside every
   agent's lane — the agent who needs the fix may be unable to push the fix.
   Verify `agent → config-file` resolution before claiming a fix is shippable.
   Resolution paths: (a) add a config-file exception in the hook (config editable by
   any registered agent; merging to main stays manual via PR), (b) route the fix
   through the governance merge path (e.g. Fred merges `content/*` branches per the
   commit-authorization decision doc), or (c) if the user wants lanes removed, do it
   as a **formal deprecation decision** (strip the lane check, keep main-block and
   lock checks) — never a silent config edit.
4. **Hyphenated script name.** `prismatic-pre-push-hook.py` cannot be imported
   normally — use `importlib.util.spec_from_file_location`.
5. **Truncated tool output.** If terminal/execute_code results collapse to
   placeholders ("1 lines output"), stop retrying the same call: write results to
   `/tmp` files and read them back in slices, or print explicit char-limited slices
   from execute_code.
6. **Don't assume a mechanism is gone.** A user may believe a mechanism was
   deprecated ("I thought we got rid of it"). Verify enforcement state first, then
   answer with evidence rather than agreeing or refuting from memory.

## Fix pattern (lane grant) — plan, verify, then claim
1. Branch from `origin/main` as `content/kai-<topic>-YYYYMMDD`.
2. Add the path to the target agent's owner lanes in the yaml, with a header note
   citing the decision/approval that authorizes the change.
3. If the fix file itself is blocked (bootstrap self-block), implement the
   config-file exception in the hook in the same PR and unit-test both behaviors.
4. Commit with a real Linear issue ref (`[Kai] <summary> (#GRO-NNNN)`).
5. Push a PR; the governance merge authority (Fred, for `content/`) merges.
6. **Only after the yaml is on main**: rebase and push any blocked auto-regen
   branches — the regen branch must contain the fixed yaml for its own push to pass.
   Ordering matters; pushing the regen first fails again.

## Verification gates
- importlib unit test: the target path's resolution for the affected agent must flip
  BLOCK → ALLOW against the real edited config.
- Post-merge: an actual test push of a `content/kai-*` branch touching the granted
  path. Do not report the lane fix as complete until a real push succeeds.

## References
- `references/gro-4988-investigation-2026-09-13.md` — full GRO-4988 investigation:
  verified mechanism, importlib unit-test recipe, blocked auto-regen details,
  bootstrap self-block evidence, governance docs, and what was done vs still open.
