# Task ID schema recovery and passive producer wait

Use this reference when a Prismatic event-admission slice is contract-ready but the deployed task-admission route rejects the task identifier or when launch completion must be separated from producer completion.

## Durable lesson

A task contract name can be semantically correct while the deployed admission schema still requires a bounded issue-style `task_id` (`<PREFIX>-<NUMBER>`). If the route returns HTTP `422`, treat it as a schema/admission failure, not a producer failure.

## Recovery pattern after HTTP 422

1. Prove the failed request caused no durable side effects before retrying:

```text
TASK_EXISTS=0
WRITER_LEASES=0
ACTIVE_CLAIMS=0
OUTBOX_ROWS_FOR_EVENT=0
TEMP_CONFIGS_REMOVED=true
POLICY_RESTORED=true
CONTROL_AUTH_RESTORED=true
```

2. Validate the corrected payload locally against the **deployed** schema before reopening any temporary credential/policy window.
3. Prefer an honest internal compliant ID such as `CRONAUTH-1` over borrowing or inventing a Linear-style number. Keep the upstream accepted contract/name in the task body and handoff.
4. Reuse the same bounded worktree/task content and re-admit only once through the canonical event + cap-1 consumer path.
5. Record both the rejected attempt and the compliant retry in the handoff so future sessions do not treat the rejected ID as a launched producer.

## Launch completion is not producer completion

The event consumer can reach `CLAIM_STATE=completed` once it has successfully launched the durable harness. That is only launch proof.

Required distinction:

```text
CLAIM_STATE=completed          # one-shot consumer launched the harness
HARNESS_STATE=running          # producer still active
PRODUCER_COMPLETED=false       # implementation not complete
VERIFICATION_STATUS=pending    # no candidate acceptance yet
```

Do not claim candidate correctness, acceptance, review readiness, PR readiness, merge readiness, deployment readiness, or successor admission from `CLAIM_STATE=completed` alone.

## Passive completion wait pattern

When Michael's policy is no frequent polling and AGY has no wall-clock cap, attach a passive PID-exit wait to the receipt-bound harness PID instead of adding cron/Telegram/API polling or an inactivity kill.

Pattern:

```bash
tail --pid=<pane_pid> -f /dev/null
python3 - <<'PY'
# after the producer exits, print canonical receipt/run-state/result paths,
# exact HEAD/tree, tracked status, and RESULT.md existence for the review lane
PY
```

Requirements:

- Use `pane_pid`, `session`, and paths from `launch-receipt.json` / `harness-run.json`; never guess tmux names or manifest paths.
- Use `notify_on_complete=true` for the bounded wait process so review begins on exit.
- Do not terminate or restart the producer from the wait job.
- Do not mutate Linear/GitHub/production from the wait job.

## Handoff fields to preserve

```text
TASK=<compliant internal ID>
UPSTREAM=<accepted contract or Linear issue>
STATUS=PRODUCER_RUNNING
BASE_COMMIT=<sha>
BASE_TREE=<tree>
TASK_SHA256=<sha256>
EVENT_ID=<task-admission:...>
CLAIM_ID=<uuid>
LAUNCH_ID=<harness id>
OUTBOX_STATUS=processed
CLAIM_STATE=completed
PRODUCER_PID=<pid>
PRODUCER_RUNNING=true
WRITER_CAP=1
TEMP_CONFIGS_REMOVED=true
NEXT_GATE=producer terminal result, exact-head local reproduction, independent review
NOT_CLAIMING=producer completion, candidate correctness, acceptance, push, PR, merge, Linear write, deployment, live DB migration, runner/cron activation, successor admission
```
