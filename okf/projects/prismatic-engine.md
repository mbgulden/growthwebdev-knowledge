---
type: Index
title: Prismatic Engine
description: Index of OKF concepts for the prismatic-engine repository.
resource: https://github.com/mbgulden/prismatic-engine
tags: [index, project, prismatic-engine]
timestamp: 2026-06-19T10:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/prismatic-engine
git_path: okf/index.md
last_verified: 2026-06-19
verified_by: fred
status: current
---

# Prismatic Engine

The prismatic-engine is the cross-project orchestration layer for the
growthwebdev stack. It owns the dispatcher, Linear rate-limit codification,
gateway service, and capability registry.

## OKF bundle location

Pilot OKF docs live in the engine repo at `okf/`:

- [`okf/architecture.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/architecture.md) — Module map, public API surface, two-dispatcher model
- [`okf/review-loop-canonical.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/review-loop-canonical.md) — Self-review + peer review loop codification (GRO-2024)
- [`okf/linear-rate-limit.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/linear-rate-limit.md) — Linear API rate-limit codification (GRO-2008/2010/2020/2034)

## Tier status

| Tier | Title | Status |
|---|---|---|
| Tier 1 | Unblock dispatcher | ✅ Done |
| Tier 2 | Modularize dispatcher | ✅ Done |
| Tier 3 | Update inventory | ✅ Done |
| Tier 4 | Architecture doc | ✅ Done |
| Tier 5a | OKF pilot | 🚧 In Progress |

## Related Linear issues

GRO-2008, GRO-2010, GRO-2020, GRO-2024, GRO-2030, GRO-2031, GRO-2032, GRO-2034, GRO-2037, GRO-2039
