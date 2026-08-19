---
type: Report
title: AOT Governance Finalization — 2026-07-06
description: Finish the homepage/nav recovery and convert the branch/PR/workspace cleanup into a reusable governance system suitable for the Prismatic Web Plugin.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/reports/aot-governance-finalization-2026-07-06.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# AOT Governance Finalization — 2026-07-06

## Purpose

Finish the homepage/nav recovery and convert the branch/PR/workspace cleanup into a reusable governance system suitable for the Prismatic Web Plugin.

## Immediate production outcome

Production homepage/nav recovery is complete and verified:

- `nav-fix.css?v=10` is live on production.
- The integrated “Active Oahu is a Kailua-based outfitter” homepage copy is live.
- The awkward `aot-quick-answer` homepage block is absent.
- Open PR queue was cleared by merging the clean outstanding PRs.

## Branch reconciliation outcome

Before cleanup:

- `origin/staging` was behind `origin/main` by 36 commits.
- `origin/main` was behind `origin/staging` by 1 commit.
- `git cherry -v origin/main origin/staging` showed the staging-only redirect patch was already represented on production before the staging sync.

Action taken:

- Opened and merged PR #51 from current `main` into `staging`.
- This used a normal GitHub PR/merge path — no force-push, no shared-branch rewrite.

After cleanup:

```text
origin/main tree    = ffa848d3344e43acfbea5bc034bee00d07eb1ba5
origin/staging tree = ffa848d3344e43acfbea5bc034bee00d07eb1ba5
staging behind main = 0
main behind staging = 2
```

Interpretation:

- Production and staging now have identical deployable site trees.
- Remaining ahead/behind is history-only drift from the normal staging merge path and the old redirect commit.
- Agents must not merge staging into production merely to chase history shape.

## Governance system shipped

Public site repo now contains the Prismatic Web Governance Guard:

- `.prismatic-web-governance.json`
- `scripts/prismatic_web_governance.py`
- `.github/workflows/prismatic-web-governance.yml`
- `docs/PRISMATIC_WEB_GOVERNANCE_SYSTEM.md`
- `docs/AOT_SITE_MANAGEMENT_STANDARDS.md`

Guard capabilities:

1. Workspace cleanliness check.
2. Branch ahead/behind counts.
3. `git cherry -v` patch-equivalence detection.
4. Production/staging tree-SHA equality detection.
5. Open PR hygiene: age, mergeability, protected paths, overlaps.
6. Live production marker checks for homepage/nav regressions.
7. Stale remote branch warning.
8. Markdown + JSON reporting for CI, Linear, Hermes cron, and plugin distribution.

## Long-term governance model

The Prismatic Web Plugin should install this governance layer for every managed website:

1. A site-specific `.prismatic-web-governance.json` policy.
2. A portable stdlib `scripts/prismatic_web_governance.py` checker.
3. A scheduled/manual GitHub Action that uploads reports.
4. A site standards doc requiring the guard before claims about staging, production, or PR safety.
5. Optional Hermes no-agent watchdog that runs from a dedicated clean worktree and reports only WARN/FAIL.

## Active Oahu project boundaries

Active Oahu now has clear repo roles:

| Repo | Role |
|---|---|
| `active-oahu-tours-mirror` | Public deployable site mirror and public-safe site governance docs |
| `active-oahu-business` | Private business OKF, operations, compliance, vendor/analytics notes, governance program records |
| `aot-seo-knowledge` | Private SEO/GEO/AI-search strategy, keyword data, competitor research, content briefs |

## Remaining backlog

The core branch/PR mess is cleaned up. Remaining governance debt:

1. Stale remote branch pruning — report first, delete only when owner/dependency is known.
2. Expand the governance guard into a reusable Prismatic Web Plugin template installer.
3. Add project-level governance indexes in the private business OKF so all Active Oahu projects point to the correct repo/source-of-truth.

## Verification expectation

For future edits to this system, use focused ad-hoc verification when no canonical suite exists:

- create `/tmp/hermes-verify-*.py` via `tempfile`
- assert changed paths exist and have no conflict markers
- compile Python scripts
- run the guard in `--report-only`
- assert live production markers
- assert tree equality / branch reconciliation semantics
- clean up the temporary verifier

Do not call this “suite green” unless a canonical suite or Lighthouse run actually passed.
