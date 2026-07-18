---
type: Audit
title: Prismatic Enterprise Governance Audit — 2026-07-06 07:34 UTC
description: Live production-grade governance baseline for the Prismatic Engine, including dashboard control proof, telemetry integrity, traceability, and the Linear closeout tree.
tags: [audit, governance, enterprise, dashboard, linear, north-star]
timestamp: 2026-07-06T07:34:00Z
resource: okf/audits/prismatic-enterprise-governance-audit-2026-07-06.md
status: current
verified_by: fred
last_verified: 2026-07-06
linear_issue: GRO-3523
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/prismatic-enterprise-governance-audit-2026-07-06.md
---

# Prismatic Enterprise Governance Audit — 2026-07-06 07:34 UTC

This audit is the stricter, production-grade successor to the earlier 10/10 governance baseline.
It answers a harder question: **can an operator run the factory end-to-end from the dashboard without guessing, reading logs, or stitching together hidden control paths?**

## North Star alignment

This audit still points back to the North Star:
- the engine must run without Michael,
- every component must be swappable,
- the overnight factory must keep producing verified results,
- governance is not optional,
- and the factory must be visible enough to be reviewed from a dashboard.

## Live surface checked

Live inspection of `http://127.0.0.1:9000/dashboard` and its major tabs showed:

- **Dashboard tab**: main control shell renders, the agent topology is visible, and the new Recovery Command Strip surfaces consumer health without leaving the default viewport.
- **Dashboard control sample**: `Refresh recovery` returns live status for `prismatic-consumer.service`, heartbeat truth, and pool counts; `Open queue view` moves directly into the ingestion queue tab.
- **Merge Pipeline tab**: live pending counts, recent auto-merges, and the canonical merge map are visible.
- **Foundation tab**: control buttons exist for `Run Peer Review Orchestrator` and `Verify Sync / Git Status`.
- **Foundation control sample**: `Verify Sync / Git Status` returned visible sync output, including the current branch (`merge/pipeline-v2`), modified files, and untracked files.
- **Workspaces tab**: registered workspace table renders and exposes `+ Register Context`.
- **Signals tab**: live WebSocket signal stream is visible and actively updating.
- **GCP Quotas tab**: quota panes and `Trigger Sync` are visible, and the live view now degrades gracefully with `SYNCING`, `ACTIVE`, `BLOCKED`, and `EXHAUSTED` states instead of raw `null%` / `undefined` text.

## Enterprise governance baseline

| # | Gate | Green means | Current baseline |
|---|---|---|---|
| 1 | Runtime health and restartability | Gateway, consumer, curator, and merge surfaces are reachable and returning healthy state. | Green |
| 2 | Dashboard navigation and pane rendering | Top-level tabs, panes, and tables render correctly and switch between operational views. | Green |
| 3 | Control button end-to-end proof | Dashboard buttons invoke the intended control-plane action and surface the result back to the operator. | Yellow |
| 4 | Merge governance visibility | Merge backlog, contention, and canonical-winner mapping are visible from the dashboard. | Green |
| 5 | Recovery / replay / DLQ visibility | Recovery state is surfaced in the control plane and can be reviewed without digging through logs. | Yellow |
| 6 | Quota telemetry integrity | Quota data is complete, non-null, and carries enough freshness metadata to trust it operationally. | Yellow |
| 7 | Dispatcher / webhook identity integrity | Work is routed with the correct issue identity and the webhook path does not leak placeholder IDs. | Green |
| 8 | Observability and signal clarity | Signal, log, and status views are understandable, current, and useful for operator triage. | Green |
| 9 | Documentation traceability | North Star, standards, audits, indexes, and project pages cross-link cleanly. | Green |
| 10 | Change control and rollback provenance | Locks, release notes, and service restart paths are explicit and repeatable. | Green |
| 11 | Task coverage and ownership | Every yellow/red gate has a concrete Linear tree with a clear owner path. | Yellow |
| 12 | Operator UX usefulness | The dashboard is not just present; it is actually helpful for managing the factory. | Yellow |

## Gate ownership matrix

This matrix is the authoritative task coverage map for every non-green enterprise gate. A yellow or red gate is not allowed to exist without an owner, a Linear issue, an explicit finish line, and an evidence target.

| Gate | Status | Owner | Owning Linear issue(s) | Finish line | Evidence target |
|---|---|---|---|---|---|
| 3. Control button end-to-end proof | Yellow | `agent:fred` | [GRO-3525](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3525), [GRO-3526](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3526) | Every dashboard button triggers the correct backend endpoint/process and returns live, correct status/feedback to the operator UI instead of generic error codes or failing silently. | Live dashboard/API proof attached to the owning issue and reflected back into the audit before the gate moves green. |
| 5. Recovery / replay / DLQ visibility | Yellow | `agent:ned` | [GRO-3529](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3529), [GRO-3530](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3530), [GRO-3540](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3540), [GRO-3531](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3531) | The Recovery Command Strip is visible in the default dashboard viewport, displaying `prismatic-consumer.service` status, DLQ count, and heartbeat truth, and allows operator-initiated retry/replay of failed tasks. | Dashboard screenshot/API output proving recovery state, DLQ count, heartbeat state, and action boundary behavior. |
| 6. Quota telemetry integrity | Yellow | `agent:fred` | [GRO-3533](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3533), [GRO-3534](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3534), [GRO-3535](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3535) | Quota payloads are normalized, non-null, contain freshness timestamps, and display graceful status degradation (`SYNCING`, `ACTIVE`, `BLOCKED`, `EXHAUSTED`) instead of raw null/undefined text. | Targeted quota-pane verification showing normalized payloads, freshness metadata, and empty/error states. |
| 11. Task coverage and ownership | Yellow | `agent:fred` | [GRO-3541](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3541), [GRO-3543](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3543) | Every yellow/red gate in the enterprise scorecard has an explicit owner, a corresponding Linear issue, and mapped exit criteria documented in the OKF. | This matrix plus the temporary verifier proving all non-green gates are covered by owner, Linear issue, finish line, and evidence target. |
| 12. Operator UX usefulness | Yellow | `agent:fred` | [GRO-3542](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3542), [GRO-3544](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3544), [GRO-3527](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3527) | The dashboard operator interface renders a clear status hierarchy, context-rich panels, and obvious error/success feedback states that actively help triage and run the factory. | Live UI proof that default-view hierarchy, pane context, and feedback states are understandable without log spelunking. |

### Coverage assertion for [GRO-3541](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3541)

- Non-green gates in this audit: 3, 5, 6, 11, 12.
- Covered non-green gates in the matrix: 3, 5, 6, 11, 12.
- Red gates: none confirmed in the latest live check.
- Completion rule: [GRO-3541](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3541) can close when the verifier confirms every non-green gate row contains an owner, at least one Linear issue, a finish line, and an evidence target.

## Enterprise gap to Linear issue traceability

Every non-green enterprise gate is now linked to a concrete Linear closeout path.
This table is the canonical gap map for [GRO-3538](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3538); do not mark a gate green until its linked issue(s) satisfy the exit criteria below.

| Enterprise gap | Baseline | Owner | Linear issue(s) | Exit criteria |
|---|---|---|---|---|
| Gate 3 — Control button end-to-end proof | Yellow | `agent:fred` | [GRO-3525](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3525), [GRO-3526](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3526) | Every dashboard button has live endpoint/process proof, visible success/failure feedback, and no silent generic error path. |
| Gate 5 — Recovery / replay / DLQ visibility | Yellow | `agent:ned` | [GRO-3529](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3529), [GRO-3530](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3530), [GRO-3540](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3540), [GRO-3531](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3531) | Recovery, restart, retry/replay, heartbeat, watchdog, and DLQ state are visible from the dashboard and verified against the live service boundary. |
| Gate 6 — Quota telemetry integrity | Yellow | `agent:fred` | [GRO-3533](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3533), [GRO-3534](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3534), [GRO-3535](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3535) | Quota panes are normalized, non-null, timestamped, and verified with live data plus empty/failure states. |
| Gate 11 — Task coverage and ownership | Yellow | `agent:fred` | [GRO-3541](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3541), [GRO-3543](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3543), [GRO-3538](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3538) | Every yellow/red enterprise gate has an explicit owner, Linear issue, and documented exit criteria in the OKF. |
| Gate 12 — Operator UX usefulness | Yellow | `agent:fred` | [GRO-3542](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3542), [GRO-3544](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3544), [GRO-3527](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3527) | The operator UI exposes a useful status hierarchy, context-rich panels, and clear success/error feedback for running the factory. |

## Current read on the baseline

- **Provisional score:** 7/12
- **Green:** runtime health and restartability, dashboard navigation, merge governance visibility, dispatcher / webhook identity integrity, observability and signal clarity, documentation traceability, change control and rollback provenance
- **Yellow:** control button end-to-end proof, recovery / replay / DLQ visibility, quota telemetry integrity, task coverage and ownership, operator UX usefulness
- **Red:** none confirmed in the latest live check

## Why the current baseline is in flight

The dashboard is real and broad, but the enterprise governance loop is still work in progress with several key control and telemetry features in flight.
Every yellow gate now has a clear owner path, a corresponding Linear issue, and explicit exit criteria documented in the scorecard and audit matrix.

## Linear closeout tree

The enterprise closeout tree is already created in Linear:

### Parent epic
- [GRO-3523](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3523) — Prismatic Enterprise Governance — production-grade closeout

### Child epics
- [GRO-3524](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3524) — Enterprise dashboard command plane hardening
- [GRO-3528](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3528) — Enterprise control plane recovery and replay
- [GRO-3532](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3532) — Enterprise quota and telemetry integrity
- [GRO-3536](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3536) — Enterprise governance traceability and audit loop

### Child tasks
- [GRO-3525](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3525) — Verify every dashboard tab and button end-to-end
- [GRO-3526](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3526) — Fix dashboard operator feedback copy and error states
- [GRO-3527](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3527) — Make the dashboard panes context-rich and action-oriented
- [GRO-3529](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3529) — Expose restart, retry, and replay controls with live proof
- [GRO-3530](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3530) — Surface watchdog, heartbeat, and DLQ state in the dashboard
- [GRO-3540](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3540) — Surface recovery card in default dashboard viewport
- [GRO-3531](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3531) — Verify recovery actions against the live service boundary
- [GRO-3533](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3533) — Normalize quota payloads and remove null or undefined values
- [GRO-3534](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3534) — Add freshness timestamps and failure handling to quotas
- [GRO-3535](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3535) — Validate telemetry panes with live data and empty states
- [GRO-3537](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3537) — Publish the enterprise governance audit in OKF
- [GRO-3538](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3538) — Link every enterprise gap to a Linear issue
- [GRO-3539](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3539) — Keep the OKF indexes synchronized with the enterprise governance docs
- [GRO-3541](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3541) — Enterprise governance task coverage and owner matrix
- [GRO-3542](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3542) — Make the dashboard operator UX genuinely helpful
- [GRO-3543](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3543) — Map enterprise governance gates to owners and exit criteria
- [GRO-3544](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-3544) — Make dashboard status hierarchy and feedback states obvious

## OKF sync obligations

This audit must be discoverable from the OKF root and the audit index.
The corresponding enterprise scorecard must also be linked from the standards index.

## Exit criteria for the enterprise closeout

The enterprise pass is only complete when:
1. every gate in the enterprise scorecard is green,
2. every dashboard button has been proven to do something useful,
3. every telemetry pane is trustworthy,
4. every recovery path is visible and testable,
5. and every remaining gap has been closed or explicitly queued in Linear.
