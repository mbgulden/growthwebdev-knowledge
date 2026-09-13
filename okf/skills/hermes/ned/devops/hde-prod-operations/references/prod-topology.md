# HDE Prod Topology — verified 2026-08-27

Session-verified map. Re-probe with `scripts/probe-hde-prod.sh` before trusting any row.

## Branch inventory (repo mbgulden/hd-platform, local clone /home/ubuntu/work/hd-platform)
- `main` (prod frontend, CF Pages production_branch): Astro app `hd-platform-frontend` v0.1.0.
  - `src/pages/deconditioning.astro` = "Somatic Experiment Station" paid page (the page the 14-day demo mirrors).
  - **NO `functions/`, NO `_redirects`, NO `_headers`** on main. Same-origin `/api/*` POST → 405 on both custom domain and .pages.dev.
  - `package.json` scripts: `build` = `astro build` + `postbuild` = `node scripts/route-complete-build.mjs` (preserves 230 legacy files, 529 redirects, sitemap). Build takes ~3s with warm node_modules.
  - main branch protection: OFF (no required status checks, no restrictions).
- `ned/hde-deconditioning-checkout-source` (local, 404+ commits) = **the branch hde-api.service runs** (systemd WorkingDirectory=/home/ubuntu/work/hd-platform).
- `staging/ned-hde-phase4` = monorepo era (docs/, functions/, api/ in one tree). Source of:
  - `docs/sanctuary-demo/index.html` (124-line self-contained page, inline JS, canonical → humandesignengine.com/sanctuary-demo/)
  - `functions/api/demo/start.js`, `functions/api/checkout/{create-session,session}.js` (CF Pages proxies)
  - `api/routes/stripe_webhook.py` `/demo/start` route (the port source)
  - Serves at `staging.humandesignengine.com` with a WORKING end-to-end demo (2026-08-27: POST /api/demo/start → 200 + deep link).
- Stale local checkouts also exist: hd-platform-prod-merge, hd-platform-GRO-3988, hd-platform-staging. `_hde_production_deploy_archive/20260719T032417Z/` = the last monorepo prod deploy.

## Cloudflare (TWO accounts — do not mix)
- **GrowthWeb** `196c1798da487413b0281ccc570f05a1` (Michael@growthwebdev.com) — owns:
  - Pages project `hd-platform` (id a45d6798-74d0-48eb-97d4-8454d786a404; subdomain hd-platform.pages.dev; domains: hd-platform.pages.dev + humandesignengine.com)
  - Zone `humandesignengine.com` (id 5bc0972595ff588618e45fda74a51128)
  - Zone workers incl. `hd-platform` script (no routes listed in account API; 405s on /api/* come from here — source not found in any local repo; 204 on GET /workers/scripts/hd-platform = modules not fetchable via this API shape)
  - Auth: global-key pair `CLOUDFLARE_GROWTHWEB_EMAIL` + `CLOUDFLARE_GROWTHWEB_API_KEY` (X-Auth-Email / X-Auth-Key headers) — verified working for zone + workers + Pages APIs.
- `CLOUDFLARE_PAGES_API_TOKEN` = Bearer token, 53 chars, **works against the GrowthWeb account only** (verified: GET pages project → 200). Against the other account (id 632f481b...) → 10000 Authentication error.
- `CLOUDFLARE_AOT_*` = separate ActiveOahuTours account/zone. Not HDE.

## Backend (hde-api)
- systemd unit `hde-api`: `WorkingDirectory=/home/ubuntu/work/hd-platform`, ExecStart `.venv/bin/python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000`.
- Unit env has `DATABASE_URL=sqlite+aiosqlite:////home/ubuntu/work/hd-platform/production_database.db` (EMPTY file, 0 tables — red herring). The app's repo `.env` `DATABASE_URL=postgresql+asyncpg://hde_app:...@127.0.0.1:5432/hde` wins (repo .env loaded by the app). **Real DB = Postgres hde.**
- CORS: `allow_origins=["*"]` (api/main.py). OPTIONS preflight verified 200 with correct allow-origin/headers/methods.
- Demo env: no `HDE_DEMO_INVITE_CODE` set → code check disabled. `HDE_ONBOARDING_BOT_USERNAME=Humandesigncompanionbot` (repo .env). `send_customer_onboarding_email` fires as background task.
- Restart: `sudo systemctl restart hde-api` (NOPASSWD sudo). From the agent shell, plain `systemctl` → "Interactive authentication required".

## Verified probe outputs (2026-08-27, before/after demo port)
- BEFORE: `GET humandesignengine.com/sanctuary-demo/` → 200, 21620 bytes, title = home title (Pages home fallback; identical bytes to `/definitely-not-a-page-xyz123/`).
- BEFORE: `POST api.humandesignengine.com/api/demo/start` → 404 (route absent). `POST .../api/checkout/create-session` with `{}` → 422 (alive).
- AFTER port (commit 8833dc9 on running branch, service restarted): `POST api.humandesignengine.com/api/demo/start` {email} → **200** `{success, access_status:demo, trial_days:14, deep_link: https://t.me/Humandesigncompanionbot?start=hde_demo_...}`.
- Same-origin probes: `POST humandesignengine.com/api/checkout/create-session` (real payload) → 405; `POST hd-platform.pages.dev/api/checkout/create-session` → 405. Old monorepo deploy `a2b0aadb.hd-platform.pages.dev/api/checkout/create-session` → 502.
- Staging: `POST staging.humandesignengine.com/api/demo/start` → 200 (working reference).

## Unresolved / watch
- **Paid checkout on prod may be broken**: the deconditioning page's same-origin fetch 405s everywhere, yet the flow presumably worked for real users before — possibly a zone-level rule I did not fully map, or it regressed with the Astro migration. Verify with a real checkout flow before declaring paid path dead.
- **Wrangler 6111**: `npx wrangler@latest pages deploy` failed "Invalid format for Authorization header" with CLOUDFLARE_API_TOKEN=*** in env, while the same token works as curl Bearer. Suspect: stale OAuth in `~/.wrangler/config.json` (check `~/.hermes/profiles/ned/home/.config/.wrangler/` — wrangler writes logs under a profile-relative home) shadowing the env token. Untested fallback (NOT verified end-to-end): direct Pages upload API — `POST /accounts/{acct}/pages/projects/{proj}/deployments` (body `{"branch":"main","commit_id":...}`) → `POST {upload_url}/...` with multipart files. See Cloudflare docs; the wrangler error log has the full request context.
