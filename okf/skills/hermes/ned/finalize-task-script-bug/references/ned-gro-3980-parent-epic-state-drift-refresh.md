# GRO-3980 parent-epic redispatch: state drift + stale dispatch label

Use this when an already-implemented parent epic is redispatched even though a remote `ned/<issue>` branch, PR, prior finalization comments, and local RESULT evidence already exist.

## Observed pattern

- Linear drifted from `In Review` back to `Backlog` and retained `dispatch:ready`.
- The prior implementation was real: branch `ned/GRO-3980`, PR #29, commit `4ce1c01`, and parent doc existed.
- The shared canonical checkout was dirty/on unrelated work, so touching it would have risked staging another agent's changes.
- The parent epic was intentionally **not Done** because child GRO-3985 remained the final green gate.

## Safe refresh sequence

1. Re-read Linear issue/comments/children first; distinguish real incomplete work from state drift.
2. Inspect PR status/checks. `In Review` plus branch is not enough if the PR has a failing check.
3. Fetch the remote task branch and create a clean detached worktree from it:
   ```bash
   git -C /home/ubuntu/work/hd-platform fetch origin ned/GRO-3980 main --prune
   git -C /home/ubuntu/work/hd-platform worktree add --detach /tmp/hd-platform-gro3980-refresh origin/ned/GRO-3980
   ```
4. Lock/heartbeat only the actual lane file, not the dirty shared checkout.
5. Run fresh focused verification from the clean worktree. For a parent docs/ops snapshot, `npm ci` + `npm run build` is enough when the branch is docs-only; record npm audit warnings separately, not as branch regressions.
6. Run any documented future-refresh probes, but treat absent child outputs honestly. In this case `python3 -m py_compile scripts/operations/*.py` was not applicable because the parent branch had no `scripts/operations/*.py`; that absence is evidence the parent should remain `In Review`, not `Done`.
7. Re-run finalize from the clean worktree with explicit repo and lock scope:
   ```bash
   PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro3980-refresh \
   FINALIZE_LOCK_FILES='docs/operations/hde-operational-consolidation-epic-3980.md' \
   bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-3980 ned/GRO-3980 ned
   ```
8. Re-query Linear. If state is restored but `dispatch:ready` remains, remove only that label by first reading current label IDs and writing back the keep-list. Do not hand-copy label UUIDs from old output; one typo causes `labelIds contained an entry that could not be found`.
9. Unlock as `ned`, check `swarm.js status`, refresh `/tmp/issue-batches/<ISSUE>_RESULT.md`, remove the temp worktree, and return `[SILENT]` if there is no new blocker.

## Pitfalls

- `finalize_task.sh` may unlock paths as `prismatic-engine` but leave a simple `ned` lock; always run `swarm.js status` and unlock the actual owner if needed.
- Do not mark a parent epic Done just because the parent doc/PR exists. Done requires the final child green gate to be merged or otherwise verified in the canonical branch.
- Do not manually reconstruct Linear label IDs from memory. Query the issue's current labels and remove `dispatch:ready` by filtering the returned list.
