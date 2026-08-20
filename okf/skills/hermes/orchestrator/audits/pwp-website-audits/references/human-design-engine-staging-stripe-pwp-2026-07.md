# Human Design Engine staging audit pattern — July 2026

Use this as a reference pattern for pre-live PWP audits that include payments/process QA.

## Key lessons

- Audit the actual launch target (`staging.humandesignengine.com`), not live production, when the user says the new work is in staging.
- Compare live/staging deploy output with local repo/build output and state split reality explicitly.
- Strong Lighthouse scores are not enough: exercise primary CTAs, widget mounts, checkout buttons, success pages, and downstream process endpoints.
- For custom widgets, check runtime registration and selector compatibility. In this session the page mounted `<hd-bodygraph>`, while `/widget.js` initialized `.hde-chart-widget`; the section was empty despite no console errors.
- For Stripe, distinguish mock checkout from real Stripe test mode. A local mock page accepting `4242` is UI proof only, not payment workflow proof.

## Evidence checklist

- `npm run build` or canonical build command.
- Browser snapshot of staging homepage and key flows.
- Browser console after load and after button/form interactions.
- Lighthouse mobile + desktop JSON artifacts.
- Same-origin crawl with broken links, page metadata, form labels, heading skips, module heuristics.
- HTTP checks for `robots.txt`, `sitemap.xml`, favicon, 404 page, and API/process endpoints.
- Payment/session endpoint probes with redacted session IDs/tokens.

## Stripe readiness matrix

Mock checkout evidence:

- Public CTA creates a local/mock session.
- Mock payment page accepts filled card-like fields.
- Success page renders expected state.
- Downstream staging session endpoint returns expected provisioning state.

Real Stripe test-mode evidence, required before payment launch:

- Checkout redirects to `https://checkout.stripe.com/...` or uses Stripe.js Elements with test keys.
- Success: `4242 4242 4242 4242`.
- Decline: `4000 0000 0000 0002`.
- SCA/3DS: `4000 0025 0000 3155`.
- Stripe webhook signature verified from Stripe CLI/dashboard.
- Fulfillment/provisioning verified after webhook: report/email/invite/bot link as applicable.

## Report shape

- Bottom line: Green/Yellow/Red and whether to push live.
- Evidence table with concrete numbers and artifact paths.
- P0/P1 findings with evidence, impact, fix, and acceptance criteria.
- Separate “current mock walkthrough” from “real Stripe test-mode walkthrough” if staging is mocked.
