---
type: Report
title: Prismatic Governance Dashboard Ingestion Queue repair closeout — 2026-07-14
description: Current OKF state for the operator-grade Ingestion Queue repair: durable queue ledger, gateway aliases, mutation controls, audit timeline events, live browser/API proof, and remaining drainer caveat.
resource: okf/projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md
tags: [report, project, prismatic-engine, governance-dashboard, ingestion-queue, linear-webhook, operator-console]
timestamp: 2026-07-14T22:45:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md
last_verified: 2026-07-14
verified_by: fred
status: current
---

# Prismatic Governance Dashboard Ingestion Queue repair closeout — 2026-07-14

## Current state

The Governance Dashboard **Ingestion Queue** is now restored as a durable operator queue console. It is no longer green merely because the tab renders, and it no longer uses EventBus recent activity as the primary queue ledger.

| Area | State | Evidence boundary |
|---|---:|---|
| Gateway aliases | green | `/api/gateway/webhooks/*` routes verified live. |
| Durable queue DB | green | API source reports `linear_webhook_queue.db`. |
| Linear webhook enqueue | green | Temp-state verifier posted `/webhooks/linear` and observed durable row insert. |
| Retry/purge mutation | green | Temp-state verifier proved retry `updated: 1`, purge `deleted: 1`, and missing retry returns `404` / `updated: 0`. |
| QueueControl timeline | green | Retry/purge timeline events recorded with `source: QueueControl`. |
| DispatcherControl timeline | green | Dispatcher control route records audit-safe `source: DispatcherControl` events. |
| Dashboard tab | green | Live browser proof: queue left loading state, rendered durable row, no console errors. |
| Regression contract | green | `scripts/verify-governance-dashboard-contract.py` now checks the prefixed queue paths and durable source. |
| Drainer service | yellow/red | `prismatic-webhook-drain.timer` remains inactive/disabled; `prismatic-webhook-drain.service` remains masked. Not unmasked silently. |

## What shipped in prismatic-engine

Merged PR:

- <https://github.com/mbgulden/prismatic-engine/pull/261>

Git evidence:

| Item | Value |
|---|---|
| Merge commit | `9c20214e` |
| Repair commit | `ca552abe` — `[Fred] Restore real ingestion queue contract (#GRO-3721)` |
| Target branch | `deploy-fresh` |
| Linear task | `GRO-3721` |

Changed prismatic-engine files:

| File | Purpose |
|---|---|
| `prismatic/ingestion_queue.py` | New schema-tolerant durable queue adapter for `linear_webhook_queue.db`. |
| `prismatic/gateway/server.py` | Gateway aliases, durable queue stats/list/retry/purge, Linear webhook enqueue, audit timeline controls. |
| `prismatic/gateway/templates/dashboard.html` | Explicit queue empty/error states; prefixed `/api/gateway` contract remains canonical. |
| `prismatic/gateway/test_ingestion_queue_contract.py` | Focused regression tests for enqueue, retry/purge, and control timeline events. |
| `scripts/verify-governance-dashboard-contract.py` | Durable dashboard contract now catches missing `/api/gateway/webhooks/queue` and wrong queue source. |

## Restored route contract

These routes are part of the current contract:

```text
GET  /api/webhooks/stats
GET  /api/gateway/webhooks/stats
GET  /api/webhooks/queue
GET  /api/gateway/webhooks/queue
POST /api/webhooks/queue/retry/{task_id}
POST /api/gateway/webhooks/queue/retry/{task_id}
POST /api/webhooks/queue/purge
POST /api/gateway/webhooks/queue/purge
POST /api/dispatcher/{action}
POST /api/gateway/dispatcher/{action}
POST /webhooks/linear
```

The dashboard uses:

```js
const API_PREFIX = "/api/gateway";
fetch(`${API_PREFIX}/webhooks/queue`);
```

So the `/api/gateway/...` aliases are non-negotiable.

## Queue source-of-truth contract

The queue source is durable SQLite:

```text
PRISMATIC_STATE_DIR/linear_webhook_queue.db
```

Expected normalized row shape:

```json
{
  "id": 123,
  "event_id": "...",
  "identifier": "GRO-1234",
  "agent_name": "fred",
  "action": "update",
  "event_type": "Issue",
  "dispatch_status": "pending",
  "queued_at": "...",
  "received_at": 1234567890.0,
  "processed_at": null,
  "raw_json": "{...}"
}
```

Expected stats shape:

```json
{
  "source": "linear_webhook_queue.db",
  "received": 0,
  "auth_failed": 0,
  "queued": 0,
  "processed": 0,
  "failed": 0,
  "average_dispatch_latency_seconds": 0.0,
  "recent_latencies": [],
  "queue_depths": {
    "pending": 0,
    "processing": 0,
    "completed": 0,
    "failed": 0
  }
}
```

EventBus remains useful for timeline/activity context, but **not** as the primary queue ledger.

## Verification evidence

Scope label: **ad hoc targeted verification + durable regression-contract pass; not full suite green**.

Fresh verification used `/tmp/hermes-verify-*` scripts with cleanup. Latest exact done-criteria verifier:

```text
AD_HOC_VERIFICATION: PASS
scope: Exact Ingestion Queue operator-grade done-criteria verification
cleanup=PASS removed /tmp/hermes-verify-6m1rkv2v.py
```

Focused checks run:

```text
python3 -m py_compile prismatic/gateway/server.py prismatic/ingestion_queue.py scripts/verify-governance-dashboard-contract.py
/home/ubuntu/.prismatic/venv_stable/bin/python3 -m pytest -q prismatic/gateway/test_ingestion_queue_contract.py
/home/ubuntu/.prismatic/venv_stable/bin/python3 scripts/verify-governance-dashboard-contract.py
```

Observed focused pytest result:

```text
3 passed
```

Live API probes after merge/restart:

```text
GET /api/gateway/webhooks/stats      -> 200, source linear_webhook_queue.db
GET /api/gateway/webhooks/queue      -> 200, source linear_webhook_queue.db, total 1
GET /api/gateway/dispatcher/status   -> 200
prismatic-gateway.service            -> active
```

Browser proof on `http://127.0.0.1:9000/dashboard` → **INGESTION QUEUE**:

```text
WEBHOOK INGESTION QUEUE
1 total
TEST-001    Fred    Create    Pending    7/5/2026, 6:43:16 PM    Retry
```

Important negatives verified:

```text
Loading queue items...  false
Queue API unavailable   false
browser JS errors       0
mockQueue fallback      absent
accepted_noop retry/purge compatibility strings absent
```

## Remaining caveat: drainer service

The dashboard now shows durable queue truth regardless of the drainer. However, the queue drainer service was intentionally left unchanged:

```text
prismatic-webhook-drain.timer   inactive / disabled
prismatic-webhook-drain.service masked
```

Reason: prior journal history showed signal/TERM failures. Do not unmask/enable from a browser route or as a silent side-effect. The next slice should either:

1. inspect the drainer unit/script in isolation;
2. run a safe dry-run or one-shot proof that exits cleanly;
3. then explicitly unmask/enable if safe, or document a separate blocker/follow-up.

## Operational lesson

Do **not** call the Ingestion Queue green just because:

- the tab renders;
- `/api/webhooks/queue` returns rows;
- EventBus recent events are mapped into queue-shaped rows;
- retry/purge return `accepted_noop`.

The durable success condition is: `linear_webhook_queue.db` is the queue ledger, `/api/gateway/...` aliases work, retry/purge mutate rows or clearly report not-found, timeline audit events are recorded, and browser proof shows no stuck loading or JS errors.
