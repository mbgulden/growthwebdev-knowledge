---
type: Report
title: Active Oahu Homepage/Nav Recovery + Prismatic Web Governance System
description: Records the immediate production homepage/nav fixes and the portable governance system added for long-term Prismatic Web Plugin site management.
tags: [active-oahu, homepage, navigation, branch-governance, prismatic-web-plugin, website-management]
timestamp: 2026-07-06T05:50:00Z
status: active
resource: okf/hubs/active-oahu/reports/aot-prismatic-web-governance-2026-07-06.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-tours-mirror
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Homepage/Nav Recovery + Prismatic Web Governance System

## TL;DR

The immediate homepage/nav production fixes were merged and verified live. The deeper issue was not a single page: Active Oahu needed a standing governance system that prevents branch drift, stale PR buildup, unclear staging state, and agent workspace confusion.

This report records both outcomes:

1. **Immediate recovery shipped:** PR #42 and PR #43 merged to `main`; production verified with `nav-fix.css?v=10`, integrated homepage About copy, and no `aot-quick-answer` block.
2. **Long-term guardrail implemented:** a portable Prismatic Web Governance Guard suitable for distribution in the Prismatic Web Plugin.

## Immediate Moves Completed

| Move | Status | Evidence |
|---|---:|---|
| Merge nav readability fix | ✅ Done | PR #42 merged into `main` as `5b7c2351` |
| Merge homepage About/AEO placement fix | ✅ Done | PR #43 merged into `main` as `bc876b02` |
| Verify production picked up nav CSS | ✅ Done | `nav-fix.css?v=10` present on live production |
| Verify ugly quick-answer block removed | ✅ Done | `aot-quick-answer` count = `0` on live production |
| Verify integrated homepage copy exists | ✅ Done | `Active Oahu is a Kailua-based outfitter` present on live production |

Production verification loop result:

```text
try=4 http=200 cache=BYPASS nav=nav-fix.css?v=10 about=1 quick=0 bytes=116015
VERIFIED
```

## Root Governance Problem

The homepage/nav mess exposed a larger operating failure:

- `origin/staging` was not a reliable source of truth.
- The public Pages mirror was serving a different artifact than the stale `origin/staging` branch.
- Real fixes were sitting in open PRs while production remained rough.
- Agents could inspect different local branches/workspaces and reach contradictory conclusions.
- Existing governance was AOT-specific and drift-focused, not a complete website-management control plane.

## New System Added

| Artifact | Purpose |
|---|---|
| `.prismatic-web-governance.json` | Site-specific governance policy/config |
| `scripts/prismatic_web_governance.py` | Portable stdlib-only governance checker |
| `.github/workflows/prismatic-web-governance.yml` | Daily/manual/PR GitHub Actions guard |
| `docs/PRISMATIC_WEB_GOVERNANCE_SYSTEM.md` | Plugin distribution and operating spec |
| `docs/AOT_SITE_MANAGEMENT_STANDARDS.md` update | Makes the governance guard mandatory before staging/production claims |
| `PRISMATIC_ENGINE.yaml` update | Registers the guard as part of AOT site management |

## What the Guard Checks

| Surface | Check |
|---|---|
| Workspace | Dirty worktree warning to stop accidental `git add .` WIP capture |
| Branch topology | Production/staging ahead/behind counts vs configured policy |
| Open PRs | Age, mergeability, protected-path touches, file overlap |
| Live production | HTTP status, no-cache fetch, required markers, forbidden markers |
| Remote branches | Old non-allowed branches that should be pruned or closed |

## First Guard Run — Current AOT Health

The first run correctly reports a mixed state:

| Check | Result | Meaning |
|---|---:|---|
| live-production | ✅ PASS | Homepage/nav fix is live |
| open-prs | ✅ PASS | Remaining open PRs are clean/mergeable after hydration |
| branch-drift | ❌ FAIL | `origin/staging` is behind `origin/main` by 28 commits and has 1 staging-only commit |
| stale-branches | 🟡 WARN | Many old remote branches remain |
| workspace | 🟡 WARN | Expected during implementation branch; CI clean checkout will not show this |

This is the desired behavior: the guard confirms the immediate user-facing fix while refusing to pretend the broader branch/workspace governance problem is solved.

## Long-Term Operating Plan

### Phase 1 — Ship the governance guard

- Open PR from `content/prismatic-web-governance-system`.
- Run the guard in CI and upload reports as artifacts.
- Treat branch-drift FAIL as the known cleanup backlog, not as a blocker to installing the guard.

### Phase 2 — Clean up AOT branch topology

- Decide whether `staging` should be reset/rebuilt from `main` or retired in favor of preview branches.
- Preserve the 1 staging-only commit only if still needed.
- Close or delete stale remote branches after verifying no open PR depends on them.
- Keep `main` as production source unless Cloudflare Pages config proves otherwise.

### Phase 3 — Add recurring reporting

- Run GitHub Action daily.
- Optionally mirror the Markdown report into Linear or Hermes cron when WARN/FAIL appears.
- Do not rely on silent local cron only; stale governance must be visible.

### Phase 4 — Promote to Prismatic Web Plugin

For each managed website, plugin install should create:

1. `.prismatic-web-governance.json`
2. `scripts/prismatic_web_governance.py`
3. `.github/workflows/prismatic-web-governance.yml`
4. site-specific standards doc referencing the guard
5. required/forbidden live markers that encode recent regressions so rollbacks are caught

## Definition of Done

This system is not done when the files exist. It is done when:

- The guard runs locally and in CI.
- The guard catches real AOT drift and live homepage state.
- Agents cannot credibly claim “staging has fixes” without a report.
- Stale PR/branch buildup becomes visible before it becomes gnarly.
- The same pattern can be copied into another Prismatic-managed site with only JSON config changes.

## Next Action

Open and merge the governance-system PR, then run a focused AOT cleanup pass to resolve:

1. `origin/staging` vs `origin/main` topology.
2. stale remote branches older than 14 days.
3. remaining open PRs (#44 and #46) before they age into blockers.
