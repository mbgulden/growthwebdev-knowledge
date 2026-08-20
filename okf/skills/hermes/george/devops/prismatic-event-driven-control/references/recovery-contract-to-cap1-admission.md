# Recovery contract → cap-1 same-worktree admission

Use this reference when a failed Prismatic producer leaves a blocked committed candidate and Michael authorizes a bounded same-worktree recovery, but not a replay of the original event.

## Durable sequence

1. **Preserve the failed producer boundary first.** Keep the original event/producers distinct: `ORIGINAL_TASK`, `ORIGINAL_EVENT_COUNT`, `ORIGINAL_REPLAYED=false`, `PRODUCER_COMPLETED=false`, exit/signal/source if known, and exact candidate `HEAD`/`TREE`/parent.
2. **Freeze repair contracts as artifacts, versioning every review repair.** When independent review finds a contract defect, preserve the old file/hash and create V2/V3/etc.; do not overwrite or relabel the blocked artifact.
3. **Do not treat `CLEAN/PASS` on the repair contract as event authorization.** Separate gates:
   - contract artifact `CLEAN/PASS`;
   - byte-identical bus/worktree task copies;
   - deployed admission envelope preflight `PASS`;
   - independent envelope/task-copy `CLEAN/PASS`;
   - Michael's explicit one-event/cap-1 authorization.
4. **When a review is procedurally invalid, record it as invalid and retry scoped review.** Do not count a subagent review that switched to unrelated project state or asked for out-of-scope files as artifact judgment; preserve hashes and event count unchanged while dispatching a tighter exact-artifact retry.
5. **Validate against deployed code, not remembered schemas.** Use the live immutable release parser/policy/launcher/config loaders and a disposable SQLite file for zero-mutation preflight. Expected drift can include body-required `idempotency_key`/`status`, nested response coordinates, context headers, consumer flags, producer launcher shape, whole-second freshness, and policy keys.
6. **Use trusted temporary control files only under validator-accepted parents.** If executable trust validation rejects a Hermes profile path because parent modes are group-writable, move only temporary wrapper/config files under a trusted Prismatic secrets/runtime parent; do not weaken filesystem checks or chmod broad directories.
7. **Execute exactly one POST and one ordinary consumer invocation.** After `HTTP=201` and `CONSUMER_STATUS=processed`, prove event-scoped SQLite rows, lifecycle sequence, `writer_lease_count=0`, `selectable_outbox=0`, restored policy/auth, and removed temporary configs.
8. **Bind live producer proof to the launch receipt, not guesses.** Read `launch-receipt.json`, `harness-run.json`, and `activity.json`; verify pane PID start ticks through `/proc/<pid>/stat`; use the receipt's tmux/session/manifest paths. Do not guess names.
9. **Attach a passive wait only after receipt identity matches.** Use `tail --pid=<pane_pid> -f /dev/null` as a Hermes background process with notify-on-complete. This is passive: no polling, no deadline, no kill.
10. **If the producer exits during closeout, reconcile terminal state instead of preserving stale running proof.** Do not repost, rerun the consumer, or launch a second producer. Terminal artifacts decide whether the next gate is exact-head review, archive reproduction, or fail-closed recovery.

## Proof packet fields

```text
TASK_ID=<internal repair task id>
CONTRACT_SHA256=<frozen task/contract hash>
ENVELOPE_SHA256=<reviewed admission envelope hash>
DEPLOYED_PREFLIGHT=PASS;release=<immutable release>;report=<path>
HTTP_STATUS=201
REPLAYED=false
EVENT_COUNT=1
CONSUMER_INVOCATION_COUNT=1
CONSUMER_STATUS=processed
CLAIM_ATTEMPT=1
LIFECYCLE=claimed,validated,launch_started,launched
LAUNCH_ID=<run id>
PANE_PID=<pid>
PANE_START_TICKS=<ticks>
PRODUCER_COMPLETED=false
VERIFICATION_STATUS=pending
ACTIVE_SLOT_COUNT=1
WRITER_LEASE_COUNT=0
SELECTABLE_OUTBOX=0
POLICY_RESTORED=true
CONTROL_AUTH_RESTORED=true
PASSIVE_WAIT=<Hermes process id>;tail_pid_<pid>;no_polling_no_deadline_no_kill
ORIGINAL_TASK=<do-not-replay task id>
ORIGINAL_EVENT_COUNT=1
ORIGINAL_REPLAYED=false
AD_HOC_OR_CANONICAL=ad-hoc targeted admission and live receipt proof
NOT_CLAIMING=producer completion, implementation correctness, candidate acceptance, canonical suite, PR, merge, deployment, cron/timer mutation, or Linear write
```

## Pitfalls

- A `CLEAN/PASS` repair contract is not permission to POST.
- A valid repair authorization for `CRONRUNNERR-1` is not authorization to replay `CRONRUNNER-1`.
- Local response-shape assertions are not canonical success/failure; SQLite readback and deployed consumer status are.
- Do not make profile-directory executables trusted by relaxing permissions; place temporary executables/configs where the deployed validator already trusts parent modes.
- Do not use fixed HEAD while a live producer is running; running producers may legitimately advance the worktree. Verify exact checkpoint ancestry and receipt-bound process state instead.
