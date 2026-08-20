# Live-verifier-red state drift refresh

Use when an already-implemented Ned issue resurfaces with a remote `ned/<issue>` branch/PR/evidence, but Linear has drifted back to `Backlog` or carries stale `dispatch:ready`, and the acceptance verifier is expected to return nonzero because production is still red.

Pattern:

1. Treat this as a refresh/redispatch, not a rebuild, once prior implementation evidence is present.
2. Create a clean detached worktree from `origin/ned/<issue>`; do not touch a dirty shared checkout.
3. Re-run build/static checks that prove the verifier code still works.
4. Re-run the live verifier honestly. If it exits nonzero because production remains red, that is valid evidence for an acceptance-verifier task — do not call it a local test failure.
5. Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` with both kinds of evidence:
   - code/build verifier health (passing)
   - live production status (red, with counts and output artifact path)
6. Run `finalize_task.sh` with `PRISMATIC_REPO_ROOT=<clean-worktree>` and `FINALIZE_LOCK_FILES='<actual task files>'` to restore `In Review` and post the routine finalization comment.
7. Re-query Linear after finalize. If `dispatch:ready` is still present on an `In Review` issue, remove it with `issueUpdate(labelIds=<all labels except dispatch:ready>)` and re-query.
8. Verify locks are clear and remove the temporary worktree.

Important distinction: a live verifier returning `ok=false` can be the correct acceptance result for a monitoring/coverage issue. The task is not Done/green, but the redispatch can still be completed by preserving the red evidence, restoring review state, and braking the scanner loop.

Example evidence fields worth recording:
- PR URL and head branch
- PR check status, especially Pages vs stale Workers Builds distinction
- `npm ci`, `npm run build`, syntax check exits
- live verifier command, exit code, output JSON path
- live counts: crawled URLs, missing analytics pages, duplicate snippets, GTM IDs, funnel routes missing events
- post-finalize Linear state/labels and lock status
