# HDE website/payment/PWP/PDF readiness audit pattern (2026-07-15)

Use this pattern after HDE Telegram launch proof is GREEN but before broad public traffic or paid website funnel exposure.

## Evidence to collect

Run these from the relevant checkouts:

```bash
# Bot runtime, staging checkout
cd /home/ubuntu/work/hd-platform-staging
systemctl is-active hde_router.service
systemctl is-active hde_api_staging.service || true
sudo docker inspect -f '{{.State.Health.Status}}' guest-hermes-23
/home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_router_metrics.py --pretty
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty

# Frontend/build/PWP, frontend checkout
cd /home/ubuntu/work/hd-platform
npm run build
npm run pwp:verify
PWP_STAGING_URL=<correct-base-url> npm run qa:flows -- --reporter=list
```

Live route smoke should include at least:

- `https://humandesignengine.com/`
- `/deconditioning/`
- `/success/`
- `/privacy/`
- `/terms/`
- `/academy/`
- public checkout/API base actually used by the frontend
- `api.humandesignengine.com` if public API is expected
- `reports.humandesignengine.com` if public report delivery is expected

Use `curl -L -w 'http=%{http_code} bytes=%{size_download} type=%{content_type}'` and check page titles/required text. A `200` homepage fallback is not route success.

## Payment-specific pitfalls

- `hde-payment.service active` only proves a process exists. It does not prove Stripe checkout works.
- Local `POST /create-checkout` must return either a Stripe Checkout URL or a controlled JSON error. Empty reply after Stripe 401/4xx is a blocker.
- Root-domain `/api/*` returning static HTML is a public routing bug if the frontend points there.
- `api.humandesignengine.com` behind Cloudflare Access blocks public checkout/API unless intentionally split into private/public endpoints.
- Never print Stripe keys/webhook secrets; redact `sk_*`, `pk_*`, `whsec_*`, checkout session URLs, DB/Redis URLs.

## PWP / visual QA pitfalls

- PWP installed in `package.json` is not proof; run `npm run pwp:verify`.
- If Playwright browser is missing, record it as an environment blocker and run `npx playwright install chromium` before rerunning.
- PWP staging checkout tests need the *actual* public/staging base URL. If `PWP_STAGING_URL=https://humandesignengine.com` posts to `/api/checkout/create-session` and that route is homepage fallback, the test should fail.

## Bot PDF visual checks

- Live Telegram media proof proves documents were sent, not that PDFs match brand.
- Use `pdfinfo` to check pages/page size/creator and `pdftoppm -png -f 1 -singlefile <pdf> /tmp/hde-pdf-proof/<name>_page1` to create visual baselines.
- Run semantic/manual visual QA on rendered PNGs for navy/gold palette, typography, clipping, chart clarity, placeholder assets, and product naming.
- If `pdftotext` extracts almost no text, record a PDF accessibility/readability risk even if visual output looks acceptable.

## Report shape

Create dated artifacts under `reports/`, e.g.:

- `reports/hde_onboarding_payment_bot_ux_audit_YYYYMMDD.md`
- `reports/hde_onboarding_payment_bot_ux_audit_YYYYMMDD.json`

Include:

- overall GREEN/YELLOW/RED
- bot runtime evidence
- website route smoke table
- payment/API routing smoke table
- PWP/build status
- PDF generation/visual-readiness status
- primary risks
- phased execution plan:
  1. freeze/map funnel
  2. route correctness
  3. payment/post-payment onboarding hardening
  4. bot container/conversation routing robustness
  5. UX/UI + PWP + PDF visual readiness
  6. controlled rollout/monitoring

Before commit, run `git diff --cached --check`, targeted staged secret scan, and a `/tmp/hermes-verify-*` artifact verifier that parses JSON/Markdown, validates expected findings/phases, and scans for secret-shaped strings.
