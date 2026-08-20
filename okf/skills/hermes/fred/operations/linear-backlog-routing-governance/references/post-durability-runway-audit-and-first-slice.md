# Post-Durability Runway Audit Pattern

Use this after a production durability/live-route repair is accepted and Michael asks to resume Prismatic Engine work.

## Trigger

- Accepted markers such as `PRODUCTION_WORKTREE_DURABILITY_OK`, `WORKSPACE_TREE_PRODUCTION_OK`, or `PRODUCTION_RUNTIME_WORKSPACE_TREE_REPAIR_OK`.
- User says not to resume from memory, not to bulk-dispatch, and not to skip production fallout checks.

## Required sequence

1. **Reconfirm fallout first**
   - Run live `systemctl show` and `systemctl cat` for the gateway.
   - Verify `WorkingDirectory` points at the durable runtime checkout and not the mutable dev checkout.
   - Verify runtime checkout branch/head/clean state.
   - Hit local `/workspace-tree`, safe preview, and traversal block routes.
   - Redact saved `systemctl cat` artifacts because unit files may include secret environment lines.
   - If fallout fails, stop; do not start backlog work.

2. **Audit live repo/GitHub/Linear state**
   - Fetch/prune the dev checkout.
   - Read branch, HEAD, clean/dirty/ahead state, open PRs, and current open Linear queue.
   - Do not rely on session memory for issue status.
   - If the dev checkout has local WIP auto-checkpoint commits on `main`, it is not safe to branch from.

3. **Park WIP before starting a task**
   - Create a backup branch pointing at the current `main` HEAD.
   - Reset dev `main` hard to `origin/main` only after preserving the WIP branch.
   - Do not delete worktrees/branches during this runway slice.

4. **Select, then start only one narrow slice**
   - If production fallout is clear, select from the next runway category rather than generic backlog noise.
   - Prefer scorecard/rubric baseline → closure/handoff protocol → cohesive app surface → public/portable readiness → plugin lifecycle/governance → assigned-agent recovery.
   - Use live Linear evidence and PR state to justify the 1–3 recommended tasks.
   - Start only the first task from a clean `feature/fred-...` branch.

5. **Verify and write back**
   - For docs-only slices, use `/tmp/hermes-verify-*` with exact `changed_paths_checked`, required headings/markers, secret-pattern scan, and `git diff --check`.
   - Use branch names accepted by the lane hook; Fred branches must use `feature/`, not `docs/`.
   - Write PR URL, commit SHA, verification command/output, and non-claim boundary back to Linear.

## Pitfalls captured

- Do not let a passed production proof become permission to skip a fresh fallout check.
- Do not start from a local `main` that is ahead of `origin/main`; park it first.
- Do not classify generic gateway/security tasks as the next production-fallout task if the fallout gate is clean; move to the next runway priority.
- Do not bulk-dispatch large AGY/Fred queues after an audit. The audit selects the next task sequence; it does not launch it.
- Do not use `docs/fred-...` branches in Prismatic Engine; the hook expects Fred work on `feature/`.

## Minimal markers

```text
POST_DURABILITY_FALLOUT_CLOSED_OK
LIVE_PRISMATIC_RUNWAY_AUDIT_OK
NEXT_FRED_TASK_SEQUENCE_SELECTED_OK
NEXT_FRED_TASK_BRANCH_SCOPE_OK
NEXT_FRED_TASK_SLICE_IMPLEMENTED_OK
NEXT_FRED_TASK_PR_READY_OK
PRISMATIC_POST_DURABILITY_RUNWAY_EXECUTED_OK
```
