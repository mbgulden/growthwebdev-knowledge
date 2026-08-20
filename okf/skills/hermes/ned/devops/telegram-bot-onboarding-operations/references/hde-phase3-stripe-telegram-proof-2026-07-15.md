# HDE Phase 3 Stripe → webhook → Telegram proof pattern — 2026-07-15

Use this when proving the HDE paid onboarding path after staging checkout session creation already works.

## Durable lesson

Phase 3 is not green when Stripe checkout redirects successfully. It is green only after:

1. A Stripe **test-mode checkout is completed** through Stripe-hosted checkout.
2. `checkout.session.completed` reaches the staging webhook endpoint.
3. The webhook creates/updates the user and creates an unused invitation token.
4. `/api/checkout/session?session_id=...` resolves to exactly one Telegram deep link.
5. A real human tester taps the Telegram link and sends `/start` so the router marks the invitation used and creates/links the `BotInstance`.
6. Router metrics stay clean.

If step 5 is missing, report **YELLOW**, not GREEN.

## Verification recipe

### 1. Prove Stripe test checkout completion

Use Playwright against the Stripe-hosted checkout with Stripe test card `4242 4242 4242 4242`. Redact the checkout URL and session id in all output.

Capture only safe fields from Stripe retrieval:

```json
{
  "status": "complete",
  "payment_status": "paid",
  "mode": "subscription",
  "customer_present": true,
  "subscription_present": true
}
```

### 2. Verify webhook behavior

Watch redacted `hde_api_staging.service` logs for:

```text
Received Stripe webhook: checkout.session.completed
POST /api/webhooks/stripe
```

If automatic Stripe delivery happened before a fix and returned `500`, do not claim the automatic path is proven. A signed replay is acceptable to prove the same handler after the fix, but label it clearly.

Signed replay pattern:

- Load `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` from the service env without printing them.
- Retrieve the completed Stripe test session.
- Build a minimal `checkout.session.completed` payload from that real session.
- Sign it as `t=<timestamp>,v1=<hmac_sha256(secret, timestamp.payload)>`.
- POST to `http://127.0.0.1:<staging-port>/api/webhooks/stripe`.
- Expect `200` and `{"success": true, "event_received": "checkout.session.completed"}`.

### 3. DB/user/invitation checks

Use the same env as `hde_api_staging.service`; do not import DB models before env is loaded.

Verify only safe booleans/state:

- user exists,
- `subscription_status == "active"`,
- Stripe customer id is present,
- invitation exists,
- invitation token is present,
- invitation is unused before Telegram `/start`,
- `BotInstance` does **not** have to exist before the Telegram link is tapped.

Do not print customer emails, tokens, DB URLs, or raw IDs unless strictly necessary; redact them in reports.

### 4. Consent/premium pitfall

Do **not** infer coach consent from payment. For Solo checkout, consent should remain false unless the checkout metadata explicitly grants consent for an eligible premium/coaching product.

Also confirm whether Solo should set `is_premium`. In the 2026-07-15 proof, Solo produced `subscription_status=active` and an invitation, but `is_premium=false` under current metadata rules; this was reported as a remaining product-semantics risk, not silently treated as launch green.

### 5. Common blocker: model/schema drift

A real Phase 3 webhook exposed this staging bug:

```text
TypeError: 'coach_review_consent' is an invalid keyword argument for User
```

Root cause: checkout processing used coach-review consent fields, but the staging `shared.database.User` model did not include them. Fix class: align the staging ORM model and idempotent migrations with the checkout/coach-gate fields, then restart `hde_api_staging.service` and re-prove the webhook.

Related hardening: do not leave a hardcoded credential-bearing fallback DB URL in `shared/database.py`; use a placeholder fallback such as `__SET_DATABASE_URL__` and return no engine when unset.

## Report status rules

- 🟢 GREEN: real test checkout completion, webhook-created state, success-page Telegram link, **and** human Telegram `/start` proof are all evidenced.
- 🟡 YELLOW: checkout/webhook/user/invitation/success link are proven, but the human Telegram tap/start proof is missing.
- 🔴 RED: checkout completion or webhook state creation fails.

## Ad-hoc verifier requirements

For the report verifier under `/tmp/hermes-verify-*`, check:

- Markdown and JSON reports exist and JSON parses.
- Status is semantically correct (`YELLOW` if Telegram proof is pending).
- No Stripe keys, webhook secrets, Telegram bot tokens, DB URLs, Redis URLs, or unredacted `?start=` tokens appear in reports.
- The phase test user exists with active subscription state and an unused invitation.
- Coach consent was not inferred from Solo payment.
- Changed Python files compile.
- Router metrics are clean.
- Any stale temp verifier named in the warning is gone.
