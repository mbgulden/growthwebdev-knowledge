# Linear rate-limit circuit breaker closeout — 2026-07-17

Session context: Prismatic Linear request-count burn recovery after the old poll-driven dispatcher exhausted the Linear API budget. This reference captures the durable review/closeout pattern, not a one-off PR narrative.

## Slice boundary that worked

Treat recovery as staged markers, not one broad “fix polling” claim:

```text
LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
DISPATCHER_POLLING_BUDGET_OK
LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
ASSIGNED_AGENT_EVENT_DISPATCH_OK
LINEAR_EVENT_DRIVEN_DISPATCH_RECOVERY_OK
```

When Slice 1 lands, verify and report it as **circuit breaker + emergency poller stop only**. Preserve non-claims:

```text
NOT_CLAIMING=event_driven_dispatch_complete,webhook_queue_active,dispatcher_polling_budget_ok,Linear_budget_recovered_before_reset,Linear_mutations_applied,canonical_full_suite_green
```

## Live verification pattern for Slice 1

Use a fresh `/tmp/hermes-verify-*` script and remove it after. Avoid live Linear API calls unless the task explicitly requires them; local Gateway readback is enough for circuit state proof.

Checks that mattered:

```text
PR merged and CI green
runtime checkout head matches merge commit
/api/gateway/linear/rate-limit returns 200 with marker LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
prismatic-dispatcher.service user unit is disabled/inactive
old poll process `/home/ubuntu/.prismatic/venv_stable/bin/prismatic-engine serve` absent
ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher present
allow-file absent
dispatcher log size does not grow over a short interval
core services active: gateway, consumer, merge
focused py_compile and tests pass
```

Important security pitfall: `systemctl --user cat prismatic-dispatcher.service` can print `LINEAR_API_KEY=...`. Do **not** echo that raw output into chat or durable docs. If a log captured it, sanitize the log before reading/reporting and only report `token redacted` / `secret present` style facts.

## Code surfaces from Slice 1

Key runtime surfaces to inspect for the circuit-breaker pattern:

```text
prismatic/linear_rate_limit.py
prismatic/dispatcher.py
prismatic/gateway/server.py
prismatic/gateway/templates/dashboard.html
tests/test_linear_rate_limit.py
tests/test_linear_rate_limit_api.py
tests/test_dispatcher_linear_circuit_breaker.py
```

Expected implementation concepts:

```text
LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK marker
rate-limit header capture: x-ratelimit-requests-limit / remaining / reset
RATELIMITED / 429 detection
cooldown_active snapshot
ensure_linear_circuit_closed before Linear calls
record_linear_response_headers after successful Linear responses
trip_linear_circuit_from_error on HTTP/GraphQL rate-limit errors
local API: /api/gateway/linear/rate-limit
broad poll skip helper such as linear_broad_poll_allowed
```

## Slice 2 prompt shape

The next prompt after Slice 1 should be narrow and explicit:

```text
DISPATCHER_POLLING_BUDGET_OK
```

Goal:

```text
remaining poll fallback
→ max Linear calls/cycle
→ TTL cache for broad scans
→ route/agent/origin scans not every cycle
→ cooldown respected
→ budget state visible
→ event/webhook path remains primary
```

Prompt requirements:

- Do not re-enable the old 30-second broad poller as the primary path.
- Do not remove the `ConditionPathExists=/home/ubuntu/.prismatic/allow-poll-dispatcher` kill switch unless replaced by an equal/stronger safety gate.
- Do not add new broad `get_issues_with_label(...)` loops.
- Do not claim webhook queue / assigned-agent dispatch in the polling-budget slice.
- Add tests for call budget, TTL caching, cooldown skip, and dashboard/API budget state.

## Reporting lesson

When Fred is actively building, George’s highest-value lane is review/closeout and refreshed next-slice prompts. If Michael asks whether to send an older digest, provide a refreshed prompt reflecting the latest deployed slice rather than reusing the stale digest.