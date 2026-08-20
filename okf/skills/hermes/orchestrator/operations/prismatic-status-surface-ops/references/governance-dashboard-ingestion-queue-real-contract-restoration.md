# Governance Dashboard Ingestion Queue Real-Contract Restoration

Session pattern captured from the Prismatic Governance Dashboard Ingestion Queue repair for GRO-3721.

## Trigger

Use this when the Ingestion Queue tab renders but is not an operator-grade queue console, especially when:

- the UI fetches `/api/gateway/webhooks/queue` but only `/api/webhooks/queue` works;
- the queue endpoint maps EventBus/timeline activity into queue-shaped rows;
- retry/purge returns `accepted_noop` rather than mutating a queue row;
- the browser tab can show cards/taxonomy but the table remains stuck on `Loading queue items...`.

## Durable target contract

The queue source of truth is `PRISMATIC_STATE_DIR/linear_webhook_queue.db`, not EventBus recent activity.

Expected row keys:

```text
id, event_id, identifier, agent_name, action, event_type,
dispatch_status, queued_at, received_at, processed_at, raw_json
```

Expected stats keys:

```text
source=linear_webhook_queue.db
received, auth_failed, queued, processed, failed,
average_dispatch_latency_seconds, recent_latencies,
queue_depths.pending, queue_depths.processing,
queue_depths.completed, queue_depths.failed
```

EventBus may remain timeline/activity context, but it is not the queue ledger.

## Restoration steps

1. Restore/create a small adapter such as `prismatic/ingestion_queue.py` that owns DB path resolution, schema init/migration, row normalization, stats, enqueue, retry, and purge.
2. Make all dashboard aliases work, especially the prefixed routes:
   - `GET /api/gateway/webhooks/stats`
   - `GET /api/gateway/webhooks/queue`
   - `POST /api/gateway/webhooks/queue/retry/{task_id}`
   - `POST /api/gateway/webhooks/queue/purge`
   - `POST /api/gateway/dispatcher/{action}`
3. Reconnect `POST /webhooks/linear` and `POST /api/gateway/linear` to insert a durable queue row while preserving HMAC validation and EventBus publishing.
4. Implement retry as a real mutation: set `dispatch_status='pending'` and `processed_at=NULL`; return `updated: 1` for real rows and clear `404`/`updated: 0` for missing rows.
5. Implement purge as a real mutation over completed/failed/stale/skipped/no-op/dispatched statuses and `failed:%`; return `deleted` count.
6. Record audit timeline events for queue controls with `source: QueueControl`, and dispatcher controls with `source: DispatcherControl`. Browser routes must not shell out.
7. Keep dashboard UI honest: no permanent loading state, explicit error/empty state, prefixed `/api/gateway` fetches, no `mockQueue` fallback.

## Legacy schema pitfalls

- Existing `webhook_counters` may use `key/value`, not `name/value`.
- Existing `webhook_counters` may lack `updated_at`.
- SQLite cannot `ALTER TABLE ... ADD COLUMN ... UNIQUE`; use a plain column plus idempotent application logic or a safe index when possible.
- Treat legacy `processed` rows conservatively in depth stats; do not assume only `completed/failed/pending/processing` exist.

## Verification pattern

Use both durable tests and live proof:

```text
python3 -m py_compile prismatic/gateway/server.py prismatic/ingestion_queue.py scripts/verify-governance-dashboard-contract.py
/home/ubuntu/.prismatic/venv_stable/bin/python3 -m pytest -q prismatic/gateway/test_ingestion_queue_contract.py
/home/ubuntu/.prismatic/venv_stable/bin/python3 scripts/verify-governance-dashboard-contract.py
```

Add a fresh `/tmp/hermes-verify-*` wrapper that:

- sets isolated `PRISMATIC_STATE_DIR` with `tempfile.mkdtemp(prefix='hermes-queue-state-')`;
- posts a Linear webhook fixture;
- verifies normalized row shape and stats shape;
- verifies retry mutates and missing retry is explicit;
- marks a row completed, purges it, and verifies `deleted` count;
- verifies QueueControl and DispatcherControl timeline items;
- removes the temp state and verifier.

For live proof after merge/restart:

- `systemctl is-active prismatic-gateway.service` is `active`;
- `/api/gateway/webhooks/stats` returns `source: linear_webhook_queue.db`;
- `/api/gateway/webhooks/queue` returns `200` and durable rows if present;
- browser opens `/dashboard`, clicks **INGESTION QUEUE**, table leaves `Loading queue items...`, queue badge matches API total, and console has zero JS errors.

## Drainer caveat

Do not silently unmask or enable `prismatic-webhook-drain.service` from the dashboard repair. If the timer is inactive and service is masked, report it as a separate yellow/red ops decision unless a safe dry-run/one-shot proof shows the drainer exits cleanly.