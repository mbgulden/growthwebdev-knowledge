# CF Access expected-public bypass classification

Use this when a CF Access health check reports `UNLOCKED` for routes that may be intentionally public checkout/report/webhook paths.

## Pattern

1. Verify live no-redirect behavior for the exact path.
2. Read the matching Zero Trust Access app and policies.
3. Classify before mutating:
   - **Protected internal app:** should return Access `302`.
   - **Expected public bypass:** app name/domain explicitly mark a public checkout/report/webhook/static path and policy is `decision=bypass` with `include=everyone`.
   - **Verifier-IP bypass:** policy is `decision=bypass` but scoped only to IP includes, often Fred/Michael verifier `/32`; from that machine origin `200` is not proof the route is public to everyone.
   - **Unexpected unlocked:** not Access `302`, not expected-public, not narrow verifier-IP.
4. Alert only on **unexpected unlocked**. Keep checkout/webhook public exceptions reachable unless separately asked to harden app-level signature validation.
5. In no-agent cron mode, all-clear stdout should be empty. Use an env flag such as `CF_ACCESS_HEALTH_VERBOSE=1` for manual classification reports.

## Verification shape

Use a fresh `/tmp/hermes-verify-*` script that asserts:

```text
py_compile=pass
unexpected_unlocked_count=0
expected_public_bypass_count=<expected count>
hostname_wide_sensitive_apps_locked=true
verifier_ip_bypass_classified=true
quiet_all_clear_stdout_empty=true
```

Then run the cron through the scheduler and inspect the latest output artifact; expected all-clear is `Status: silent (empty output)`.

## Pitfall

Do not fix a public-checkout alert by locking the entire API hostname or webhook path behind Access. Stripe/payment/provider callbacks generally cannot complete an Access login. Treat webhook signature validation as a separate application-auth hardening issue.
