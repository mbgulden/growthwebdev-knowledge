# 2026-09-13 — KPI dashboard surface correction + pipeline env pitfalls

## Surface: prismatic.growthwebdev.com, NOT humandesignengine.com
- Michael's correction (2026-09-13): the KPI dashboard (PE-KPI-FUNNEL) lives on
  **prismatic.growthwebdev.com** (Prismatic Engine gateway dashboard, `localhost:9000`
  via cloudflared tunnel; repo prismatic-engine; `prismatic/gateway/dashboard_src/`
  + `prismatic/gateway/routes/pwp.py`). NOT on humandesignengine.com.
- Stale specs said otherwise: hd-platform `scripts/kpis/hde-kpi-system.md` and OKF
  `okf/integrations/kpi-dashboard-pec-kpi-funnel.md` both list
  `humandesignengine.com/pwp/kpi-dashboard.html` as the surface. Wrong — on HDE,
  `/pwp/*` is a CF Pages catch-all (serves home HTML with 200 for any path).
- 2026-09-13 incident: rendered dashboard was deployed to HDE CF Pages
  (hd-platform PR #64, commit f0981d5, verified live), then rolled back after the
  correction (PR #65, revert a6308b8; verified at origin + targeted CF edge purge).
  HDE main restored to 67638e9 content.
- Integration gap (next step): the prismatic PWP tab is the **config** surface only
  (`/api/pwp/sites/kpi`, Configure-KPIs modal); NO gateway route serves the rendered
  metrics dashboard yet. Plan: add a route in `prismatic/gateway/routes/pwp.py` that
  renders from the `publish_kpi_tracker` collections; hd-platform
  `scripts/kpis/render-dashboard.mjs` is the reference implementation (data-source
  banner + noindex).

## Pipeline env pitfall (hd-platform scripts/kpis/*.mjs)
- The scripts read `process.env` directly and do NOT load the repo `.env`. Source it
  first: `set -a; . ./.env; set +a` before build-report / sync-sheet / send-email / cli.
- Live state 2026-09-13: `STRIPE_SECRET_KEY` (sk_live_) in hd-platform/.env works
  (events API 200; one transient 401 observed → fetch is wrapped in try/catch with
  fixture fallback so a bad key can't kill the daily cron).
  `HDE_GOOGLE_SERVICE_ACCOUNT_JSON` / `HDE_KPI_SHEET_ID` / `HDE_SMTP_*` absent
  everywhere → GA4 = fixture; sheet sync degrades to `/tmp/hde-kpi-sheet.csv`;
  email degrades to `/tmp/kpi-email.eml`. Both degradations are by design (verified).
- Data-source honesty (added 2026-09-13 to build-report/render-dashboard): report
  carries `data_source: {stripe: live|fixture_fallback|fixture, ga4: live|fixture}`
  and the rendered page shows a visible warning banner when not both live. Never let
  a public page silently display seed data as production numbers.

## Deploy mechanics (details in hde-prod-operations)
- Strict-superset dist check + preview-first deploy + revert-PR rollback + targeted
  CF `purge_cache`. hd-platform main: direct push blocked by push rule — use a PR.
