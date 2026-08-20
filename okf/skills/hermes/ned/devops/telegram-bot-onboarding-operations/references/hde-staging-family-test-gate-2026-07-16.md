# HDE staging family-test gate — consent, checkout, Telegram boundary, PDF, coach portal

## Durable lessons

- Staging/family-test consent is not the same as premium/sovereign coach consent. If the checkout sends `family_test_review_consent=true` and `coach_review_consent=true`, the webhook must preserve `coach_review_consent=true` even for Solo/family-test users. Otherwise the UI looks consented while the DB silently discards consent because the user is not premium.
- Verify consent at the DB record created by a real Stripe sandbox checkout, not only by checking frontend metadata strings. The proof row should show `coach_review_consent=true`, `coach_review_consent_source=staging_family_test_checkout`, an active subscription/user state, and an unused onboarding invitation.
- A server-side Telegram gate can prove bot identity (`getMe` safe fields), deep-link token generation, invitation state, guide/provisioning canary, and PDF generation. It cannot prove the real Telegram `/start` tap; that remains a human phone boundary.
- Cloudflare Access header simulation through the public edge is misleading: public curl cannot inject real Access identity headers through Cloudflare. To prove app/origin logic, simulate headers against the origin/Nginx path locally with `Host: staging.humandesignengine.com`; to prove browser login, a real approved user must open the portal through Cloudflare.
- For PDF/report gates, file existence and size are insufficient. Generate through the live guest API, map `/workspace/...` to `/home/ubuntu/users/guest_ID/...`, run `pdftotext` for real headings, and render at least the first page with `pdftoppm`/visual QA when quality matters.
- Secret scans should avoid treating placeholder strings like `"***"` as real leaked credentials. Scan for realistic token/key shapes with length thresholds.

## Verification recipe

1. Create a real Stripe sandbox Checkout Session from staging with metadata:
   - `family_test_review_consent=true`
   - `coach_review_consent=true`
   - `coach_review_consent_source=staging_family_test_checkout`
2. Complete the sandbox checkout in browser.
3. Query the staging DB for the created email and verify:
   - user exists
   - `subscription_status == active`
   - `coach_review_consent is true`
   - `coach_review_consent_source == staging_family_test_checkout`
   - latest invitation exists and is unused
4. Verify Telegram boundary:
   - `getMe` safe fields only; never print token
   - deep link is `https://t.me/$HDE_ONBOARDING_BOT_USERNAME?start=<token>`
   - report that real `/start` still requires a phone tap
5. Run server-side guest proof:
   - `python3 scripts/hde_guest_canary.py --guest-id 23 --pretty`
   - direct guest API `Yes pdf report`
   - `pdftotext` contains report headings
6. Verify coach portal:
   - public `/coach/dashboard` returns 200
   - public `/api/coach/session` returns 401 unauthenticated
   - origin-local simulated CF headers accept allowed emails and reject disallowed emails
7. Run family monitor and ensure any warnings have explicit reasons.
8. Commit only after pycache/runtime noise is cleaned.

## Production gate rule

Do not promote production on server-side proof alone. Remaining human gates are: real Telegram phone canary and real Cloudflare Access browser login by an approved email.