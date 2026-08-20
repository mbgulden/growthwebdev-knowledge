# HDE completed-code redispatch refresh with Pages green / Workers red

Use this when an HD Platform issue is redispatched even though a `ned/<issue>` branch, PR, and prior Linear evidence already exist, and the only remaining blocker is the duplicate `Workers Builds: hd-platform` check.

Session pattern proven on GRO-4013:

1. Query Linear before touching the dirty primary checkout. If state drifted back to `Backlog` and `dispatch:ready` returned, treat this as a refresh/drift repair, not a rebuild.
2. Inspect the PR directly with `gh pr view <PR> --json statusCheckRollup,mergeable,mergeStateStatus,headRefOid,files`.
3. Create a clean detached verifier worktree from `origin/ned/<issue>` under `/tmp`, not from the dirty shared checkout:
   ```bash
   git fetch origin ned/<issue> main --prune
   git worktree add --detach /tmp/hd-platform-<issue>-refresh origin/ned/<issue>
   ```
4. If dependencies are absent, run the repo install (`npm install --no-package-lock` in this repo) before `npm run build`.
5. Rerun the real proof:
   - `npm run build`
   - issue-specific focused artifact check, e.g. `test -f dist/community/index.html && grep -q '<expected copy>' dist/community/index.html`
   - confirm only ignored runtime artifacts (`.astro/`, `dist/`, `node_modules/`) appear afterward.
6. Update `/tmp/issue-batches/<ISSUE>_RESULT.md` with fresh verification, PR check status, and the known Pages-vs-Workers blocker.
7. Rerun finalize with absolute script path and explicit env, because `~` can break after sourcing profile envs:
   ```bash
   export HOME=/home/ubuntu
   PRISMATIC_REPO_ROOT=/tmp/hd-platform-<issue>-refresh \
   FINALIZE_LOCK_FILES='docs/... src/...' \
   bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE> ned/<ISSUE> ned
   ```
8. Re-query Linear. If `dispatch:ready` remains, remove it and add `agent:needs-human-review` while keeping `agent:ned` and the issue `In Review`.
9. Verify `swarm.js status` has no active locks.
10. Remove the temp worktree after deleting bulky ignored artifacts if needed:
    ```bash
    rm -rf /tmp/hd-platform-<issue>-refresh/node_modules /tmp/hd-platform-<issue>-refresh/dist /tmp/hd-platform-<issue>-refresh/.astro
    git worktree remove --force /tmp/hd-platform-<issue>-refresh
    ```
11. If no new blocker exists beyond the already-known Workers integration mismatch, cron delivery should be `[SILENT]`.

Do not add `assets.directory` to root `wrangler.jsonc` to appease Workers. Keep Pages-compatible config as the source of truth.