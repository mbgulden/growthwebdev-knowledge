# Redispatch refresh: rewrite RESULT after finalize, not before

## Pattern

When a cron redispatch finds an already-implemented branch/PR and the issue has drifted back to `Backlog` or regained `dispatch:ready`, the right flow is:

1. Verify the existing task branch from a clean worktree.
2. Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md` with the fresh verifier/build/PR-check evidence.
3. Rerun `finalize_task.sh` with an absolute path plus explicit `PRISMATIC_REPO_ROOT` and `FINALIZE_LOCK_FILES`.
4. Re-query Linear, remove stale `dispatch:ready` if it remains, and re-query locks.
5. Rewrite the RESULT file again with the actual post-finalize facts: timestamp, final Linear state, label cleanup, lock cleanup, and remote branch SHA.

## Pitfall

Do not leave the local RESULT in a pre-finalize state such as "Finalization refresh to be rerun" after finalize has actually completed. The RESULT file is the cron's durable local evidence artifact; if it is stale, the next redispatch looks ambiguous even though Linear and Git are correct.

## Verification checklist

- Linear state is `In Review` after finalize.
- `dispatch:ready` is gone when this is a redispatch refresh.
- `node /home/ubuntu/.antigravity/swarm.js status` prints `No active locks.`
- `git ls-remote origin refs/heads/ned/<ISSUE>` matches the expected commit.
- `/tmp/issue-batches/<ISSUE>_RESULT.md` describes completed finalization, not intended finalization.
