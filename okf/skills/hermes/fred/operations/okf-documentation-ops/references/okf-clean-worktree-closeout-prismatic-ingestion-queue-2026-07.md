# OKF Clean Worktree Closeout Pattern — Prismatic Ingestion Queue

Session pattern captured from documenting the Prismatic Governance Dashboard Ingestion Queue repair in the OKF hub.

## Trigger

Use this when the user asks to document current state in OKF after operational work, and the primary `growthwebdev-knowledge` worktree is dirty or on an unrelated branch.

## Pattern

1. Do not edit the dirty hub worktree in place.
2. Fetch and create a clean temporary worktree from `origin/main`:

```bash
cd /home/ubuntu/work/growthwebdev-knowledge
git fetch origin --quiet
git worktree add /tmp/<okf-topic> origin/main
cd /tmp/<okf-topic>
git switch -c feature/fred-okf-<topic>
```

3. Add only the OKF record and required index edits.
4. Use required frontmatter: `type`, `title`, `description`, `resource`, `tags`, `timestamp`, `linear_issue`, `git_repo`, `git_path`, `last_verified`, `verified_by`, `status`.
5. Include evidence boundaries explicitly: ad hoc targeted verification vs durable contract vs full suite-green.
6. Update both a master/discovery index and the relevant project index when applicable.
7. Run a fresh `/tmp/hermes-verify-*` OKF verifier that checks:
   - doc exists;
   - required frontmatter is present;
   - `resource` and `git_path` match the repo-relative file path;
   - local Markdown links resolve;
   - new doc is reachable from indexes;
   - evidence markers are present;
   - verifier cleans itself up.
8. Commit, push, open a PR, merge only if clean.
9. Post-merge, fetch `origin/main`, create a fresh readback worktree, and verify the merged doc/indexes from `origin/main` rather than trusting the feature branch.
10. Remove both temp OKF worktrees and `/tmp/hermes-verify-*` scripts.

## Useful closeout content shape

For operational repairs, capture:

- current matrix of green/yellow/red areas;
- exact merged PR and commit evidence;
- changed files and why each mattered;
- restored route/API contract;
- source-of-truth contract;
- verification commands and observed outputs;
- browser/live proof boundaries;
- remaining caveats or blocked follow-ups;
- operational lesson / pitfall to avoid next time.

## Stale verification guard pattern

If a guard says verification is stale after a real verification pass, rerun a small exact-scope `/tmp/hermes-verify-*` script instead of arguing with the guard. Keep it focused on the changed paths and changed behavior, remove the script, and state `ad hoc targeted verification` explicitly. Avoid broad `/tmp/hermes-verify-*` cleanup assertions that can fail because unrelated historical temp files exist.