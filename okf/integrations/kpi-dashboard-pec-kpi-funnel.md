---
type: Integration
title: KPI Dashboard (PE-KPI-FUNNEL) — spec landed, renderer pending
description: State of the HDE KPI dashboard: kpi-collections.json spec (schema 1.0, 6 collections, BigQuery+GA4 sources, Google Sheet/email delivery) is committed on 2 feature branches only; PWP publish_kpi_tracker capability is on prismatic-engine origin/main (the old ned/pwp-publish-kpi-tracker branch was deleted 2026-09-13 — see deletion manifest); renderer slice 2 unbuilt. Tracker ticket GRO-4919.
tags: [kpi, pwp, dashboard, hde, linear, ga4, bigquery, integration]
timestamp: 2026-09-13T02:47:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/kpi-dashboard-pec-kpi-funnel.md
last_verified: 2026-09-13
verified_by: ned
status: current
---

# KPI Dashboard (PE-KPI-FUNNEL) — state of record

> Recorded 2026-09-05 by Ned during the infra-sweep loose-end cleanup, per
> Michael's direction: "needs to be documented and put into a linear task."
> Tracker: [GRO-4919](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4919)
> (land spec on live branch + build renderer slice 2 + deploy).
> **2026-09-13 update:** PWP branch retirement — the
> `ned/pwp-publish-kpi-tracker` branch of prismatic-engine was verified 100%
> superseded by origin/main and deleted (remote + local; manifest:
> [2026-09-13 deletion manifest](2026-09-13-pwp-publish-kpi-tracker-branch-deletion-manifest.md)).

## What is DONE (spec / slice 1 — "first-slice complete" from the 07-31 handoff)

The canonical spec is `scripts/kpis/kpi-collections.json`:

- `schema_version: 1.0`, `owner: ned`, `last_verified: 2026-07-28`
- `collection_window`: rolling 24-month; persistence via **BigQuery** (Stripe→BQ
  export) + **GA4 Data API**
- **6 collections**: `funnel_top`, `funnel_sanctuary`, `funnel_buy_report`,
  `delivery_onboarding`, `aggregates_growth`, `site_hygiene`
- `globally_required`: tracking property, loader-on-every-page, dataLayer event set,
  GA4 recommended events
- `share_targets`:
  - `google_sheet` — `HDE_KPI_SHEET_ID` + `HDE_GOOGLE_SERVICE_ACCOUNT_JSON` env,
    tab layout (Daily/weekly/monthly)
  - `email`
- `delivery_cadence`: daily 06:30 America/Los_Angeles (skip if no new events, covers
  previous 24h UTC), weekly Mon, monthly
- `pwp_dashboard_surface`: `humandesignengine.com/pwp/kpi-dashboard.html`, renders all
  6 collections, **iframe-hosted on the PWP dashboard**

**Where the spec lives (important — it is NOT on any live branch):**

| Copy | Location | State |
|---|---|---|
| 4,949B (07-28 original) | `hd-platform-staging` worktree, branch `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15` | **tracked** (but on a stale feature branch) |
| 12,010B (08-19/08-20 evolved) | `hd-platform-prod-merge` + `hfg-gro4797-branch` | **tracked only on** `feature/gro-4797-hde-guest-fleet-drift-elimination` and `ned/gro-4823-claim-guard-2026-08-21`; the `hd-platform-prod-merge` copy is in a plain dir **with no .git** (untracked, at risk) |
| 1,659B (site-scoped, active-oahu) | `active-oahu-tours-mirror-2529` | tracked; different scope (site KPIs, not HDE funnel) |

**PWP capability** (the consumer side — **now on prismatic-engine origin/main**, 44 files
under `prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/`, verified
2026-09-13; merged via PR #410 `b8cefdb2` + PWP-P2 `ab168e04` + Phase-3 wireup `94318073`):
funnel_form.py (4.2 modal CSS relocated in, CSRF + edit-prefill), linear_status.py (F8),
operator_cli.py/.mjs, cron_orchestrator.py, pending_changes.py, plus
`capabilities/provision_site/` (PWP-P2, Cloudflare-first). Main continued past the old
branch's July state: 4.7 KPI dashboard, 4.8 Zapier prod endpoint, 4.9 funnel form,
4.10 FareHarbor, Phase 5.0, credentials centralization (`6f6a3491`), path-portability
fix (`4e7fd99b`). Related PE-KPI-FUNNEL epic:
[GRO-4356](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4356) (12 tasks);
[GRO-4387](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4387) (Backlog)
adapts `build-report.mjs` → `dashboard_data.js`.

## What is NOT done (slice 2 — the renderer)

1. **Land the spec canonically**: merge the 12,010B evolved `kpi-collections.json`
   onto the live staging branch (or pin it in the canonical HDE repo main line).
   Today the only live-branch copy is the 4,949B 07-28 original.
2. **Build the renderer**: `pwp/kpi-dashboard.html` + data endpoint + the Google
   Sheet export job per `share_targets`/`delivery_cadence` in the spec.
3. **Deploy** to the PWP dashboard surface (iframe per `pwp_dashboard_surface`) and verify.

## Pitfalls

- Do NOT treat the 07-31 "first-slice complete" handoff as implying the dashboard is
  live — slice 1 is the **spec file**, not a rendered page.
- The 12KB evolved spec in `hd-platform-prod-merge` (no .git) is **not under version
  control**. If that dir is cleaned, only the 07-28 4.9KB version (on the stale
  feature branch) and the two feature branches survive. Re-verify before relying on it.
- Two different `kpi-collections.json` files share the name: the HDE funnel spec
  (12KB) and the active-oahu site spec (1.6KB). They are unrelated except in schema.
- The old PWP worktree `~/work/prismatic-pwp-ubersuggest-auth` is now detached at
  origin/main (its branch was deleted 2026-09-13). Do not resume work from it without
  a fresh branch; the golden thread for this line is GRO-4919, not any branch name.

## Verification (2026-09-05; PWP-branch items re-verified 2026-09-13)

- `hd-platform-staging` branch `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15`:
  `git log --all -- scripts/kpis/kpi-collections.json` → tracked; appears on
  `feature/gro-4797-hde-guest-fleet-drift-elimination` + `ned/gro-4823-claim-guard-2026-08-21`.
- 2026-09-13: `git ls-tree -r origin/main -- prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker | wc -l` → 44 files;
  `git ls-remote origin | grep pwp-publish-kpi` → 0 (branch gone from GitHub);
  `gh pr list --repo mbgulden/prismatic-engine --head mbgulden:ned/pwp-publish-kpi-tracker --state all` → `[]`.
- PE-KPI-FUNNEL epic + 12 tasks confirmed in Linear (GRO-4356 family).
