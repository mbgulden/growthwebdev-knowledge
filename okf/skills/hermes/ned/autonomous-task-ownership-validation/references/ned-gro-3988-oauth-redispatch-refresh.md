# GRO-3988 OAuth-scope redispatch refresh pattern

Use this when a Google OAuth/GA4/GTM/Search Console task is redispatched after a prior implementation already exists.

## Pattern

1. Treat `Backlog` + `dispatch:ready` as possible state drift, not proof the task needs rebuilding.
2. Verify completion signals first:
   - remote/local `ned/<issue>` branch exists;
   - PR exists and points at the expected branch;
   - prior Linear finalizer/evidence comments exist;
   - local RESULT file exists or can be refreshed;
   - implementation artifacts are present in the task branch.
3. Still rerun the mandatory blocker search before saying OAuth is blocked:
   - OKF integrations under `/home/ubuntu/work/growthwebdev-knowledge/okf/integrations/`;
   - `session_search` for the issue ID and GA/GTM/GSC/OAuth terms;
   - relevant `.env*` and Google credential files, redacting values.
4. Re-run focused verification from the existing task worktree/branch instead of rebuilding from scratch:
   - `python3 -m py_compile scripts/google-oauth-scope-flow.py`;
   - `python3 scripts/google-oauth-scope-flow.py --help`;
   - generate the consent URL and assert required scope names are present;
   - `npm run build`;
   - `git diff --check`;
   - verify worktree clean on `ned/<issue>...origin/ned/<issue>`.
5. Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` with the fresh evidence and current blocker.
6. Rerun `finalize_task.sh` with absolute path and explicit environment:
   - `PRISMATIC_REPO_ROOT=<task-worktree>`
   - `FINALIZE_LOCK_FILES='<actual files>'`
   - `bash /home/ubuntu/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE> ned/<ISSUE> ned`
7. Re-query Linear after finalize. If acceptance is still human-OAuth-blocked, keep the issue `In Review`, remove stale `dispatch:ready`, and add `agent:needs-human-review` + `requires:human-approval`.
8. Re-check swarm locks. If finalize printed successful repo-qualified unlocks but simple-owner locks remain, unlock them with the same simple owner form used to acquire them.

## Evidence notes from GRO-3988

- Existing implementation branch/PR: `ned/GRO-3988`, PR #45.
- Implementation artifacts: `scripts/google-oauth-scope-flow.py` and `docs/operations/hde-google-oauth-scope-flow-2026-07-19.md`.
- Fresh verification passed locally, while PR checks were mixed: Cloudflare Pages green; Workers Builds red with the known non-Pages Workers class.
- Linear comment ordering can be misleading: `comments(last:N)` may omit the newest finalizer comment. Use a wider query if the transcript says `comment: ok` but the small comment window looks stale.
- Finalize left simple-owner locks behind in this session; manual `swarm.js unlock <path> ned` cleared them.

## Human action remains the blocker

For this class, do not mark green/Done until the human Google consent loop produces a usable credential and live GA/GTM/GSC API checks pass. The correct blocker wording is: Michael must open the generated Google consent URL and return the resulting `code=` or failed localhost redirect URL; no tokens belong in git or Linear.
