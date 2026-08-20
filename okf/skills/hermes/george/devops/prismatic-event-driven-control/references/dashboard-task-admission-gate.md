# Dashboard task-admission gate pattern

Use this reference when a Prismatic successor task is contract-ready but the event-driven dashboard admission route is not verified yet.

## Situation signal

A task contract exists, but live discovery shows only read/recovery/queue surfaces such as:

- `/health`
- `/dashboard`
- `/api/webhooks/queue/status`
- `/api/dispatcher/status`
- `/api/dashboard/recovery-control/status`

These are not enough to start a producer unless a specific authenticated operator/task-admission contract is verified.

## Required admission receipt fields

Before launching AGY/Fred/Ned/Kai as a producer, require a durable dashboard/event admission record binding:

```text
TASK_ID=<exact task id>
BASE_COMMIT=<exact commit>
BASE_TREE=<exact tree when available>
TASK_SHA256=<digest of the task contract file>
PRODUCER_ID=<agent/profile>
WORKTREE=<task-specific clean worktree>
WRITER_CAP=<usually 1>
ADMITTED_BY=<dashboard/operator/event identity>
ADMITTED_AT=<timestamp>
```

## Non-substitutes

Do not treat any of these as admission:

- cron polling;
- Telegram polling or a Telegram instruction alone;
- direct Linear polling;
- fake webhook delivery;
- generic dispatcher action that reports `accepted_noop`;
- recovery-control routes that only record restart/retry/replay actions;
- webhook queue read/retry/purge routes for already-ingested tasks;
- direct AGY/Fred/Ned launch without a durable admission record.

## Safe action while blocked

If the implementation slice is clear but admission is blocked:

1. Write a bounded task contract file with `STATUS=QUEUED_NOT_ADMITTED_EVENT_ONLY`.
2. Include the exact accepted base commit/tree and allowed paths.
3. Hash the task file and record it in the handoff/queue state.
4. State `TASK_ADMITTED=false`, `PRODUCER_STARTED=false`, `ACTIVE_PRODUCERS=0`.
5. Run only ad-hoc targeted verification of the contract/handoff/dashboard read paths.
6. If the missing piece is the admission route itself, launch/read a separate read-only preflight for the authenticated endpoint/ledger/UI prerequisite instead of starting the implementation producer.
7. Do not start producer execution until the real admission route exists and admits that exact digest.

## Scope-splitting pitfall

When a successor task involves provider/gateway/status integration, independently check whether it is actually multiple slices. Keep pure deterministic adapter logic separate from gateway hardening, outbound provider REST transport, and dashboard admission. See `references/pure-adapter-slice-boundaries.md`.

## Report marker

```text
TASK_CONTRACT_READY=true
TASK_ADMITTED=false
PRODUCER_STARTED=false
GENERIC_DISPATCH=PAUSED_EVENT_DRIVEN_ONLY
NOT_CLAIMING=producer execution, deploy, restart, Linear write, or canonical suite proof
MARKER=TASK_CONTRACT_READY_EVENT_ADMISSION_BLOCKED
```
