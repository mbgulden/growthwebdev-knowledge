---
type: Report
title: Prismatic dispatcher incident history
description: Consolidated current/historical dispatcher incident and recovery record for Prismatic Engine, with operator-control audit boundaries and provenance.
resource: okf/projects/prismatic-engine/dispatcher-incident-history.md
tags: [report, prismatic-engine, dispatcher, incident, control-plane]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/dispatcher-incident-history.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic dispatcher incident history

## Incident/recovery timeline

| Era | What happened | Current treatment |
|---|---|---|
| Polling/batch dispatcher era | Dispatcher work depended on periodic/batch invocation patterns and stranded outputs. | Historical root cause pattern. |
| Event-driven dispatch push | Branches and hub docs record event-driven dispatch decisions and incident recovery. | Preserve as provenance; verify before treating as live. |
| Governance dashboard controls | Dashboard needs route aliases and visible controls, but browser routes must be audit-safe. | Current boundary: record operator intent; do not shell out from browser routes. |
| Ingestion Queue repair | QueueControl/DispatcherControl timeline items were restored for durable queue/operator actions. | Current verified model for audit timeline behavior. |

## Dispatcher-control intent/audit boundary

Dashboard dispatcher routes may expose `start`, `stop`, `restart`, or `status` style intents, but those intents are not proof that a service was safely controlled. Unless an approved service-control path exists, routes should record timeline/operator intent and return explicit state rather than shelling out directly.

## Current known durable controls

- Queue retry/purge records `QueueControl` timeline events.
- Dispatcher route aliases record `DispatcherControl` timeline events.
- The durable operator queue uses `linear_webhook_queue.db`; EventBus can remain activity context.

## What should not be treated as current operational truth

- Old branch docs that imply direct service control without current source verification.
- EventBus recent events mapped into queue-shaped rows.
- `accepted_noop` mutation responses for real operator queue actions.

## Batch 3 archival queue

Dispatcher incident source docs and event-driven dispatch decision records should be deduped into one archival appendix in Batch 3 after source families are reviewed.

## Provenance

| Source repo | Branch | Head | Path | Class | Hash |
|---|---|---|---|---|---|
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `okf/event-driven-dispatch.md` | `hidden-useful` | `a1ab286953fa` |
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `okf/tier-7-architecture.md` | `hidden-useful` | `190df1a550ca` |
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `okf/tier-7-journey.md` | `hidden-useful` | `0fb18e0b338f` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/dispatch/kai-delta-dispatcher-health-audit.md` | `hidden-useful` | `216b4b8f2ce2` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/dispatch/ned-delta-dispatcher-health-audit.md` | `hidden-useful` | `bf21e749d5b8` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/dispatcher-entrypoint-inventory.md` | `hidden-useful` | `d111ab7913a1` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/prismatic-core-dispatcher-py.md` | `hidden-useful` | `2554fbf42011` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/tests-api-test-dispatch-gateway-py.md` | `hidden-useful` | `36f608a8d2c7` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/agy-night/module-cards/tests-test-dispatcher-activation-py.md` | `hidden-useful` | `97cff1e8c92a` |
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `docs/pwp/runbooks/dispatcher-config-missing.md` | `hidden-useful` | `3853a49857a4` |

Selection notes:
- Batch 2 current incident history; detailed archival docs remain Batch 3.


## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
