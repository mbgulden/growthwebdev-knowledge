# Ned redispatch drift refresh pattern

Use when the scanner redispatches a Linear issue that already has a branch/PR/result evidence, but Linear drifted back to `Backlog` or still carries `dispatch:ready`.

## Pattern

1. Re-query Linear before rebuilding. Read state, labels, and last comments. If the comments already show prior implementation/evidence and there is no out-of-lane dequeue, treat it as state drift first, not missing work.
2. Inspect the existing branch/worktree/result file. Prefer the prior clean worktree/branch if available (for example `/tmp/hd-platform-gro4008` + `ned/GRO-4008`) and verify it is clean against origin.
3. Rerun the lightweight verifier/build/smoke needed for fresh evidence. Redact live Stripe checkout session IDs (`cs_live_...`) from any persisted logs or reports before writing results.
4. Update `/tmp/issue-batches/<ISSUE>_RESULT.md` with the refresh evidence and current not-green blocker. Keep runtime artifacts/logs out of git.
5. Rerun finalize with explicit repo/locks:

```bash
PRISMATIC_REPO_ROOT=/tmp/hd-platform-gro4008 \
FINALIZE_LOCK_FILES='package.json scripts/hde-production-smoke.mjs scripts/verify_hde_production_smoke.mjs scripts/docs/gro-4008-production-smoke-cron.md' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh GRO-4008 ned/GRO-4008 ned
```

6. Post-finalize, verify Linear again. If `dispatch:ready` remains, remove it explicitly with `issueRemoveLabel`; `finalize_task.sh` transitions state and comments but does not reliably clear redispatch labels.
7. Check locks after finalize. Current `finalize_task.sh` unlocks using owner `prismatic-engine`; if you acquired locks as `ned`, simple owner locks may remain. Manually unlock those with `swarm.js unlock <path> ned`.

## Pitfalls

- Do not rebuild new code just because the scanner says `dispatch:ready`; stale labels can resurrect already-submitted issues.
- Do not report green when the implementation is verified but the live proof intentionally fails (e.g. production report download returns HTML fallback). Keep issue `In Review`, not Done.
- Do not leave live Stripe session IDs in RESULT.md, logs, Linear comments, or chat output.
