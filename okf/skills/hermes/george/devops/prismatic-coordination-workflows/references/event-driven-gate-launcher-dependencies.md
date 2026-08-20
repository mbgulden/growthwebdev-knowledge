# Event-driven gate launcher dependencies

Use this reference when advancing Prismatic work through the dashboard/event-queue gate and a producer/launcher boundary is involved.

## Durable lesson

A healthy queue and cap-1 state are not sufficient to admit the next task. Before admission, verify that the consumer has a task-generic, request-bound launcher that can execute the exact admitted worktree/task. If the only executable producer is task-specific, disabled, or hard-coded to a prior task, admission must be withheld fail-closed.

## Required pre-admission checks

1. Confirm queue/cap state separately:
   - no pending global candidate for unrelated work;
   - no writer leases;
   - active producers are zero or within the authorized cap;
   - prior terminal reconciliations are not claimable by the consumer predicate.
2. Inspect the configured producer map shape, not just guessed filenames. Verify:
   - producer identity;
   - executable path;
   - executable mode;
   - timeout;
   - policy allowlisted worktrees.
3. If the launcher is unreadable by design (`000`), do not chmod it to inspect. Use read-only privileged inspection only when allowed, and report no secrets.
4. Bind launcher safety to content, not name:
   - no hard-coded old task ID;
   - no hard-coded old worktree/task file;
   - no hard-coded old supervisor/ledger;
   - launch IDs must be request/task bound, not prior-task prefixed.
5. If a generic launcher is missing, stop before admission and ask/record an authorization point for a separate bootstrap source slice.

## Fail-closed outcomes

Stop and report an authorization point when any of these is true:

- the only real launcher is disabled or mode `000` and task-specific;
- enabling/reusing the launcher would violate exact task/worktree binding;
- admitting now would create a non-executable stale row;
- policy updates, launcher enablement, deployment, or service restarts would be required but were not explicitly authorized.

## Safe next sequence

1. Preserve blocker evidence in a compact report.
2. Update the handoff with `NEXT_SLICE_ADMISSION_WITHHELD` and `GENERIC_EVENT_LAUNCHER_DEPENDENCY_BLOCKED`.
3. Request authorization for a George-owned task-generic launcher bootstrap slice.
4. Put that bootstrap through local proof, independent exact-head review, merge authorization, immutable release proof, and separate deployment/config authorization.
5. Only after the generic launcher is live should the source successor be admitted at cap 1.

## Reporting boundary language

Use a compact proof block like:

```text
RESULT=BLOCKED
SCOPE=event-driven next-slice admission
ACTIVE_PRODUCERS=0
NEXT_TASK_ADMITTED=false
GENERIC_EVENT_LAUNCHER_READY=false
POLICY_CHANGED=false
LAUNCHER_ENABLED=false
NOT_CLAIMING=producer launch, policy update, merge, deploy
MARKER=NEXT_SLICE_BLOCKED_ON_GENERIC_EVENT_LAUNCHER_AUTHORIZATION
```
