---
name: pwp-website-audits
description: "Audit live websites against Prismatic Website Package (PWP) standards: module contracts, reusable theme discipline, accessibility, SEO/static output, performance, and conversion structure."
triggers:
  - User asks to audit a website using PWP standards
  - User asks whether a site/page/theme is PWP-compliant
  - User asks for PWP acceptance gaps, theme review, or website QA against PWP module contracts
---

# PWP Website Audits

Use this skill to audit a live or local website against PWP standards. The goal is to produce an evidence-backed, decision-oriented audit with prioritized fixes — not a generic website critique.

## Standards to load/check

Before auditing, locate and read the current PWP docs when available:

- `plugins/pwp/docs/module-contracts.md` — registered modules and assembly rules
- `plugins/pwp/docs/community-theme-submission-checklist.md` — acceptance bar for reusable theme packages
- `plugins/pwp/docs/theme-agent-prompt-packs.md` — review/verification expectations
- `plugins/pwp/templates/tokens.schema.json` — token contract when auditing theme packages

If these paths are not in the active repo, search the workspace for `plugins/pwp/docs/module-contracts.md` and equivalent PWP docs.

## Audit workflow

1. **Identify the real target.**
   - If the user names a staging/pre-live URL, audit that staging target first. Do not substitute production just because it is public or easier to inspect.
   - Prefer live production URL only when the user generically says “website” and has not specified staging, preview, or another environment.
   - Also inspect the local repo/build when available, but distinguish staging findings, live production findings, and local source findings explicitly.
   - Watch for split reality: production may be served from `docs/*.html` or legacy static output while the local Astro source/staging deployment looks cleaner.

2. **Build/run local source when available.**
   - Run the canonical build command, e.g. `npm run build` for Astro.
   - If needed, serve `dist/` with a simple static server to inspect rendered output.
   - Treat build success as evidence, not proof of PWP compliance.

3. **Collect live evidence.**
   - Browser snapshot for visible structure, nav, forms, CTAs, and console errors.
   - Lighthouse mobile + desktop for performance, accessibility, best practices, and SEO.
   - Crawl same-origin links for broken internal links and page-level metadata.
   - Parse HTML for: title, meta description, canonical, OG/Twitter tags, JSON-LD, H1 count, heading skips, landmarks, form labels, image alts, inline styles, `!important`, and detected PWP-like modules.
   - For pre-live audits, exercise links, buttons, forms, and checkout/process paths from the browser, not just static HTML. Capture whether each path is real production/test infrastructure or a local/mock simulation.
   - For payment flows, distinguish **mock checkout**, **live Checkout session creation**, and **real Stripe test mode**. A hosted `https://checkout.stripe.com/...` URL proves real Stripe-backed Checkout creation, but live-mode keys do not prove test-card/SCA/decline readiness. Real Stripe test-mode readiness requires hosted Stripe Checkout or Stripe.js evidence, success/decline/SCA test cards, webhook verification, and downstream fulfillment/provisioning proof.
   - If obvious staging `.env` files are placeholders, look deeper before declaring Stripe unavailable: systemd `Environment=`/`EnvironmentFile=`, payment-specific env files, published/deployed worktree env copies, payment-link inventories, and Stripe price/webhook documents. Redact secrets; report only prefix/length/live-vs-test/API status.
   - Do not treat `whsec_...` webhook signing secrets as API keys. They validate incoming webhook payloads but cannot authenticate to Stripe REST API or mint test keys.
   - Compare Stripe Price objects to the user-stated product model. Do not silently align site copy to whichever stale/wrong Price IDs happen to exist; create/reuse correct Products/Prices when authorized and verify amount, recurrence, product name, and mode.
   - For widgets/custom elements, verify the full mount/render contract at runtime: expected selector/custom element exists, initializer is registered, visible UI renders, API endpoint is reachable, and the success result actually renders in the browser. A 200 JSON response is not enough if the result renderer throws and displays a generic error.
   - For SaaS/bot/process flows, continue past the website into staging runtime contracts: systemd service env files, token/bot identity, DB side effects, orchestrator calls, container health, and in-container model/provider configuration. Label each claim as source-level, staging-runtime, or not-yet-verified.

4. **Score against PWP categories.**
   - Module composition: `BaseLayout`, `SiteHeader`, `SiteFooter`, `Hero`, `CardGrid`, `LeadCapture`, `TrustPanel`, `FAQ`, `RichTextPage`, `PricingOrPackages` where relevant.
   - Reusable theme contract: tokenized styles, shared module classes, no one-off page dumps.
   - Accessibility: WCAG evidence, labels, focus, contrast, headings, landmarks.
   - SEO/static output: metadata, canonical, OG/Twitter, sitemap/robots/404 where in scope, local asset integrity.
   - Performance: Lighthouse mobile/desktop and obvious render-blocking issues.
   - Conversion: single clear primary CTA, trust/process modules, lead capture path, pricing/report/API funnel clarity.

5. **Prioritize bluntly.**
   - P0 = blocks PWP acceptance or live conversion/SEO/accessibility.
   - P1 = important but not acceptance-blocking.
   - P2 = polish or future-proofing.
   - End with one bounded next implementation slice and explicit acceptance criteria.

## Payment and process-flow audit checks

When the user asks to verify checkout, Stripe, onboarding, bookings, or other revenue/process paths before launch:

- Start from the public CTA/button and complete the browser flow end-to-end.
- Record exact URLs, redirect targets, session IDs only in redacted form, visible success/error states, and downstream effects.
- Use Stripe test cards only against real Stripe test mode. `4242 4242 4242 4242` proves a real Stripe success path only when the page is Stripe Checkout/Stripe.js backed by `sk_test_...`; live-mode Checkout creation proves hosted Checkout wiring only — do not submit card numbers against live mode.
- If only a live key is available, it is acceptable to verify hosted Checkout URL creation, Stripe object correctness, and signed webhook handling, but label the remaining success/decline/SCA matrix as blocked on test-mode credentials or Stripe CLI/Dashboard access.
- Before changing code to match existing Stripe IDs, retrieve the Price/Product objects and compare them to the intended offer. If the user states a different product model, fix the Stripe objects or checkout payload rather than normalizing the business model to stale prices.
- Required real Stripe test-mode matrix: success card `4242 4242 4242 4242`, decline card `4000 0000 0000 0002`, SCA/3DS card `4000 0025 0000 3155`, webhook receipt, and fulfillment/provisioning verification.
- For subscription models, verify Product/Price objects before editing copy or code. If the current Price IDs are stale or attached to the wrong products, create/reuse correct Prices that match the user-stated offer rather than changing the business model to fit old Stripe data.
- For delayed renewal offers, Stripe Checkout can use `mode=subscription` with one upfront one-time line, one recurring line, and `subscription_data.trial_period_days` for the included period. Verify the initial `amount_total` and recurring interval.
- Treat SCA/3DS in headless browsers carefully: a hosted `three-ds-2-challenge` iframe proves the app reached the SCA branch, but it is not a completed SCA redirect if hCaptcha/iframe automation stalls. Label this as “challenge triggered only” unless a normal browser/manual run completes it.
- If staging intentionally uses mock mode, say so plainly and mark Stripe as **not fully verified** until real test keys/webhooks are exercised.
- Include a user-facing walkthrough for whatever test path is actually available now, plus a separate walkthrough/acceptance list for the real payment test path if different.

## PWP-specific red flags

- Large handcrafted static pages with many inline `style=` attributes.
- Route/client/screenshot-specific CSS instead of reusable token/module styles.
- Missing `theme.json`, `tokens.json`, registry entry, fixture/sample evidence, or screenshot/accessibility proof for a claimed PWP theme.
- Missing FAQ fixture/module when reviewing common marketing pages.
- Live production differs materially from local Astro/PWP source.
- A staging redesign drops production's legacy static/content URL surface. Treat this as a launch blocker until every live URL is served, redirected, or explicitly approved for removal.
- `_redirects` exists but the actual static/staging server does not honor it. Verify redirects on the public URL; if not honored, materialize safe redirect HTML aliases or configure the host.
- SEO scores that look “okay” while main pages lack descriptions, canonicals, or OG/Twitter tags.
- Strong visual homepage but duplicated forms/CTAs that blur the primary funnel.
- CTA/widget mount mismatch: page uses a custom element or selector that the loaded script never initializes, leaving a visually empty primary action.

## Output format

Keep it concise and operational:

1. **Bottom line** — Green/Yellow/Red and why.
2. **Evidence table** — build, browser, Lighthouse, crawl.
3. **PWP scorecard** — status by category.
4. **Top findings** — P0/P1 with evidence and fix.
5. **Recommended next slice** — one task with finish-line acceptance criteria.
6. **Artifact paths** — audit JSON, Lighthouse reports, screenshots if captured.

## References

- `references/human-design-engine-pwp-audit-2026-07.md` — example audit pattern: live-vs-local mismatch, Lighthouse/crawl evidence, and PWP acceptance scoring.
- `references/human-design-engine-staging-stripe-pwp-2026-07.md` — pre-live staging audit pattern with Stripe mock-vs-real test-mode checks, widget mount verification, and process-flow walkthrough expectations.
- `references/deconditioning-telegram-bot-workflow-audit-2026-07.md` — deep process-flow audit pattern for checkout → invitation → Telegram `/start` → container/bot provisioning workflows, including runtime service/env/token mismatch checks.
- `references/hde-staging-launch-remediation-2026-07.md` — active remediation pattern after a staging audit: split source/runtime worktrees, widget mount/render contracts, consent-vs-entitlement gates, Telegram router identity, provisioning idempotency, and guest Hermes MiniMax model wiring.
- `references/hde-route-complete-static-launch-2026-07.md` — route-complete static launch pattern for replacing a production site with a staging redesign without dropping legacy SEO/revenue URLs; includes postbuild preservation, materialized redirects, crawl verification, and route/process/polish status labels.
- `references/hde-stripe-live-checkout-subscription-model-2026-07.md` — Stripe remediation pattern for staging checkout audits: deeper credential discovery beyond obvious `.env`, webhook-secret vs API-key distinction, live-vs-test evidence labels, validating Price/Product objects against the intended business model, and modeling upfront + delayed recurring subscription Checkout.
- `references/hde-stripe-test-mode-checkout-matrix-2026-07.md` — real Stripe test-mode payment matrix pattern: creating/reusing test Products/Prices, wiring staging-only test IDs, success/decline/SCA card evidence, Stripe-delivered webhook verification, fulfillment proof, and headless 3DS caveats.
