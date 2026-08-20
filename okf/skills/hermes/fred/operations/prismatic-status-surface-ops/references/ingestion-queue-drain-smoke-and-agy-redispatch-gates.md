# Ingestion Queue Drain Smoke and AGY Redispatch Gates

Session pattern captured from the July 2026 Prismatic dashboard/ingestion queue recovery after Kai’s audit documents were handed back to Fred.

## Trigger

Use this when the durable Ingestion Queue tab is mostly restored but Michael/Kai asks for proof before claiming readiness, especially when the requested marker is:

```text
INGESTION_QUEUE_DRAIN_SMOKE_OK
```

or the larger marker is being considered:

```text
DASHBOARD_DISPATCH_INGESTION_READY_OK
```

## Boundary

Do **not** claim `DASHBOARD_DISPATCH_INGESTION_READY_OK` unless all of these are true:

1. governance dashboard contract passes in a dependency-complete environment;
2. durable queue payload/stats/retry/purge work against `linear_webhook_queue.db`;
3. bounded drain proves a real status transition;
4. AGY dispatcher model/preflight is fixed;
5. exactly one AGY task proof, starting with GRO-3837, consumes and emits nonzero tokens and ends with a real `DONE: GRO-3837 ...` result.

If only the queue/drain proof passes, the correct final marker is:

```text
INGESTION_QUEUE_DRAIN_SMOKE_OK
```

## Preserve-before-proof rules

- Do not reset away the durable ingestion queue work.
- Do not replace `linear_webhook_queue.db` with EventBus-only, mock, or static queue rows.
- Do not reintroduce old compatibility no-op strings for retry/purge.
- Do not classify missing dependencies as app failures; retry inside the project venv first, e.g. `/home/ubuntu/.prismatic/venv_stable/bin/python3`.
- Do not bulk dispatch AGY/RC task trees while proving queue readiness.

## Dependency-complete dashboard contract

Run the existing contract in the project venv before declaring the dashboard contract blocked:

```bash
cd /home/ubuntu/work/prismatic-engine
/home/ubuntu/.prismatic/venv_stable/bin/python3 scripts/verify-governance-dashboard-contract.py
```

Expected useful signal:

```text
AD_HOC_VERIFICATION: PASS
scope: Governance dashboard regression contract: all tabs use live adapters, no mock/static regressions
failures: []
```

Important queue expectations:

```text
/api/webhooks/queue           -> source linear_webhook_queue.db
/api/gateway/webhooks/queue   -> source linear_webhook_queue.db
/api/webhooks/stats           -> source linear_webhook_queue.db
/api/gateway/webhooks/stats   -> source linear_webhook_queue.db
```

## Focused drain smoke pattern

Use a temporary verifier under `/tmp` with `tempfile.NamedTemporaryFile(prefix="hermes-verify-", suffix=".py", dir="/tmp", delete=False)` and an isolated state dir:

```python
state = Path(tempfile.mkdtemp(prefix='hermes-queue-state-', dir='/tmp'))
os.environ['PRISMATIC_STATE_DIR'] = str(state)
os.environ['DRAIN_BATCH_SIZE'] = '10'
```

The smoke should use the real modules, not a shadow implementation:

```python
from prismatic import ingestion_queue as q
import drain_webhook_queue as drainer
```

Required assertions:

1. `q.enqueue_linear_event(...)` inserts a Linear-like issue payload with `agent:agy`.
2. `q.queue_payload()` sees the row and reports `source = linear_webhook_queue.db`.
3. `q.queue_stats_payload()` reports one pending row.
4. `drainer.drain(args, dispatch_fn=fake_dispatch)` with `max=1` calls the stub dispatcher exactly once and returns zero.
5. The row normalizes to `completed` after drainer sets `dispatched`.
6. Stats show completed depth and no pending depth.
7. `q.retry_task(id)` resets the terminal row to `pending`.
8. A terminal `failed:*` row plus a live `processing` row are set up.
9. `q.purge_queue()` deletes only the terminal row and preserves the `processing` row.
10. Output ends with `INGESTION_QUEUE_DRAIN_SMOKE_OK` and the verifier script/state dir are cleaned up.

Compact output shape to preserve for reports:

```text
INGESTION_QUEUE_DRAIN_SMOKE_OK
db=/tmp/hermes-queue-state-.../linear_webhook_queue.db
inserted=True
initial_source=linear_webhook_queue.db
initial_total=1
initial_pending_depth=1
drain_rc=0
drain_stdout=[drain] Processing 1 pending events | [drain]   ✓ GRO-SMOKE-001 dispatched | [drain] Done: dispatched=1 no_op=0 failed=0 stale=0 dry_run=False
dispatch_calls=['GRO-SMOKE-001']
post_drain_status=completed
post_drain_completed_depth=1
retry_status=ok
retry_item_status=pending
purge_deleted=1
post_purge_total=1
post_purge_survivor=GRO-SMOKE-LIVE
post_purge_survivor_status=processing
cleanup=PASS removed /tmp/hermes-verify-xxxx.py
```

## AGY model/preflight recovery is separate

The ingestion queue proof does not fix AGY dispatch. If AGY previously failed with:

```text
invalid --model "gemini-3.5-flash-high"
dispatch.tokens.actual_input=0
dispatch.tokens.actual_output=0
```

then fix model routing/preflight before any redispatch.

Current AGY CLI model names are display-style strings from `agy models`, for example:

```text
Gemini 3.5 Flash (High)
Gemini 3.5 Flash (Medium)
Claude Sonnet 4.6 (Thinking)
GPT-OSS 120B (Medium)
```

Patch routers/supervisors to normalize legacy lowercase aliases before preflight/launch:

```python
MODEL_ALIASES = {
    "gemini-3.5-flash-high": "Gemini 3.5 Flash (High)",
    "gemini-3.5-flash": "Gemini 3.5 Flash (Medium)",
    "gemini-3.1-pro-high": "Gemini 3.1 Pro (High)",
    "gemini-3.1-flash-lite": "Gemini 3.5 Flash (Low)",
    "claude-sonnet-4-6": "Claude Sonnet 4.6 (Thinking)",
    "claude-opus-4-6-thinking": "Claude Opus 4.6 (Thinking)",
}
```

Preflight without dispatching a Linear task:

```bash
python3 -m py_compile \
  /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_pool_aware_router.py \
  /home/ubuntu/work/prismatic-hub-ui/scripts/agy_sandbox_event_supervisor.py

python3 /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_pool_aware_router.py model
agy models
agy --print 'Reply with exactly: OK' --print-timeout 30s --model 'Gemini 3.5 Flash (High)'
```

Expected:

```text
router_model=Gemini 3.5 Flash (High)
agy_preflight=OK
```

## One-task AGY proof gate

Before claiming AGY recovery, inspect the target Linear issue and old comments. For GRO-3837, the old bad evidence may look like:

```text
Started ... model: gemini-3.5-flash-high
Agent abandoned this task
```

That means no proof has passed yet. The next redispatch must be exactly one task:

```text
GRO-3837 — inventory rubric items and scoring rules
```

Required proof before Stage 1 continues:

```text
dispatch.tokens.actual_input > 0
dispatch.tokens.actual_output > 0
DONE: GRO-3837 ...
meaningful RESULT.md
meaningful Linear comment
correct next state
```

Do not launch the full 101-task tree or downstream RC tasks before this passes.

## Reporting marker

Use the honest marker:

- `INGESTION_QUEUE_DRAIN_SMOKE_OK` — queue/drain proof passed, AGY proof pending.
- `DASHBOARD_DISPATCH_INGESTION_READY_OK` — only after dashboard + ingestion + AGY model/preflight + one-task proof all pass.
