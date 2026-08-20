# GRO-4016 SIAL closeout redispatch: finalize + lock/label refresh

## Scenario

A remediation issue was redispatched after the useful docs delta had already been preserved in `/home/ubuntu/work/sentinel-it-asset-logistics` on `ned/GRO-4016-sial-closeout` with PR evidence posted. The remaining work was not a rebuild; it was a closeout refresh.

## Durable pattern

1. Verify the existing artifact first:
   - `git status --short --branch`
   - `git diff --check`
   - `git show --stat --oneline --decorate --no-renames HEAD`
   - `git ls-remote --heads origin <branch>`
   - PR state with `gh pr view` when available.
2. If worktree is clean and PR/commit already exists, rerun finalize with explicit repo root and lock files:
   ```bash
   PRISMATIC_REPO_ROOT=/home/ubuntu/work/sentinel-it-asset-logistics \
   FINALIZE_LOCK_FILES='README.md docs/separation-from-sovereign-sentinel.md docs/workspace-index.md okf/audits/index.md' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4016 ned/GRO-4016-sial-closeout ned
   ```
3. Query Linear after finalize. Confirm:
   - state is `In Review`
   - latest/wide comment window contains the finalizer comment
   - stale `dispatch:ready` label is gone
4. If `dispatch:ready` remains on a redispatch refresh, remove it manually after finalizer succeeds so the scanner stops requeueing already-finalized work.
5. Always run `swarm.js status` after finalizer. For non-`prismatic-engine` repos, locks acquired with repo owner (for example `sentinel-it-asset-logistics`) can remain even when finalize prints successful unlocks, because finalize unlocks with `prismatic-engine` as the lock namespace. Clear leftovers with the exact same namespace/owner shape used to acquire them:
   ```bash
   node /home/ubuntu/.antigravity/swarm.js unlock README.md sentinel-it-asset-logistics ned
   ```

## Evidence shape to preserve

For markdown/docs-only closeout tasks, no build suite may apply. Evidence should still include clean status, diff check, commit SHA, PR URL, secret-pattern scan or `.env` tracked-file check when the issue mentions secrets, and final lock/Linear verification.
