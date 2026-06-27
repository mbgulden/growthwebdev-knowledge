---
type: Index
title: Standards
description: Index of cross-project canonical standards.
resource: okf/standards/index.md
tags: [index, standards]
timestamp: 2026-06-19T10:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/index.md
last_verified: 2026-06-23
verified_by: fred
status: current
---

# Standards

Cross-project canonical standards. Each standard lives in `okf/standards/` and
is referenced by project-specific docs.

Every standard points back to the [North Star](../vision/prismatic-north-star.md) — the guiding document that defines what Prismatic Engine actually is and where it is going.

| Standard | OKF location | Linear |
|---|---|---|
| Review-loop codification | [`./review-loop-canonical.md`](./review-loop-canonical.md) | GRO-2024 |
| Linear rate-limit codification | [`./linear-rate-limit.md`](./linear-rate-limit.md) | GRO-2008/2010/2020/2034 |
| Webhook security model | [`./webhook-security.md`](./webhook-security.md) | GRO-2057..2062 |
| AGY peer-review standard | [`./agy-peer-review.md`](./agy-peer-review.md) | GRO-2024 |
| Production-grade dispatch | [`./dispatch-production-grade.md`](./dispatch-production-grade.md) | GRO-2057 |
| Event-driven dispatch architecture | [`./dispatch-architecture.md`](./dispatch-architecture.md) | GRO-2047/2048/2050 |
| Prismatic harness coupling taxonomy | [`./prismatic-harness-coupling-taxonomy.md`](./prismatic-harness-coupling-taxonomy.md) | GRO-2039 |
| Prismatic journal-setup independence map | [`./prismatic-independence-map-journal-setup.md`](./prismatic-independence-map-journal-setup.md) | GRO-2039 |
| Agent dispatch architecture (canonical) | [`./agent-dispatch-architecture.md`](./agent-dispatch-architecture.md) | GRO-2047/2048/2050 + the orchestrator process |
| AOT architecture template (the proven reference) | [`./active-oahu-tours-architecture-template.md`](./active-oahu-tours-architecture-template.md) | the reference implementation for any new client site |
| **Prismatic Engine process overhaul** (NEW 2026-06-23) | [`./prismatic-engine-process-overhaul.md`](./prismatic-engine-process-overhaul.md) | 12 bugs + 9 anti-pattern rules from the /yolo session |
| **Cloudflare Access — OKF publisher lockdown** (NEW 2026-06-23) | [`./cloudflare-access-okf-publisher.md`](./cloudflare-access-okf-publisher.md) | 8 hostnames locked + health-check cron + IP update script |
| **PWP ingest spec** | [`./pwp-ingest-spec.md`](./pwp-ingest-spec.md) | GRO-2138 |
| **PWP distill spec** | [`./pwp-distill-spec.md`](./pwp-distill-spec.md) | GRO-2140 |
| **Mega-task workflow** (the orchestration process) | [`./mega-task-workflow.md`](./mega-task-workflow.md) | the workflow for "big project" intakes |
| **AGY architecture — The Recipe** (NEW 2026-06-23, regression-tested) | [`./agy-architecture-recipe.md`](./agy-architecture-recipe.md) | GRO-2237 | The canonical AGY reference. Read this BEFORE changing anything AGY. |
| **Ned architecture — The Recipe** (NEW 2026-06-23) | [`./ned-architecture-recipe.md`](./ned-architecture-recipe.md) | GRO-2238 | The canonical Ned reference. |
| **Kai architecture — The Recipe** (NEW 2026-06-23) | [`./kai-architecture-recipe.md`](./kai-architecture-recipe.md) | GRO-2239 | The canonical Kai reference. |
| **UI/UX plan for the PWP** (10 surfaces) | [`./ui-ux-plan.md`](./ui-ux-plan.md) | GRO-2185 |
| **Prismatic Portable Core Spec** (2026-06-27, current) | [`./prismatic-portable-core-spec.md`](./prismatic-portable-core-spec.md) | GRO-2786..2818 | D1–D6 signed off by Michael. Source of truth for the portability epic. 10 invariants + 20 outstanding items. Streams 1-5 dispatched. |

## What counts as a "standard"

A standard is a cross-project invariant: if you don't follow it, you break
something shared. Examples:

- The review loop (Worker → AGY peer review → Fred verify → Done).
- The LinearBudget gate (every Linear GraphQL call goes through `check_and_consume`).

A standard is *not* a project-specific runbook or architecture decision.
Those go in project `okf/` or `okf/decisions/` respectively.
