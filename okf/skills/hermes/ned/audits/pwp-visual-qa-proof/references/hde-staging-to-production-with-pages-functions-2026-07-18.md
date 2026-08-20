# HDE staging-to-production promotion with Cloudflare Pages Functions

## Context
HDE staging can be VM-backed/nginx-backed while production `humandesignengine.com` is Cloudflare Pages. A staging build can visually pass and still fail production checkout if Pages Functions are missing from the promoted artifact.

Observed failure before promotion:

```text
POST https://humandesignengine.com/api/checkout/create-session
HTTP 405
```

The staging HTML/VM route was healthy, but production same-origin checkout needed Pages Functions to proxy browser calls to `api.humandesignengine.com`.

## Durable promotion rule
When promoting HDE staging to production, verify both content and production-only routing shape before deploying `--branch main`.

Required pre-promotion checks:

```bash
node --check functions/api/checkout/create-session.js
node --check functions/api/checkout/session.js
node --check functions/create-checkout.js
npm run build
```

Required production proxy files:

```text
functions/api/checkout/create-session.js
functions/api/checkout/session.js
functions/create-checkout.js
```

They should proxy to the public API origin:

```text
https://api.humandesignengine.com/api/checkout/create-session
https://api.humandesignengine.com/api/checkout/session
https://api.humandesignengine.com/create-checkout
```

## Promotion verification
After `wrangler pages deploy dist --project-name hd-platform --branch main`, prove all of these:

1. Cloudflare Pages latest production deployment is the new deployment ID and branch `main`.
2. Cache-busted production HTML has the modern emdash shell and expected price/copy markers.
3. Production same-origin APIs return HTTP 200 plus Stripe Checkout URLs:

```bash
curl -sS -D /tmp/headers -o /tmp/body \
  -X POST https://humandesignengine.com/api/checkout/create-session \
  -H 'Content-Type: application/json' \
  --data '{"email":"smoke@example.test","product_name":"Human Design Natal Report","product_description":"Smoke","price_cents":900,"metadata":{"name":"Smoke","email":"smoke@example.test","report":"natal","birthdate":"1989-04-12","birthtime":"17:07","location":"Meridian, ID"}}'
```

4. Browser smoke `/buy-report/` reaches Stripe and shows the intended amount without completing payment.

## Pitfall
Do not assume a staging VM sync proves production Pages Functions. Staging can work through nginx while production returns 405 from Pages. If production checkout precheck returns 405, add/verify Pages Functions before promotion, not after.