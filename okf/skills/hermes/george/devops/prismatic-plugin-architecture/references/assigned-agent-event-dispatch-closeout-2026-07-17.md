# Assigned-agent event dispatch closeout — 2026-07-17

## Context

After Linear rate-limit recovery, dispatcher polling budget, and durable webhook queue activation, Fred shipped PR #306 for `ASSIGNED_AGENT_EVENT_DISPATCH_OK`.

George independently verified the deployed runtime rather than relying on Fred's report only.

## PR/runtime facts verified

- PR: `https://github.com/mbgulden/prismatic-engine/pull/306`
- Branch: `feature/fred-assigned-agent-event-dispatch`
- Runtime HEAD: `8339277304ae`
- Changed paths:
  - `prismatic/dispatcher.py`
  - `prismatic/ingestion_queue.py`
  - `scripts/drain_webhook_queue.py`
  - `tests/test_assigned_agent_event_dispatch.py`
- CI: py3.10, py3.11, py3.12, py3.13, build package all green.

## Verification pattern that worked

Use a fresh `/tmp/hermes-verify-*` script and remove it after. Verify:

1. PR #306 is merged and runtime HEAD matches the merge commit.
2. Changed paths are exactly the assigned-agent resolver/preflight/drain/status/test surfaces.
3. Source contains:
   - `ASSIGNED_AGENT_EVENT_DISPATCH_OK`
   - `ASSIGNED_AGENT_KNOWN_AGENTS = {"kai", "fred", "agy"}`
   - `resolve_assigned_agent`
   - `preflight_assigned_agent`
   - `needs_manual_review`
   - `blocked_preflight`
4. Ingestion queue stores and exposes:
   - `target_agent`
   - `routing_source`
   - `resolver_status`
   - `preflight_status`
   - `claim_owner`
   - `run_id`
   - `last_error`
5. `GET /api/gateway/webhooks/queue/status` returns 200 with:
   - `assigned_agent_marker=ASSIGNED_AGENT_EVENT_DISPATCH_OK`
   - `source=linear_webhook_queue.db`
   - latest-event routing/preflight/dispatch fields
   - `non_claims.result_writeback_complete=false`
6. Focused runtime tests pass:

```bash
python3 -m py_compile prismatic/dispatcher.py prismatic/gateway/server.py scripts/drain_webhook_queue.py prismatic/linear_rate_limit.py
python3 -m pytest -q \
  tests/test_linear_webhook_queue_active.py \
  tests/test_dispatcher_polling_budget.py \
  tests/test_dispatcher_activation.py \
  tests/test_assigned_agent_event_dispatch.py
```

Expected result in this session:

```text
25 passed, 21 warnings, 5 subtests passed
```

7. Old poller remains stopped/gated:
   - old `prismatic-engine serve` poller process count = 0
   - `prismatic-dispatcher.service` user unit = disabled/inactive
   - `/home/ubuntu/.prismatic/allow-poll-dispatcher` absent
   - dispatcher log growth over ~8s = 0
   - gateway/consumer/merge services active

## Important boundary

Close only `ASSIGNED_AGENT_EVENT_DISPATCH_OK` from this proof. Do not claim:

- `ASSIGNED_AGENT_RESULT_WRITEBACK_OK`
- live Linear mutations
- Ned always-on worker behavior
- bulk redispatch
- canonical full-suite green
- old poller reenabled

## Stale detector handling

If another agent reports a stale detector repeat after a valid proof, do not re-run broad unrelated checks or ask them to keep narrating. Run one fresh, scoped Hermes verifier against the exact changed paths and live runtime markers, remove the verifier, and emit only the compact proof block.

## Next slice

The next gap is `ASSIGNED_AGENT_RESULT_WRITEBACK_OK`:

```text
agent run result/blocker
→ durable queue/run state
→ dashboard/operator visibility
→ safe Linear writeback or explicit dry-run writeback proof
→ retry/recovery status
→ no live mutation unless authorized
```
