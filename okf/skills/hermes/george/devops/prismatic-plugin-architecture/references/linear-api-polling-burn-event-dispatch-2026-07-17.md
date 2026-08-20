# Linear API polling burn / event-dispatch recovery — 2026-07-17

## Session learning

Michael asked for an audit of Linear API limits, what was burning them, and which existing branches/worktrees already solved or partially solved over-polling / event-based dispatch.

The durable technique was to audit **live API headers + service state + runtime code paths + logs + branch sources**, then produce both a full report and a Fred-first digest.

## Evidence pattern that worked

1. Query Linear with a minimal safe GraphQL request and record only headers, never token values:
   - `x-ratelimit-requests-limit`
   - `x-ratelimit-requests-remaining`
   - `x-ratelimit-requests-reset`
   - complexity limit/remaining/reset
2. Inspect runtime service state:
   - `prismatic-dispatcher.service`
   - `PRISMATIC_POLL_INTERVAL`
   - gateway/consumer/drain services and timers
3. Inspect runtime checkout, not only mutable dev checkout:
   - `/home/ubuntu/.prismatic/runtime/prismatic-engine`
4. Count dispatcher Linear call paths, not just process names.
5. Parse logs for rate-limit failures and endpoint noise.
6. Inspect webhook/event queue state and existing drainer/consumer scripts.
7. Rank existing branches/worktrees into reuse buckets.

## Concrete finding from this session

The Linear request-count limit was the bottleneck, not GraphQL complexity:

```text
x-ratelimit-requests-limit: 2500
x-ratelimit-requests-remaining: 15
x-ratelimit-complexity-limit: 3000000
x-ratelimit-complexity-remaining: 2999998
```

The active dispatcher ran every 30 seconds and made broad issue/label scans. Estimated idle-cycle calls:

| Code path | Calls/cycle |
|---|---:|
| `setup_pipeline_issues()` | 1 |
| `route_dispatch_ready_issues()` | 11 |
| per-agent `get_issues_with_label(agent::<name>)` for five agents | 5 |
| `recover_stalled_agy()` | 1 |
| `detect_origin_completions()` | 11 |
| **Minimum total** | **~29** |

At 30s interval this is about 3480 requests/hour, above the observed 2500/hour cap.

## Existing event-based foundations found

- `POST /api/gateway/linear` and `POST /webhooks/linear` existed as webhook intake.
- `scripts/drain_webhook_queue.py` existed to drain `linear_webhook_queue.db` with `dispatch_issue_by_identifier`.
- A consumer existed at `/home/ubuntu/.hermes/profiles/orchestrator/scripts/event_handlers/dispatch_consumer_v3.py` and was event-scoped rather than broad full-queue polling.
- The webhook drain service/timer existed as prior systemd units, but the active service was masked and the timer disabled/inactive.
- The queue DB was effectively empty/old-test-only, so webhook intake was not the active source of dispatch truth.

## Branch/source buckets to inspect first

A-source reuse candidates:

- `scripts/drain_webhook_queue.py`
- `POST /api/gateway/linear`, `POST /webhooks/linear`
- `dispatch_consumer_v3.py`
- `feature/fred-assigned-agent-wake-contract`
- `feature/fred-assigned-agent-behavior-contract`
- `feature/fred-dispatch-preflight-decision`

B-source candidates:

- `feature/fred-ingestion-queue-real-contract`
- `feature/fred-real-ingestion-recovery-adapters`
- `feature/fred-ingestion-queue-operator-semantics`
- `feature/fred-ingestion-attention-deeplink`

C/D background:

- backup `prismatic-webhook-drain.service.bak*` units
- Ned DLQ/empty-queue branches for health lessons only

## Recommended staged markers

Use these markers rather than one giant vague “fix polling” task:

```text
LINEAR_RATE_LIMIT_CIRCUIT_BREAKER_OK
DISPATCHER_POLLING_BUDGET_OK
LINEAR_WEBHOOK_QUEUE_ACTIVE_OK
ASSIGNED_AGENT_EVENT_DISPATCH_OK
LINEAR_EVENT_DRIVEN_DISPATCH_RECOVERY_OK
```

## Pitfalls

- Do not claim event-driven dispatch is active just because a webhook endpoint exists.
- Do not add another broad poller or increase `get_issues_with_label` scans.
- Do not enable an old drain timer until its service path points at the durable runtime checkout and proof passes.
- Do not expose Linear tokens or API keys in reports; record only header names/counts/reset timestamps.
- Dashboard polling local gateway routes can be noisy but is not necessarily Linear API burn unless the route internally calls Linear.
- A service can be “active” while the durable event queue is effectively empty; inspect queue DB counts.

## Fred digest shape

For Fred, use a short digest first and the full audit as appendix:

```text
status
live header proof
current burn source
existing work to reuse
current event path gaps
implementation order
Do-not-do list
compact verification packet format
```
