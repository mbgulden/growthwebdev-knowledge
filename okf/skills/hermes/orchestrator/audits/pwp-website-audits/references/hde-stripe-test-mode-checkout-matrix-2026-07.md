# HDE Stripe Test-Mode Checkout Matrix — July 2026

Use this as a concrete reference for pre-live website/process audits involving Stripe Checkout, subscriptions, webhooks, and downstream fulfillment.

## Durable lessons

### 1. Do not stop at obvious `.env` files

If staging `.env` has placeholders, inspect deeper before declaring Stripe unavailable:

- systemd `Environment=` / `EnvironmentFile=`
- service-specific payment envs such as `payment/.env`
- published/deployed worktree env copies
- payment-link or Stripe inventory notes
- Stripe Dashboard/CLI availability

Redact secrets. Report only key prefix, length, mode, Stripe account id, and API auth result.

### 2. Webhook signing secret is not an API key

`whsec_...` validates incoming webhook payloads. It cannot authenticate to Stripe REST API, create Checkout sessions, or mint/reveal test keys.

### 3. Validate Stripe Price/Product objects against the business model

Do not normalize copy or checkout payloads to whatever stale Price IDs exist. Retrieve Price/Product objects and compare:

- product name
- amount
- one-time vs recurring
- interval
- live/test mode
- active flag

In this session, existing deconditioning IDs pointed at unrelated one-time workbook products. Correct fix was to create/reuse proper products/prices matching the intended offers.

### 4. Modeling upfront + delayed renewal in Checkout

For an offer like “$1,500 upfront, 1 year included, then $29/month,” Stripe Checkout accepted:

- `mode=subscription`
- line item 1: one-time upfront price
- line item 2: recurring monthly renewal price
- `subscription_data[trial_period_days]=365`

The resulting Checkout session showed an initial amount total equal to the upfront amount while carrying the recurring renewal after the trial.

### 5. Staging test mode can use test-only price IDs without changing production source

When source/prod is wired to live Price IDs, patch the staging runtime/static worktree with test Price IDs for browser/card matrix verification. Keep source code aligned to production/live IDs unless the project has an explicit env-driven price-ID config system.

### 6. Required real test-mode matrix

A Stripe payment/process path is materially verified only after:

- `sk_test_...` authenticates to the correct Stripe account
- staging webhook endpoint exists in test mode and provides `whsec_...`
- app creates hosted `cs_test_...` Checkout sessions
- success card `4242 4242 4242 4242` reaches success page
- Stripe-delivered `checkout.session.completed` webhook hits app and returns 200
- downstream fulfillment/provisioning is observed, not inferred
- decline card `4000 0000 0000 0002` shows the expected Stripe decline error
- SCA card `4000 0025 0000 3155` triggers 3DS/hosted challenge

### 7. Headless browser SCA caveat

Stripe 3DS/SCA may load a hosted `three-ds-2-challenge` iframe and then stall in headless automation due to iframe/hCaptcha/browser constraints. Treat this as:

- Green for “app reaches SCA branch” if the challenge iframe appears.
- Not green for “completed SCA redirect” unless a normal browser/manual run or automatable challenge completion proves the post-SCA success path.

Say this distinction plainly.

## Evidence labels to use

- **mock checkout** — local `/checkout/pay?session_id=cs_test_mock...`; not real Stripe.
- **live Checkout creation** — hosted `https://checkout.stripe.com/...` with `cs_live_...`; proves real Stripe wiring, but do not submit cards.
- **test Checkout creation** — hosted `https://checkout.stripe.com/...` with `cs_test_...`; ready for test card matrix.
- **Stripe-delivered webhook** — event arrives from Stripe infrastructure and the app logs/returns 200.
- **signed local webhook smoke** — useful for signature handler, but not a substitute for Stripe-delivered event delivery.

## Minimal safe reporting format

```text
Stripe mode: test/live/mock
Checkout session: cs_test/cs_live/mock, redacted
Success card: pass/fail/not-run
Decline card: pass/fail/not-run
SCA: completed / challenge triggered only / not-run
Webhook: Stripe-delivered 200 / signed-local only / not-run
Fulfillment: observed deep link/report/provisioning / not observed
Secrets printed: no
```
