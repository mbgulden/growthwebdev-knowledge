---
type: Standard
title: OKF worktree reconciliation
description: Canonical standard for reconciling hidden OKF/docs across branches, stale refs, and archived worktrees before promotion or cleanup.
resource: okf/standards/okf-worktree-reconciliation.md
tags: [standard, okf, worktree, reconciliation, cleanup, provenance]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/okf-worktree-reconciliation.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# OKF worktree reconciliation

## Standard

When project docs appear missing but branches/worktrees suggest they existed, run an OKF treasure-hunt reconciliation before promoting or cleaning anything.

## Required source inventory

Inventory at minimum:

- local branches;
- remote-tracking branches;
- stale local refs even when fetch fails;
- attached worktrees from `git worktree list --porcelain`;
- archived local `okf/` directories;
- canonical hub branches and current `origin/main`.

## Extraction rule

Use `git ls-tree` and `git show` for hidden branches. Do not checkout polluted historical branches in the main worktree and do not merge them directly.

## Required manifests

| Manifest | Purpose |
|---|---|
| branch inventory | Branch/ref/path/SHA provenance. |
| candidate docs | File-level metadata, status, hash, and current-existence checks. |
| exact duplicate groups | Hash-based duplicate families. |
| concept families | Title/path/issue/date similarity groups. |
| selected canonical/archive records | Explicit source list before writing promoted docs. |
| final cleanup candidates | Only after promotion/archive/quarantine are verified. |

## Cleanup rule

Cleanup remains blocked until useful docs are promoted, historical docs are archived, unsafe/private material is quarantined/reviewed, and duplicate families are recorded. Branch deletion always requires explicit human approval.

## Unsafe/private rule

Do not publish or promote unsafe/private candidates without manual review and redaction. Quarantine records may include counts, repo/branch/head, redacted path markers, and safe hash prefixes only.

## Related Prismatic records

- [Prismatic OKF treasure-map report](../reports/prismatic-okf-treasure-hunt-2026-07-15.md)
- [Prismatic OKF drift and recovery history](../projects/prismatic-engine/okf-drift-and-recovery-history.md)
- [Prismatic archive index](../projects/prismatic-engine/archive/index.md)

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
