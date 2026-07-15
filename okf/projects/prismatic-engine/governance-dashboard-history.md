---
type: Report
title: Prismatic governance dashboard history
description: Durable history and current map of Prismatic governance dashboard route separation, live proof expectations, ingestion queue repair, and operator evidence boundaries.
resource: okf/projects/prismatic-engine/governance-dashboard-history.md
tags: [report, prismatic-engine, governance-dashboard, gateway, ingestion-queue]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/governance-dashboard-history.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic governance dashboard history

## Current map

The governance dashboard is the operator surface for Prismatic control-plane visibility. Current rules:

- `prismatic.growthwebdev.com` `/` and `/dashboard` serve the governance dashboard.
- Marketing belongs on `prismaticengine.com` / `www.prismaticengine.com`.
- Dashboard JavaScript uses `/api/gateway` prefixed routes.
- UI changes need live browser/API/console proof.

## Route separation

Route separation repaired the prior confusion between governance dashboard and marketing surface. The repo-local map and OKF hub records should keep this boundary visible so future agents do not blend product marketing with operator console routes.

## Ingestion Queue repair

The Ingestion Queue repair is the current proof standard:

- `/api/gateway/webhooks/queue` returns durable queue rows.
- Queue source is `linear_webhook_queue.db`, not EventBus recent events.
- Retry/purge mutate rows and report counts.
- QueueControl and DispatcherControl timeline events exist.
- Browser proof showed no stuck loading state and no console errors.

See [Ingestion Queue repair closeout](./ingestion-queue-repair-2026-07-14.md).

## Live proof expectations

| Surface | Minimum proof |
|---|---|
| Dashboard tab | Browser open/click proof plus console check. |
| API-backed panel | Live API status/body sample and source-of-truth confirmation. |
| Queue controls | Seeded durable row, mutation result, and timeline event. |
| Docs/index changes | Frontmatter/link/index verifier plus post-merge readback. |

## Provenance

| Source repo | Branch | Head | Path | Class | Hash |
|---|---|---|---|---|---|
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/portability-core/stream5-agy-queue-design-checklist.md` | `hidden-useful` | `cadab63ab71c` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `okf/audits/prismatic-enterprise-governance-audit-2026-07-06.md` | `hidden-useful` | `92bb2249bb9c` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `okf/standards/prismatic-enterprise-governance-scorecard.md` | `hidden-useful` | `9839a0bbbbef` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `okf/standards/prismatic-governance-scorecard.md` | `hidden-useful` | `25ea97c5724c` |
| `prismatic-engine` | `backup/gro-3522-full-okf-blocked` | `f5a85cd42f28` | `okf/standards/prismatic-governance-scorecard.md` | `hidden-useful` | `db0b619f8257` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/directory-indexes/prismatic-gateway.md` | `hidden-useful` | `6df779b9b4a1` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/gateway-event-flow-map.md` | `hidden-useful` | `a5498e13554b` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-gateway-alert-manager-py.md` | `hidden-useful` | `9a54918b9b0b` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-gateway-event-bus-py.md` | `hidden-useful` | `b716e1377d2c` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-gateway-ipc-bridge-py.md` | `hidden-useful` | `14896e6341d1` |

Selection notes:
- Current governance dashboard history includes landed route separation, durable queue, API/browser proof expectations.


## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
