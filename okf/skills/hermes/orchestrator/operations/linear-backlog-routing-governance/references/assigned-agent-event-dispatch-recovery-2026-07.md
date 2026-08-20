# Assigned-agent event dispatch recovery — July 2026

Use this reference when restoring Linear webhook/event dispatch after the rate-limit circuit breaker, polling budget, and durable webhook queue slices are already landed.

## Goal

Restore the useful path without re-enabling the old broad poller:

`Linear webhook event → durable linear_webhook_queue row → exact intended agent resolver → per-agent preflight → exactly one wake/claim → operator-visible queue/API state`

This is assigned-agent recovery, not AGY-only. The architecture must support Kai, Fred, AGY, and future named agents through the same resolver/preflight/wake contract.

## Non-negotiables

- Do **not** re-enable the old 30-second broad poller.
- Do **not** create `/home/ubuntu/.prismatic/allow-poll-dispatcher`.
- Do **not** wake all agents for one event.
- Do **not** allow cross-agent stealing: Fred work must not wake Kai, Kai work must not wake AGY, etc.
- Do **not** bulk-redispatch old backlog while proving the event path.
- Do **not** claim result writeback unless actual completion/result/blocker writeback is implemented and proven separately.
- Prefer fixture/dry-run writeback proof; no live Linear mutations unless explicitly authorized.

## Implementation shape

1. **Resolver**
   - Input: durable queue row / webhook payload metadata.
   - Look for `agent:<name>` / `agent::<name>` labels first, then explicit `agent`, `agent_name`, or `target_agent` metadata.
   - Known minimum agents: `kai`, `fred`, `agy`.
   - Outcomes:
     - exactly one known agent → `resolved` with `target_agent` and `routing_source`
     - no agent metadata → `needs_manual_review`, zero wakes
     - conflicting agents → `needs_manual_review`, zero wakes
     - unknown agent → `needs_manual_review`, zero wakes
     - known-but-disabled agent → resolve target, then fail preflight, zero wakes

2. **Preflight**
   - Fail closed before waking anything.
   - Check row state is not already terminal/claimed/running/completed.
   - Check target agent is enabled and has a launcher/runtime path.
   - Check shared Linear rate-limit circuit before a dispatch attempt.
   - Persist `preflight_status`, `dispatch_status`, and `last_error`.
   - Use `deferred_rate_limit` for cooldown, `blocked_preflight` for agent/runtime/claimed failures.

3. **Exactly-one wake**
   - One event may wake only the resolved target agent.
   - Fixture proof should use dry-run/stub launchers and assert:
     - `agent:kai` → wakes only Kai
     - `agent:fred` → wakes only Fred
     - `agent:agy` → wakes only AGY
     - ambiguous/missing/unknown/disabled/claimed/cooldown → wakes nobody

4. **Durable queue/API state**
   - Extend `linear_webhook_queue` or equivalent with operator-visible fields:
     - `target_agent`
     - `routing_source`
     - `resolver_status`
     - `preflight_status`
     - `dispatch_status`
     - `claim_owner`
     - `run_id`
     - `last_error`
     - `updated_at`
   - Expose `ASSIGNED_AGENT_EVENT_DISPATCH_OK` separately from the queue activation marker so prior `LINEAR_WEBHOOK_QUEUE_ACTIVE_OK` proof remains intact.
   - `/api/gateway/webhooks/queue/status` should be enough for George/operator verification without reading source files.

## Verification pattern

Use a fresh tempfile-created `/tmp/hermes-verify-*` script and remove it after. Keep detailed logs under `/tmp/fred-assigned-agent-event-dispatch-verify.log` and print compact `KEY=VALUE` lines.

Minimum command set:

```bash
python3 -m py_compile prismatic/dispatcher.py prismatic/gateway/server.py scripts/drain_webhook_queue.py prismatic/linear_rate_limit.py
python3 -m pytest -q \
  tests/test_linear_webhook_queue_active.py \
  tests/test_dispatcher_polling_budget.py \
  tests/test_dispatcher_activation.py \
  tests/test_assigned_agent_event_dispatch.py
```

Runtime/local fixture proof should include:

- temp `PRISMATIC_STATE_DIR` / fixture DB
- `PRISMATIC_ASSIGNED_AGENT_DRY_RUN=1`
- Kai/Fred/AGY each produce exactly one dry-run wake/claim
- ambiguous fixture produces `needs_manual_review` and zero wakes
- queue status/API includes marker and routing/preflight/dispatch fields
- old poller process count is zero
- `prismatic-dispatcher.service` remains disabled/inactive or gated inactive
- allow-file remains absent
- core services stay active after deploy

## Compact proof block

```text
COMMAND=<exact command or grouped summary>
RESULT=PASS
LOG=/tmp/fred-assigned-agent-event-dispatch-verify.log
SCOPE=assigned-agent resolver + per-agent preflight + exactly-one wake/dispatch + dashboard/API state
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=old_poller_reenabled,bulk_redispatch,Ned_always_on_worker,live_Linear_mutations,canonical_full_suite_green,ASSIGNED_AGENT_RESULT_WRITEBACK_OK
MARKER=ASSIGNED_AGENT_EVENT_DISPATCH_OK
cleanup=PASS
```

## Pitfalls

- Do not let a truthy result dict from a dispatcher compatibility function automatically become `dispatched`; inspect `result["status"]` so `needs_manual_review`, `blocked_preflight`, and `deferred_rate_limit` persist correctly.
- Do not skip missing-agent rows as `no_op` before the resolver sees them; missing metadata must become `needs_manual_review` with zero wakes.
- Keep result/blocker writeback as the next slice (`ASSIGNED_AGENT_RESULT_WRITEBACK_OK`) unless actual agent completion has been proven.