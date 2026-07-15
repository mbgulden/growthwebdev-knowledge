---
type: Standard
title: Prismatic dashboard live proof
description: Canonical proof standard for Prismatic dashboard/control-plane UI, API, browser-console, and operator-action claims.
resource: okf/standards/prismatic-dashboard-live-proof.md
tags: [standard, prismatic-engine, dashboard, live-proof, verification]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-dashboard-live-proof.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic dashboard live proof

## Standard

Prismatic dashboard/control-plane claims require live proof. Source inspection alone is not enough for UI or operator-console changes.

## Applies to

- `prismatic.growthwebdev.com` governance dashboard surfaces.
- Gateway/API-backed dashboard panels.
- Operator controls such as queue retry/purge and dispatcher intent routes.
- Any OKF/Linear closeout claiming dashboard behavior is fixed.

## Minimum evidence by claim type

| Claim | Required proof |
|---|---|
| Dashboard route renders | Browser readback of the live route plus no blocking console errors. |
| API-backed panel works | live API status/body sample and source-of-truth check. |
| Queue panel works | Durable DB source shown; EventBus activity cannot masquerade as queue ledger. |
| Operator mutation works | Seeded row/action, mutation count/result, and audit timeline event. |
| Route separation is correct | Live URL/host proof distinguishing governance dashboard from marketing surface. |
| Documentation closeout is current | OKF verifier plus post-merge `origin/main` readback. |

## Anti-patterns

- Claiming “green” because a template exists.
- Treating EventBus recent events as durable queue rows.
- Reporting browser behavior without console/API evidence.
- Treating a local dirty checkout as canonical hub proof.
- Hiding a disabled/masked drainer behind a green UI claim.

## Evidence wording

Use explicit scope labels:

```text
Ad hoc targeted dashboard/API verification: PASS
Scope: <specific dashboard/API contract> — not full suite green.
```

## Related Prismatic records

- [Prismatic project index](../projects/prismatic-engine/index.md)
- [Governance dashboard history](../projects/prismatic-engine/governance-dashboard-history.md)
- [Ingestion Queue repair closeout](../projects/prismatic-engine/ingestion-queue-repair-2026-07-14.md)

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
