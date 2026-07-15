---
type: Report
title: Prismatic canonical merge winner maps archive
description: Historical archive record for canonical merge winner map duplicates discovered across Prismatic backup branches.
resource: okf/projects/prismatic-engine/archive/canonical-merge-winner-maps.md
tags: [report, archive, prismatic-engine, canonical-merge, okf]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/archive/canonical-merge-winner-maps.md
last_verified: 2026-07-15
verified_by: fred
status: historical
---

# Prismatic canonical merge winner maps archive

## Why this archive exists

Four canonical merge winner map candidates were discovered across backup/Ned branches. They are valuable provenance for future cleanup because they explain which branch outputs were considered winners at the time.

## Current vs historical boundary

The maps are historical merge/provenance evidence. They do not override the current canonical OKF structure landed in [Prismatic Engine project index](../index.md).

## Canonical duplicate family

| Source count | Treatment |
|---:|---|
| 4 | Preserve one archive summary and record duplicate sources; do not promote raw duplicates. |

## Source/provenance table

| Source repo | Branch | Head | Path | Class | Recommendation | Hash |
|---|---|---|---|---|---|---|
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `okf/audits/canonical-merge-winner-map-2026-07-06.md` | `hidden-useful` | `promote or merge into canonical project record` | `bf4556dd18ec` |
| `prismatic-engine` | `backup/gro-3522-full-okf-blocked` | `f5a85cd42f28` | `okf/audits/canonical-merge-winner-map-2026-07-06.md` | `hidden-useful` | `promote or merge into canonical project record` | `ec25f54a21b4` |
| `prismatic-engine` | `backup/gro-3522-inlane-disconnected` | `239a6c59ca11` | `okf/audits/canonical-merge-winner-map-2026-07-06.md` | `hidden-useful` | `promote or merge into canonical project record` | `bf4556dd18ec` |
| `prismatic-engine` | `ned/GRO-3520-local-okf-full` | `432374dabed2` | `okf/audits/canonical-merge-winner-map-2026-07-06.md` | `hidden-useful` | `promote or merge into canonical project record` | `bf4556dd18ec` |


## Duplicate/superseded handling

| Hash prefix | Duplicate count | Sample paths |
|---|---:|---|
| `bf4556dd18ec` | 3 | `{'branch': 'backup/gro-3515-full-okf-blocked', 'class': 'hidden-useful', 'path': 'okf/audits/canonical-merge-winner-map-2026-07-06.md', 'repo': 'prismatic-engine', 'title': 'Canonical Merge Winner Map — 2026-07-06 06:24 UTC'}`, `{'branch': 'backup/gro-3522-inlane-disconnected', 'class': 'hidden-useful', 'path': 'okf/audits/canonical-merge-winner-map-2026-07-06.md', 'repo': 'prismatic-engine', 'title': 'Canonical Merge Winner Map — 2026-07-06 06:24 UTC'}`, `{'branch': 'ned/GRO-3520-local-okf-full', 'class': 'hidden-useful', 'path': 'okf/audits/canonical-merge-winner-map-2026-07-06.md', 'repo': 'prismatic-engine', 'title': 'Canonical Merge Winner Map — 2026-07-06 06:24 UTC'}` |


## Cleanup status

Cleanup remains blocked. These maps must be referenced in the final cleanup manifest before any duplicate branch/worktree cleanup is proposed.

## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
