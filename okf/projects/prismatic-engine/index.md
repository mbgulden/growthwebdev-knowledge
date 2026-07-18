---
type: Index
title: Prismatic Engine
description: Canonical OKF project index for Prismatic Engine governance, dispatcher, dashboard, OKF recovery, and production-hardening records.
resource: okf/projects/prismatic-engine/index.md
tags: [index, project, prismatic-engine, governance, dispatcher]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/index.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic Engine

## Current status

Prismatic Engine is the governance/control-plane workspace for dispatcher operations, gateway routing, Prismatic Dashboard surfaces, lane governance, and OKF recovery. The current production lane uses `deploy-fresh`; the application repo currently has a repo-local breadcrumb map but no first-class `okf/` tree on `deploy-fresh`.

Canonical OKF records now live in this hub project directory. The repo-local spoke map is `prismatic-engine/docs/okf-map.md` and points future agents back here.

## Canonical records

| Record | Status | Purpose |
|---|---:|---|
| [Enterprise Governance Audit — 2026-07-06](../../audits/prismatic-enterprise-governance-audit-2026-07-06.md) | current | Production-grade dashboard/control-plane baseline, 12-gate enterprise rubric alignment, and Linear closeout tree. |
| [Enterprise Governance Scorecard](../../standards/prismatic-enterprise-governance-scorecard.md) | current | 12-gate rubric for enterprise-grade Prismatic operations. |
| [Ingestion Queue repair closeout](./ingestion-queue-repair-2026-07-14.md) | current | Durable Linear webhook queue, `/api/gateway` aliases, retry/purge mutation, QueueControl/DispatcherControl audit proof. |
| [Tier 7 journey](./tier-7-journey.md) | current/historical synthesis | Chronological production-grade hardening journey and what is still current. |
| [Tier 7 architecture](./tier-7-architecture.md) | current/historical synthesis | Salvaged architecture map for dispatcher, gateway, dashboard, and staging governance. |
| [Dispatcher incident history](./dispatcher-incident-history.md) | current/historical synthesis | Dispatcher incident/recovery timeline and audit-safe control boundary. |
| [Governance dashboard history](./governance-dashboard-history.md) | current | Dashboard route separation, live proof rules, and ingestion queue repair history. |
| [OKF drift and recovery history](./okf-drift-and-recovery-history.md) | current | How Prismatic OKF drift happened, where records were found, and prevention policy. |

## Current architecture/docs map

| Surface | Canonical docs |
|---|---|
| Dashboard / control plane | [Governance dashboard history](./governance-dashboard-history.md), [Ingestion Queue closeout](./ingestion-queue-repair-2026-07-14.md) |
| Enterprise governance | [Enterprise Governance Audit](../../audits/prismatic-enterprise-governance-audit-2026-07-06.md), [Enterprise Governance Scorecard](../../standards/prismatic-enterprise-governance-scorecard.md), [Prismatic dashboard live proof](../../standards/prismatic-dashboard-live-proof.md) |
| Dispatcher / operator controls | [Dispatcher incident history](./dispatcher-incident-history.md), [Tier 7 architecture](./tier-7-architecture.md) |
| Production hardening | [Tier 7 journey](./tier-7-journey.md), [Tier 7 architecture](./tier-7-architecture.md) |
| Documentation governance | [OKF drift and recovery history](./okf-drift-and-recovery-history.md), [Treasure-map report](../../reports/prismatic-okf-treasure-hunt-2026-07-15.md) |
| Repo-local breadcrumb | `prismatic-engine/docs/okf-map.md` |


## Historical/archive records

Batch 3 archive records preserve provenance without turning hidden branch contents into current truth:

- [Archive index](./archive/index.md)
- [Ned scan-triage history](./archive/ned-scan-triage-history.md)
- [AGY audit history](./archive/agy-audit-history.md)
- [Canonical merge winner maps](./archive/canonical-merge-winner-maps.md)
- [Plugin ecosystem history](./archive/plugin-ecosystem-history.md)
- [Other Prismatic docs history](./archive/other-prismatic-docs-history.md)
- [Unsafe/private quarantine](./archive/unsafe-private-quarantine.md)

Cleanup remains blocked until these archive records, duplicate manifests, and quarantine review are referenced by a final cleanup manifest.

## Historical/archival families queued for Batch 3

Batch 2 promotes current canonical records only. These families are deliberately queued, not dropped:

- Ned scan-triage OKF runs — summarize/archive as historical rather than promoting every per-run file.
- AGY audit docs — summarize/archive as historical after reviewing relevance.
- Canonical merge winner maps — preserve one canonical map and record duplicate/superseded copies.
- `unsafe/private` candidates — quarantine/review only; do not publish until manually reviewed and redacted.

## Repo-local spoke map

The project repo contains:

```text
prismatic-engine/docs/okf-map.md
```

Use that map as the repo-local breadcrumb. The canonical hub records are in `growthwebdev-knowledge/okf/projects/prismatic-engine/`.

## Source/provenance summary

Batch 2 is based on `/tmp/prismatic-okf-treasure-hunt/manifests/batch2-selected-canonical-records.json`, which selected 42 provenance sources from 1,850 priority candidate docs across hidden Prismatic branches and hub branches.

Primary hidden source families include:

- `backup/gro-3515-full-okf-blocked`
- `backup/gro-3522-full-okf-blocked`
- `backup/gro-3522-inlane-disconnected`
- `feature/tier-5a-okf-pilot`
- `ned/GRO-3520-local-okf-full`
- `origin/feature/fred-okf-gap13-sync`
- `origin/feature/okf-dispatcher-incident-v2`

| Source repo | Branch | Head | Path | Class | Hash |
|---|---|---|---|---|---|
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `see manifest` | `okf/audits/canonical-merge-winner-map-2026-07-06.md` | `hidden-useful` | `see manifest` |
| `prismatic-engine` | `backup/gro-3522-full-okf-blocked` | `see manifest` | `okf/audits/canonical-merge-winner-map-2026-07-06.md` | `hidden-useful` | `see manifest` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-gap13-sync` | `see manifest` | dispatcher / event-driven OKF docs | `duplicate-superseded` | `see manifest` |
| `growthwebdev-knowledge` | `origin/feature/okf-dispatcher-incident-v2` | `see manifest` | dispatcher incident / webhook docs | `duplicate-superseded` | `see manifest` |

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
