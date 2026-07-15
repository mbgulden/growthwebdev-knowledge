---
type: Report
title: Prismatic Tier 7 architecture
description: Current/salvaged architecture map for Prismatic Engine Tier 7 hardening across dispatcher, gateway, governance dashboard, staging, and documentation control surfaces.
resource: okf/projects/prismatic-engine/tier-7-architecture.md
tags: [report, prismatic-engine, tier-7, architecture, dispatcher, dashboard]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/tier-7-architecture.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic Tier 7 architecture

## Current architecture map

| Layer | Current/salvaged role | Boundary |
|---|---|---|
| Gateway | FastAPI/API surface for governance dashboard and webhook aliases. | Route truth must be verified live. |
| Dashboard | Operator UI for governance status, queue state, dispatcher/control intent. | UI proof requires browser/API/console evidence. |
| Dispatcher | Agent/workflow execution plane and operator intent surface. | Dashboard controls should record audit-safe intent unless an approved service-control path exists. |
| Durable queue | `linear_webhook_queue.db` for Linear webhook queue truth. | EventBus is timeline/activity context, not queue ledger. |
| Staging governance | Governor-controlled promotion boundary. | No direct push to production lanes. |
| OKF hub | Durable documentation and provenance layer. | Hidden branch docs are source material, not current truth by default. |

## Dispatch/gateway flow

```text
Linear/GitHub/Webhook events
  -> gateway route / webhook handler
  -> durable ledger or EventBus context as appropriate
  -> dashboard/operator surface
  -> audit timeline for operator controls
  -> verified OKF record for durable learning
```

## Known contradictions with current `deploy-fresh`

- Hidden branches contain first-class `okf/` trees; current `deploy-fresh` does not.
- Some historical docs refer to direct spoke paths that no longer exist on the current lane.
- Dispatcher/service controls must be treated as current only when verified against live service and source.

## Provenance

| Source repo | Branch | Head | Path | Class | Hash |
|---|---|---|---|---|---|
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/projects/human-design-engine/staging-stripe-launch-2026-07-13.md` | `duplicate-superseded` | `5b5cab02a9a5` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/standards/prismatic-staging-governance.md` | `duplicate-superseded` | `511a9327f88f` |
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `portable-skills/cloudflare-deployment/references/staging-access-control.md` | `duplicate-superseded` | `31a481849ec3` |
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `portable-skills/cloudflare-deployment/references/staging-css-matching.md` | `duplicate-superseded` | `5eb42242afcc` |
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `portable-skills/cloudflare-deployment/references/staging-gate-pattern.md` | `duplicate-superseded` | `698302941fa4` |

Selection notes:
- Architecture doc is synthesized from current Prismatic dashboard/dispatcher/gateway facts plus hidden branch signals.


## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
