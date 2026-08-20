# PWP Google Registration & Launch Analytics Audit

Use this reference when a PWP/HDE site needs launch audit plus Google Analytics, Google Tag Manager, and Google Search Console registration.

## Preconditions

- Production deploy permission must be explicit before modifying the live site.
- Google registration requires an OAuth principal with access to Analytics Admin, Tag Manager, and Search Console. A `GOOGLE_API_KEY` is not enough for create/list/mutate calls.
- Do not print Google tokens, OAuth refresh tokens, GA/GTM admin credentials, Stripe keys, or Cloudflare keys.

## Audit checklist

1. Crawl canonical production routes with cache-busting and record:
   - HTTP status/final URL
   - title, H1, meta description, canonical
   - Open Graph title/image
   - JSON-LD count/type
   - GA4/GTM presence
   - legacy markers that should be absent
2. Crawl the sitemap with a browser-like User-Agent; some Cloudflare rules may 403 default Python user agents.
3. Check sitemap URLs for:
   - redirect loops
   - non-200 statuses
   - missing canonical tags
   - legacy/deprecated pages still indexed
   - pages without analytics tags
4. Run PWP local proof:
   - `PWP_STAGING_URL=https://<production-domain> npm run pwp:verify`
5. Run live Lighthouse on representative routes:
   - `/`
   - `/buy-report/`
   - `/free-human-design-reading-generator/`
   - `/deconditioning/`
6. Verify payment/API surfaces without completing payment:
   - production same-origin checkout returns HTTP 200 and Stripe URL
   - Stripe session prefix is expected (`cs_live_` only after live cutover)
   - public report delivery returns origin status, not Cloudflare Access redirect
7. Check security/ops:
   - SSL dates
   - `robots.txt`
   - `sitemap.xml`
   - security headers: HSTS, CSP, frame options, permissions policy, referrer policy, nosniff

## Google registration workflow

### Auth discovery

```bash
gcloud auth list --format=json
gcloud config get-value project
gcloud auth print-access-token >/tmp/google_token
```

If no active account exists, stop and report the blocker. Do not fake registration from an API key.

API-key-only blocker proof:

```bash
curl -sS 'https://analyticsadmin.googleapis.com/v1beta/accountSummaries?key=$GOOGLE_API_KEY'
curl -sS 'https://www.googleapis.com/webmasters/v3/sites?key=$GOOGLE_API_KEY'
```

Expected when blocked: `401` with `API keys are not supported by this API` / `Login Required`.

### GA4

With OAuth/admin access:

1. List accessible accounts/properties.
2. Reuse an existing property only if it is confirmed to belong to the domain.
3. Otherwise create a GA4 property/data stream for the canonical domain.
4. Record Measurement ID as `G-...` in the site config/env.
5. Add site-wide tracking in the shared layout, not copied one-off legacy pages only.
6. Verify every sitemap route includes the tag or intentionally opts out.

### GTM

With OAuth/admin access:

1. Create or reuse a container for the domain.
2. Publish a minimal container with GA4 Config, page_view, checkout CTA, checkout session created, purchase/success events.
3. Install both head and noscript snippets site-wide.
4. Verify `GTM-...` appears on canonical, report, free-reading, legacy, and generated library pages.

### Search Console

With OAuth/admin access:

1. Add URL-prefix or Domain property for the canonical domain.
2. Prefer DNS verification through Cloudflare when possible; otherwise add a static `google*.html` file or meta tag.
3. Submit sitemap: `https://<domain>/sitemap.xml`.
4. Use URL Inspection API sparingly for key launch URLs.

## HDE-specific pitfalls

- HDE has mixed Astro and copied legacy static surfaces. Add analytics in the shared layout and in the postbuild legacy normalizer, or tags will remain partial.
- Legacy pages may already contain a GA4 ID such as `G-Q6TPL08VM7`; do not assume it is the correct property until verified through Google Admin/Search Console access.
- Production is Cloudflare Pages; staging may be VM/nginx backed. Registration verification must hit the canonical production domain.
- Do not index private-ish operational pages (`coach_dashboard.html`, `cron-health.html`) unless Michael explicitly wants them public.
- Keep Search Console verification artifacts stable through `route-complete-build.mjs` so production deploys do not delete them.

## Reporting format

Report:

- What was registered/configured.
- If blocked, exact OAuth/auth blocker and the proof response.
- Coverage counts: sitemap URL count, analytics-tagged count, missing-canonical count, live Lighthouse scores, PWP proof counts.
- Priority gap list with owner/action.
