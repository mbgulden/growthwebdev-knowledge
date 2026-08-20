# Deconditioning → Telegram Bot Workflow Audit Pattern (HDE, 2026-07)

Use this as a reference pattern when a PWP/pre-live audit includes a paid workflow that provisions bots, containers, onboarding links, or other downstream automation.

## What mattered

The `/deconditioning/` page itself was only the entry point. The real launch risk lived in the chain:

```text
/deconditioning/
  → package selection
  → email modal
  → /api/checkout/create-session
  → checkout/pay or Stripe Checkout
  → /success?session_id=...
  → /api/checkout/session
  → Telegram deep link
  → /start <token>
  → tenant router validates token
  → BotInstance row
  → VM/container orchestrator
  → Telegram proxy forwards messages to guest container
```

## Durable audit checks

### 1. Separate UI smoke from real fulfillment

- A browser checkout/success screen is not enough.
- Confirm whether checkout is mock/local or Stripe-hosted/test mode.
- If mock mode returns `cs_test_mock_...`, mark payment as UI smoke only.
- Verify downstream side effects separately: user row, invitation/token row, bot instance row, container state, and Telegram message routing.

### 2. Audit deep-link identity as a contract

For Telegram onboarding workflows, verify all of these match:

- Bot username shown in public deep links returned by the API.
- Bot username printed/logged by backend notification code.
- Bot token loaded by the running router/service.
- `getMe` result for that token.
- Systemd service `EnvironmentFile` used by the router.

A mismatch means users can receive valid-looking links that no running service handles.

### 3. Check the actual router daemon, not just source code

Source code may implement `/start <token>` correctly while runtime is broken. Check:

- service is running
- correct env file loaded for staging/production
- Telegram `getUpdates` does not return `401 Unauthorized`
- logs are free of repeated token/auth errors
- router can send messages to the target chat/bot identity

### 4. Validate provisioning idempotency

Container/bot provisioning must tolerate partial prior attempts. Look for stale poisoned state:

- `BotInstance.status = provisioning` older than startup window
- existing guest scaffold directories from prior attempts
- path conflicts such as `config.yaml` existing as a directory when code writes it as a file
- containers/images/network resources left by failed runs

Acceptance should include running the same test user twice or proving cleanup/rollback makes repeated attempts safe.

### 5. Verify rollback and cancellation paths

For subscription-backed bots, test more than happy path:

- invalid/used/expired invite token
- orchestrator failure rolls token back to unused or marks failure clearly
- subscription cancellation marks user inactive
- bot/container stops or suspends
- stale provisioning rows are remediated by watchdog or admin runbook

## Example red flags from this session

- Public API returned `https://t.me/HDE_CoachBot?start=...` while logs printed `HDE_MasterBot`, and the valid token resolved to another username.
- Router service loaded production `.env` while auditing staging and logged repeated Telegram `401 Unauthorized`.
- Orchestrator failed on stale filesystem state: `config.yaml` existed as a directory.
- DB had a stale `BotInstance` stuck in `provisioning`.
- Staging checkout was mock mode, so card `4242` did not prove real Stripe test-mode readiness.

## Reporting stance

Call this RED if the purchase-to-token half works but the token-to-bot/container half is not verified. Present the architecture as present, but do not call the workflow launch-ready until Stripe/test payment, Telegram `/start`, provisioning, and first bot reply all pass end-to-end.
