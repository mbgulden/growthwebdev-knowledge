# Linear webhook queue activation — July 2026 pattern

Use when moving Linear dispatch recovery from bounded fallback polling to durable webhook/event intake.

## Scope boundary

`LINEAR_WEBHOOK_QUEUE_ACTIVE_OK` proves durable intake + bounded drain + operator visibility. It does **not** prove assigned-agent wake/dispatch. Do not claim `ASSIGNED_AGENT_EVENT_DISPATCH_OK` until exact-agent resolver, preflight, wake, and one intended task dispatch are implemented and proven.

## Durable intake contract

- `POST /api/gateway/linear` and `/webhooks/linear` must persist a row in `linear_webhook_queue.db` for relevant Linear issue events.
- Row must include: `event_id`/idempotency key, identifier, event type/action, received timestamp, raw/sanitized payload, `dispatch_status`, and agent label/name when available.
- Duplicate fixture webhook with the same `event_id` must not create duplicate dispatch work.
- Default production state must be durable (`~/.prismatic/db`), not repo-local mutable state.

## Bounded drain contract

- `scripts/drain_webhook_queue.py` must support bounded run shape (`--max`, single batch/once semantics; no infinite loop).
- Pending issue events with an `agent:*` label may call the single-issue dispatch function; tests should inject a stub dispatch function to prove exactly one intended attempt without live Linear mutations.
- Terminal/decision statuses should be persisted: `dispatched`, `no_op`, `failed`, `stale`, `deferred_rate_limit`/manual-review equivalent.
- Before dispatch attempts, check the shared Linear rate-limit circuit. If cooldown is active, do **not** call dispatch; set `deferred_rate_limit`, record drain result/counts, and return without crash-looping.

## API/dashboard visibility

Expose an operator status endpoint/card with:

- `marker=LINEAR_WEBHOOK_QUEUE_ACTIVE_OK`
- `source=linear_webhook_queue.db` or documented equivalent
- `queue_depth` / `pending_count`
- processed/status counts
- latest event identifier/status
- `last_drain_at`, `last_drain_result`, and drain counts

## Service/timer rule

Do not enable or unmask `prismatic-webhook-drain.service`/timer until its `ExecStart` points at the durable runtime checkout (`/home/ubuntu/.prismatic/runtime/prismatic-engine`) or stable venv entrypoint, never `/home/ubuntu/work/prismatic-engine`. It is acceptable for this slice to leave the service masked/disabled if manual bounded drain proof is complete.

## Required focused tests

1. Fixture webhook persists exactly one durable row.
2. Duplicate fixture webhook is idempotent.
3. Drain processes one pending row into `dispatched`/`no_op`/`failed` without broad polling.
4. Rate-limit cooldown prevents dispatch attempt and records blocked/deferred status.
5. API/dashboard queue status reflects pending and processed rows.
6. Service/timer unit path, if present/changed, uses durable runtime path.

## Verification packet shape

Use fresh tempfile-created `/tmp/hermes-verify-*` scripts and clean them up. Minimum commands:

```bash
python3 -m py_compile prismatic/gateway/server.py scripts/drain_webhook_queue.py prismatic/dispatcher.py prismatic/linear_rate_limit.py
python3 -m pytest -q tests/test_linear_webhook_queue_active.py tests/test_linear_rate_limit.py tests/test_dispatcher_polling_budget.py
node --check /tmp/hermes-dashboard-inline-linear-webhook-queue.js
```

Add a tempfile fixture DB/state proof for idempotency, one dispatch attempt, cooldown deferral with zero dispatch calls, status API fields, old poller disabled/gated, and no allow-file.

Emit compact KEY=VALUE proof:

```text
COMMAND=<exact command or grouped summary>
RESULT=PASS|FAIL|BLOCKED
LOG=/tmp/<topic>.log
SCOPE=durable Linear webhook/event queue intake + bounded drain + dashboard/API status
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=ASSIGNED_AGENT_EVENT_DISPATCH_OK,live_Linear_mutations,old_poller_reenabled,canonical_full_suite_green
MARKER=LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
cleanup=PASS
```
