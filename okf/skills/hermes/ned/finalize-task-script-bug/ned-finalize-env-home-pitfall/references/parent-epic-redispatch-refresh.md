# Parent epic redispatch refresh (GRO-4004 pattern)

When a parent epic is redispatched even though a `ned/<issue>` branch, PR, RESULT, and prior Linear finalization evidence exist:

1. Do not rebuild in the dirty canonical checkout. Create a clean detached worktree from `origin/ned/<issue>`.
2. Verify the durable parent gate, including the expected red/not-green state if child gates remain open.
3. For Node/Astro repos, a fresh worktree may lack `node_modules`; run the lockfile install (`npm ci`) before `npm run build`. `astro: not found` is dependency setup, not code evidence.
4. Rerun finalize with the absolute script path and explicit scope:
   ```bash
   PRISMATIC_REPO_ROOT=/tmp/<repo>-<issue> \
   FINALIZE_LOCK_FILES='scripts/foo.mjs scripts/docs/foo.md' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE> ned/<ISSUE> ned
   ```
5. Re-query Linear. Confirm state `In Review`; remove stale `dispatch:ready` if it remains.
6. Run `swarm.js status`; if simple-owner locks remain, unlock them with the same simple form used to acquire them (`swarm.js unlock <path> ned`).
7. Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` and return `[SILENT]` if there is no new human blocker.

Do not mark a parent epic Done/green just because its parent gate script works. Keep it open while child gates remain Todo/In Review or any required live acceptance proof is red.
