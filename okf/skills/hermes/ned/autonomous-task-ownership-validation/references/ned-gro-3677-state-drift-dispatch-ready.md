# Already-finalized redispatch with Linear state drift + dispatch:ready

Session pattern: a previously finalized PWP task was redispatched even though the remote branch and prior Linear finalization comments existed. Fresh verification still passed, but a follow-up Linear query showed the issue had drifted back to `Backlog` and still carried `dispatch:ready`.

## Decision rule

If all completion signals exist but Linear has drifted back to an executable scanner state:

1. Treat the task as a recovery/finalization refresh, not a rebuild.
2. Use a clean detached worktree from `origin/ned/<ISSUE>` for fresh focused verification and any `/tmp/hermes-verify-*` ad-hoc detector evidence.
3. Update `/tmp/issue-batches/<ISSUE>_RESULT.md` with the fresh command output.
4. Rerun `finalize_task.sh <ISSUE> ned/<ISSUE> ned` to restore `In Review` and post the standard evidence comment.
5. Re-query Linear after finalize. The script exits 0 even on warnings; Linear is authoritative.
6. If `dispatch:ready` remains after state correction, remove just that label with `issueUpdate(labelIds=[existing labels except dispatch:ready])`.
7. Return `[SILENT]` when no blocker remains.

## Worktree pitfall

If `git worktree add /tmp/<issue>-finalize ned/<ISSUE>` fails because an older worktree already owns the branch, do not fall back to the dirty shared checkout and do not rebuild. `finalize_task.sh` may still transition Linear/comment even when `PRISMATIC_REPO_ROOT` points at the unavailable temp path and prints a repo-path warning. Accept that only after a follow-up Linear query confirms `In Review` and the evidence comment exists.

## Evidence to preserve

Record in the result file:

- branch SHA verified
- focused pytest command + pass count
- ad-hoc verifier path, command, exit code, assertion summary, cleanup status
- finalize transcript lines for transition/comment
- post-finalize Linear state
- final label list after removing `dispatch:ready`
