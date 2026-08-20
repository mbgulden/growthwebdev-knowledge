# PR backlog zero → deploy-fresh promotion handoff

Use this after a PR cleanup / merge-train pass reduces `mbgulden/prismatic-engine` open PRs to zero.

## Trigger

- `gh pr list --state open` returns `[]`.
- Ned scanner returns `EMPTY`.
- `origin/deploy-fresh` still diverges substantially from `origin/main`.

## Pattern

1. Verify the clean state first:
   - `gh pr list --repo mbgulden/prismatic-engine --state open --limit 100 --json ...`
   - `python3 ~/.hermes/profiles/ned/scripts/prismatic/lanes/ned/scan_tasks.py`
   - `node ~/.antigravity/swarm.js status`
2. Check branch divergence:
   - `git rev-list --left-right --count origin/main...origin/deploy-fresh`
3. Do a **dry-run merge only** in a throwaway worktree:
   - `git worktree add -B ned/promote-deploy-fresh-to-main /tmp/ned-promote-deploy-fresh origin/main`
   - `git merge --no-commit --no-ff origin/deploy-fresh || true`
   - collect `git diff --name-only --diff-filter=U`
4. If conflicts cross root metadata, API, tests, gateway, harnesses, or other non-Ned lanes, **do not directly resolve/push** as Ned.
5. Create a Linear handoff for Fred/orchestrator, not AGY, with:
   - conflict file list,
   - divergence counts,
   - dry-run evidence,
   - protected-branch guardrails,
   - success criteria: integration branch + verification + PR into `main`.
6. Remove the throwaway worktree after collecting evidence.
7. Clean up stale `dispatch:ready` labels from completed merge-train issues (`Done` + `dispatch:ready`) so the scanner does not re-trigger old work.

## Ownership rule

This is not a generic AGY task. If AGY already triaged but could not safely complete hands-on conflict resolution, route the branch-promotion handoff to Fred/orchestrator with `agent:needs-human-review`. Do not tag `agent:agy` by default.

## Pitfalls

- Do not push directly to `main` or `deploy-fresh`.
- A zero-PR queue is not the same as fully integrated branches; check `main...deploy-fresh` divergence.
- Dry-run merge conflicts in root/project files are useful evidence, not a mandate for Ned to cross lanes.
- Completed issues can retain `dispatch:ready`; remove it from `Done` issues after merge-train completion.
