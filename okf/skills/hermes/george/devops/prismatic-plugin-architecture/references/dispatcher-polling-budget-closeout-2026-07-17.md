# Dispatcher polling budget closeout — 2026-07-17

Session lesson from George reviewing Fred's `DISPATCHER_POLLING_BUDGET_OK` slice.

## Context

The Linear event-driven dispatch recovery was split into staged markers:

```text
LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
DISPATCHER_POLLING_BUDGET_OK
LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
ASSIGNED_AGENT_EVENT_DISPATCH_OK
LINEAR_EVENT_DRIVEN_DISPATCH_RECOVERY_OK
```

After Slice 1 landed, PR #303 implemented Slice 2: a polling fallback safety net while keeping the old 30-second broad poller disabled/gated.

## Review pattern that worked

Verify Slice 2 against the deployed durable runtime checkout, not only the mutable dev worktree.

Required proof shape:

```text
PR merged + CI green
runtime head matches merge commit
/api/gateway/linear/rate-limit returns 200 and embeds polling_budget marker
/api/gateway/dispatcher/status returns 200 and embeds polling_budget marker
polling_budget.marker == DISPATCHER_POLLING_BUDGET_OK
old poller process == 0
prismatic-dispatcher.service disabled/inactive
ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher present
allow-file absent
dispatcher log growth == 0 over observation window
core services active
focused deployed-runtime tests pass
```

Do not require or invent a standalone `GET /api/gateway/dispatcher/polling-budget` route if the deployed implementation exposes the budget via existing status/rate-limit endpoints. In this session that route returned 405, while the real deployed proof was:

```text
GET /api/gateway/linear/rate-limit -> 200, polling_budget present
GET /api/gateway/dispatcher/status -> 200, polling_budget present
```

Report the nuance explicitly instead of failing the slice for the absent standalone route.

## What to verify statically

Changed/surface files included:

```text
prismatic/dispatcher.py
prismatic/gateway/server.py
prismatic/gateway/templates/dashboard.html
tests/test_dispatcher_linear_circuit_breaker.py
tests/test_dispatcher_polling_budget.py
```

Look for:

```text
DISPATCHER_POLLING_BUDGET_OK
DISPATCHER_POLLING_BUDGET_MARKER
get_dispatcher_polling_budget_snapshot
max_calls_per_cycle
cache_hits/cache_misses
linear_broad_poll_allowed
polling_budget in Gateway status payload
```

## Boundary language

Slice 2 only proves bounded/cached/paced/visible fallback polling. It does **not** prove:

```text
LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
ASSIGNED_AGENT_EVENT_DISPATCH_OK
live Linear mutations
old poller reenabled
canonical full-suite green
```

Next slice should be `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK` and should start from current queue/drain reality:

```text
POST /api/gateway/linear and POST /webhooks/linear exist
scripts/drain_webhook_queue.py exists
/home/ubuntu/.prismatic/db/linear_webhook_queue.db exists
prismatic-webhook-drain.service masked/inactive
prismatic-webhook-drain.timer disabled/inactive
linear_webhook_queue has only old processed fixture row unless newer proof exists
```

## Pitfall

Do not collapse `DISPATCHER_POLLING_BUDGET_OK` into full event-driven dispatch recovery. Treat it as the safety-net slice between circuit breaker and durable webhook queue activation.