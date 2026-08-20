# Stale Outbox Terminal-Reconciliation Bootstrap

Use when the event-driven Prismatic queue is blocked by an oldest durable outbox row whose source work is already merged/accepted, but the outbox/claim state remains retryable and ordinary consumption would launch another producer.

## Trigger shape

A bootstrap repair may be needed only when all are true:

```text
SOURCE_WORK=current-main exact or otherwise independently accepted
OUTBOX=oldest pending/claimed/retryable row
CLAIM=retryable_failed or expired claimed row
WRITER_LEASE=empty
ACTIVE_PRODUCERS=0
ORDINARY_CONSUMER=would select the stale row first and may launch another producer
```

Do **not** run the normal consumer to see what happens when this shape is present. That can violate same-event attempt caps or launch duplicate work.

## Required boundary before implementation

1. Prove the source work is already merged/accepted on the current base.
2. Prove all prior admitted producer attempts are terminal and no producer is alive.
3. Prove live runtime launchers/supervisors will not be executed by the repair.
4. Ask Michael for an explicit one-time bootstrap exception if the normal event path cannot repair its own oldest row.
5. Restrict the code slice to the admission/consumer/API/test paths needed for reconciliation.
6. Do not mutate the live database during implementation or review.

## Safe reconciliation contract

The repair action should be authenticated and task-specific. It should:

- bind exact task/event/claim IDs and expected prior state;
- bind candidate commit/tree/merge/evidence digests;
- run in one `BEGIN IMMEDIATE` transaction;
- reject active writer leases;
- reject unexpired claims;
- reject completed/launched rows;
- reject corrupted lease timestamps with a bounded domain error, not an internal exception;
- transition stale row to a truthful terminal state such as `outbox=failed` and `claim=terminal_failed`;
- keep `launch_receipt_json=null` so no fake launch is implied;
- write only a bounded immutable lifecycle digest, not bulky evidence text;
- provide exact idempotent replay for the same evidence;
- reject conflicting replay;
- prove the ordinary consumer no longer selects the terminalized row;
- never invoke launcher, subprocess, producer, deploy, restart, or Linear write.

## Proof to collect before PR/review

```text
COMMAND=<changed-path format/lint + focused transaction/API tests + diff-check>
RESULT=PASS
SCOPE=four or otherwise authorized paths
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=canonical full suite, independent review, merge, deployment, live DB mutation
MARKER=...TERMINAL_RECONCILIATION_FOCUSED_OK
```

Then run a broader admission/auth gate and finally the canonical suite before commit/PR acceptance. If tool budget/time runs out before canonical, report `PARTIAL`; do not imply the candidate is accepted.

## PR/review publication sequence

After focused and canonical tests pass:

1. Commit only the authorized paths and prove `git status --short` is empty.
2. Push the exact branch and verify the remote branch SHA equals the local candidate commit.
3. Open a focused PR whose body binds commit, tree, parent, exact changed paths, canonical log path/digest, and explicit non-claims.
4. Mark independent exact-head review as pending in the PR body and handoff; do not merge from self-review.
5. Verify the live PR via API after creation. If the CLI JSON field set is insufficient, query the pull request API directly and assert head SHA, base SHA, state, merged=false, body markers, and exact file list.
6. Write a durable checkpoint report and update the current handoff before stopping or switching tasks.
7. Run a final post-write consistency verifier that rechecks exact Git head/tree, clean worktree, live PR head/base, canonical log digest, handoff/checkpoint markers, stale live DB boundary, and zero active producers.

Proof block:

```text
COMMAND=<post-write consistency verifier + py_compile + changed-path ruff + git diff/status>
RESULT=PASS
LOG=<path>
LOG_SHA256=<sha256>
SCOPE=exact PR head/tree + canonical log + handoff/checkpoint + live stale-state boundary + zero producers
AD_HOC_OR_CANONICAL=ad-hoc targeted closeout
NOT_CLAIMING=independent review, merge, deployment, live reconciliation
MARKER=...REVIEW_PENDING_CHECKPOINT_OK
```

## Reporting boundary

Separate these states clearly:

- implemented in source;
- focused/broad tests passed;
- canonical suite passed or not run;
- independent review status;
- merged/not merged;
- deployed/not deployed;
- live database reconciled/not reconciled;
- queue ready/not ready for successor admission.
