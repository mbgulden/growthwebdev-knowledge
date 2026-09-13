---
name: hde-prod-operations
description: "Use when operating or deploying HDE (humandesignengine.com)."
---

# HDE Production Operations (humandesignengine.com)

Class-level ops for the Human Design Engine production stack. Full map (branch inventory, auth matrix, verified probe outputs) → `references/prod-topology.md`. Read-only health probe → `scripts/probe-hde-prod.sh`.

## Production topology (verified 2026-08-27)

| Layer | Where |
|---|---|
| Frontend | CF Pages project `hd-platform`, **production_branch=main**, custom domain `humandesignengine.com` attached to the Pages project. Current prod = **Astro** app. Monorepo-era code (`docs/`, `functions/api/*`) is NOT on main — it lives on `staging/ned-hde-phase4` |
| Backend | `hde-api.service` (uvicorn `api.main:app` :8000) in `/home/ubuntu/work/hd-platform` (branch `ned/hde-deconditioning-checkout-source`, local-only). Public: `api.humandesignengine.com` → tunnel → :8000 |
| DB | **Postgres** `127.0.0.1:5432/hde` via `DATABASE_URL` in repo `.env` — it overrides the unit env's sqlite. `production_database.db` (0 tables) is a red herring |
| CF auth | **TWO accounts.** GrowthWeb `196c1798da487413b0281ccc570f05a1` owns hd-platform + zone: global-key pair `CLOUDFLARE_GROWTHWEB_EMAIL/KEY` (X-Auth-Email/X-Auth-Key). `CLOUDFLARE_PAGES_API_TOKEN` is a **Bearer** token that works ONLY against the GrowthWeb account (wrong account → 10000 "Authentication error") |
| Env | `HDE_ONBOARDING_BOT_USERNAME=Humandesigncompanionbot` (repo .env). Backend CORS `allow_origins=["*"]` |

## Frontend → API routing (RESTORED 2026-08-27, PR #58 / merge 0137d86)

`functions/api/checkout/{create-session,session}.js` are back on `main` (ported
from the monorepo line), so same-origin `/api/checkout/*` POSTs work again —
verified live: `POST /api/checkout/create-session` on `humandesignengine.com`
→ 200 + `cs_live_` URL. New page that POSTs to the API: same-origin fetch is
fine for the restored checkout routes; for anything else, prefer the absolute
`https://api.humandesignengine.com/api/...` (CORS `*`, preflight 200) — never
assume a same-origin route exists. Full session record:
`references/2026-08-sanctuary-demo-restore-and-checkout-fix.md`.

## Pitfall: "right URL, wrong content" = Pages home fallback
CF Pages serves **home HTML with HTTP 200** for unknown routes. Verify by content, not status: curl the suspect URL and a nonsense URL, compare byte size + `<title>`. Byte-identical size = route missing (fallback).

## Deploy frontend to prod
1. Worktree from `origin/main`, branch `ned/...`, commit prefix `[Ned] ... (#GRO-xxx)`.
2. `npm run build` — NOT bare `astro build`: postbuild `scripts/route-complete-build.mjs` preserves ~230 legacy files + generates redirects/sitemap.
3. `npx wrangler pages deploy dist --project-name=hd-platform --branch=main` with `CLOUDFLARE_API_TOKEN=*** (the Bearer one, GrowthWeb account) + `CLOUDFLARE_ACCOUNT_ID=196c1798...`.
   - **`--branch=main` is mandatory** — without it you get a preview deploy and prod silently keeps the old one.
   - 2026-09-13: wrangler 4.131.1 works with `CLOUDFLARE_API_TOKEN` + `CLOUDFLARE_ACCOUNT_ID` exported (deployments list + preview deploy verified end-to-end); the 08-27 6111 did not reproduce. If it reappears, check stale OAuth in `~/.wrangler/` first (see Notes).
4. After deploy: run `scripts/probe-hde-prod.sh`. `/sanctuary-demo/` must show title "14-Day Sanctuary Demo" and a byte size different from `/`.

## Pre-deploy safety (verified 2026-09-13)
- **Strict-superset check**: build a clean baseline worktree at the CURRENT prod source SHA (`git worktree add --detach /tmp/base <prod-sha>`, symlink `node_modules`), `npm run build` both, then `comm -23 baseline.txt new.txt` (removed files) must be **empty** and `comm -13` must list only your intended new files. Content diffs on shared files: allow only machine-generated additive ones (`_redirects`, `sitemap.xml`, `route-complete-summary.json`).
- **Preview first**: `npx wrangler pages deploy dist --project-name=hd-platform` **without** `--branch=main` → verify the preview URL by content (new route + home + one legacy route) before touching prod.
- **Confirm the intended public surface before first prod deploy of a new content class** — and with the human. 2026-09-13: I deployed the HDE KPI dashboard to humandesignengine.com per stale specs (hde-kpi-system.md / OKF kpi-dashboard-pec-kpi-funnel.md both said `humandesignengine.com/pwp/kpi-dashboard.html`). The correct surface is **prismatic.growthwebdev.com** (Prismatic Engine gateway dashboard, `:9000` via cloudflared) — Michael corrected me mid-session. I deployed it (hd-platform PR #64, f0981d5) then rolled back (PR #65, a6308b8). HDE `/pwp/*` is a CF Pages catch-all (200 + home HTML on ANY path) — it is not a real surface.

## Rolling back a Pages deploy (wrong deploy / wrong surface)
1. Revert the bad commit on a `ned/...` branch from `origin/main`: `git checkout -B ned/<x>-rollback origin/main && git revert --no-edit <bad-sha>`. Push the branch, open + `gh pr merge --squash` (direct push to main is blocked — see Notes).
2. CF auto-redeploys (github:push). Poll `GET /accounts/{acct}/pages/projects/hd-platform/deployments?per_page=1` (Bearer Pages token) until latest stage = `success` and `deployment_trigger.metadata.commit_hash` = your revert SHA.
3. **Verify on the new deployment's own URL** (`https://<short_id>.hd-platform.pages.dev/...`), NOT the custom domain: the custom-domain edge cache keeps serving deleted files for minutes after a successful deploy. A removed route still 200-ing on the custom domain is edge lag, not a failed rollback.
4. Clear the lag with a targeted purge (GrowthWeb global key from `/home/ubuntu/cf_setup_staging.py`, `X-Auth-Email`/`X-Auth-Key` — NOT the Pages Bearer): `POST /client/v4/zones/5bc0972595ff588618e45fda74a51128/purge_cache` body `{"files": ["https://humandesignengine.com/<removed-path>", ...]}`.
5. Re-probe the custom domain after the purge.

## Route/feature port into the running backend (template: sanctuary demo, 2026-08-27)
1. Find the route in the staging branch; diff required symbols (request model, constants, helpers) against the running checkout — the running branch often ALREADY has model columns + migrations (here `shared/database.py` had all demo columns + `ALTER TABLE`), so the port is route code only.
2. Patch `api/routes/stripe_webhook.py` (imports already present: hmac, secrets, select, BackgroundTasks, User/Invitation, bot username, onboarding emailer).
3. Syntax-check via `ast.parse` in execute_code — the terminal parser false-positives and blocks `py_compile` in some compound command shapes.
4. Commit → `sudo systemctl restart hde-api` (sudo is NOPASSWD; plain `systemctl` from the agent = "Interactive authentication required").
5. Verify: POST local :8000 → public `api.humandesignengine.com` → control route (checkout `{}` → 422 = alive).
6. Clean up test rows from the REAL DB (Postgres via asyncpg — not the empty sqlite).

## Coach portal client management: promote to "premium client" (2026-09)

The dashboard `GET /api/coach/clients` (served by the staging orchestrator `:8011`, behind the promoted `api.humandesignengine.com` portal) lists **only** users satisfying **all five**:
`is_premium=True` AND `subscription_status="active"` AND `coach_review_consent=True` AND `coach_review_consent_revoked_at IS NULL` AND (`coaching_container_end IS NULL` OR `coaching_container_end >= now`).

Promote a user to a premium client (direct Postgres UPDATE on prod `127.0.0.1:5432/hde`, `hde_app` role, via asyncpg):
- Set `is_premium=True`, `coach_review_consent=True`, `coach_review_consent_at=now()`, `coach_review_consent_source='admin_promotion'`, `coach_review_consent_revoked_at=NULL`, and `coaching_container_end = now() + interval '6 weeks'` (matches the checkout `is_premium_tier` 6-week window). A user can be `is_premium=True`/`active` yet still invisible because consent is False or the container window expired — check all five, not just the flag.
- **Verify by reading back through the live endpoint, not just the DB row:** `GET :8011/api/coach/clients` (with the coach's CF-Access email header or token) and confirm the user appears with `container_status` and a future `coaching_container_end` (or `null` if never-expire).
- **Never-expire = `coaching_container_end = NULL`** (the predicate treats NULL as unexpired) — no new flag needed.
- **Promotions must clear the trial-lifecycle flags** (`trial_expires_at`, `deletion_scheduled_at`, `deactivated_at`) or the purge cron deletes/reactivates the account against you (a demo user's scheduled deletion can be hours away). A `suspended` bot container auto-wakes on the client's next Telegram message — don't force-flip `bot_instances.status`.
- **Bulk scope check first:** `users` mixes ~5 real clients with ~37 synthetic test rows (`example.com/.invalid/.test`, `fred+*`, `guest+*`, `deleted+demo+*`). "Activate the other accounts" is ambiguous — list + classify, then confirm with Michael (he chose deactivate for the synthetic rows: `subscription_status='inactive'`, `is_premium=FALSE`).
- **asyncpg gotchas:** read `DATABASE_URL` from `hd-platform-staging/.env` (strip the `postgresql+asyncpg://` prefix); no `con.commit()` (auto-commit per statement — a script "crashing" on commit() already applied); placeholders are `$1,$2`, not `%s`; `bot_instances` joins via `user_id` (no email column).
- **Before promoting a *named* client, confirm the account exists.** Michael's "Alicia" was not in `users` (nor any of 11 tables, all columns, case-insensitive) — don't guess an email. Sweep first: enumerate `information_schema.columns` per table and `LOWER(CAST(col AS TEXT)) LIKE '%name%'` across every column; on zero hits, **ask for the account's email** before creating/assuming a row.
- Full record (predicate, SQL, the all-table sweep, and the related stripe-15.x timeout fix): `references/2026-09-coach-premium-promotion.md`.

## Notes
- `main` push: a repo push rule rejects direct pushes to main (`Use deploy-fresh for staging, then merge manually`) — observed 2026-09-13. Use a `ned/...` branch + PR; `gh pr merge --squash --delete-branch` works and triggers the CF git redeploy (github:push trigger). GitHub branch protection (required checks) is a separate thing from this push rule.
- Local nginx `humandesignengine` + `cloudflared-hde` = legacy, NOT the origin. Ignore.
- Stale `~/.wrangler` OAuth state may shadow `CLOUDFLARE_API_TOKEN`; check `~/.wrangler/config.json` when wrangler auth fails but curl Bearer works.
- Coaching portal (promoted 2026-08-25, "A"): live at `api.humandesignengine.com/coach/dashboard` + `/api/coach/*` via the `api-humandesignengine` nginx (`:8091` = `cloudflared-hde` tunnel target) → orchestrator `:8011`. Double-gated: edge CF Access 302 (the `api` host app already covers all paths) + origin 403 on missing `cf_access_jwt_assertion`. The dead apex `coach_dashboard.html` copies are now redirect stubs; `docs/becca-coaching.html` is marketing (untouched). Full record: `references/hde-coach-portal-promotion-2026-08-25.md`.
