# HDE Stripe Live Cutover — 2026-07-18

Session-specific reference for switching Human Design Engine report checkout from Stripe test/sandbox to live mode.

## Durable layout

- Active payment runtime env: `/home/ubuntu/work/hd-platform/.env`
- Payment service: `hde-payment.service`
- Service env source: `EnvironmentFile=/home/ubuntu/work/hd-platform/.env`
- Payment server entrypoint: `/home/ubuntu/work/hd-platform/payment/server.py`
- Validated published live env source: `/home/ubuntu/.prismatic/published/work/hd-platform/.env`

Do not print raw env files or key values. Redact as `sk_live_[REDACTED]`, `sk_test_[REDACTED]`, `whsec_[REDACTED]`.

## Successful cutover sequence

1. Load/obey this skill before touching payment config.
2. Inspect active and published env modes with redaction.
3. Validate the candidate live key from the published env against Stripe `/v1/account`; require the expected account, `charges_enabled=true`, and `details_submitted=true`.
4. Validate configured live Price IDs under the same live key if present. HDE one-off reports use dynamic `price_data`, but workbook/retreat products can still depend on configured live `price_...` values.
5. Backup active env outside git, e.g. `/home/ubuntu/work/hd-platform/.env.backup-pre-live-stripe-<UTC>.`
6. Copy only payment-related values from the published live env into the active env:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PUBLISHABLE_KEY` when present
   - configured `*_PRICE_ID` values
   - set `ENVIRONMENT=production`
7. Restart only `hde-payment.service` unless another service has been proven to need a restart.
8. Verify the actual running process has `ENVIRONMENT=production`, `STRIPE_SECRET_KEY` starts with `sk_live_`, and the webhook secret starts with `whsec_` by reading `/proc/<MainPID>/environ` with redacted reporting.
9. Create smoke Checkout Sessions through both production routes without completing payment:
   - `https://humandesignengine.com/api/checkout/create-session`
   - `https://api.humandesignengine.com/api/checkout/create-session`
10. Retrieve the created Checkout Session from Stripe and require:
   - session id prefix `cs_live_`
   - `livemode=true`
   - `mode=payment`
   - expected `amount_total` (Natal smoke was `900` cents)
   - `payment_status=unpaid`
11. Browser-smoke the customer `/buy-report/` flow and confirm the Stripe Checkout page no longer shows `Sandbox`. Do not enter card details or complete a payment unless explicitly authorized.
12. Check `hde-payment.service` remains `active/running`, with no restart loop and no recent secret-bearing logs.

## Rollback

If live checkout fails after env replacement, restore the timestamped `.env.backup-pre-live-stripe-*`, restart `hde-payment.service`, and verify checkout returns `cs_test_`/Sandbox again before investigating.

## Pitfalls from this session

- A production checkout route returning `HTTP 200` is not proof of live payments; require `cs_live_` plus Stripe API `livemode=true`.
- The active env and the published env can differ. Always verify the service's actual process environment after restart.
- Do not assume live Price IDs are required for HDE one-off reports; those use `price_data`. Still validate any configured Price IDs for adjacent products before claiming the whole payment surface is live-clean.
