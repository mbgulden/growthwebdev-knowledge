---
type: Report
title: GRO-585 Hreflang signal audit — 2026-07-12
description: Audited static HTML hreflang signals for Active Oahu Tours after the Japanese route cleanup and Hawaiian diacritical pass.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/reports/golden-thread/gro-585-hreflang-audit-20260712/README.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# GRO-585 Hreflang signal audit — 2026-07-12

## Scope

Audited static HTML hreflang signals for Active Oahu Tours after the Japanese route cleanup and Hawaiian diacritical pass.

Issue: [GRO-585](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-585)

## Baseline

| Metric | Before |
|---|---:|
| HTML files scanned | 310 |
| Files with hreflang clusters | 298 |
| Files without hreflang clusters | 12 |
| Issue counts | `{"en_href_mismatch": 137, "counterpart_missing": 80, "missing_en_or_ja": 34, "ja_href_mismatch": 26, "duplicate_hreflang": 23}` |
| Pages with existing en/ja counterpart | 218 |
| Pages with missing counterpart | 80 |

## Changes

1. Replaced hreflang clusters on 218 files where both English and Japanese routes exist.
   - `en` now points to the current English canonical route.
   - `ja` now points to the verified Japanese counterpart route.
   - Duplicate/mismatched clusters were collapsed to one `en` + one `ja` pair.
2. Removed invalid hreflang clusters from 80 files where the expected counterpart route does not exist.
   - No fake `/ja/` fallbacks were created.
   - This avoids sending search engines to missing or non-equivalent Japanese pages.

## Final scan

| Metric | Final |
|---|---:|
| HTML files scanned | 310 |
| Files with valid hreflang clusters | 218 |
| Files without hreflang clusters | 92 |
| Hreflang issue counts | `{}` |
| Valid en/ja counterpart clusters | 218 |

## Interpretation

All remaining hreflang clusters now point only to verified existing route pairs. Pages without a real translated counterpart no longer advertise a fake or stale alternate. This is safer for users and search engines than keeping broken `ja` alternates.

## Artifact files

- `hreflang-before.json` — full baseline scan.
- `safe-pair-fix.json` — changed files with verified counterparts.
- `invalid-cluster-removal.json` — removed invalid no-counterpart clusters.
- `hreflang-final.json` — final zero-issue scan.

## Follow-up

If the business wants every English page to have a Japanese alternate, the next work is content/route creation for the 80 missing counterpart pages, not hreflang tag editing.
