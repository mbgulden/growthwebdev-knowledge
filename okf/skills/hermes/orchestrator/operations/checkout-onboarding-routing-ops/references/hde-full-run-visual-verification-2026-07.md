# HDE Full Run Visual Verification Notes — 2026-07

Session learning from a full staging run-through of the paid Solo Sanctuary flow.

## Full Run Shape That Worked

Verify the whole customer path, not just source/build checks:

1. Start at live staging product page (`/deconditioning`).
2. Capture product page screenshot showing Solo + Sovereign choices.
3. Open checkout email modal and capture screenshot.
4. Create a fresh Stripe test Checkout session using the real staging API contract:
   - `POST /api/checkout/create-session`
   - test-mode Price ID for staging
   - `success_url=https://staging.humandesignengine.com/success?session_id={CHECKOUT_SESSION_ID}`
5. Capture Stripe hosted Checkout screenshot before entering card details.
6. Complete success card flow (`4242 4242 4242 4242`).
7. Verify redirect to success page.
8. Capture the success page state.
9. Verify backend: Stripe webhook, active user row, durable invitation, and `/api/checkout/session` lookup.
10. Run disposable router simulation so the real customer's invite stays unused.
11. Run fresh build + Python compile after any patch discovered during the run.

## Screenshot Pattern

If browser visual tooling is unreliable, use Chromium headless or CDP to produce actual PNG files, but clean up any temporary helper scripts before final verification. Store screenshots outside the repo when they are evidence artifacts, not product assets.

Useful screenshot names:

- `01-product-page.png`
- `02-email-modal.png`
- `03-stripe-checkout.png`
- `04-success-recovery-fallback.png` if webhook/session lookup races
- `05-success-open-telegram.png`
- `06-success-sessionid-fixed.png`

## Stripe Session Lookup Pitfall

In the Stripe Python SDK, `stripe.checkout.Session.retrieve(session_id)` may return a Stripe object rather than a dict. Do not assume `session.get(...)` exists.

Robust pattern:

```python
session = stripe.checkout.Session.retrieve(session_id)
customer_details = getattr(session, "customer_details", None) or {}
metadata = getattr(session, "metadata", None) or {}
resolved_email = (
    getattr(session, "customer_email", None)
    or getattr(customer_details, "email", None)
    or (customer_details.get("email") if isinstance(customer_details, dict) else None)
)
resolved_name = (
    getattr(customer_details, "name", None)
    or (customer_details.get("name") if isinstance(customer_details, dict) else None)
    or "Friend"
)
metadata_get = metadata.get if hasattr(metadata, "get") else lambda key, default=None: getattr(metadata, key, default)
```

Symptom of the bug:

- Stripe retrieve call logs `response_code=200`
- app still returns `400 Invalid checkout session`
- log says `Failed to retrieve Stripe session: get`

This means Stripe retrieval succeeded; local object access failed.

## UX Gate

Direct `session_id` success-page lookup must land on the one-step CTA without requiring the fallback email path. The fallback is good as a recovery anchor, but it should not be the normal success path once webhook processing has completed.

Expected live success text:

```text
You’re in.
Nothing else to figure out right now. We’ll show you one step at a time.
Next step
Open your private Telegram sanctuary
Open Telegram
The link does not expire; come back whenever you need.
```

## Backend Evidence Shape

For a fresh paid test customer, capture:

```json
{
  "user_exists": true,
  "subscription_status": "active",
  "invite_exists": true,
  "invite_used": false,
  "invite_expires_days_from_now": 3650.0,
  "email_lookup": {"status": 200, "has_deep_link": true},
  "session_lookup": {"status": 200, "has_deep_link": true}
}
```

For router simulation, use disposable records and verify:

```json
{
  "bot_exists": true,
  "bot_status": "active",
  "telegram_user_id": "...",
  "invite_used": true,
  "forwarded_to_guest_api": true,
  "last_telegram_text": "...",
  "cleanup": "deleted disposable router-smoke records"
}
```
