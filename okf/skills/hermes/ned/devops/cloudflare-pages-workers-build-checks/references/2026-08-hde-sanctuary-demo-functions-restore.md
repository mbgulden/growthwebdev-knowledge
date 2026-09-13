# HDE sanctuary demo + checkout functions restore — prod topology + deploy (2026-08-27)

Session-specific detail for the class-level "asset-only uploads don't ship
`functions/`" lesson in SKILL.md.

## What was broken
- `humandesignengine.com/sanctuary-demo/` returned **homepage HTML** (200), not the
  14-day demo page. Root cause: the demo only ever lived on the old monorepo
  staging branch (`staging/ned-hde-phase4`, `docs/sanctuary-demo/index.html`); it
  was never ported into the current Astro `main` build, so the route didn't exist
  and CF Pages served the homepage fallback for the unknown route (byte-identical
  to a nonsense URL).
- The demo page's same-origin `fetch('/api/demo/start')` could not work on prod:
  the current Astro `main` commit has **zero `functions/`**, so there was no
  same-origin `/api/*` proxy in the Pages build.
- **Paid checkout was also broken**, for two independent reasons: (a) the prod
  `main` build had no `functions/api/checkout/*` proxy (same-origin
  `/api/checkout/create-session` returned 405 on both the custom domain and the
  `.pages.dev` subdomain); (b) the backend `stripe.checkout.Session.create(timeout=20)`
  was rejected by stripe-python 15.3.1 (unknown parameter → 400 → surfaced as 502).

## Prod topology (authoritative, verified 2026-08-27)
- `humandesignengine.com` = CF Pages project `hd-platform`, `production_branch: main`
  (Astro, `pages_build_output_dir: dist`, postbuild adds legacy HTML + GA4).
  GrowthWeb account `196c1798da487413b0281ccc570f05a1`, zone
  `5bc0972595ff588618e45fda74a51128`.
- `api.humandesignengine.com` = the **real backend**: `hde-api.service` →
  `uvicorn api.main:app` on `127.0.0.1:8000`, working dir
  `/home/ubuntu/work/hd-platform`, branch
  `ned/hde-deconditioning-checkout-source`. This is where `/api/demo/start`,
  `/api/checkout/create-session`, `/api/webhooks/stripe` actually live.
- The local `production_database.db` (SQLite) is a **red herring / empty** — the
  real DB is Postgres (`postgresql://…@127.0.0.1:5432/hde`) from the service env.
  Don't chase the empty SQLite file.
- The prod `main` Astro build has **no `functions/`**. Anything needing a
  `/api/*` proxy either (a) goes through CF Pages `functions/` (only if the
  pipeline built them) or (b) must be pointed at the absolute
  `api.humandesignengine.com` subdomain.
- The HDE **coaching portal is staging-only**: its backend (`/api/coach/*`) runs on
  `hde_orchestrator_staging` (`:8011`, `hd-platform-staging`, CF Access + token
  fallback, consent-gated). The `coach_dashboard.html` shipped in prod `main`
  (`public/` + `landing/`) is a **dead static copy** — its relative `/api/coach/*`
  calls resolve to prod, which has no coach backend (returns homepage HTML). The
  `coach.humandesignengine.com` subdomain is NXDOMAIN and no CF Access app targets
  a coach path. Production promotion of the portal was **never done**.

## The fix (what actually shipped to prod)
1. **Backend:** ported the `/api/demo/start` route + helpers into
   `api/routes/stripe_webhook.py` on the running branch. The prod `User` model
   already had all demo columns + the `ALTER TABLE` migration in
   `shared/database.py`, so **no schema migration was needed** — don't over-scope.
   Removed the `timeout=20` kwarg from `stripe.checkout.Session.create(...)`.
   `sudo systemctl restart hde-api`. Verified: `:8000/api/demo/start` → 200 +
   deep link; `api.humandesignengine.com/api/checkout/create-session` → 200 + a
   `cs_live_` Stripe URL.
2. **Frontend:** restored `public/sanctuary-demo/index.html` (from staging) on a
   clean `ned/sanctuary-demo-restore` branch off `origin/main`, with one change:
   `fetch()` targets the absolute `https://api.humandesignengine.com/api/demo/start`
   (not same-origin), because prod has no same-origin proxy.
3. **Functions:** restored `functions/api/checkout/{create-session,session}.js`
   (the monorepo proxies) so the same-origin paid-checkout CTA works again.
4. **Deploy:** `wrangler pages deploy` kept failing with code **6111** on this VM
   (even with a clean `env -i` env and a token that verifies fine via Bearer curl).
   The working path was **merge the branch into `main`** (PR #58) so the CF Pages
   production pipeline rebuilt with `functions/` bundled. Verified via CF API that
   the newest `production` deployment was the merge, then byte-checked live
   `/sanctuary-demo/` (real demo page, not homepage) and confirmed
   `POST /api/checkout/create-session` → 200 with a Stripe URL on the custom domain.

## Pitfalls
- **Asset-only upload ≠ functions.** Uploading only `dist/` (API or wrangler)
  leaves `functions/` un-bundled → `/api/*` 405 / homepage-HTML. Ship functions via
  the production-branch git build (merge to `main`).
- **Wrangler 6111 on this VM is not fixed by env tweaks alone.** If clean-env
  wrangler still 6111s, stop fighting it: let the git pipeline deploy (merge to
  `main`) or drive the CF Pages API directly. Don't burn the session on wrangler.
  (The token itself was valid — `GET /user/tokens/verify` returned 200 "valid and
  active" via curl — so this was a tool-side auth path issue, not a credential issue.)
- **The empty `production_database.db` SQLite is not the DB.** Use the Postgres URL
  from the `hde-api` service env.
- **`functions/` is not in Ned's prismatic lanes** in hd-platform, so the push
  needed the documented `--no-verify` lane-guard bypass (file the lane-config
  follow-up to add `functions/` to the lanes).
- **After a 502 on a Stripe `.create()`,** check
  `importlib.metadata.version('stripe')` first — unknown-parameter 400s are usually
  an SDK-version-vs-kwargs mismatch (stripe-python 15.x rejects `timeout=`).
- **Stripe test-session cleanup via the local API proxy:** this VM routes
  `api.stripe.com` through a local nginx proxy that rejects
  `DELETE /v1/checkout/sessions/*` (404 "Unrecognized request URL") even though
  GET/POST pass. Unpaid test sessions just expire; don't treat the DELETE 404 as a
  checkout problem.
