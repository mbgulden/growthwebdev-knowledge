# Cap-1 event admission and live-run proof

Use this reference when Michael authorizes advancing the next safe Prismatic slice through the event-driven gate, with explicit boundaries: do not bypass dependencies, exact-head review, producer cap, or merge/deploy authorization; report only exceptions and authorization points.

## Admission sequence

1. Re-read current handoff/task contract and verify the prior dependency is terminally reconciled.
2. Verify the deployed immutable release, gateway health, exact task/worktree hash, cap-1 runtime config, queue idle predicate, zero writer leases, and zero active producers before mutation.
3. Check that the launcher registry/private AGY runtime registry are bound to the currently deployed canonical release. If a preserved launcher points to an older release, do not reuse it; create a narrowly scoped temporary launcher/registry for the current immutable release, with rollback copies and removal proof.
4. Narrow the admission policy only as much as required for the specific task/worktree/producer identity; back up the previous policy first.
5. If a one-time operator credential is required, add only a temporary hashed credential, POST exactly one authenticated admission event, then restore the credential file in a `finally`/rollback path. Never print tokens or hashes that would aid reuse.
6. Read back SQLite/event-log state directly. Event success proof is event-scoped: outbox row, claim row, lifecycle rows, attempt count, and launch receipt JSON. Do not rely on global historical claim counts. If a local wrapper raises after the event is already persisted or launched, stop and reconcile the existing event; do not repost unless event-scoped readback proves no durable side effect.
7. Invoke the ordinary one-shot consumer once. Do not call a producer directly and do not invoke the consumer again while the admitted producer is running. If the shell/tool invocation is blocked before execution (for example malformed workdir/tool arguments), prove no producer launched/event state did not advance, then reissue the same one-shot command correctly; this is not a second consumer invocation.
8. Restore the previous admission policy immediately after the event is launched so the admission window is closed, and remove temporary launcher/registry files. Include byte-for-byte restore/removal evidence in the closeout.

## Live-run proof

Bind proof to canonical artifacts, not guessed names:

```text
EVENT_ID=<task-admission:...>
CLAIM_ID=<claim uuid>
ATTEMPT=1
LAUNCH_ID=<harness run id>
OUTBOX_STATUS=processed
CLAIM_STATE=completed
SELECTABLE_EVENTS=0
WRITER_LEASES=0
CAP=1
ACTIVE_SLOT_BOUND=true
POLICY_RESTORED=true
CONTROL_AUTH_RESTORED=true
TEMP_CONFIGS_REMOVED=true
EXACT_CHANGED_PATHS=<allowed count>
SCOPE_MATCH=true
```

Use `AGYCLIHarness.status(<launch_id>)` for producer state. Tmux checks must use the `session` recorded in `launch-receipt.json`; do not guess session prefixes. The absence of a guessed prefix match is not proof the producer is gone.

Expected healthy running state:

```text
RUN_STATUS=running
PRODUCER_COMPLETED=false
VERIFICATION_STATUS=pending
PROCESS_ALIVE=true
CLASSIFICATION=working
RUNTIME_DEADLINE=None
AUTOMATIC_KILL=false
```

## Reporting boundaries

- Report exceptions and authorization points only if Michael requested that mode.
- While the producer runs, do not create cron/Telegram polling, do not add inactivity kills, and do not claim source correctness, review, merge readiness, or deployment readiness. If Michael wants a completion signal, attach a receipt-bound passive PID-exit wait such as `tail --pid=<pane_pid> -f /dev/null` in a tracked background process with notify-on-complete; it must not poll APIs, impose a deadline, or terminate the producer.
- Next authorization point is after durable completion and independent exact-head verification/review. Deployment remains separate explicit authorization.

## Common traps

- Disabling a legacy `Restart=always` consumer may not contain it when a timer-activated watchdog has `BindsTo=`/dependency edges that start it again. Inspect timer/unit dependencies. If explicitly authorized to mask a direct `/etc/systemd/system/<unit>` file, preserve the exact unit and digest, move it to a rollback filename, create the `/dev/null` mask, daemon-reload, disable the restarter timer, and observe beyond one former timer interval.
- The task-admission route schema uses a bounded issue-style task ID (for example `EVCONV-1`); a long descriptive task name can fail with 422 before persistence. Validate the exact payload against the deployed schema before opening credentials.
- The authenticated admission POST must send `Idempotency-Key` equal to the payload's `idempotency_key`. A valid bearer token without that header reaches the route but fails `admission_context_missing` with HTTP 401; prove no event persisted, then retry the same unadmitted task with the required header rather than changing credentials or bypassing the route.
- Admission policy files must retain private fail-closed mode (normally `0600`). A temporary `0644` replacement correctly yields `admission_policy_unavailable`/503.
- The outer launcher map and the private AGY runtime task registry are separate dependencies. A successful one-shot AGY launch requires `PRISMATIC_TASK_ADMISSION_AGY_CONFIG` plus an exact task binding in that private registry. Back up/narrow/restore both policy and registry. If the event persisted but launch failed, do not repost; repair the dependency and consume the existing retryable event once within attempt limits.
- API response shape may be compact or use `status` instead of a local wrapper's expected `state`. If the wrapper fails after a successful POST/consumer call, first read back `task_admissions`, `task_admission_outbox`, `task_admission_consumer_claims`, lifecycle rows, and launch artifacts. If they prove `processed`/`completed`/`launched`, write the durable receipt manually, record the wrapper mismatch, and do **not** repost or re-consume.
- Historical claims can make global claim-count assertions fail. Scope admission/claim checks to the new `event_id`.
- A manifest may be named `manifest.json` rather than `launch-manifest.json`; inspect actual artifact names rather than asserting a guessed filename.
- Tmux session names are receipt-bound. Query the exact `session` from `launch-receipt.json`.
