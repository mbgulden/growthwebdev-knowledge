---
type: Integration
title: KPI Dashboard (PE-KPI-FUNNEL) — spec landed, renderer pending
description: State of the HDE KPI dashboard: kpi-collections.json spec (schema 1.0, 6 collections, BigQuery+GA4 sources, Google Sheet/email delivery) is committed on 2 feature branches only; PWP publish_kpi_tracker capability exists; renderer slice 2 unbuilt. Tracker ticket GRO-4919.
resource: okf/integrations/kpi-dashboard-pec-kpi-funnel.md
tags: [kpi, pwp, dashboard, hde, linear, ga4, bigquery, integration]
timestamp: 2026-09-05T17:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/kpi-dashboard-pec-kpi-funnel.md
last_verified: 2026-09-05
verified_by: ned
status: current
---

# KPI Dashboard (PE-KPI-FUNNEL) — state of record

> **Recorded 2026-09-05 by Ned** during the infra-sweep loose-end cleanup, per
> Michael's direction: "needs to be documented and put into a linear task."
> Tracker: [GRO-4919](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4919)
> (land spec on live branch + build renderer slice 2 + deploy).

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

**PWP capability** (the consumer side, exists and tested):
`prismatic-pwp-ubersuggest-auth/prismatic/shipped_plugins/pwp/capabilities/publish_kpi_tracker/`
— imported by `prismatic/shipped_plugins/pwp/plugin.py:24`; provision_site step tests
cover github/stripe/zapier/funnel_config. Related PE-KPI-FUNNEL epic:
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

## Verification (2026-09-05)

- `hd-platform-staging` branch `ned/hde-phase4-paid-bot-onboarding-quality-2026-07-15`:
  `git log --all -- scripts/kpis/kpi-collections.json` → tracked; appears on
  `feature/gro-4797-hde-guest-fleet-drift-elimination` + `ned/gro-4823-claim-guard-2026-08-21`.
- PWP capability present: `grep publish_kpi_tracker prismatic/shipped_plugins/pwp/plugin.py` → line 24.
- PE-KPI-FUNNEL epic + 12 tasks confirmed in Linear (GRO-4356 family).
