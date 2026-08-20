# Dirty checkpoint recovery contract after interrupted cap-1 producer

Use when an admitted cap-1 producer terminates before creating a descendant commit / `RESULT.md`, but leaves an allowlisted dirty worktree that may contain coherent repair work.

## Trigger

- Producer is terminal (`failed` / `review_pending`, exit evidence reconciled).
- `RESULT.md` absent or no committed descendant exists.
- Worktree has uncommitted tracked changes in a bounded allowlist.
- Michael asks to keep working, but no explicit new event/producer authorization has been given.

## Required sequence

1. **Close the previous producer first**
   - Prove terminal status from harness/process artifacts.
   - Prove cleanup/survivors/active-slot state.
   - Preserve failed-producer truth; do not convert terminal failure into success.

2. **Refresh current authority before designing recovery**
   - Read current Linear metadata, description, and relations read-only.
   - Record state, updated-at, parent, blockers/blocked issues, and export hash.
   - Do not write Linear as part of recovery-contract preparation.

3. **Bind the dirty checkpoint exactly**
   - Record HEAD, tree, parent, tracked diff hash, dirty path allowlist, and per-file blob identities.
   - Include metadata boundaries: `.prismatic-task/` and `STARTED.md` are not implementation commit material.
   - If any identity later drifts, classify `BLOCKED_CHECKPOINT_DRIFT` and stop.

4. **Reproduce from a clean archive, not the dirty worktree**
   - Create a fresh `.git`-free archive of the exact committed blocked head.
   - Apply only the preserved dirty diff.
   - Prove byte equality for every allowlisted implementation file before testing.

5. **Classify verification honestly**
   - Run compile, Ruff check, Ruff format, and focused tests.
   - Run canonical `tests/` for both blocked head and dirty repair archive.
   - Compare failed-test identities, not only counts.
   - If failures are identical and dirty repair has no repair-only regressions, report `BLOCKED_CANONICAL_BASELINE_NO_REPAIR_REGRESSIONS`; never claim canonical green.

6. **Freeze a no-authority recovery contract**
   - Reserve a future task ID only conceptually and keep event count at zero.
   - State that the artifact grants no source edit, commit, task copy, POST, consumer invocation, producer launch, PR, merge, deploy, cron/timer, DB, or Linear write.
   - Require future separately authorized recovery to verify checkpoint identity first, avoid reset/clean/stash/rebase/merge/amend, stay within allowlisted paths, create exactly one normal descendant commit, write bound `RESULT.md`, reproduce the candidate archive, and require fresh exact-head review.

## Report shape

```text
COMMAND=<authority read + dirty archive reproduction + canonical baseline comparison + contract freeze>
RESULT=PARTIAL
LOG=/tmp/hermes-verify-<slice>.log
SCOPE=<issue/task>
AD_HOC_OR_CANONICAL=ad-hoc targeted plus canonical baseline classification
NOT_CLAIMING=contract acceptance, task copies, event, producer, source edit, commit, candidate acceptance, canonical green, PR, merge, deployment/restart, cron/timer mutation, production DB mutation, or Linear write
MARKER=<DIRTY_RECOVERY_CONTRACT_REVIEW_PENDING>
```

## Pitfalls

- Do not dispatch exact-head review when no descendant commit exists; review the frozen recovery contract instead.
- Do not let focused green erase producer failure or absent `RESULT.md`.
- Do not use stale Linear/task topology when preparing a new recovery contract.
- Do not reset, clean, stash, or rewrite a dirty checkpoint to make reproduction easier; externalize reproduction in a disposable archive.
- Do not treat a reserved future task ID as admission authority.
