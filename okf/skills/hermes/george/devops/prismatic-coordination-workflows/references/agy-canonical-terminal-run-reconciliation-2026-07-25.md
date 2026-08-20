# AGY Canonical Terminal Run Reconciliation — 2026-07-25

Use this reference when a Prismatic AGY producer task must be resumed after a harness, provider label, or containment repair.

## Durable pattern

1. **Fail closed on stale or invalid attempts.** If an attempt exits before edits because of provider/model labels, timeout argv parsing, or harness admission mismatch, record it as a terminal failed attempt, verify process-tree cleanup and zero survivors, and do not accept its result.
2. **Separate provider preflight from producer proof.** A one-line AGY auth/model preflight can prove the canonical model string and argv compatibility, but must be labeled ad-hoc and not claimed as task completion.
3. **Bind the fresh attempt to the same frozen task/event/base.** Before dispatch, re-hash the task file and pinned AGY binary; assert event ID, task SHA, base commit/tree, admitted receipt, writer cap, and accepted workflow commit/tree.
4. **Launch through the accepted harness only.** Do not hand-run the producer after a harness repair. Use the canonical harness so cap-one slot, activity ledger, no-wall-clock runtime, and process containment all exercise the production path.
5. **Preserve no-wall-clock semantics in receipts.** Record `runtime_deadline=null`, `automatic_kill=false`, active slot identity, pane PID/start-tick identity, and activity classification. These prove the run is supervised without elapsed-time cancellation.
6. **Use event-driven terminal observation.** Prefer an exact file-event watcher (for example Linux `inotify` on the run directory for `process-result.json`) over polling loops. The watcher should reconcile once when the terminal artifact appears, not cancel on elapsed time.
7. **Do not overclaim.** Running means only running. Completion, candidate acceptance, GitHub CI green, deployment, restart, Linear update, and released runtime each require their own evidence.

## Proof packet fields

```text
RUN_ID=<canonical run id>
EVENT_ID=<task admission event id>
TASK_SHA256=<frozen task digest>
BASE_COMMIT=<task base commit>
BASE_TREE=<task base tree>
MODEL=<canonical AGY model id>
STATUS=<running|failed|completed>
ACTIVITY=<starting|working|quiet|suspect>
PANE_IDENTITY_LIVE=<true|false>
ACTIVE_SLOT=<slot run id>
RUNTIME_DEADLINE=null
AUTOMATIC_KILL=false
VERIFICATION_STATUS=<pending|passed|failed>
AD_HOC_OR_CANONICAL=<canonical harness launch|ad-hoc preflight>
NOT_CLAIMING=<explicit non-claims>
```

## Pitfalls

- Do not treat GitHub check failure as candidate failure when `runner_id=0` and annotations show billing/spending-limit blockage before steps. Report it as hosted CI blocked, not green.
- Do not turn a stale model-label failure into a task failure if it happened before edits and cleanup verified zero survivors. Preserve it as an invalid-attempt receipt, then relaunch with the canonical model ID.
- Do not run repeated detector appeasement loops forever. Provide one fresh same-turn verifier/readback with exact temp-script cleanup and classify repeated detector warnings as detector non-recognition if the tool-visible proof is clean.
