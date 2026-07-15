---
type: Decision
title: Prismatic OKF hub-and-spoke map
description: Decision record establishing growthwebdev-knowledge as the canonical Prismatic OKF hub while prismatic-engine keeps a repo-local breadcrumb map.
resource: okf/decisions/prismatic-okf-hub-and-spoke-map.md
tags: [decision, prismatic-engine, okf, hub-and-spoke, documentation]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/decisions/prismatic-okf-hub-and-spoke-map.md
last_verified: 2026-07-15
verified_by: fred
status: accepted
---

# Prismatic OKF hub-and-spoke map

## Context

Prismatic Engine historical OKF docs were scattered across backup branches, Ned drift branches, knowledge-hub branches, and archived worktrees. The current `prismatic-engine/deploy-fresh` branch does not contain a first-class `okf/` tree, which caused agents to assume docs were missing.

## Decision

Canonical Prismatic OKF records live in the hub:

```text
growthwebdev-knowledge/okf/projects/prismatic-engine/index.md
```

The application repo keeps a repo-local breadcrumb map:

```text
prismatic-engine/docs/okf-map.md
```

The breadcrumb points agents from the app repo to the canonical hub project index, archive index, treasure-map report, and current project records.

## Consequences

- Agents starting in `prismatic-engine` should read `docs/okf-map.md` before searching for a local `okf/` tree.
- Hub records are verified from `growthwebdev-knowledge origin/main`, not from a dirty local checkout.
- Historical docs are archived in the hub rather than merged raw from hidden branches.
- Unsafe/private candidates remain quarantined until manual review.

## Alternatives considered

| Alternative | Reason rejected |
|---|---|
| Restore all hidden branch OKF docs directly into `prismatic-engine` | Too much stale/duplicate/private risk. |
| Leave docs only in hidden branches | Future agents cannot discover them safely. |
| Treat branch-summed OKF counts as unique docs | Inflates duplicates and creates false cleanup confidence. |

## Related records

- [Prismatic project index](../projects/prismatic-engine/index.md)
- [Prismatic archive index](../projects/prismatic-engine/archive/index.md)
- [Prismatic OKF treasure-map report](../reports/prismatic-okf-treasure-hunt-2026-07-15.md)
- [OKF worktree reconciliation standard](../standards/okf-worktree-reconciliation.md)

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
