# HDE Stripe Live Checkout / Subscription Model Remediation — 2026-07

Use this as a reference pattern for PWP/pre-live audits where checkout appears stuck in mock mode or product pricing does not match the intended business model.

## Durable lessons

### 1. Look beyond the obvious `.env`

In this session, source/staging `.env` files had placeholder Stripe keys, but a valid production/live key existed in a published environment copy:

```text
/home/ubuntu/.prismatic/published/work/hd-platform/.env
```

Search strategy should include, with secrets redacted:

- active source `.env`
- staging/runtime `.env`
- systemd unit files and `EnvironmentFile=` targets
- payment-specific env files such as `payment/.env`
- published/deployed worktree env copies when present
- payment link inventory files for price IDs, webhook IDs, and account IDs

Never print keys. Report only prefix, length, live/test mode, Stripe account ID, and API status.

### 2. Webhook secret is not an API key

A Stripe `whsec_...` signing secret can validate webhook payloads. It cannot authenticate to the Stripe REST API or mint a test key. Verify this directly if needed with a harmless `/v1/account` request; expect `401` when using `whsec_...` as API auth.

### 3. Distinguish live Checkout from test-card readiness

A valid `sk_live_...` key can prove real hosted Checkout session creation, but it does **not** permit test-card/SCA/decline matrix testing. Do not submit card numbers against live mode.

Evidence labels:

- **Live Checkout green:** endpoint returns `https://checkout.stripe.com/...` using a live key; no payment submitted.
- **Test-card matrix blocked:** no `sk_test_...` key or Stripe CLI/Dashboard login is available.
- **Mock-only:** endpoint returns local `/checkout/pay?session_id=cs_test_mock_...`.

### 4. Validate Stripe objects against the intended product model

Do not blindly align the page to whatever Stripe price IDs happen to be configured. Compare current Stripe objects to the user-stated business model.

In this session, old deconditioning price IDs pointed to wrong one-time products:

```text
Belief Standard Workbook: $19 one-time
Belief Comprehensive Workbook: $29 one-time
```

The corrected model was:

```text
Solo Sanctuary:
  $29/month recurring subscription

Sovereign Container:
  $1,500 upfront 6-week container
  includes 1 year support
  then renews at $29/month after 365 days
```

Correct Stripe shape:

```text
Solo:
  one line item: monthly recurring $29 price
  Checkout mode: subscription

Sovereign:
  line item 1: one-time $1,500 upfront price
  line item 2: recurring $29/month renewal price
  Checkout mode: subscription
  subscription_data.trial_period_days: 365
```

Stripe accepts a subscription Checkout Session with both a one-time upfront price and a recurring monthly price when the recurring line is trialed via `subscription_data[trial_period_days]=365`. The initial `amount_total` should equal the upfront container amount.

### 5. API contract extension pattern

For a Checkout API that previously accepted one `price_id`, extend the request body to support:

```python
recurring_price_id: Optional[str] = None
subscription_trial_days: Optional[int] = None
```

Build `line_items` as:

```python
line_items = []
if body.price_id:
    line_items.append({"price": body.price_id, "quantity": 1})
if body.recurring_price_id:
    line_items.append({"price": body.recurring_price_id, "quantity": 1})
```

Then:

```python
session_kwargs = {
    "mode": "subscription" if body.is_subscription else "payment",
    "line_items": line_items,
    ...
}
if body.is_subscription and body.subscription_trial_days:
    session_kwargs["subscription_data"] = {
        "trial_period_days": body.subscription_trial_days,
        "metadata": body.metadata or {},
    }
```

### 6. Verification pattern

Use a focused `/tmp/hermes-verify-*` ad-hoc verifier that proves:

- canonical build passes (`npm run build`)
- API file compiles (`python3 -m py_compile api/routes/stripe_webhook.py`)
- Stripe price objects match intended amount/recurrence/product mode
- public page contains expected prices, price IDs, and trial metadata
- report Checkout returns hosted Stripe URL
- Solo Checkout returns hosted Stripe URL in subscription mode
- Sovereign Checkout returns hosted Stripe URL with upfront + renewal payload
- webhook signature validation accepts a locally signed benign event
- signed `checkout.session.completed` smoke creates an onboarding deep link when appropriate

Always state: **ad-hoc verification, not full suite-green**.

## Pitfalls caught

- Treating placeholder `.env` as proof no API key exists.
- Treating a webhook signing secret as if it could generate or replace an API key.
- Aligning UI prices to the wrong active Stripe objects instead of the intended product model.
- Sending `mode=subscription` with a one-time Price ID only, which Stripe rejects: “You must provide at least one recurring price in subscription mode when using prices.”
- Claiming Stripe test-mode readiness from live-mode Checkout creation.
