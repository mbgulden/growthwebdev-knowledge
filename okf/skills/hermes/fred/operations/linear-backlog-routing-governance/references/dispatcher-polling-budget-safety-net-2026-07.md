# Dispatcher Polling Budget Safety Net — July 2026

Use this reference after `LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK` is already landed and the next goal is to make any remaining Linear poll fallback cheap, bounded, observable, and secondary to webhook/event dispatch.

## Durable pattern

1. **Keep the old poller gated while coding**
   - Do not re-enable the 30-second `prismatic-engine serve` poller just to test fallback logic.
   - Preserve the reversible user-systemd kill switch: `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher` with the allow-file absent unless an operator explicitly opts in.
   - Verify gateway/consumer/merge services independently; keeping them active is not the same as restoring the poller.

2. **Per-cycle Linear call budget**
   - Add a dispatcher-local cycle budget object around Linear GraphQL calls.
   - Configuration knobs used in this slice:
     - `PRISMATIC_POLL_MAX_LINEAR_CALLS_PER_CYCLE` — hard cap; default used was `6`.
     - `PRISMATIC_POLL_FALLBACK_ENABLED` — explicit fallback enable/disable gate.
   - Each `gql(..., source=...)` call consumes one budget unit when a cycle budget is active.
   - Budget exhaustion should set visible status and skip remaining broad scans; it must not crash-loop the dispatcher.

3. **TTL cache broad label/team scans**
   - Cache `get_issues_with_label(label, team_id, max_issues)` results with `PRISMATIC_POLL_LABEL_SCAN_TTL_SECONDS` (default used was `300`).
   - Track `cache_hits` and `cache_misses` in dispatcher budget status.
   - Return a copy/deep-copy-style value from cache so caller mutation cannot poison the cached row set.

4. **Cadence broad scan sections**
   - Do not run all broad scans every fallback tick. Gate them separately:
     - `PRISMATIC_POLL_PIPELINE_SCAN_CADENCE`
     - `PRISMATIC_POLL_ROUTE_SCAN_CADENCE`
     - `PRISMATIC_POLL_AGENT_SCAN_CADENCE`
     - `PRISMATIC_POLL_RECOVERY_SCAN_CADENCE`
     - `PRISMATIC_POLL_ORIGIN_SCAN_CADENCE`
   - The July 2026 slice used a low idle-call profile: agent label scans can run as a small fallback, while pipeline/route/recovery/origin scans are slower cadence.
   - Record skipped sections and `last_skip_reason` so the dashboard can distinguish `idle`, `budget-exhausted`, `cadence-skipped`, and `cooldown` states.

5. **Respect the Slice 1 circuit breaker first**
   - Before broad fallback scans, read the Linear rate-limit/cooldown state.
   - If cooldown is active: do not spend another Linear request; mark `rate_limit_cooldown_active=true` and skip broad polling.

6. **Dashboard/API proof fields**
   - Surface `polling_budget` beside Linear rate-limit state in:
     - `/api/gateway/linear/rate-limit`
     - `/api/gateway/dispatcher/status`
   - Minimum fields:
     - `marker=DISPATCHER_POLLING_BUDGET_OK`
     - `poll_fallback_enabled`
     - `max_calls_per_cycle`
     - `calls_used_this_cycle` / `last_cycle_calls`
     - `calls_remaining_this_cycle`
     - `calls_by_source`
     - `cache_hits` / `cache_misses`
     - `skipped_sections`
     - `last_skip_reason`
     - `rate_limit_cooldown_active`
     - cadence values

## Tests to add

- Idle fallback cycle stays below configured cap.
- Budget exhaustion skips remaining broad scans without crashing.
- TTL cache prevents repeated same-label Linear scans inside TTL.
- Active Linear cooldown prevents broad polling entirely.
- Gateway API exposes budget state.

## Verification shape

Use a fresh `tempfile.mkstemp(prefix='hermes-verify-dispatcher-polling-budget-', dir='/tmp')` script. Keep it no-live-Linear: use local focused tests, py_compile, dashboard JS syntax check, and runtime API readback only.

Minimum command packet:

```text
python3 -m py_compile prismatic/dispatcher.py prismatic/linear_rate_limit.py prismatic/gateway/server.py && \
python3 -m pytest -q tests/test_linear_rate_limit.py tests/test_linear_rate_limit_api.py tests/test_dispatcher_linear_circuit_breaker.py tests/test_dispatcher_polling_budget.py tests/test_dispatcher_activation.py && \
node --check /tmp/hermes-dashboard-inline-dispatcher-polling-budget.js
```

If deployed, add live readback without Linear API calls:

- runtime HEAD equals merge commit
- `/api/gateway/linear/rate-limit` returns `LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK` and nested `polling_budget.marker=DISPATCHER_POLLING_BUDGET_OK`
- `/api/gateway/dispatcher/status` includes the same `polling_budget` marker
- `prismatic-dispatcher.service` remains disabled/gated
- `/home/ubuntu/.prismatic/allow-poll-dispatcher` remains absent
- exact old poller process count is 0
- dispatcher log has no growth during observation window

## Non-claims

Do not claim these from this slice:

- `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK`
- `ASSIGNED_AGENT_EVENT_DISPATCH_OK`
- live Linear mutations
- old poller re-enabled
- webhook queue is active
