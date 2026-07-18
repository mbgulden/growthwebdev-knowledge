---
type: Report
title: OKF Source-of-Truth Reconciliation — 2026-07-18
description: Control report for consolidating growthwebdev OKF worktrees and branches around origin/main, beginning with the Agent Memory Governance OKF standard.
resource: okf/reports/okf-ssot-reconciliation-2026-07-18.md
tags: [okf, source-of-truth, worktrees, branches, governance, memory]
timestamp: 2026-07-18T22:25:00Z
linear_issue: none
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/okf-ssot-reconciliation-2026-07-18.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# OKF Source-of-Truth Reconciliation — 2026-07-18

## Executive summary

The canonical OKF source of truth is `origin/main` in `mbgulden/growthwebdev-knowledge`.

The first source-of-truth repair is complete: Agent Memory Governance now exists on `origin/main`, is indexed from both the master index and standards index, and the temporary Agent Memory branch/worktree was removed after merge.

No unrelated OKF branch, worktree, or PR cleanup was executed. Remaining branches are source candidates until classified by manifest.

## Agent Memory Governance status

| Field | Value |
|---|---|
| Canonical path | `okf/standards/agent-memory-governance.md` |
| Canonical source | `origin/main` |
| PR | `https://github.com/mbgulden/growthwebdev-knowledge/pull/22` |
| Merge commit | `77fe9fbbcf7dda6445114f5f8f6581ce5fc73986` |
| Temporary worktree | `/tmp/gwd-memory-okf` removed after remote readback |
| Temporary branch | `feature/fred-agent-memory-governance` removed after merge/prune |
| Verification boundary | Ad hoc targeted OKF verification only; not full docs-suite green |

## Current inventory snapshot

Generated from `/tmp/okf-ssot-full-inventory.json`.

| Source class | Count |
|---|---:|
| OKF-ish refs inventoried | 60 |
| Open PRs remaining | 4 |
| Attached worktrees after Agent Memory cleanup | 1 |
| Hidden historical candidates | 35 |
| Open OKF candidates | 17 |
| Prismatic OKF family branches | 5 |
| Unclassified refs | 3 |

## Current attached worktree

| Worktree | Branch | Head | Classification |
|---|---|---|---|
| `/home/ubuntu/work/growthwebdev-knowledge` | `feature/fred-okf-hde-cron-closeouts-20260713` | `0d7add65cb59` | Dirty source candidate; do not treat as canonical; source-manifest before promotion/cleanup |

## Remaining open PRs

| PR | Branch | Mergeability | Recommendation |
|---|---|---|---|
| #12 | `feature/fred-okf-gap13-sync` | mergeable | Source-manifest before merge/close/delete |
| #8 | `feature/pwp-astro-emdash-okf` | mergeable | Source-manifest before merge/close/delete |
| #5 | `feature/okf-dispatcher-incident` | conflicting | Extract useful incident content with `git show`; do not checkout over canonical tree |
| #3 | `feature/okf-pwp-process-doc` | conflicting | Extract useful process content with `git show`; do not checkout over canonical tree |

## Cleanup policy

```yaml
cleanup_executed: false
canonical_source_of_truth: origin/main
approval_required_before_any_unrelated_cleanup: true
source_manifest_required_before_promotion: true
```

Allowed without further approval:

- Remove a temporary worktree/branch created in the same session after its PR is merged and remote readback proves canonical presence.

Not allowed without a source manifest and explicit approval:

- Deleting old OKF branches.
- Closing old OKF PRs as superseded.
- Removing dirty local worktrees.
- Promoting historical docs from backup/Ned scan branches.
- Publishing private/client-sensitive content.

## Next recommended family

Next slice: `feature/fred-okf-hde-cron-closeouts-20260713` in the dirty primary hub checkout.

Reason:

- It is the only attached worktree left for the hub.
- It contains many untracked OKF files and modified indexes.
- It may include useful HDE/cron closeout material, but it must not be treated as canonical until a source manifest separates useful docs from branch noise.

Suggested deliverable:

1. Create `/tmp/okf-hde-cron-source-manifest.json`.
2. Classify every dirty/untracked path as `promote`, `archive`, `duplicate`, `unsafe/private`, or `noise`.
3. Promote only selected docs through a clean worktree from `origin/main`.
4. Merge, verify remote readback, then remove only temporary clean worktrees/branches.
5. Leave the dirty primary checkout alone until its sources are fully accounted for.

## Queued source material

A PDF received in the Hermes session was extracted to `/tmp/hde-sanctuary-pdf-extract.txt`. It appears to be HDE Sanctuary onboarding/email source material and should be handled in the HDE OKF family, not the Agent Memory standard.

## Verification boundary

This report is based on live git/GitHub inventory and remote readback. It does not claim full docs-suite green. Every subsequent promotion batch needs its own focused `/tmp/hermes-verify-*` proof against the changed paths and remote canonical source.
