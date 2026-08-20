# HDE Phase 1 + Phase 2 staging funnel fix pattern — 2026-07-15

Use this when the HDE public website → Stripe → success page → Telegram bot workflow needs to be hardened before broad paid traffic.

## Durable lessons

1. Treat `https://staging.humandesignengine.com/deconditioning/` as the canonical customer workflow source for bot onboarding, not Telegram as a standalone entrypoint.
2. Verify route correctness before debugging checkout. A homepage fallback can make pages appear alive while product/legal/success routes are wrong.
3. For staging Stripe checkout, do not send live Price IDs to a test-mode Stripe key. Either configure test Price IDs or intentionally omit Price IDs on staging and build Checkout Sessions with `price_data`.
4. Keep non-staging/live Price ID behavior intact while stripping Price IDs only when `window.location.hostname.startsWith('staging.')`.
5. Success/cancel URLs should use the current page origin on staging: `${window.location.origin}/success?...` and `${window.location.origin}/deconditioning/`.
6. The staging API must mount the checkout router (`stripe_webhook_router`) so `/api/checkout/create-session` is a real POST endpoint. A GET returning `405 Method Not Allowed` is useful evidence that the route is mounted and POST-only.
7. Verify checkout handoff with both API POST and browser behavior: POST returns a `https://checkout.stripe.com/` URL, and a browser from `/deconditioning/` reaches Stripe after clicking the CTA.
8. For Cloudflare-protected public route smoke in ad-hoc verification, use `curl` with a normal user agent rather than Python `urllib`; the lesson is the retry pattern, not that either tool is broken.
9. PDF QA can be layered when semantic vision tooling is unavailable: render PDF page with `pdftoppm`, inspect dimensions/bytes, run `pdfinfo`, and OCR with `tesseract` to prove non-blank legible content. Label this as mechanical/OCR PDF proof, not full semantic design review.

## Verification recipe

- `npm run build`
- `npm run pwp:verify`
- `PWP_STAGING_URL=https://staging.humandesignengine.com npm run qa:flows -- --reporter=list`
- POST a staging checkout payload to `/api/checkout/create-session`; assert returned URL starts with `https://checkout.stripe.com/`.
- Route-smoke staging pages with `curl -A 'HermesPhase12Verifier/1.0'` and expected page-title markers.
- `py_compile` changed staging API files.
- Check `hde_api_staging.service`, `hde_router.service`, and guest container health.
- Render a known generated PDF to PNG and run OCR smoke.

## Governance notes

- Ned lane guard may reject frontend/package/test snapshots outside Ned-owned lanes. If so, commit only in-lane implementation/docs and explicitly report that full PWP harness assets need the owning lane to canonicalize them.
- If using two checkouts (`hd-platform` source + `hd-platform-staging` runtime), commit/push each repo separately and avoid reusing the same branch name to a local remote if it already points at another repo branch.
