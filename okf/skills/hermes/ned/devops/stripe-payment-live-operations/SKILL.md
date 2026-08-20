---
name: stripe-payment-live-operations
description: Use when switching a payment integration from Stripe test/sandbox mode to live mode, verifying Stripe Checkout, or diagnosing whether a checkout flow is safe for real customer charges.
---

# Stripe Payment Live Operations

Use this for Stripe live/test cutovers, checkout-mode verification, webhook-secret validation, and public-payment readiness checks.

## Operating stance

- Do **not** call a payment flow live just because checkout routing works.
- Live means the active payment server is using a valid `sk_live_...` secret and the customer-facing Stripe Checkout page is not labeled Sandbox.
- Never paste full Stripe keys, webhook secrets, checkout session IDs with sensitive metadata, or raw `.env` contents into chat.
- Redact keys in logs as `sk_live_[REDACTED]`, `sk_test_[REDACTED]`, and `whsec_[REDACTED]`.
- Historical leaked keys, transcript fragments, and old recovery files are not usable credentials. Validate any candidate live key against Stripe before touching production config.

## Discovery checklist

1. Inspect the active payment service environment and the production env file with redaction.
2. Identify whether the active key is `sk_test_`, `sk_live_`, placeholder, or absent.
3. Validate a candidate live key via Stripe `/v1/account` before using it:
   ```bash
   curl -fsS https://api.stripe.com/v1/account \
     -H "Authorization: Bearer $STRIPE_SECRET_KEY" \
     | python3 -m json.tool
   ```
4. Confirm `charges_enabled=true` and `details_submitted=true` for the expected Stripe account.
5. Check webhook secret mode. A live secret usually must come from the live Stripe webhook endpoint, not the test endpoint.
6. For products using configured Price IDs, verify each `price_...` exists under the same live key and has the expected amount/currency/livemode.
7. For products using `price_data`, live Price IDs are not required, but the resulting checkout session still must be created with the live secret key.

## Safe cutover pattern

1. Backup the current production env file outside git.
2. Update only the production payment runtime env, not staging, unless explicitly requested.
3. Replace `STRIPE_SECRET_KEY=sk_test_...` with a validated `sk_live_...`.
4. Replace `STRIPE_WEBHOOK_SECRET=whsec_...` with the live webhook endpoint secret.
5. Restart the payment service via the platform's normal process manager. If direct `systemctl restart` is blocked by sudo/polkit, use an approved autorestart pattern only when the unit is already supervised and you have verified restart behavior.
6. Verify service health and logs with secrets redacted.
7. Create a live-mode Checkout Session using a smoke payload, but do **not** complete payment unless explicitly authorized.
8. Browser-check the customer-facing flow and confirm the Stripe Checkout page no longer shows `Sandbox`.
9. Verify public API routes still return 200/Stripe URLs and are not blocked by Access/auth redirects.
10. Run build/syntax checks for any code changed during the cutover.
11. If payment/report server code imports shared repo modules, restart the systemd service and check the journal for import failures. Standalone scripts run as `/path/subdir/server.py` may need the repo root added to `sys.path` before sibling imports. See `references/2026-07-hde-payment-systemd-import-path.md`.

## HDE notes

- HDE one-off reports currently use `price_data` for lowered report prices, so live Price IDs are not required for Natal/Synastry/Transit/Bundle.
- Other products may still use configured Price IDs and must be validated in the live Stripe account before live claims.
- HDE's active payment service reads `/home/ubuntu/work/hd-platform/.env`; the validated published live Stripe env has been found at `/home/ubuntu/.prismatic/published/work/hd-platform/.env`. Do not copy the whole file blindly; copy only payment keys/price IDs and set `ENVIRONMENT=production`.
- After live cutover, prove live mode by retrieving a created Checkout Session from Stripe and requiring `cs_live_` plus `livemode=true`; absence of the Stripe Checkout `Sandbox` label is useful browser proof but not sufficient by itself.
- HDE deploy path: `dist/` is git-ignored on every hd-platform branch (main, deploy-fresh, feature/*). `humandesignengine.com` is a **Cloudflare Pages custom domain on project `hd-platform`** (`production_branch: main`) — production ships via `wrangler pages deploy dist --project-name=hd-platform --branch=main` (token in terminal env, never `wrangler login` on this box). **Omitting `--branch main` while in a git checkout on a feature branch auto-deploys a *preview*; the prod domain keeps serving the old production deployment.** Local nginx `humandesignengine` site + `cloudflared-hde` tunnel are legacy, NOT the static origin. See `references/2026-08-hde-stuck-redirecting-checkout.md` (deploy + topology section).
- `/deconditioning/` pricing model + end-to-end verification recipe (price IDs, smoke payloads, trial proof via `amount_total`): see `references/hde-deconditioning-pricing-model.md`.
- See `references/hde-stripe-live-cutover-2026-07-18.md` for the session-specific HDE findings and commands.

## Blocker language

If no valid live key is present, say directly:

> Blocked: no valid live Stripe secret key is available on this box. Current active key is test/sandbox. Provide a valid `sk_live_...` and live webhook secret through a secure credential channel, then I can complete the cutover.

Do not imply the site is ready for real charges until the live key is installed and verified end-to-end.

## References

- `references/hde-stripe-live-cutover-2026-07-18.md` — session-specific HDE findings and commands.
- `references/hde-dual-backend-routing-2026-08-19.md` — HDE prod dual-backend nginx routing map (unified FastAPI :8000 vs legacy :8002), wrong-price/wrong-product diagnosis recipe (direct-probe both backends, Stripe session retrieval incl. `line_items` expand envelope), webhook cutover pitfalls (handler path rewrite, CF 1010 on DC-IP public POSTs), and the subscription-button-lands-on-$9-report failure mode.
- `references/hde-deconditioning-pricing-model.md` — `/deconditioning/` live Price IDs + Sovereign dual-price/trial model, end-to-end verification recipe (incl. `amount_total`-based trial proof and the DC-IP browser-check caveat), dirty-tree build-verification pattern, and the credential-scrubber script pitfall.
- `references/2026-07-hde-payment-systemd-import-path.md` — service restart + import-path pitfalls when payment/report server code imports shared repo modules.
- `references/2026-08-hde-stuck-redirecting-checkout.md` — "stuck Redirecting…" checkout failure class: frontend fetch with no timeout + button disabled pre-try, CF Function proxy gap, and `async def` FastAPI handler with blocking `stripe.*` calls freezing the uvicorn event loop. Three-layer fix (frontend AbortController + CF Function 504 + `def`/`timeout=20`), plus the preview-vs-production `wrangler --branch=main` deploy gotcha and byte-hash live verification.
- `references/2026-07-stripe-auth-loader-hd-platform.md` — how the PWP `auth_loader` discovers the production Stripe key in `/home/ubuntu/work/hd-platform/.env`, the `STRIPE_RESTRICTED_KEY > STRIPE_API_KEY > STRIPE_SECRET_KEY` preference chain, and the live `step_register_stripe` verification recipe against `ezshare.systems` (2026-07-30 Phase 4 work, Linear GRO-4361).
