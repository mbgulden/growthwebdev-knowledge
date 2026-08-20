# HDE Stripe report checkout + CTA proof — 2026-07

Use this reference when Michael asks to test or modify HDE Stripe report forms, report pricing, report fulfillment, or report-page CTAs that should point customers toward Sanctuary/coaching/consultations.

## Durable pattern

1. **Inventory every checkout surface before editing.** For HDE this can include:
   - Astro source page: `src/pages/buy-report.astro`
   - legacy/static mirrors: `docs/buy-report.html`, `landing/buy-report.html`, `docs/landing-reports.html`, `landing/landing-reports.html`, `public/landing-reports.html`, upsell pages, product catalog, affiliate pages
   - checkout component: `payment/static/hd-checkout.js`
   - payment server: `payment/server.py`
   - FastAPI checkout/webhook routes: `api/routes/stripe_webhook.py`, `api/routes/payment.py`
   - reports server templates: `reports/server.py`
2. **Lower displayed prices and server-side prices together.** Do not leave old Stripe Price IDs wired for the lowered one-off report products unless matching test/live Price IDs were actually created. For staging/test keys, prefer `price_data.unit_amount` so Stripe Checkout matches the site display.
3. **Test both checkout route families.** HDE has had both:
   - payment server routes: `/create-checkout`, `/checkout`, `/webhook`, `/static/hd-checkout.js`
   - FastAPI routes: `/api/checkout/create-session`, `/api/checkout/session`, `/api/webhook`
4. **Verify fulfillment separately from checkout URL creation.** A Stripe Checkout URL only proves payment handoff. Also prove report fulfillment maps products correctly:
   - `natal` -> natal PDF
   - `transit` -> transit PDF
   - `synastry` -> relationship PDF
   - `bundle` -> natal + transit + relationship PDF when partner metadata exists
5. **Generate real PDFs through `/api/compute`.** Check `success`, PDF existence, and non-trivial byte size. Source/HTML/PDF text QA is required if template content changed.
6. **Browser-smoke the customer form on staging.** Fill `https://staging.humandesignengine.com/buy-report/`, click checkout, and verify the Stripe sandbox page shows the expected product and lowered price.
7. **Cloudflare Access is a production-readiness boundary.** If `api.humandesignengine.com` or `reports.humandesignengine.com` returns a Cloudflare Access 302 login for public checkout/static routes, do not claim public production readiness. Report exact exemptions needed instead.
8. **Do not conflate staging and production route health.** Staging same-origin `/api/checkout/create-session` can work while production `/api/...` or `api.humandesignengine.com/...` is still blocked/misrouted.

## CTA copy standard

One-off reports should be framed as snapshots, not the main transformation product. Add CTAs at checkout/report-bottom surfaces for:

- Human Design Sanctuary
- Coaching Container
- Human Design Consultations

Preferred message shape:

> The report is the snapshot. The Sanctuary is where the work happens. A one-off chart can name your mechanics. Real answers and progress come from applying your design to relationships, family, work, emotional waves, transits, and the situations you are actually living.

Also add a comparable next-step CTA block inside generated report PDFs, not only on the marketing page.

## Known verification snippets

- Use static contract tests with mocked Stripe calls to assert `unit_amount`, metadata, and fulfillment mapping without creating excessive Stripe sessions.
- Use live/staging smoke tests against local services (`127.0.0.1` ports) and public staging (`staging.humandesignengine.com`) separately.
- If `systemctl restart` requires interactive auth, do not claim a normal restart. If using TERM + systemd autorestart, explicitly verify new MainPID/service active state.

## Pitfalls

- Do not leave report UI at the lowered price while server code still sends old live Price IDs.
- Do not call a checkout form tested just because direct API POST works; at least one browser form click should reach Stripe sandbox.
- Do not call customer fulfillment tested from checkout creation alone; check report generation and delivery mapping.
- Do not treat Cloudflare Access redirects as valid checkout responses.
- Avoid recording setup-state failures as durable facts. Capture the fix pattern: inspect service `WorkingDirectory`, `EnvironmentFile`, and route/proxy boundaries before claiming live checkout health.
