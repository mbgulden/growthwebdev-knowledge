# Assigned AGY Dispatch Recovery

Use this reference when Ned/Kai/Fred or a parent task is blocked because an assigned AGY child was supposedly dispatched/completed but no durable standalone artifact, branch, PR, or Linear transition exists.

## Trigger signals

- Parent task reports: "AGY completed" but remains blocked in Todo or manual-review.
- Dispatcher only wrote `/tmp/issue-batches/<ID>.txt` or local specs, with no supervisor pickup evidence.
- Linear/watchdog state says the child is queued/dispatched because `agent:agy` and `dispatch:ready` labels exist, but direct proof shows no bus row, task file, sandbox, producer, branch, or PR.
- Generic AGY dispatch is intentionally paused, but a specific assigned child task is required to unblock the current cap-1 lane.
- Shared repository checkout is on an unrelated Ned/Fred branch while the assigned task must start from current remote main.
- A held owner-lane PR is conflicting on a path that an assigned child must reconcile first.

## Recovery pattern

1. **Do not resume generic dispatch.** Treat the blockage as an exact assigned-child recovery, not permission to wake the broad merge factory.
2. **Reconcile actual state first.** Verify parent/child issue IDs, remote main SHA, current PR/CI truth, existing artifacts, and whether the child output already exists unpromoted. Treat labels, Linear status, and watchdog summaries as untrusted until direct sources prove bus row/event, consumed task, sandbox, active/finished producer, artifact/branch/PR, and consumer checkpoint sanity. If a consumer cursor is ahead of the bus or bound to the wrong child HOME, record dispatch-foundation debt but do not repair cursor/bus/runtime state inside the child recovery unless separately authorized.
3. **Preserve cap 1.** Launch at most one assigned AGY producer. Queue the sibling child behind it; do not run both concurrently.
4. **Use a clean source worktree.** If the shared checkout is on another owner branch or PR, create a detached clean worktree from exact remote main for the AGY source/clone path. Do not let a producer inherit the mutable shared checkout.
5. **Replace stale issue-batch/cache files.** Archive old `/tmp/issue-batches/<ID>*` material, write a fresh exact task packet, and hash it. The task must forbid push, PR, merge, Linear mutation, deploy/restart, and second-task launch unless explicitly authorized.
6. **Smoke the child AGY environment before relaunch.** If a producer fails before edits from an unsupported/stale model identifier or auth path, verify the intended AGY CLI/model under the child auth HOME, confirm the worktree is still exact/clean, then relaunch the same hashed task without raising cap.
7. **Verify the consumed task file.** During the supervisor jitter window, read/hash the generated `AGY_TASK.md` from the real sandbox root. Abort or quarantine if it contains stale push/PR/Done instructions or the wrong base marker.
8. **Treat supervisor `DONE` as untrusted.** Parse `RESULT.md`, then verify actual Git state: `HEAD`, parent, tree, changed paths, clean worktree, source-file hash equality, diff check, and bounded secret signature scan.
9. **Reconcile result-location claims.** A result packet may claim a sandbox commit while the actual commit exists only in the detached source worktree. If so, classify as `DONE_BUT_RESULT_LOCATION_CLAIM_FALSE`: no remote side effects if no branch/PR exists, but the candidate is still untrusted until independently reviewed by exact commit/tree/parent.
10. **Only after exact review.** If independent review returns `CLEAN`, push one exact branch/open one focused PR and require hosted CI before merge. If `REPAIR`, repair the same child task; do not start the sibling child.
11. **Coordinate held owner lanes durably.** If the child docs/code path conflicts with an owner’s PR train, post a compact correction on the held PR: exact candidate/base/path, `STATE=INDEPENDENT_REVIEW_PENDING|CI_PENDING|MERGED`, what the owner must not edit yet, and explicit non-authorization for merge/rebase/lane bypass. This PR comment is coordination evidence; it is not completion proof.

## Proof packet fields

```text
PARENT_ISSUE=<parent task>
CHILD_ISSUE=<assigned AGY task>
GENERIC_DISPATCH=PAUSED
CAP=1
ACTIVE_PRODUCERS=<0|1>
BUS_ROWS=<count for child issue>
CONSUMER_CURSOR=<cursor and DB identity if relevant>
BUS_MAX_ROWID=<canonical bus max rowid if relevant>
SOURCE_WORKTREE=<clean detached worktree>
BASE_SHA=<remote main sha>
TASK_SHA256=<fresh exact task packet>
SUPERVISOR_RESULT=<DONE|FAILED_BEFORE_EDITS|REPAIR|...>
RESULT_LOCATION_RECONCILIATION=<SANDBOX_MATCH|SOURCE_WORKTREE_COMMIT|MISSING_COMMIT>
CANDIDATE_SHA=<sha or none>
CHANGED_PATHS=<allowlist result>
SOURCE_COPY_HASH=<sha256/equality result>
SECRET_SCAN=<PASS|FAIL>
REMOTE_SIDE_EFFECTS=<branch/pr/linear/deploy false unless proven>
NEXT_CHILD=<queued child issue or none>
NOT_CLAIMING=<generic dispatch resumed, Linear Done, merge, deploy, cap increase>
```

## Pitfalls

- A generated cron/supervisor response is not proof the AGY child actually consumed or completed the task.
- `agent:agy` plus `dispatch:ready` labels are not dispatch proof; require direct bus/task/sandbox/producer/artifact evidence.
- A consumer process can be active but unusable for this child if its cursor is ahead of the bus, it watches the wrong DB, or it uses the wrong child auth HOME.
- `RESULT.md` can be internally false; verify Git objects and paths directly.
- A valid local candidate in a detached worktree is not a PR and not completion.
- Shared checkouts on owner branches can contaminate AGY source cloning; use exact remote-main detached worktrees.
- Stale issue-batch files can silently override corrected task text.
- Sibling child tasks are queued, not launched, until the active child closes.
