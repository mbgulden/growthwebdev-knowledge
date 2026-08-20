# Multi-agent dispatch recovery gates — 2026-07-15

## Session learning

Michael clarified that Prismatic dispatch recovery must not be scoped as an AGY-only repair. AGY is the first visible broken path because of the invalid model/config failure, but the class-level behavior Michael wants restored is broader:

```text
Linear/task event
→ durable queue
→ agent resolver
→ per-agent preflight
→ safe dispatch / wake-up behavior
→ execution result
→ dashboard-visible state
→ retry/recovery
```

Historical expected behavior: when work is assigned/labeled for Kai, Kai wakes and executes it. Fred should wake for Fred work. AGY should wake for AGY work. Always-on workers like Ned can claim eligible work, but only with safety rails.

## Architecture distinction to preserve

Separate these layers explicitly:

1. **Durable ingestion queue** — stores Linear/task/webhook events (`linear_webhook_queue.db` or configured durable state).
2. **Agent resolver** — maps assignee/labels/metadata/routing rules to a target agent such as `kai`, `fred`, `agy`, `ned`.
3. **Per-agent preflight** — validates that the target agent is enabled, configured, has valid model/provider/runtime, supports the task type, and can safely accept it.
4. **Dispatch / wake-up layer** — one-shot dispatch or always-on worker claim/heartbeat behavior.
5. **Execution evidence** — input/output tokens or equivalent, result artifact/log path, Linear comment/state update, dashboard state.
6. **Operator dashboard** — queued/claimed/running/completed/failed/retryable/stale/blocked work by target agent.

## Gates to add beyond AGY proof

Keep `AGY_SINGLE_TASK_PROOF_OK` as the first proof when recovering from AGY-specific failures, but do not stop there if Michael asks for dispatch generally.

Add these gates:

```text
AGENT_RESOLVER_OK
PER_AGENT_PREFLIGHT_OK
MULTI_AGENT_DISPATCH_CONTRACT_OK
ALWAYS_ON_WORKER_SAFETY_OK
```

### `AGENT_RESOLVER_OK`

Proves assignment/label/metadata can map a task to a target agent; unknown/disabled/ambiguous agents fail closed with a reason, usually `needs_manual_review`.

### `PER_AGENT_PREFLIGHT_OK`

Proves each target agent has runtime/model/provider/task-type validation. Invalid model aliases must be caught before launch; unsupported task types fail closed with a visible reason.

### `MULTI_AGENT_DISPATCH_CONTRACT_OK`

Proves at least two target agents are resolved/preflighted correctly, at least one real task dispatch succeeds end-to-end, no unrelated work launches, and the dashboard shows target agent + status/result/blocker reason.

### `ALWAYS_ON_WORKER_SAFETY_OK`

Required before restoring Ned-style always-on behavior. Proves the worker claims only eligible assigned tasks, respects max-claim/rate limits, records heartbeat/claim ownership, can be paused/stopped, and does not execute stale/future-stage tasks automatically.

## Safety rules

Do not recreate an uncontrolled always-on worker. Require:

- enabled-agent allowlist;
- clear routing rules;
- per-agent preflight;
- dependency/stage guardrails;
- one-task proof before batch/always-on mode;
- rate limits / max claim count;
- dry-run mode;
- dashboard-visible claimed/running/completed/failed states;
- operator stop/pause control;
- no secret leakage;
- no cross-agent task stealing unless explicitly configured.

## Review packet section to request from Fred/implementation agents

Ask for this section when reviewing dispatch recovery:

```markdown
## Multi-agent dispatch recovery

### Current support
- AGY:
- Kai:
- Fred:
- Ned / always-on worker:
- Future agents:

### Routing sources checked
- Linear assignee:
- Linear labels:
- task metadata:
- fallback/default behavior:

### Gate results
| Gate | Result | Evidence | Notes |
|---|---|---|---|
| AGENT_RESOLVER_OK | PASS/BLOCKED |  |  |
| PER_AGENT_PREFLIGHT_OK | PASS/BLOCKED |  |  |
| MULTI_AGENT_DISPATCH_CONTRACT_OK | PASS/BLOCKED |  |  |
| ALWAYS_ON_WORKER_SAFETY_OK | PASS/BLOCKED/N/A |  |  |

### Smallest next fix
- If blocked, name the missing piece and the next proof command.
```

## Prompt artifact from the session

The session produced a Fred handoff addendum doc:

```text
/home/ubuntu/work/prismatic-engine/docs/prompt-for-fred-multi-agent-dispatch-recovery-addendum-2026-07-15.md
```

That path is session-specific and may move; the durable reusable content is captured in this reference.
