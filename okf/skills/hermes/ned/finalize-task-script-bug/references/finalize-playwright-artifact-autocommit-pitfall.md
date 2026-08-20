# Finalize + Playwright artifact auto-commit pitfall

When refreshing an already-implemented issue from a clean temporary worktree, Playwright can leave `test-results/.last-run.json` even when the focused spec passes. `finalize_task.sh` runs `git add -A` in `PRISMATIC_REPO_ROOT` and will commit any untracked artifact it sees.

Observed pattern:

1. Create detached `/tmp/...` worktree from `origin/ned/<issue>`.
2. Run `npm ci`, `npm run build`, and `npx playwright test ...`.
3. `git status --short` shows `?? test-results/`.
4. Running `finalize_task.sh` with `PRISMATIC_REPO_ROOT=<tmp-worktree>` creates a local detached commit containing `test-results/.last-run.json`.
5. The pushed task branch remains unchanged, but the finalize transcript can look like a real task commit happened.

Safe pattern:

```bash
cd /tmp/<clean-worktree>
npm run build
npx playwright test tests/flows/<spec>.ts --project=desktop-chromium --reporter=list
rm -rf test-results playwright-report .playwright
# or at least: git clean -fd -- test-results playwright-report .playwright
git status --short --branch  # must be clean before finalize
PRISMATIC_REPO_ROOT=/tmp/<clean-worktree> \
FINALIZE_LOCK_FILES='<actual changed lane files>' \
bash ~/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE> ned/<ISSUE> ned
```

Post-finalize verification:

- Re-query Linear state and labels; remove stale `dispatch:ready` if the issue was redispatched after prior completion.
- Verify the remote branch SHA (`git ls-remote --heads origin ned/<issue>`) separately from any detached local finalize commit.
- If a detached artifact commit was accidentally created, do **not** push it. Record that the pushed branch remains at the expected SHA, remove the temporary worktree, and refresh the local RESULT with the caveat.
