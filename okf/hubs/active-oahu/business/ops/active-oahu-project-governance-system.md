---
type: Operations
title: Active Oahu Project Governance System
description: **Date:** 2026-07-06 **Owner:** Kai, Orchestrator of Tourism **Scope:** Active Oahu Tours, Active Oahu LLC, tourism-adjacent Active Oahu projects, and future Prismatic Web Plugin site installs.
tags: [active-oahu, hub, migrated]
timestamp: 2026-08-19T14:27:09Z
status: current
resource: okf/hubs/active-oahu/business/ops/active-oahu-project-governance-system.md
git_repo: mbgulden/growthwebdev-knowledge
migrated_from_repo: mbgulden/active-oahu-business
last_verified: 2026-08-19
verified_by: kai
---

# Active Oahu Project Governance System

**Date:** 2026-07-06  
**Owner:** Kai, Orchestrator of Tourism  
**Scope:** Active Oahu Tours, Active Oahu LLC, tourism-adjacent Active Oahu projects, and future Prismatic Web Plugin site installs.

## Goal

Keep every Active Oahu project clean, clear, and auditable:

- no mystery staging/production claims
- no stale open PR pile
- no untracked agent workspaces getting mixed together
- no private OKF leaking into the public deploy mirror
- no homepage/nav regressions silently reappearing
- no future tourism project launching without the same governance guardrails

## Repo source-of-truth map

| Repo | Visibility | Source of truth for |
|---|---:|---|
| `mbgulden/active-oahu-tours-mirror` | Public | Deployable static website files, public-safe site governance docs, Cloudflare Pages source |
| `mbgulden/active-oahu-business` | Private | Business OKF, compliance, operations, incidents, vendor/account notes, analytics notes, internal decisions, future tourism-adjacent entities |
| `mbgulden/aot-seo-knowledge` | Private | SEO/GEO/AI-search strategy, keyword data, competitor intelligence, content briefs |

Decision rule: if the file explains how the business operates or contains internal vendor/account/analytics/incident context, it belongs here in `active-oahu-business`, not in the public site mirror.

## Governance layers now in place

### 1. Public site governance guard

Installed in `active-oahu-tours-mirror`:

- `.prismatic-web-governance.json`
- `scripts/prismatic_web_governance.py`
- `.github/workflows/prismatic-web-governance.yml`
- `docs/PRISMATIC_WEB_GOVERNANCE_SYSTEM.md`
- `docs/AOT_SITE_MANAGEMENT_STANDARDS.md`

The guard checks:

1. Workspace cleanliness.
2. Production/staging ahead-behind counts.
3. `git cherry -v` patch-equivalence.
4. Production/staging tree-SHA equality.
5. Open PR health.
6. Live production homepage/nav markers.
7. Stale remote branches.
8. Markdown + JSON report output.

### 2. Non-force staging reconciliation

Staging was brought forward via PR #51 from current `main` into `staging`.

Outcome:

```text
staging behind main = 0
main behind staging = 2
origin/main tree    = ffa848d3344e43acfbea5bc034bee00d07eb1ba5
origin/staging tree = ffa848d3344e43acfbea5bc034bee00d07eb1ba5
```

Meaning:

- Deployable trees are identical.
- Remaining divergence is history-only.
- Agents must not merge staging into production just to chase history shape.
- No shared branch force-push was used.

### 3. Hermes governance watchdog

Kai profile script:

```text
/home/ubuntu/.hermes/profiles/kai/scripts/aot_governance_watchdog.py
```

Cron:

```text
AOT governance watchdog — 0 19 * * * — deliver origin — no_agent
```

Behavior:

- Maintains a dedicated clean detached worktree at `/home/ubuntu/work/aot-governance-watchdog-worktree`.
- Runs the guard from `origin/main`.
- Emits nothing when healthy.
- Emits WARN/FAIL summaries to Michael when drift or stale branches exist.

## Operating rules for all Active Oahu web projects

1. Branch from `main` for new public-site work unless a documented project-specific rule says otherwise.
2. Use feature branches and PRs; never push directly to `main`.
3. Never force-push shared branches (`main`, `staging`, `deploy-fresh`).
4. Before saying “staging has it,” “production is fixed,” or “this PR is safe,” run the governance guard.
5. For visible homepage/layout changes, verify rendered/browser behavior, not just curl/DOM markers.
6. Keep internal OKF in `active-oahu-business`; keep SEO intelligence in `aot-seo-knowledge`; keep the public mirror deploy-focused.
7. Stale branches are cleanup backlog, not automatic deletion candidates. Delete only after owner/dependency review.
8. Future tourism-adjacent site repos should receive the Prismatic Web Governance Guard at repo creation.

## Prismatic Web Plugin distribution requirements

The reusable governance package now lives in the public site mirror at:

```text
prismatic-web-plugin/governance/
```

It includes:

| Artifact | Purpose |
|---|---|
| `README.md` | Human install/operating guide |
| `templates/prismatic-web-governance.json.tmpl` | Site-specific config template |
| `templates/prismatic-web-governance.yml.tmpl` | GitHub Actions workflow template |
| `scripts/install_prismatic_web_governance.py` | Stdlib installer that writes config, workflow, and guard into a target repo |

The plugin-worthy governance package installs:

| Artifact | Purpose |
|---|---|
| `.prismatic-web-governance.json` | Site-specific policy, branches, URLs, live markers |
| `scripts/prismatic_web_governance.py` | Portable stdlib guard |
| `.github/workflows/prismatic-web-governance.yml` | Scheduled/manual/PR reporting |
| `docs/PRISMATIC_WEB_GOVERNANCE_SYSTEM.md` | Human operating model |
| site standards doc section | Requires guard before production/staging claims |
| optional Hermes watchdog | Autonomous WARN/FAIL reporting from a clean worktree |

For a new managed site, the first plugin install should configure required/forbidden live markers for that site’s homepage/nav equivalent. The guard should start in `--report-only` until initial debt is cleaned.

## Current status

| Area | Status | Notes |
|---|---:|---|
| Production homepage/nav | ✅ Clean | nav v10 live, About copy integrated, quick-answer block absent |
| Open PRs | ✅ Clean | Remaining PR pile cleared during recovery |
| Staging branch | ✅ Deployable-tree clean | identical tree to main after PR #51 |
| Governance guard | ✅ Installed | CI + local + watchdog capable |
| OKF repo boundaries | ✅ Established | public/private/SEO repo split documented |
| Stale remote branches | 🟡 Backlog | monitor/report first, prune after owner review |
| Plugin packaging | ✅ Complete | reusable installer/templates live in `prismatic-web-plugin/governance/` |

## Next actions

1. Add per-project governance registry entries for any future Active Oahu tourism projects as they appear.
2. Run stale-branch owner/dependency review before pruning.
3. Keep the daily watchdog enabled until stale branch backlog is resolved.
4. Install the governance package at repo creation time for every future Active Oahu / Prismatic-managed tourism site.
