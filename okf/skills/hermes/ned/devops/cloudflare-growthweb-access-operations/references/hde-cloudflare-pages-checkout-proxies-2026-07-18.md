# HDE Cloudflare Pages Checkout Proxies — 2026-07-18

Session-specific reference for the production checkout `405` failure after staging promotion.

## Symptom

- Staging checkout worked through VM/nginx/API routing.
- Production `https://humandesignengine.com/api/checkout/create-session` returned `HTTP 405` because `humandesignengine.com` is Cloudflare Pages, not the local nginx root.
- `https://api.humandesignengine.com/api/checkout/create-session` could work while the same-origin production route still failed.

## Durable fix pattern

Add Cloudflare Pages Functions to the Pages project before promoting staging/static content to production:

- `functions/api/checkout/create-session.js` proxies `POST` and `OPTIONS` to `https://api.humandesignengine.com/api/checkout/create-session`.
- `functions/api/checkout/session.js` proxies to `https://api.humandesignengine.com/api/checkout/session`.
- `functions/create-checkout.js` proxies legacy `POST`/`OPTIONS` to `https://api.humandesignengine.com/create-checkout`.
- Document the route contract in `docs/hde-production-pages-functions.md`.

## Required verification

Before production deploy:

```bash
node --check functions/api/checkout/create-session.js
node --check functions/api/checkout/session.js
node --check functions/create-checkout.js
npm run build
```

After production deploy, POST a smoke payload to all relevant routes and require `HTTP 200` plus a Stripe Checkout URL:

- `https://humandesignengine.com/api/checkout/create-session`
- `https://humandesignengine.com/create-checkout`
- `https://api.humandesignengine.com/api/checkout/create-session`

Then browser-smoke `/buy-report/` to Stripe without completing payment.

## Pitfalls

- Deploying verified staging `dist/` alone can still break production checkout if Pages Functions are missing from the Pages deployment.
- Do not use the Cloudflare Pages API token for Access-app operations; use the global-key `X-Auth-Email` + `X-Auth-Key` shape from `/home/ubuntu/cf_setup_staging.py` for Access bypass work.
- Do not leave nginx backup files in `/etc/nginx/sites-enabled/`; duplicate enabled server blocks create misleading warnings.
