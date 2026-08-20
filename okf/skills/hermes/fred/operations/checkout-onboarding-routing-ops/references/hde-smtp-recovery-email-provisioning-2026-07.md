# HDE SMTP Recovery Email Provisioning — 2026-07

Use this when the checkout/onboarding recovery email path is coded but logs `Customer onboarding email skipped: SMTP credentials incomplete.`

## Durable findings

- HDE checkout recovery emails use SMTP env vars loaded by the API/payment services:
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASS`
  - `FROM_EMAIL`
- Staging and production env files may both need provisioning:
  - `/home/ubuntu/work/hd-platform-staging/.env`
  - `/home/ubuntu/work/hd-platform/.env`
- Relevant services to restart after SMTP env changes:
  - `hde_api_staging.service`
  - `hde-api.service`
  - `hde-payment.service`
- Google Workspace/Gmail app passwords should be stored in `.env` either quoted or, preferably, normalized to the 16-character no-space form. Unquoted spaces cause shell sourcing to fail (`command not found` on the second group).

## Safe provisioning pattern

1. Inspect current SMTP env status without printing secrets. Report only set/unset and length/prefix where safe.
2. If user provides a Gmail app password with spaces, remove spaces before writing `SMTP_PASS`.
3. Update both staging and production env files if the feature is expected in both.
4. Restart all services that load those env files.
5. Verify with the same application send function used by the webhook, not a separate toy SMTP script.
6. Run canonical verification after env/code changes:
   - `npm run build`
   - `python3 -m py_compile api/routes/stripe_webhook.py`
7. In the final report, do not echo the secret. State `SMTP_PASS set: true` and length only.

## Example verification evidence

```text
smtp_test_sent: true
hde_api_staging.service active
hde-api.service active
hde-payment.service active
SMTP_PASS set: true
SMTP_PASS length: 16
```

## Pitfalls

- Do not tell the user only what they need to do if they hand over the app password; provision it immediately and verify the send path.
- Do not leave a spaced app password unquoted in `.env`; systemd may load some values differently than shell tests, so normalize to no-space form for consistency.
- Do not print app passwords, SMTP credentials, Stripe keys, webhook secrets, bot tokens, or Telegram onboarding links in logs or summaries.
