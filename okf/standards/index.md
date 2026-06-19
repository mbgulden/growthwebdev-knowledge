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
last_verified: 2026-06-19
verified_by: fred
status: current
---

# Standards

Cross-project canonical standards. Each standard lives in `okf/standards/` and
is referenced by project-specific docs.

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

## What counts as a "standard"

A standard is a cross-project invariant: if you don't follow it, you break
something shared. Examples:

- The review loop (Worker → AGY peer review → Fred verify → Done).
- The LinearBudget gate (every Linear GraphQL call goes through `check_and_consume`).

A standard is *not* a project-specific runbook or architecture decision.
Those go in project `okf/` or `okf/decisions/` respectively.
