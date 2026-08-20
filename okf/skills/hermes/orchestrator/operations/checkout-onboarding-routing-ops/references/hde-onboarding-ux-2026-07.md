# HDE Onboarding UX Notes — 2026-07

Class: checkout → paid onboarding → Telegram sanctuary routing.

## User Preference Signal

Michael explicitly wants the onboarding customer experience to work like the “next step” app idea:

- one visible next step at a time
- “stupid easy” human-readable flow
- no timeout pressure
- safe for autistic, ADHD, and trauma-loaded users
- durable recovery if interrupted mid-purchase or mid-setup
- email should hold the reference link so users can resume later

## Implementation Pattern Used

### Success page

Changed from an anxious systems state:

- “Activating your container… please do not close this window”
- `Launch Telegram Onboarding Bot`
- “Link expires in 24 hours”
- premium calendar shown alongside Telegram

To a one-step state:

```text
You’re in.

Nothing else to figure out right now. We’ll show you one step at a time.

Next step

Open your private Telegram sanctuary

[Open Telegram]

That is the only thing to do right now. The link does not expire; come back whenever you need. We’ll also email this step for reference.
```

For Sovereign/premium, calendar reveal is hidden until the Telegram CTA is clicked.

### Durable onboarding links

- New webhook-created invitations use far-future timestamps (`timedelta(days=3650)`) for non-null DB compatibility.
- Public lookup endpoint returns latest unused invitation without filtering by `expires_at`.
- Tenant/master bots do not reject paid active users due to invitation timestamp passing.
- Active subscription and token usage remain gates.

### Email recovery anchor

Webhook path schedules `send_customer_onboarding_email(email, deep_link, is_premium)` after token creation.

Email body should stay plain and calm:

```text
You’re in.

Nothing else to figure out right now.

Your next step is simple:

Open your private Telegram sanctuary:
{deep_link}

This link does not expire. If you get interrupted, overwhelmed, distracted, or need to come back later, use this email and pick up right here.
```

SMTP missing credentials should log/skip and never fail checkout.

## Verification Pattern

After patching this class of flow, verify:

1. `npm run build`
2. Python compile for changed API/router modules.
3. Staging service restart if runtime code changed.
4. Live DOM/browser text contains one primary CTA (`Open Telegram`) and no timeout/scary copy.
5. Premium flow initially shows no calendar button; follow-up reveal only appears after Telegram CTA click.
6. Intentionally old unused invitation for an active user still returns a deep link and can onboard in router smoke.
7. SMTP-missing path returns false/logs skipped without throwing.
