---
type: Standard
title: Prismatic Enterprise Governance Scorecard
resource: okf/standards/prismatic-enterprise-governance-scorecard.md
description: Production-grade governance rubric for the Prismatic Engine, aligned with the North Star and the enterprise audit.
tags: [standard, governance, scorecard, enterprise, north-star]
timestamp: 2026-07-06T07:34:00Z
linear_issue: GRO-3523
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/prismatic-enterprise-governance-scorecard.md
last_verified: 2026-07-06
verified_by: fred
status: current
---

# Prismatic Enterprise Governance Scorecard

This is the stricter, production-grade version of the earlier 10/10 governance rubric.
It does not ask whether the engine is merely healthy; it asks whether the dashboard and control plane are genuinely trustworthy for enterprise operations.

## North Star anchor

From the Prismatic North Star source preserved in [Prismatic archive provenance](../projects/prismatic-engine/archive/other-prismatic-docs-history.md):

- The engine must run without Michael.
- Every component must be swappable.
- The overnight factory must keep producing verified results.
- Governance is not optional.
- The factory must be visible enough to be reviewed from a dashboard.

## Enterprise rubric

Each gate is worth 1 point. **12/12 = enterprise green.**

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

## Current read on the baseline

- **Provisional score:** 7/12
- **Green:** runtime health and restartability, dashboard navigation, merge visibility, dispatcher/webhook integrity, observability clarity, documentation traceability, change-control provenance
- **Yellow:** control button end-to-end proof, recovery/replay/DLQ visibility, quota telemetry integrity, task coverage and ownership, operator UX usefulness
- **Red:** none confirmed in the latest live check

## Enterprise standard for 12/12

To hit 12/12, the operator must be able to:
1. open the dashboard,
2. understand the factory at a glance,
3. trigger the control-plane buttons,
4. see a trustworthy response,
5. inspect merge and recovery state without log spelunking,
6. trust the quota and telemetry panes,
7. and trace every non-green condition to a specific Linear issue.

## How to use this scorecard

- If any gate changes, update the scorecard and the enterprise audit together.
- If a gate is yellow or red, the corresponding Linear issue must stay open until the gate is green.
- If the dashboard claims a control exists, the control must be verified live before it is considered green.

## What changed from the earlier 10/10 rubric

This standard intentionally raises the bar.
The earlier scorecard was useful for baseline health, but enterprise governance requires proof of control, not just visibility.
