---
type: Index
title: Prismatic Engine historical/archive records
description: Archive index for Prismatic Engine OKF treasure-hunt families that are useful as provenance but not current operational truth.
resource: okf/projects/prismatic-engine/archive/index.md
tags: [index, archive, prismatic-engine, okf]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/archive/index.md
last_verified: 2026-07-15
verified_by: fred
status: historical
---

# Prismatic Engine archive

This directory records historical/archival Prismatic OKF families discovered during the treasure hunt. These records preserve provenance and cleanup safety without turning historical branch contents into current operational truth.

## Archive records

| Record | Status | Purpose |
|---|---:|---|
| [Ned scan-triage history](./ned-scan-triage-history.md) | historical | Summarizes Ned scan-triage OKF runs without promoting every generated file. |
| [AGY audit history](./agy-audit-history.md) | historical | Preserves AGY audit evidence patterns for revalidation, not current dashboard truth. |
| [Canonical merge winner maps](./canonical-merge-winner-maps.md) | historical | Records canonical merge winner map duplicates and cleanup boundary. |
| [Plugin ecosystem history](./plugin-ecosystem-history.md) | deferred/historical | Records that no plugin ecosystem candidates were selected in Batch 3 and how to handle later plugin docs. |
| [Other Prismatic docs history](./other-prismatic-docs-history.md) | historical | Indexes residual Prismatic docs that do not fit current records or specific archive families. |
| [Unsafe/private quarantine](./unsafe-private-quarantine.md) | quarantine | Redacted existence/count record for unsafe/private candidates; no raw content promoted. |

## Boundary

- These docs are historical/archive records.
- They do not make hidden branch behavior current.
- They do not authorize deleting backup branches, stale refs, worktrees, or local archive directories.
- Unsafe/private candidates remain quarantined until manual review.
- Cleanup remains blocked until a final cleanup manifest is produced and explicitly approved.

## Source manifest

Batch 3 source selections are recorded locally at:

```text
/tmp/prismatic-okf-treasure-hunt/manifests/batch3-selected-archive-records.json
```

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
