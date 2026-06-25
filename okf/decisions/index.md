---
type: Index
title: Decisions
description: Architecture decision records for the growthwebdev stack.
resource: okf/decisions/index.md
tags: [index, decisions, adr]
timestamp: 2026-06-19T10:30:00Z
linear_issue: GRO-2039
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/decisions/index.md
last_verified: 2026-06-25
verified_by: fred
status: current
---

# Decisions

Architecture Decision Records (ADRs). One file per decision, capturing
the context, decision, and consequences.

| Decision | Date | OKF location | Linear |
|---|---|---|---|
| OKF adoption (hub-and-spoke) | 2026-06-19 | [`./okf-adoption.md`](./okf-adoption.md) | GRO-2039 |
| Tier 1-4 cleanup (engine unification) | 2026-06-19 | (see project spokes) | GRO-2008/2010/2020/2030/2031/2032/2034 |
| Event-driven dispatch (Tier 6 part 1) | 2026-06-19 | [`./event-driven-dispatch.md`](./event-driven-dispatch.md) | GRO-2042/2047/2048/2050 |

## Format

Each decision doc follows the OKF format with frontmatter:

- `type: Decision`
- `linear_issue` — link to Linear issue that drove the decision
- `status` — proposed | accepted | superseded

Body sections:

1. **Context** — what's the problem?
2. **Decision** — what did we choose?
3. **Consequences** — what follows from this choice?
4. **Alternatives considered** — what else did we look at?
