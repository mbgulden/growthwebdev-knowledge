---
type: Report
title: Ned Pipeline Gap Analysis — 2026-06-15
description: Gap analysis on the Ned review pipeline — identifies where compression feedback loops are breaking.
resource: /home/ubuntu/work/ned-review-pipeline-gap-2026-06-15.md
tags: [report, ned, pipeline, compression]
timestamp: 2026-06-19T10:52:02Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/reports/ned-pipeline-gap-2026-06-15.md
last_verified: 2026-06-19
verified_by: kai
status: current
migrated_from: /home/ubuntu/work/ned-review-pipeline-gap-2026-06-15.md
---

# Ned-Review — Pipeline Gap Report

**Date:** 2026-06-15 02:47 UTC
**Status:** Zero-Work Path (no `agent:ned-review` issues found)
**Action:** Pipeline gap detected, comments posted to GRO-1644 + GRO-1649

## Scan Summary

| Metric | Value |
|--------|-------|
| `agent:ned-review` issues in Todo/In Progress | **0** |
| `agent:ned-*` issues In Progress | **21** (healthy pipeline) |
| Recently Done `agent:ned-*` (last 24h) | **5** (GRO-1653, 1634, 1635, 1594, 1644) |

## Key Finding: GRO-1644 Closed Without Fix

**GRO-1644** ("Replace 158 hardcoded /home/ubuntu paths in skill SKILL.md files") was marked Done at 23:09 UTC after a ned-audit report was posted. **The audit identified the problem but the actual path replacement fix was never executed.**

### Current On-Disk State

```
25 SKILL.md files contain 86 occurrences of /home/ubuntu
```

Top 10 files:
| File | Count |
|------|-------|
| prismatic-engine-operations/SKILL.md | 20 |
| antigravity-cli-orchestration/SKILL.md | 13 |
| ned-audit-agent/SKILL.md | 7 |
| ned-infra-agent/SKILL.md | 5 |
| agy-oauth-authentication/SKILL.md | 5 |
| kai-content-agent/SKILL.md | 4 |
| agy-vision-pipeline/SKILL.md | 3 |
| ned-review-agent/SKILL.md | 3 |
| linear-task-execution-loop/SKILL.md | 3 |
| homelab-inventory-management/SKILL.md | 2 |
| + 15 more with 1-2 each | 21 |

## GRO-1645 — Work Complete on Disk, Linear Stalled

Bearer token credential cleanup IS done. Remaining "Bearer" references are code examples and documentation patterns (`f"Bearer {token}"`, redacted `"Bearer sk-xxx...xxxx"`). No live secrets. However, the assigned agent (`ned-code`) never executed — 2 dispatcher routing comments with zero output.

## GRO-1649 — Quality Gate Still Blocked

NEEDS_FIX since 00:25 UTC. Blocked on GRO-1644's unexecuted fix.

## Chain of Events

1. GRO-1498 → Done (but issues remained)
2. Second Witness audit → GRO-1644 (paths) + GRO-1645 (tokens) created
3. GRO-1644 → ned-audit posted report → **closed Done without fix**
4. GRO-1645 → In Progress, dispatched to Ned 2x → no agent output
5. GRO-1649 → pre-flight gate → 3x false APPROVED → 1x corrected NEEDS_FIX (00:25 UTC)
6. GRO-1653 → meta issue → closed Done (superseded by GRO-1649)
7. **Now (02:47 UTC):** 86 paths still remain, still blocked

## Recommendations

1. Route GRO-1644 fix to ned-code (actual path replacement)
2. Transition GRO-1645 to Done (work complete on disk)
3. Re-verify GRO-1649 after fix for final APPROVED
