# Finalize vs. lane-rejection recovery

## Trigger

A Ned task has a committed change, but the requested path is rejected by the safe-push lane guard after `finalize_task.sh` has already run.

## Safe recovery

1. Treat the failed push as a delivery blocker: a local commit and a finalizer transcript are not a completed task.
2. Immediately read back Linear state/comments. `finalize_task.sh` can have moved the issue to `In Review` despite no remote branch/PR.
3. Check the actual acquired lock separately. The finalizer's default lock list can differ from the task's acquired path; explicitly unlock the acquired lane after confirming it is Ned-owned.
4. Preserve the committed work as a transferable patch under `/tmp/issue-batches/<ISSUE>-handoff/` and record its SHA-256. Do not force-push or bypass a lane guard for an out-of-lane path.
5. Restore Linear to `Todo` and post a corrective evidence comment: failed path, local commit, verification scope, handoff patch/checksum, and the needed owner/exception.
6. Re-query Linear to verify the state correction persisted.

## Prevention

Before invoking `finalize_task.sh`, set `FINALIZE_LOCK_FILES` to the actual locked path (and `PRISMATIC_REPO_ROOT` when using a clean worktree). Post-finalize, verify both the Linear readback and `swarm.js status <actual-path>` before pushing.

## Verification evidence

For provenance/document handoffs, use a fresh `tempfile.mkstemp(prefix="hermes-verify-", suffix=".py", dir="/tmp")` verifier. It should run `git diff --check`, validate all frozen-manifest hashes against the named Git object, parse any generated JSON GraphQL artifacts, compile temporary helper scripts, scan the deliverable for credential-shaped strings, print a compact assertion summary, and remove itself. Report it as ad-hoc verification, never as the full project suite.
