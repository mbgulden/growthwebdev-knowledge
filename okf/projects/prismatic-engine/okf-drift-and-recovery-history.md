---
type: Report
title: Prismatic OKF drift and recovery history
description: Record of how Prismatic OKF documentation drifted across hidden branches/worktrees and the canonical hub-and-spoke recovery policy.
resource: okf/projects/prismatic-engine/okf-drift-and-recovery-history.md
tags: [report, prismatic-engine, okf, drift, recovery, documentation-governance]
timestamp: 2026-07-15T00:00:00Z
linear_issue: GRO-3721
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/projects/prismatic-engine/okf-drift-and-recovery-history.md
last_verified: 2026-07-15
verified_by: fred
status: current
---

# Prismatic OKF drift and recovery history

## What happened

Prismatic docs appeared missing from the current repo lane because current `deploy-fresh` does not contain a first-class `okf/` tree. The documents were actually fragmented across backup branches, Ned drift branches, knowledge-hub branches, and archived worktrees.

## Hidden source pattern

Phase 1–6 confirmed:

| Signal | Count |
|---|---:|
| Priority branches found | 10 / 10 |
| Priority candidate docs | 1,850 |
| Exact duplicate groups | 402 |
| Concept families | 10 |
| Local OKF directories | 52 |

High-signal branches included:

```text
backup/gro-3515-full-okf-blocked
backup/gro-3522-full-okf-blocked
backup/gro-3522-inlane-disconnected
feature/tier-5a-okf-pilot
ned/GRO-3520-local-okf-full
ned/GRO-2445-okf-drive-drift-refresh-push
ned/GRO-2445-okf-drive-drift-check-push
origin/feature/fred-okf-gap13-sync
origin/feature/okf-dispatcher-incident-v2
origin/feature/fred-okf-hde-cron-closeouts-20260713
```

## Current rule

Do not conclude "no Prismatic OKF exists" from the current checkout alone. First inspect:

1. `prismatic-engine/docs/okf-map.md`.
2. `growthwebdev-knowledge/okf/projects/prismatic-engine/index.md`.
3. [Prismatic OKF treasure-map report](../../reports/prismatic-okf-treasure-hunt-2026-07-15.md).
4. Manifests under `/tmp/prismatic-okf-treasure-hunt/manifests/` if still present.

## Cleanup policy

No cleanup is safe until:

- hidden-useful docs are promoted or explicitly queued;
- hidden-historical docs are summarized/indexed;
- duplicate-superseded families are recorded;
- `unsafe/private` candidates are manually reviewed and quarantined/redacted;
- repo-local breadcrumb map points to final canonical structure.

## Batch 3 archive status

Batch 3 archive records are now indexed under [archive/index.md](./archive/index.md). Unsafe/private material remains redacted in [unsafe-private-quarantine.md](./archive/unsafe-private-quarantine.md). Cleanup remains blocked.

## Batch 3 queue

- Ned scan-triage OKF family.
- AGY audit family.
- Canonical merge winner maps.
- unsafe/private quarantine list.
- Archived worktree cleanup candidates.

## Provenance

| Source repo | Branch | Head | Path | Class | Hash |
|---|---|---|---|---|---|
| `prismatic-engine` | `backup/gro-3515-full-okf-blocked` | `3133a5590705` | `okf/memory/2026-06-30-drift.md` | `hidden-useful` | `e237d9205e8a` |
| `prismatic-engine` | `feature/tier-5a-okf-pilot` | `c8e904689e5b` | `okf/journal-schema-drift-fix.md` | `hidden-useful` | `5e7987dcd34d` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/audits/ned-scan-triage-2026-06-27-r20.md` | `hidden-historical` | `6ba9bc7eb118` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/audits/ned-scan-triage-2026-06-27-r21.md` | `hidden-historical` | `8009f0b2850f` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/audits/ned-scan-triage-2026-06-27-r91.md` | `hidden-historical` | `479fefb2f8ea` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/audits/ned-scan-triage-2026-06-27-r92.md` | `hidden-historical` | `a8ba4d0b9a89` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | `okf/audits/ned-scan-triage-2026-06-27-r93.md` | `hidden-historical` | `e94ac6d84ee3` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-gap13-sync` | `5b908cc5cef4` | `okf/audits/ned-scan-triage-2026-06-27-r1.md` | `duplicate-superseded` | `1fc8978d9ff7` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-gap13-sync` | `5b908cc5cef4` | `okf/plugins/prismatic-video-gen/prism_vid_6_automated_multimodal_visual_qa_loops_and_fallback_rollback_recovery.md` | `duplicate-superseded` | `d5832e5003f4` |
| `growthwebdev-knowledge` | `origin/feature/fred-okf-gap13-sync` | `5b908cc5cef4` | `okf/reports/ubersuggest-mcp-setup-and-recovery-2026-06-19.md` | `duplicate-superseded` | `c290aed90956` |

Selection notes:
- Documents the hidden branch/worktree drift pattern and future reconciliation rule.


## Verification boundary

Ad hoc targeted OKF verification only — not full docs-suite green.
