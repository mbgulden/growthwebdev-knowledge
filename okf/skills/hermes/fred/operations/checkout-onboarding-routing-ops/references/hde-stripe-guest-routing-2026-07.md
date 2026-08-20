# HDE Stripe + Guest Routing Launch Notes — July 2026

This reference captures reusable details from the HDE launch-hardening session. Keep it as session-specific detail under the class-level `checkout-onboarding-routing-ops` skill.

## Durable Workflow Corrections

- Do not conclude “Stripe key missing” from obvious `.env` files only. Check systemd runtime env and published/deployed env snapshots before declaring a blocker.
- Validate key type with Stripe before use:
  - `whsec_...` validates webhook signatures; it cannot authenticate Stripe API requests.
  - `mk_...` is not accepted as server-side Checkout API auth.
  - Use `sk_test_...`, `rk_test_...`, `sk_live_...`, or `rk_live_...` as appropriate.
- If live Stripe prices are wrong for the intended business model, create/reuse correct Products/Prices and patch app code to match intent — do not force product copy to fit accidental prices.

## Intended HDE Deconditioning Pricing Model

- Solo Sanctuary: `$29/month` recurring subscription.
- Sovereign Container: `$1,500` upfront for the 6-week container, includes 1 year, then renews at `$29/month` after 365 days.

Stripe Checkout shape:

```text
Solo:
  mode=subscription
  line_items=[monthly recurring $29]

Sovereign:
  mode=subscription
  line_items=[one-time $1500 upfront, monthly recurring $29]
  subscription_data.trial_period_days=365
```

## Test-Mode Matrix Evidence Pattern

Use test-mode Stripe objects and a real test webhook endpoint for staging. Evidence to collect:

```text
Success card 4242 4242 4242 4242 → success redirect
Stripe-delivered checkout.session.completed webhook → HTTP 200
Fulfillment lookup → onboarding deep link exists
Decline card 4000 0000 0000 0002 → expected decline error
SCA card 4000 0025 0000 3155 → 3DS challenge branch reached
Sovereign checkout creation → cs_test Checkout URL
```

If hosted 3DS gets stuck in headless browser/iframe/challenge handling, report: **SCA branch reached; manual normal-browser completion still needed**. Do not call it full SCA success.

## Guest Profile Seeding Pattern

For launch guest profiles, seed active `User` + unused `Invitation` rows. Do not create `BotInstance` rows until the real Telegram tester opens the onboarding link.

Minimum profile fields:

```text
subscription_status='active'
is_premium=false for Solo, true for Sovereign
coach_review_consent=true only when explicitly granted
coach_review_consent_source set only when consent is true
coaching_container_end set for Sovereign if the app uses it
unused Invitation token with reasonable expiry
```

Router binding path:

```text
https://t.me/TheNextNextStepBot?start=<token>
→ process_start_token
→ validate Invitation + active User
→ create/update BotInstance
→ bind telegram_user_id
→ mark invitation used
→ provision guest-hermes-{user_id}
```

Runtime chat path:

```text
Telegram chat_id
→ BotInstance.telegram_user_id
→ container guest-hermes-{user_id}
→ /api/message
→ Telegram reply
```

## Router Bug Found

SQLite-backed staging returned `Invitation.expires_at` as offset-naive, causing this failure when compared to aware UTC:

```text
TypeError: can't compare offset-naive and offset-aware datetimes
```

Durable fix:

```python
def as_aware_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
```

Use it before comparing DB datetimes to `datetime.now(timezone.utc)`.

## Disposable Router Simulation Recipe

To verify without Telegram spam or Docker startup:

1. Create disposable active user + invitation in staging DB.
2. Fake the HTTP client so Telegram sendMessage and orchestrator provision return `200`.
3. Call `process_start_token(fake_client, chat_id, token)`.
4. Monkeypatch `get_container_ip` to return `127.0.0.1`.
5. Fake guest `/api/message` to return `{"response": "ROUTED_OK..."}`.
6. Call `handle_user_chat(fake_client, chat_id, text)`.
7. Assert:

```text
bot_exists=true
bot_status=active
telegram_user_id bound
invite_used=true
forwarded_to_guest_api=true
last Telegram payload contains routed response
```

8. Delete disposable `BotInstance`, `Invitation`, and `User` rows afterward.

## Verification Discipline

After touching router/API/frontend/docs in this class of work:

```bash
npm run build
python3 -m py_compile scripts/hde_tenant_router.py
python3 -m py_compile api/routes/stripe_webhook.py  # if touched
```

Also verify active services when runtime code was restarted:

```text
hde_router.service active
hde_api_staging.service active
hde_orchestrator_staging.service active
```
