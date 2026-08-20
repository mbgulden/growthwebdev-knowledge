# Linear webhook queue closeout pattern — 2026-07-17

Use this reference when reviewing the `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK` slice after the rate-limit circuit breaker and dispatcher polling-budget slices have landed.

## Verified closeout shape

Expected staged ladder:

```text
LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
→ DISPATCHER_POLLING_BUDGET_OK
→ LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
→ ASSIGNED_AGENT_EVENT_DISPATCH_OK
```

For webhook queue closeout, verify the deployed runtime, not only the dev worktree:

```text
PR state = MERGED
runtime HEAD = merge commit
CI = py3.10, py3.11, py3.12, py3.13, build package success
core services = gateway / consumer / merge active
old poller process = 0
prismatic-dispatcher.service = disabled/inactive or gated inactive
ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher present
allow-file absent
dispatcher log growth = 0
```

## Runtime/API proof

Use local gateway APIs that do not make live Linear calls:

```text
GET /api/gateway/webhooks/queue/status
GET /api/gateway/webhooks/queue
```

Expected status semantics:

```text
marker=LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
source=linear_webhook_queue.db
pending_count / processed counts present
latest_event_status present
last_drain_result present after drain proof
last_drain_counts present after drain proof
```

## Required behavior to inspect

The drainer must respect the shared Linear rate-limit circuit before dispatching queued events. When cooldown is active:

```text
dispatch attempt count stays 0
row status becomes deferred_rate_limit
drain result becomes deferred_rate_limit
drain counts include deferred=1
```

Source markers that were useful to verify:

```text
scripts/drain_webhook_queue.py: deferred_rate_limit
scripts/drain_webhook_queue.py: _linear_dispatch_allowed
scripts/drain_webhook_queue.py: record_drain_result
scripts/drain_webhook_queue.py: deferred += 1
tests/test_linear_webhook_queue_active.py: test_rate_limit_cooldown_defers_without_dispatch_attempt
tests/test_linear_webhook_queue_active.py: test_webhook_drain_units_use_runtime_path_if_present
```

Also verify dashboard inline JavaScript with `node --check` after extracting the script, because queue status is dashboard-visible.

## Focused command pattern

```bash
python3 -m py_compile prismatic/gateway/server.py scripts/drain_webhook_queue.py prismatic/dispatcher.py prismatic/linear_rate_limit.py
python3 -m pytest -q tests/test_linear_webhook_queue_active.py tests/test_linear_rate_limit.py tests/test_dispatcher_polling_budget.py tests/test_dispatcher_activation.py
node --check /tmp/hermes-dashboard-inline-linear-webhook-queue.js
```

Label this as ad-hoc targeted runtime proof unless the project canonical full suite actually ran.

## Non-claims

Do not collapse webhook queue activation into assigned-agent dispatch. Even with durable intake, bounded drain, queue APIs, cooldown deferral, and dashboard status working, the next slice remains:

```text
ASSIGNED_AGENT_EVENT_DISPATCH_OK
```

That next slice must prove exact-agent resolver/preflight/wake behavior for Kai/Fred/AGY/future agents, fail-closed manual review for unknown/ambiguous routing, result/blocker writeback, and no broad poller or cross-agent stealing.

## Pitfalls

- Do not fail a closeout because a guessed standalone route is absent; verify the routes actually implemented by the slice.
- Do not read/report `systemctl cat` output verbatim when units include environment secrets. Check for the needed condition gate but redact/avoid printing env lines.
- Do not create `/home/ubuntu/.prismatic/allow-poll-dispatcher` during verification.
- Do not claim live Linear mutations unless intentionally performed and separately authorized/proven.
