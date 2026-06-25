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
last_verified: 2026-06-25
verified_by: fred
status: current
---

# Prismatic Engine

The prismatic-engine is the cross-project orchestration layer for the
growthwebdev stack. It owns the dispatcher, Linear rate-limit codification,
gateway service, and capability registry.

## OKF bundle location

Pilot OKF docs live in the engine repo at `okf/`:

### Concepts
- [`okf/architecture.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/architecture.md) — Module map, public API surface, two-dispatcher model
- [`okf/index.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/index.md) — Spoke OKF index

### Standards (mirrored from hub)
- [`okf/review-loop-canonical.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/review-loop-canonical.md) — Self-review + peer review loop codification (GRO-2024)
- [`okf/linear-rate-limit.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/linear-rate-limit.md) — Linear API rate-limit codification (GRO-2008/2010/2020/2034)
- [`okf/dispatch-architecture.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/dispatch-architecture.md) — Event-driven dispatch architecture (GRO-2047/2048/2050)
- [`okf/webhook-security.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/webhook-security.md) — Webhook security model (GRO-2057..2062)
- [`okf/agy-peer-review.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/agy-peer-review.md) — AGY peer review standard (GRO-2024)
- [`okf/dispatch-production-grade.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/dispatch-production-grade.md) — Production-grade dispatch standard (mandatory 7-layer security + 7-gate dispatch)

### Decisions (mirrored from hub)
- [`okf/event-driven-dispatch.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/event-driven-dispatch.md) — Why webhook over poll (GRO-2042)

### Integrations (mirrored from hub)
- [`okf/webhook-handler-test-pattern.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/webhook-handler-test-pattern.md) — Webhook test patterns

### Tier 7 Journey (mirrored from hub)
- [`okf/tier-7-journey.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/tier-7-journey.md) — Chronological narrative of Tier 7 production-grade work
- [`okf/tier-7-architecture.md`](https://github.com/mbgulden/prismatic-engine/blob/main/okf/tier-7-architecture.md) — Architecture diagram + data flow

## Tier status

| Tier | Title | Status |
|---|---|---|
| Tier 1 | Unblock dispatcher | ✅ Done |
| Tier 2 | Modularize dispatcher | ✅ Done |
| Tier 3 | Update inventory | ✅ Done |
| Tier 4 | Architecture doc | ✅ Done |
| Tier 5a | OKF pilot | ✅ Done |
| Tier 6 | Standalone + event-driven dispatch | 🚧 Partially done |
| Tier 7 | Production-grade hardening (security + cron reduction + /ws auth) | ✅ Done |

## Related Linear issues

GRO-2008, GRO-2010, GRO-2020, GRO-2024, GRO-2030, GRO-2031, GRO-2032, GRO-2034, GRO-2037, GRO-2039, GRO-2042, GRO-2047, GRO-2048, GRO-2050, GRO-2057..2062, GRO-2077, GRO-2078, GRO-2082

See [`tier-7-journey.md`](./prismatic-engine/tier-7-journey.md) for the chronological narrative.
