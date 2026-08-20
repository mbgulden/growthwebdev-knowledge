# Governance Dashboard Ingestion Queue / Dispatcher Wiring

Use this reference when the Ingestion Queue tab has visible cards/tables/buttons but the gateway is missing read models.

## Dashboard contracts

The Ingestion Queue tab expects these routes:

```text
GET  /api/gateway/webhooks/stats
GET  /api/gateway/webhooks/queue
GET  /api/gateway/dispatcher/status
GET  /api/gateway/recovery/status
POST /api/gateway/webhooks/queue/retry/{task_id}
POST /api/gateway/webhooks/queue/purge
POST /api/gateway/dispatcher/{action}
POST /webhooks/linear  # simulator alias, should flow through canonical Linear handler and preserve auth
```

## Adapter pattern

Keep normalization out of FastAPI handlers when possible. Use an adapter module like `prismatic/ingestion_status.py` to convert existing state into stable read models:

- `_webhook_counters` → received/auth_failed/published stats
- `AgentRunRecordStore` runs → queue items and depths
- dashboard dispatcher control state → running/paused/last_command/status_reason
- dashboard recovery-control state + failed run records → failure taxonomy/recent_failures/last action

Do **not** invent fake queue data. Empty queue is valid and should render as an explicit empty state.

## Control safety

Browser controls must remain audit-safe:

- persist operator intent to a dashboard state file under `PRISMATIC_STATE_DIR`
- emit timeline items with sources `DispatcherControl`, `QueueControl`, and `RecoveryControl`
- optionally publish EventBus events
- do not shell out directly from the browser request

## Dashboard requirements

The tab should show:

- loading state for queue and taxonomy
- empty queue state
- visible API error state
- normalized dispatcher statuses: `active`, `idle`, `paused`, `queue-starved`, `blocked`
- no `mockQueue` or fake success rows

## Real-contract restoration pitfall

A route returning 200 is not enough for this tab. The dashboard JavaScript uses `API_PREFIX = "/api/gateway"`, so verify the exact `/api/gateway/webhooks/queue`, `/api/gateway/webhooks/queue/retry/{task_id}`, `/api/gateway/webhooks/queue/purge`, and `/api/gateway/dispatcher/{action}` paths — not just shorter compatibility aliases such as `/api/webhooks/queue`.

Also distinguish a true retryable ingestion queue from EventBus/timeline rows that were mapped into a queue-shaped table. If `linear_webhook_queue.db` and `scripts/drain_webhook_queue.py` exist, recover/reconcile that durable queue contract before declaring the Ingestion Queue restored. See `references/governance-dashboard-ingestion-queue-real-contract-restoration.md` for the worked deep-dive pattern.

Legacy schema pitfall: live `webhook_counters` tables may use `key/value` instead of `name/value`, and may lack `updated_at`. Queue adapters must detect/migrate this non-destructively instead of dropping historical counters.

## Verification pattern

Create `/tmp/hermes-verify-*.py` and report as ad-hoc targeted verification, not suite green.

Verifier should check:

```text
changed paths exist
py_compile server + ingestion adapter + tests
node --check extracted dashboard script
focused pytest for ingestion API
GET /api/gateway/webhooks/stats normalized shape
GET /api/gateway/webhooks/queue normalized shape + status filter
GET /api/gateway/dispatcher/status normalized shape before/after control action
GET /api/gateway/recovery/status taxonomy + recent failures + last recovery action
POST dispatcher/queue/recovery controls emit timeline items
POST /webhooks/linear is supported and uses canonical signed handler
dashboard contains supported fetches and no mockQueue fallback
cleanup removes verifier and temp state
```

For live smoke, start uvicorn on a temporary port with isolated `PRISMATIC_STATE_DIR`, hit `/dashboard` and the four GET routes, perform one dispatcher/queue control action, check `/api/timeline?source=DispatcherControl`, then kill the temp process and remove temp state.
