# Linear event-driven dispatch recovery — July 2026

## Trigger
Use this reference when Linear request-count budget is near exhaustion and a Prismatic dispatcher or watchdog may be burning requests through broad label polling.

## Key distinction
Linear's **request-count** limit can exhaust even when GraphQL complexity remains healthy. Header proof to capture:

```text
x-ratelimit-requests-limit
x-ratelimit-requests-remaining
x-ratelimit-requests-reset
x-ratelimit-complexity-limit
x-ratelimit-complexity-remaining
```

If request remaining is low, stop broad polling first; do not spend the remaining budget on exploratory Linear queries.

## Emergency mitigation pattern
1. Inspect both system and user systemd units. The active burn can be a user service even when the system unit is inactive:
   - `systemctl list-units --all 'prismatic*'`
   - `XDG_RUNTIME_DIR=/run/user/1000 DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus systemctl --user status prismatic-dispatcher.service`
2. Find actual poller processes and confirm env before stopping:
   - process shape: `prismatic-engine serve`
   - env clue: `PRISMATIC_POLL_INTERVAL=30` plus `LINEAR_API_KEY`
3. Stop only the poll-driven dispatcher. Keep gateway/event consumer/merge services up when active.
4. Disable the user unit and add a reversible condition gate instead of deleting the unit:

```ini
# ~/.config/systemd/user/prismatic-dispatcher.service.d/10-linear-budget-kill-switch.conf
[Unit]
ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher
```

5. Verify:
   - no `prismatic-engine serve` poller process
   - user dispatcher unit disabled
   - condition gate present and allow-file absent
   - dispatcher log has no growth over 20–40s
   - `prismatic-gateway.service`, `prismatic-consumer.service`, and `prismatic-merge.service` remain active
   - no live Linear API calls during verification

## Slice 1: request-count circuit breaker
Add a shared module rather than more local try/excepts:

- persist local state under `PRISMATIC_LINEAR_RATE_LIMIT_STATE`, falling back to `PRISMATIC_STATE_DIR/linear_rate_limit_state.json`
- read `x-ratelimit-requests-*` headers after every Linear response
- detect GraphQL `RATELIMITED` errors and trip cooldown until reset
- make dispatcher `gql()` check the circuit before network calls
- skip broad polling sections while cooldown is active:
  - pipeline setup scans
  - `route_dispatch_ready_issues()`
  - per-agent label scans
  - stalled AGY recovery scan
  - origin completion detection
- leave local/event paths and stale process cleanup available
- expose state via dashboard/API, e.g. `/api/gateway/linear/rate-limit` and embedded `dispatcher.status.linear_rate_limit`

## Verification contract
Use a fresh `/tmp/hermes-verify-*` script and print compact KEY=VALUE lines. Required assertions:

```text
CANONICAL_TEST_LINT_BUILD_COMMAND=python3 -m py_compile ... && python3 -m pytest -q ... && node --check ...
AD_HOC_VERIFICATION=PASS
MARKER=LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
NOT_CLAIMING=event_driven_dispatch_complete,webhook_queue_active,dispatcher_polling_budget_ok,Linear_budget_recovered_before_reset,Linear_mutations_applied
cleanup=PASS
```

Do not call Linear in the verifier. Mock headers/errors and use local gateway readback only.

## Architecture target after circuit breaker
Move toward:

```text
Linear webhook → durable event/queue row → resolve assigned agent → preflight → dispatch exactly one intended issue → write result/blocker state → dashboard/Linear visibility
```

Do not restore uncontrolled always-on Ned/AGY/Fred polling as the primary mechanism. Treat polling as a low-frequency, budgeted safety net only.
