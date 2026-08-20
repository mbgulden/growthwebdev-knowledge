# Goal: Restore the Governance Dashboard Ingestion Queue to a Real Operator Queue

Use this as a starter goal prompt when the Ingestion Queue tab exists but is still not a real durable operator console.

## Mission

Repair the Governance Dashboard **Ingestion Queue** so it is backed by the canonical durable webhook queue ledger, real route contracts, safe operator controls, timeline/audit evidence, focused regression checks, and browser proof.

## Known failure pattern to verify first

- Dashboard JavaScript may use `API_PREFIX = "/api/gateway"` and call `/api/gateway/webhooks/queue`, while backend only exposes `/api/webhooks/queue`.
- The tab may show stats/taxonomy but leave the table at `Loading queue items...` or `0 total`.
- `/api/webhooks/queue` may map EventBus/recent activity into queue-shaped rows. That is not a retryable ingestion queue.
- Retry/purge may return `accepted_noop`. That is safe stabilization, not a finished queue operator control when durable queue storage exists.

## Recovery sources to check before rewriting

```text
backup/gro-3515-full-okf-blocked
backup/gro-3522-full-okf-blocked
prismatic/gateway/routers/linear_webhook.py
tests/test_gateway_webhook.py
design/gro-2880
```

Old backups usually contain the durable `linear_webhook_queue.db` read/write contract. `design/gro-2880` usually contains newer `QueueControl` / `DispatcherControl` audit-timeline patterns. Reconcile them; do not choose one blindly.

## Required repair shape

1. Restore dashboard-prefixed routes:
   - `GET /api/gateway/webhooks/stats`
   - `GET /api/gateway/webhooks/queue`
   - `POST /api/gateway/webhooks/queue/retry/{task_id}`
   - `POST /api/gateway/webhooks/queue/purge`
   - `POST /api/gateway/dispatcher/{action}`
2. Restore or add a durable queue adapter for `PRISMATIC_STATE_DIR/linear_webhook_queue.db`.
3. Reconnect Linear webhook intake so it inserts durable queue rows while preserving HMAC validation and EventBus publishing.
4. Make retry/purge mutate durable rows when safe and return real mutation counts.
5. Emit `QueueControl` and `DispatcherControl` timeline items for operator actions.
6. Clarify `prismatic-webhook-drain.service` / timer state: enable/fix it only if safe, otherwise document the intentional replacement path.
7. Extend regression checks so missing `/api/gateway/webhooks/queue`, stuck loading rows, fake queue rows, and `accepted_noop` mutation paths fail.

## Done criteria

- `/api/gateway/webhooks/queue` returns 200.
- Browser Ingestion Queue tab exits `Loading queue items...`.
- Queue data comes from durable queue storage or an explicitly documented replacement ledger, not EventBus stand-in rows.
- Linear webhook intake writes durable queue rows and still publishes EventBus.
- Retry and purge mutate durable rows or return clear not-found/error for missing rows.
- Queue/dispatcher controls emit timeline evidence.
- Drainer/consumer policy is active or intentionally retired with evidence.
- Fresh `/tmp/hermes-verify-*` ad hoc verifier passes and is cleaned up.
- Browser console has no JS errors on the Ingestion Queue tab.

## Verification language

Report as **ad hoc targeted verification + durable regression-contract pass**, not full suite green unless a canonical full suite actually ran.
