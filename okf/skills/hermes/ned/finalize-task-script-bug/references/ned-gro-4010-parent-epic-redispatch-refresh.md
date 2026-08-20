# GRO-4010 parent epic redispatch refresh pattern

Use when a parent epic that already has a `ned/...` branch/PR/result is redispatched because Linear drifted back to `Backlog` or regained `dispatch:ready`.

## Trigger signs

- Linear comments already contain prior finalization/PR evidence.
- Existing PR branch is still open and unchanged.
- The task is a parent gate/epic where the correct current result may be **not green** until children are Done.
- Scanner reports the parent again because stale `dispatch:ready` remained or state drifted.

## Safe sequence

1. Do **not** touch the dirty primary workspace. Clone or check out the remote `ned/<issue>` branch into a clean temp worktree.
2. Verify the existing branch/commit/PR, not local uncommitted noise:
   - `git clone --branch ned/<issue> --single-branch <repo> /tmp/<issue>-refresh`
   - `git status --short --branch`
   - `gh pr view <pr> --json number,url,state,mergeStateStatus,statusCheckRollup`
3. If the verifier is designed to fail while the parent is not green, treat expected nonzero exit as evidence, not as a code failure. Capture stdout and the exit code explicitly.
4. Install deps in the clean clone if needed, then run the real verifier/build (`npm ci`, `node --check ...`, live Linear verifier, `npm run build`).
5. Update `/tmp/issue-batches/<issue>_RESULT.md` with the fresh evidence and the explicit decision: keep parent In Review / not Done until children are green.
6. Run finalize with absolute script path and explicit repo/locks:
   ```bash
   PRISMATIC_REPO_ROOT=/tmp/<issue>-refresh \
   FINALIZE_LOCK_FILES='scripts/foo.mjs scripts/docs/bar.md' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh <issue> ned/<issue> ned
   ```
7. Verify after finalize:
   - issue state is `In Review`
   - newest Linear comment exists (query a wide comment window; `comments(last:N)` can surprise)
   - stale `dispatch:ready` is removed manually if still present
   - `swarm.js status` has no active locks
8. If finalize unlocks repo-qualified locks but simple-owner locks remain, unlock the simple locks using the same owner form used to acquire them.

## GRO-4010-specific lesson

For `scripts/hde-green-status.mjs`, exit `1` with `green:false` is the correct live result while child issues are incomplete. In the refresh run, live Linear reported `child_count=5`, `done_children=0`, and all children incomplete; the correct action was to rerun finalize, remove stale `dispatch:ready`, and stay silent because there was no new user-facing blocker.
