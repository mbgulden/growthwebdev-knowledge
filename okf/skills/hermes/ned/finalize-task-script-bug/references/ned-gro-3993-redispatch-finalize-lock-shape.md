# GRO-3993 redispatch refresh: finalize lock-shape pitfall

## Trigger

An already-implemented issue is redispatched because Linear drifted back to `Backlog` with `dispatch:ready`, while a remote `ned/<issue>` branch and PR already exist. You create a clean detached worktree, rerun focused verification, update `/tmp/issue-batches/<ISSUE>_RESULT.md`, and rerun `finalize_task.sh` with `PRISMATIC_REPO_ROOT` and `FINALIZE_LOCK_FILES`.

## Durable pattern

1. Treat it as a refresh, not a rebuild, when remote branch + PR + prior finalization evidence exist.
2. Verify from a clean detached worktree instead of touching a dirty shared checkout.
3. Rerun focused build/proof commands and update the local RESULT with fresh evidence.
4. Run finalize from the clean worktree:
   ```bash
   PRISMATIC_REPO_ROOT=/tmp/<clean-worktree> \
   FINALIZE_LOCK_FILES='src/layouts/Layout.astro scripts/route-complete-build.mjs scripts/docs/...' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh GRO-XXXX ned/GRO-XXXX ned
   ```
5. Re-query Linear. If `dispatch:ready` remains, remove only that stale label and re-query state/labels.
6. Run `node /home/ubuntu/.antigravity/swarm.js status` after finalize.

## Lock-shape pitfall

`swarm.js` lock ownership depends on the argument shape used when acquiring the lock. In the GRO-3993 refresh, locks were acquired with the simple form:

```bash
node /home/ubuntu/.antigravity/swarm.js lock src/layouts/Layout.astro ned
```

`finalize_task.sh` unlocks with a repo-qualified form internally and printed successful-looking lines such as:

```text
UNLOCKED: src/layouts/Layout.astro ← prismatic-engine
```

…but `swarm.js status` still showed:

```text
src/layouts/Layout.astro    ned
scripts/route-complete-build.mjs    ned
scripts/docs/hde-analytics-loader-20260718.md    ned
```

Fix: unlock residual simple-owner locks with the same owner form used to acquire them:

```bash
node /home/ubuntu/.antigravity/swarm.js unlock src/layouts/Layout.astro ned
node /home/ubuntu/.antigravity/swarm.js unlock scripts/route-complete-build.mjs ned
node /home/ubuntu/.antigravity/swarm.js unlock scripts/docs/hde-analytics-loader-20260718.md ned
```

Verification is `swarm.js status` returning `No active locks.` Do not rely on finalize's unlock transcript alone.

## Related analytics-loader refresh evidence shape

For GA/GTM loader redispatches, useful fresh proof is:

- `npm ci`
- `npm run build`
- dist scan over `dist/**/*.html` asserting exactly one `data-hde-analytics="canonical"` and expected GA4 ID coverage
- `git diff --check`
- PR check inspection (`gh pr view --json statusCheckRollup`)
- live/preview curl samples using a browser-ish user-agent when Python `urllib` gets Cloudflare 403
