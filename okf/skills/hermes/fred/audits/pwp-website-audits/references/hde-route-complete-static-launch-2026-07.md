# HDE route-complete static launch pattern — 2026-07

Use this as a reusable pattern when a staging redesign must replace a production static site without dropping indexed/revenue routes.

## Core lesson

A redesign is not production-ready just because the new Astro pages build and look right. For production replacement work, require **route-complete + process-complete + polish-complete**:

1. Route-complete: every production URL is either served, intentionally redirected, or explicitly approved for removal.
2. Process-complete: revenue/process paths are exercised end-to-end against the real intended infrastructure, not just mock UI.
3. Polish-complete: launch pages and preserved legacy corpus meet the agreed visual/SEO/accessibility bar.

## Route-complete build pattern

When production has a large legacy `docs/` corpus and staging has a smaller Astro redesign:

1. Run Astro build first so redesigned pages own their routes.
2. Postbuild-copy legacy static `docs/` files into `dist/` **only when the destination does not already exist**. Astro pages must win over legacy files.
3. Generate `sitemap.xml` and `robots.txt` from final `dist/`, not from Astro routes alone.
4. Generate redirects for:
   - extensionless aliases for `.html` pages;
   - trailing-slash aliases where needed;
   - known malformed legacy links;
   - modern replacements such as `/reports` → `/buy-report/`, `/api` → `/docs/`.
5. If public staging/static hosting does not honor `_redirects`, materialize small redirect HTML pages for aliases. Guard against file/directory conflicts when materializing both `/foo` and `/foo/`.
6. Normalize copied legacy HTML links at build time rather than editing the source content corpus when ownership/lane rules make content read-only.

## Verification pattern

Use both production-parity and crawl checks:

```bash
npm run build
```

Then ad-hoc verify:

- route summary thresholds: sitemap route count, copied legacy file count, redirect/materialized alias count;
- critical routes return <400: homepage, generator/free tool pages, bodygraph, report checkout, legal pages, representative library pages;
- public `sitemap.xml` returns 200 and includes generator/free-tool routes;
- crawl from launch pages + representative legacy index pages, ignoring `/cdn-cgi/*`, and fail on 4xx;
- browser/DOM check the primary widget/CTA, not just static HTML.

## Process-complete pitfall

Mock checkout is not Stripe readiness. If checkout returns `/checkout/pay?session_id=cs_test_mock_...`, label it **mock-green only**. Real Stripe readiness requires:

- `STRIPE_SECRET_KEY=sk_test_...` in staging service env;
- `STRIPE_WEBHOOK_SECRET=whsec_...` in staging service env;
- hosted Stripe Checkout URL (`https://checkout.stripe.com/...`);
- success card, decline card, SCA card;
- webhook signature verification;
- downstream fulfillment/provisioning proof.

## Reporting language

Use explicit status labels:

- `route-complete: green`
- `process-complete: green / mock-green / blocked`
- `polish-complete: green / partial / blocked`

Do not call production ready until all three lanes are green or the user explicitly accepts a scoped exception (for example, preserved legacy styling for launch).