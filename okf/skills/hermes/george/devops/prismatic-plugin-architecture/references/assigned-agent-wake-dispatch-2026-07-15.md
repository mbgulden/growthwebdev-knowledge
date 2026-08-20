# Assigned-agent wake dispatch recovery (2026-07-15)

## Context

During ingestion queue / AGY recovery work, Michael clarified that the desired dispatch restoration is **not AGY-only** and **not an uncontrolled always-on worker**. The older useful behavior was closer to: tasks assigned/labeled for a named agent wake that specific agent to execute the task.

Target behavior:

```text
Linear issue/event
→ durable queue row
→ resolve intended agent from assignee/label/metadata
→ preflight that exact agent
→ wake/dispatch exactly that agent for exactly that task
→ agent produces result or blocker
→ Linear/dashboard update records what happened
```

## Important distinction

Do **not** equate multi-agent dispatch with always-on Ned-style polling. The immediate goal is event-triggered assigned-agent wake behavior:

```text
assigned/labeled for Kai → Kai wakes/claims exactly that task
assigned/labeled for Fred → Fred wakes/claims exactly that task
assigned/labeled for AGY → AGY wakes/claims exactly that task
unknown/ambiguous → needs_manual_review
```

Always-on worker behavior should remain optional/future unless explicitly requested, and only with pause/stop controls, rate limits, max-claim count, dependency guards, and dashboard-visible ownership.

## Gates to add after queue/drain proof

Use these markers when reviewing or prompting dispatch recovery work:

```text
ASSIGNED_AGENT_RESOLVER_OK
PER_AGENT_PREFLIGHT_OK
ASSIGNED_AGENT_WAKE_DISPATCH_OK
ASSIGNED_AGENT_RESULT_WRITEBACK_OK
ASSIGNED_AGENT_DISPATCH_RECOVERY_OK
```

Definitions:

- `ASSIGNED_AGENT_RESOLVER_OK` — routing inputs map to intended target agents and fail closed on unknown/ambiguous/disabled targets.
- `PER_AGENT_PREFLIGHT_OK` — the exact target agent is enabled and has valid runtime/model/provider/config before wake.
- `ASSIGNED_AGENT_WAKE_DISPATCH_OK` — dispatch wakes only the resolved agent for exactly one intended task; no batch/default-agent spillover.
- `ASSIGNED_AGENT_RESULT_WRITEBACK_OK` — Linear/dashboard record target agent, preflight status, dispatch status, result/blocker, and retry/recovery state.
- `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` — all of the above pass plus queue/drain proof and at least one real one-task execution proof.

## Suggested proof order

1. Preserve queue proof if still valid:
   - `INGESTION_QUEUE_DURABLE_CONTRACT_OK`
   - `INGESTION_QUEUE_DRAIN_SMOKE_OK`
   - `DASHBOARD_QUEUE_OPERATOR_PROOF_OK`
2. Prove resolver/preflight in temp/dry-run mode for `agent:kai`, `agent:fred`, `agent:agy`, and unknown/ambiguous.
3. Run exactly one AGY task proof first if recovering from the 2026 AGY model/config failure.
4. Prove one non-AGY assigned-agent wake in the safest possible way, preferably a tiny controlled Kai or Fred task.
5. Confirm dashboard/operator surfaces show target agent, routing source, preflight status, dispatch status, result/blocker, and retry/recovery.

## Pitfalls

- Do not frame the architecture as `Linear queue → AGY only`; AGY may be the first proof target but not the whole dispatch contract.
- Do not restore uncontrolled always-on Ned-style behavior unless explicitly requested and safety-gated.
- Do not bulk redispatch after one target resolves; prove one task first.
- Do not allow cross-agent task stealing unless deliberately configured.
- Do not claim `ASSIGNED_AGENT_DISPATCH_RECOVERY_OK` if only AGY works.
- Keep prompt/checklist docs on their own branch/PR; do not contaminate Fred’s implementation branch with unrelated review artifacts.
