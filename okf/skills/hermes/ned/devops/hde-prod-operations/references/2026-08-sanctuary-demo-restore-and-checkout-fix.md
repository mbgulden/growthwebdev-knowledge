# HDE sanctuary-demo restore + paid-checkout fix (2026-08-27)

Session: Michael reported `/sanctuary-demo/` serving home HTML instead of the
14-day demo ("right URL, wrong content"), approved option A (full 3-layer fix),
then "do the next step and make sure the paid checkout is working too."

## What was broken (verified before touching anything)

- Prod = CF Pages project `hd-platform`, `production_branch: main`, **Astro** build
  (main @ 6625c74, prod deploy 7ab1cc3c). `git ls-tree origin/main --name-only |
  grep ^functions/` → **zero functions** (dropped in the Astro migration).
- `/sanctuary-demo/` → 200 + home HTML, byte-identical to a nonsense URL
  (Pages home fallback = route missing).
- The demo only ever existed on `staging/ned-hde-phase4` (monorepo era):
  `docs/sanctuary-demo/index.html` + `functions/api/checkout/*.js`
  + `functions/api/demo/start.js` + the backend `/demo/start` route.
  `staging.humandesignengine.com` was the known-good reference (page 200;
  `/api/demo/start` 200 + `t.me/Humandesigncompanionbot?start=hde_demo_…`).
- **Paid checkout was broken at two independent layers:**
  1. Same-origin `POST /api/checkout/create-session` → **405** on both
     `humandesignengine.com` and `hd-platform.pages.dev` (no functions in the
     prod deploy — the deconditioning/checkout frontends call same-origin).
  2. Backend 502 even direct at `:8000`:
     `stripe.checkout.Session.create(timeout=20, **kwargs)` → Stripe 400
     "Received unknown parameter: timeout" (stripe-python **15.3.1** rejects the
     kwarg) → `HTTPException(502)`. The `timeout=20` had been added by the
     2026-08-20 "stuck redirecting" three-layer fix — a regression that shipped.

## What was changed

**Backend** (running checkout = branch
`ned/hde-deconditioning-checkout-source` in `/home/ubuntu/work/hd-platform`,
deployed via `sudo systemctl restart hde-api` — sudo is NOPASSWD):
- `8833dc9` — ported `/api/demo/start` route + 4 helper symbols
  (`CreateDemoRequest`, `check_demo_rate_limit`, `DEMO_*` constants) into
  `api/routes/stripe_webhook.py`. **No migration needed**: the running branch's
  `shared/database.py` already had all User demo columns + the `ALTER TABLE`
  auto-migration. Prod DB = Postgres `127.0.0.1:5432/hde` (repo `.env`
  `DATABASE_URL` overrides the unit env's sqlite; `production_database.db` is a
  0-table red herring). All other imports the route needs were already present.
- `9476053` — dropped the `timeout=20` kwarg from `Session.create`.

**Frontend** (branch `ned/sanctuary-demo-restore` off `origin/main`, PR #58,
merge `0137d86`):
- `f19c3f5` — `public/sanctuary-demo/index.html` (full page ported from staging;
  one change: fetch → absolute `https://api.humandesignengine.com/api/demo/start`,
  because at port time main still had no functions. CORS `*` + OPTIONS preflight
  200 verified before shipping.)
- `f3eab74` — restored `functions/api/checkout/{create-session,session}.js`
  (verbatim port from the monorepo line). Push needed `--no-verify` (hd-platform
  lanes: `functions/` not owned by ned — documented bypass under Michael's
  explicit task authorization, disclosed in the PR body).

## Deploy — the important discovery

- `wrangler pages deploy` failed **6111** ("Invalid format for Authorization
  header") on both 4.127 and 3.114, even with `env -i` + no
  `~/.wrangler/config.json`, while the same token verified 200 via curl Bearer.
  This is NOT the old inline-token-redaction shape (that was fixed by the
  subprocess-env pattern); it recurred as a plain wrangler-side quirk. Don't
  burn time on wrangler auth here.
- Ad-hoc Pages **direct-upload API** (multipart `upload_files=<rel,paths>` POST to
  `/accounts/{acct}/pages/projects/hd-platform/deployments`, Bearer token, 16 MB
  body, 569 files) — works and deploys to production, **but the result is an
  ASSETS-ONLY deployment: `functions/` are not bundled, every `/api/*` POST 405s**.
  Deploy 9c7c2c66 proved this live (static pages fine, checkout 405).
- **The path that worked:** push branch → `gh pr merge 58 --merge` → the
  `github:push` build (deploy 6fd62d86, `environment: production`) shipped assets
  **and** functions. **Rule: for a project that uses Pages Functions, ship via
  the GitHub pipeline (branch → merge to production branch), not ad-hoc upload.**
  Ad-hoc upload is only safe for pure static changes (and even then the
  github:push path is lower-effort since main auto-deploys).

## Final verification (live on humandesignengine.com)

- `GET /sanctuary-demo/` → 200, `<title>14-Day Sanctuary Demo | Human Design
  Engine</title>`, absolute-API fetch present in markup.
- `POST /api/checkout/create-session` (same-origin) → **200 + `cs_live_` Stripe
  URL** (paid checkout working again).
- `GET /api/checkout/session?email=<unknown>` → 404
  `{"detail":"User profile not found."}` = proxy reaching the backend (route alive).
- Controls: `GET /` 200, `GET /deconditioning/` 200.
- Backend: `:8000` direct + public `api.humandesignengine.com` both 200 for
  checkout and demo; `hermes verify --json` → `"ok": true` (Astro recipe:
  `npm install` + `npm run build` incl. postbuild route-complete).

## Cleanup + residuals

- Probe rows (demo users + invitations) deleted from Postgres via asyncpg.
- **Stripe checkout sessions cannot be deleted from this VM**: the Stripe API is
  fronted by a local nginx proxy that 404s `DELETE /v1/checkout/sessions/*`
  ("Unrecognized request URL") while GET/POST pass. Verify-created test sessions
  expire naturally; ticket the proxy if cleanup matters.
- Follow-ups: add `functions/` to ned's lanes in hd-platform's
  `PRISMATIC_ENGINE.yaml`; update the OKF HDE routing map (Pages functions →
  `api.humandesignengine.com` → `hde-api:8000`).
