# HDE staging launch remediation pattern — July 2026

Use this as a concrete pattern when a PWP/pre-live audit turns into active launch wiring for a staged SaaS/payment/bot workflow.

## Core lesson

For staging launch audits, do not stop at page-level PWP findings. Follow the live user path into runtime services and verify each contract boundary:

```text
CTA/page → checkout/session API → success/invitation → Telegram deep link → router service → orchestrator → guest container → guest model provider → response
```

Every layer can be green in source while red at runtime because staging often has split worktrees, systemd services, cached static output, and environment files.

## HDE-specific runtime seams that mattered

- Source repo: `/home/ubuntu/work/hd-platform`
- Staging runtime worktree: `/home/ubuntu/work/hd-platform-staging`
- Staging API service: `hde_api_staging.service`
- Staging orchestrator service: `hde_orchestrator_staging.service`
- Telegram router service: `hde_router.service`
- Staging DB: `/home/ubuntu/work/hd-platform-staging/staging_database.db`

When patching source, mirror runtime-critical fixes into the staging worktree if services actually run from there.

## Verification pattern

### 1. Free chart/widget contracts

Check all four:

1. page mount selector/custom element
2. widget script initializer selector/custom element
3. API endpoint response
4. browser-rendered result

In this session the page originally mounted `<hd-bodygraph>`, while `widget.js` only initialized `.hde-chart-widget`. After fixing the mount, the API returned valid JSON but the result renderer still threw because `prefix` was assigned after `statCard()` calls. Browser proof must include actual rendered chart text, not only a 200 API response.

Useful acceptance evidence:

```text
/api/public/compute-chart → 200
browser widget text includes Type/Profile/Authority/Strategy/Signature
```

### 2. Stripe mock vs real test mode

Treat local/mock checkout as UI smoke only. Real Stripe readiness requires:

- hosted Stripe Checkout or Stripe.js evidence
- `4242 4242 4242 4242` success
- `4000 0000 0000 0002` decline
- `4000 0025 0000 3155` SCA/3DS
- signed webhook receipt
- downstream fulfillment/provisioning proof

### 3. Telegram router identity

Normalize bot identity through env, e.g. `HDE_ONBOARDING_BOT_USERNAME`, and verify it matches the token returned by Telegram `getMe`.

Common failure:

```text
Deep link points to HDE_CoachBot
logs mention HDE_MasterBot
running router token resolves to another bot or 401s
```

Acceptance:

```text
router journal: getUpdates HTTP/1.1 200 OK
/api/checkout/session deep_link points to the same username the router token owns
```

### 4. Consent vs entitlement

For HDE deconditioning specifically:

- Solo + Premium both get the single-router bot/sanctuary.
- `is_premium` gates Becca/Michael coach-review access, not bot entitlement.
- Coach review must require explicit user consent to review conversation summaries/progress.

Coach endpoints should require:

```python
User.is_premium == True
User.subscription_status == "active"
User.coach_review_consent == True
User.coach_review_consent_revoked_at == None
```

Solo should receive bot access but must not appear in coach review lists.

### 5. Orchestrator/provisioning idempotency

Provisioning can be poisoned by stale scaffold paths. In this session a previous failed run left:

```text
/home/ubuntu/guest_hermes_bot_3/config.yaml  # directory, not file
```

The orchestrator must quarantine/remove bad path state before writing config. Verify by calling the HMAC-protected provision endpoint and checking Docker health, not just by reading source.

Acceptance:

```text
POST /api/orchestrate/provision → 200
container guest-hermes-N Up (healthy)
```

### 6. Guest Hermes model/provider wiring

A healthy guest container can still fail to answer if Hermes inside lacks provider auth/model config.

Observed progression:

```text
/api/message → HTTP 401 Missing Authentication header  # placeholder/missing provider auth
/api/message → HTTP 400 No models provided             # auth fixed, model missing
hermes --provider openrouter --model minimax/minimax-m3 -z "..." → ok
```

For HDE guest bots, current preferred model is:

```yaml
model:
  provider: openrouter
  default: minimax/minimax-m3
```

OpenRouter model IDs verified:

```text
minimax/minimax-m3
minimax/minimax-m2.5
```

If the orchestrator writes `.env` for guest compose, propagate the real staging `OPENROUTER_API_KEY` into `GUEST_OPENROUTER_API_KEY` when no dedicated guest key exists.

## Reporting discipline

When fixes are applied during the audit, separate:

- **source verified**: syntax/build/unit smoke
- **staging runtime verified**: public URL/API/systemd/Docker/browser evidence
- **still not verified**: anything requiring real Stripe, real Telegram `/start`, or user-owned external interactions

Do not claim live-ready until the full checkout → Telegram → container → response loop is proven after the final model/provider patch.
