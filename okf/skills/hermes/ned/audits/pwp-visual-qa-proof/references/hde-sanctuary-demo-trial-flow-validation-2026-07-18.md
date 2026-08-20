# HDE Sanctuary Demo Trial Flow Validation — 2026-07-18

Use this reference when validating a semi-public HDE Sanctuary/demo/trial flow before staging or production promotion.

## Class of work

Demo/trial onboarding flow that spans static marketing HTML, FastAPI signup APIs, DB access-status columns, Telegram deep links, tenant router access gates, VM orchestrator payload context, and trial expiry/deprovision lifecycle.

## Required surfaces

- Static route: `/sanctuary-demo/` and alias `/sanctuary-demo.html`.
- API route: `POST /api/demo/start`.
- DB model/migration: `users.access_status`, `trial_expires_at`, `deactivated_at`, `deletion_scheduled_at`, `demo_started_at`, `demo_renewal_count`, `demo_last_source`, and `demo_deleted_at`.
- Public demo renewal policy: active repeats must not extend expiry; expired/deleted demo renewal requires a valid invite/admin path.
- Router: demo expiry gate before onboarding/chat forwarding.
- Orchestrator: `GUEST_ACCESS_STATUS`, `GUEST_TRIAL_EXPIRES_AT`, and prompt context.
- Lifecycle: daily timer/script transitions `demo -> expired_demo -> deprovisioning`.
- Docs: status model, upgrade continuity, retention/deletion behavior, abuse/rate-limit posture.

## Pitfalls found

1. **Repeat signup must not extend an active demo forever.**
   - If a user is already `access_status=demo` with a future `trial_expires_at`, create a new invite if needed but keep the existing expiry.
   - Only reset expiry when the prior demo is already expired or explicitly admin-approved.

2. **Browser form field access can silently fail.**
   - Avoid `form.name.value` and similar property access; `name` can collide with the form's own `name` property.
   - Use `document.getElementById('name').value`, `document.getElementById('email').value`, etc.
   - Verify by real browser submit/click, not just `fetch()` in console.

3. **Static route permissions matter on VM-backed staging.**
   - Copied files under `dist/` may inherit `0600` and Nginx will return 403.
   - After syncing ad-hoc static HTML into staging `dist/`, run `chmod 0644 dist/sanctuary-demo/index.html dist/sanctuary-demo.html dist/robots.txt` or equivalent.

4. **Systemd `EnvironmentFile` can override inline `DATABASE_URL`.**
   - `hde_api_staging.service` had inline SQLite `DATABASE_URL`, but `.env` also defined Postgres and overrode it.
   - Live staging verification failed with `UndefinedColumnError: users.access_status does not exist` until the actual active Postgres DB was migrated.
   - Always inspect the effective runtime env/source and verify columns against the DB the service actually uses.

5. **Paid upgrade should preserve the existing space without lying about container state.**
   - Clearing demo/deactivation fields is right.
   - If the demo container is `suspended`/stopped, mark it wakeable (`stopped`) rather than blindly `active`; the router can start it on next chat.

6. **Lifecycle should pause before deletion.**
   - Demo expiry should set `expired_demo`, mark bot `suspended`, call orchestrator `stop`, and schedule deletion after retention.
   - Only after `deletion_scheduled_at` passes should it call `deprovision`.

7. **Expired demo self-renewal is a production leak.**
   - Active demo repeats may get a fresh invite but must keep the same expiry.
   - `expired_demo` / `deleted_demo` users should not self-serve a new trial from the public endpoint.
   - Require a valid `HDE_DEMO_INVITE_CODE` or an admin renewal path; track `demo_renewal_count` and `demo_last_source`.

8. **Deletion must specify PII fate, not just container fate.**
   - After retention, orchestrator `deprovision` handles container/workspace removal.
   - Also mark `access_status=deleted_demo`, `subscription_status=inactive`, null Stripe/demo customer ids, clear Telegram linkage, mark invites used/expired, and anonymize email as `deleted+demo+<user_id>@humandesignengine.local` unless a hard-delete policy is approved.

9. **Production gate should block on live/human proofs.**
   - Track a blocker script such as `scripts/hde_demo_production_gate.py` that returns BLOCKED until the five proofs exist: Telegram click-through, container provisioning, paid-upgrade continuity, edge/WAF rate limit, and reminder messaging.
   - Keep this separate from ad-hoc code verification; it is production readiness, not syntax/contract proof.

10. **Transactional email style is part of the product contract.**
   - When Michael provides a reference email/PDF, extract it (`pdftotext` is enough for text PDFs) and treat its tone/structure as source material, not inspiration to be paraphrased away.
   - For the HDE Sanctuary onboarding email, preserve the quiet sequence: subject “Your next step: open your Human Design sanctuary”; “SOMATIC EXPERIMENT STATION”; “You’re in.”; “Nothing else to figure out right now. Your next step is simple.”; “Open your private Telegram sanctuary”; durable Telegram link; “This link does not expire…”; support/reply line; “Human Design Engine”; “Your private Human Design sanctuary”.
   - Style is also part of the contract. Do not ship plain-only transactional mail when the site has a themed brand surface: send `multipart/alternative` with the exact plain-text fallback plus HTML from the shared HDE light/sage helper (`shared/hde_email_theme.py`). The current source of truth is the live site theme: Outfit body type, Playfair Display logo/headlines, `#FAF7F0` light cream background, `#FDFBF7` paper panels, `#2F3631` sage-deep text, `#5F7261` sage-mid accents, `#8E9E90` sage-light support, rounded white cards, subtle sage borders, and dark-sage CTA buttons.
   - Do not reintroduce the retired email palette (`#14213d`, `#557c55`, `#c9a84c`, `#fbf7ed`), navy/gold gradient cards, or generic `Inter`/`Georgia` branding in onboarding/report-delivery email code.
   - Escape deep links before embedding them in HTML (`html.escape(..., quote=True)` or equivalent) and verify the unsafe-character case with fake SMTP capture.
   - Verify by mocking SMTP and asserting the captured MIME subject/body phrase order, MIME subtype `alternative`, both `text/plain` and `text/html` parts, theme tokens, CTA, escaped link, and absence of retired palette tokens. Do not send live mail unless explicitly approved.

## Focused ad-hoc verification pattern

When no canonical test/lint/build command exists, create a temporary verifier using an OS-safe `tempfile` path with a `hermes-verify-` prefix and label it ad-hoc, not suite green.

Verifier should check:

```text
python3 -m py_compile changed Python files + /tmp helper scripts
systemd-analyze verify /tmp/*.service /tmp/*.timer
static HTML/docs assertions
FastAPI ASGI POST /api/demo/start against tempfile sqlite DB
repeat signup does not extend active expiry
lifecycle dry-run would stop expired demo but does not commit mutation
cleanup verifier file and temp DB when possible
```

Expected marker shape:

```text
HDE_SANCTUARY_DEMO_FLOW_AD_HOC_OK_HERMES_VERIFY
```

## Staging gate closeout pattern

When asked to apply as many demo-production fixes as possible without a human phone tap:

1. Keep production untouched unless explicitly authorized.
2. Implement machine-closeable gates first: lifecycle timer, reminder timer/script, edge/WAF rate limit, and production-gate script evidence checks.
3. For Cloudflare rate limits, watch entitlement errors: include `cf.colo.id` in characteristics, and lower-plan zones may only allow `period=10` and `mitigation_timeout=10`.
4. Add reminder sender as idempotent stateful script: day 7, day 12/2-days-left, expiry day, and pre-delete warning. Verify with a tempfile SQLite DB and a tempfile reminder-state JSON under `/tmp/hermes-verify-*`.
5. Run a server-side demo walkthrough: `POST /api/demo/start`, feed the `hde_demo_` token into the router `/start` handler with mocked Telegram sends, choose a guide, let the real orchestrator provision Docker, inspect generated guest env/workspace/container, simulate paid upgrade via webhook processor without completing Stripe payment, stop/wake the same container, and record evidence.
6. Label proof honestly: “server-side router/orchestrator walkthrough” is strong staging evidence, but a final human-live Telegram proof still requires a real user tapping the deep link and sending a message.

## Production-promotion closeout pattern

When staging is green but production promotion is requested:

1. Do not promote from a dirty live checkout. Create a clean `/tmp` worktree from the target production base, usually `deploy-fresh`, and cherry-pick only the intended verified commits.
2. Fix `git diff --check` blockers in the source commits before or during promotion; amended whitespace fixes are legitimate when they only repair mechanical hygiene.
3. Keep systemd templates lane-safe in HDE by storing them under `scripts/systemd/`, not `deploy/systemd/`, because Ned's push guard owns `scripts/` but rejects `deploy/`.
4. Make `scripts/hde_demo_production_gate.py` environment-configurable: `HDE_REPO_ROOT`, `HDE_RUNTIME_DIR`, `HDE_DEMO_SYSTEMD_TEMPLATE_DIR`, `HDE_DEMO_LIFECYCLE_TIMER`, `HDE_DEMO_REMINDER_TIMER`, and template prefixes. This lets staging evidence pass with explicit staging overrides while production defaults point at production timer names.
5. Production email/report helpers must not retain staging URLs after cherry-pick; assert production-facing helper text points at `humandesignengine.com` while staging proof remains override-driven.
6. Run a `/tmp/hermes-verify-*` verifier on the clean promotion branch covering `git diff --check`, Python compile, `systemd-analyze verify`, `npm run build`, changed-file secret scan, staging gate with overrides, production gate default status, and public route smoke.
7. A production gate default of `BLOCKED` is acceptable before install if it references production timers/evidence. It means the PR is ready, not that production timers are already installed.
8. Read push/CI results after pushing. If Cloudflare Pages passes but Workers build fails, report it as an external check to resolve or waive; do not call the production deployment complete.

## Staging integration checklist

1. Lock changed files.
2. Review George/other-agent changes before accepting them.
3. Fix repeat-signup, constant-time invite-code compare, rate-limit guard, browser form field access, paid upgrade container status, and docs gaps.
4. Run local ASGI/tempfile verifier.
5. Apply live staging DB migration to the actual active database.
6. Sync static route to staging `dist/`, fix permissions, and verify Nginx route locally and via browser.
7. Restart relevant staging services: API, router, orchestrator.
8. Install/enable lifecycle timer if requested.
9. Browser-test form submit and confirm Telegram deep link appears.
10. Do not production-deploy until real Telegram/container onboarding and paid-upgrade continuity are verified or explicitly deferred.
