# Ingestion queue dashboard audit — Fred two-pass follow-up (2026-07-15)

## Context

Fred completed two passes on the protected Prismatic governance dashboard ingestion queue work after an earlier preservation handoff warned that the Ingestion Queue tab was still compatibility-shaped. The follow-up audit found the work materially improved the queue path: the dashboard now centers on a durable `linear_webhook_queue.db` contract rather than recent EventBus history pretending to be a queue.

## What changed / what to preserve

Key files in the `prismatic-engine` worktree:

- `prismatic/ingestion_queue.py` — durable queue DB contract and row normalization.
- `prismatic/ingestion_status.py` — normalized dashboard summary/recovery/dispatcher status helpers.
- `prismatic/gateway/server.py` — queue/stats/retry/purge routes and Linear webhook enqueue integration.
- `prismatic/gateway/templates/dashboard.html` — Ingestion Queue tab UI; fetches gateway webhooks queue/stats and renders retry/purge/status markers.
- `scripts/drain_webhook_queue.py` — bounded CLI drainer that must stay semantically aligned with dashboard queue state.
- `scripts/verify-governance-dashboard-contract.py` — regression contract updated to expect durable `linear_webhook_queue.db` sources and reject old no-op retry/purge messages.

Observed route shape:

- `GET /api/webhooks/stats` and `GET /api/gateway/webhooks/stats` → durable queue stats, `source=linear_webhook_queue.db`.
- `GET /api/webhooks/queue` and `GET /api/gateway/webhooks/queue` → durable queue payload from `prismatic.ingestion_queue.queue_payload()`.
- `POST /api/webhooks/queue/retry/{task_id}` and gateway alias → reset durable row to `pending` and audit operator action.
- `POST /api/webhooks/queue/purge` and gateway alias → purge terminal durable queue rows and audit operator action.
- Linear webhook handler calls `enqueue_linear_event()` after parsing the body and increments durable counters.

## Verification pattern that worked

Use ad-hoc verification as targeted evidence, not suite green:

```bash
python3 -m py_compile \
  prismatic/ingestion_queue.py \
  prismatic/ingestion_status.py \
  prismatic/gateway/server.py \
  scripts/drain_webhook_queue.py \
  scripts/verify-governance-dashboard-contract.py

python3 - <<'PY'
from pathlib import Path
html = Path('prismatic/gateway/templates/dashboard.html').read_text()
script = html.split('<script>', 1)[1].rsplit('</script>', 1)[0]
Path('/tmp/hermes-verify-dashboard-inline.js').write_text(script)
PY
node --check /tmp/hermes-verify-dashboard-inline.js
rm -f /tmp/hermes-verify-dashboard-inline.js
```

For a behavioral check, create a temp `PRISMATIC_STATE_DIR`, call `ensure_queue_db()`, enqueue a Linear-like event, assert `queue_payload()` and `queue_stats_payload()` report `source=linear_webhook_queue.db`, call `retry_task()` and assert the row is `pending`, then set the row terminal and prove `purge_queue()` removes it.

Expected ad-hoc marker:

```text
AD_HOC_INGESTION_QUEUE_BEHAVIOR_OK
```

## Honest readiness language

Use this statement when the durable contract passes but drain/dispatch proof is still pending:

```text
INGESTION_QUEUE_DURABLE_CONTRACT_OK — core durable queue payload/stats/retry/purge behavior verified ad hoc; full dashboard contract and queue-drain-dispatch proof still required before DASHBOARD_DISPATCH_INGESTION_READY_OK.
```

Do **not** claim `DASHBOARD_DISPATCH_INGESTION_READY_OK` until this full sequence is proven:

```text
Linear webhook sample
→ durable queue row pending
→ bounded drain operation
→ dispatcher/preflight decision
→ status transition completed/failed/stale
→ dashboard reflects transition
→ recovery/retry path works
```

## Next best slice

The next narrow proof slice is:

```text
INGESTION_QUEUE_DRAIN_SMOKE_OK
```

That smoke should run in a temp state dir and verify queue → drain → dispatch/status transition → dashboard stats/queue reflection → retry/recovery semantics. It should not be a broad dashboard rewrite.

## Pitfalls

- Do not confuse a durable queue contract with a proven end-to-end dispatcher run.
- Do not describe retry as “run now” unless the backend actually dispatches immediately; call it “reset to pending.”
- Purge should explicitly mean “purge terminal rows,” not delete live pending work.
- A FastAPI/TestClient verifier blocked by missing deps is an environment-prep blocker, not evidence that the dashboard contract is broken.
- Keep this queue work linked to AGY dispatch recovery: AGY still needs valid model/preflight/staged redispatch and one-task proof before bulk work resumes.
