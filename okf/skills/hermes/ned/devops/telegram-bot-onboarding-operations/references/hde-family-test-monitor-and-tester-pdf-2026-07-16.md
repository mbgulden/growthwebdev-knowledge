# HDE family test monitor + branded tester PDF — 2026-07-16

## Trigger

Michael wanted siblings/family to test the Human Design Engine staging checkout + Telegram bot flow and asked whether we could monitor conversations/update the bot live. The durable lesson is to split this into two lanes:

1. **Health + stuck-state monitor first** — safe operational dashboard, no raw transcripts.
2. **Consented transcript review second** — only after tester disclosure/consent; summarize/artifact-count by default, do not dump conversation content casually.

## Existing coach dashboard status

The coach dashboard did exist, but staging served it from canonical `hd-platform` paths rather than staging-local files:

- `/home/ubuntu/work/hd-platform/scripts/coach_dashboard.html`
- `/home/ubuntu/work/hd-platform/landing/coach_dashboard.html`
- `/home/ubuntu/work/hd-platform/public/coach_dashboard.html`
- staging orchestrator route: `GET http://127.0.0.1:8011/coach/dashboard` returned `200`

The coach dashboard is for consent-gated coach review. The family-test monitor is a different operational cockpit for checkout/onboarding/router/container stuck states.

## Family-test monitor pattern

Create a small script under the HDE staging repo, e.g. `scripts/hde_family_test_monitor.py`, that:

- Loads the same `.env` as staging without printing secrets.
- Reuses `scripts/hde_router_metrics.py` for DB/Redis/Docker health.
- Queries `User`, `Invitation`, and `BotInstance` with relationships.
- Redacts email labels.
- Separates **waiting** from **stuck**:
  - waiting: paid/active but invite not used yet;
  - stuck: invite used but no bot, Telegram link missing after bot creation, DB says active but container missing, unhealthy container, missing workspace, missing guide name.
- Includes consent flags and only reports transcript/artifact counts when active consent is present.
- Emits both JSON and HTML artifacts, e.g.:
  - `docs/hde-family-test-monitor.json`
  - `docs/hde-family-test-monitor.html`

Recommended run shape:

```bash
cd /home/ubuntu/work/hd-platform-staging
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_family_test_monitor.py \
  --include-consented-transcript-summary \
  --stdout
```

Expected stdout should summarize status, artifact paths, tester count, and stuck count. The JSON should include:

```json
{
  "mode": {
    "health_and_stuck_state": true,
    "consented_transcript_summary": true,
    "raw_transcript_content_included": false
  },
  "metrics": {},
  "testers": [
    {"waiting_reasons": [], "stuck_reasons": []}
  ]
}
```

## Branded tester PDF pattern

Produce a Human Design Engine-branded HTML guide and render it to PDF with `wkhtmltopdf` when available:

- `docs/hde-family-test-instructions.html`
- `docs/hde-family-test-instructions.pdf`

Required contents:

- Clear privacy note: operational status may be monitored; transcript review only with consent.
- Staging signup URL, usually `https://staging.humandesignengine.com/deconditioning/`.
- Stripe sandbox card:
  - card `4242 4242 4242 4242`
  - future expiry such as `12/34`
  - CVC such as `123`
  - ZIP such as `83702`
- Telegram onboarding steps: Open Telegram, press Start, choose guide name.
- Suggested guide names: Ember, Mira, George, or short custom label.
- First-conversation test prompts.
- Tester feedback checklist: stuck point, exact weird bot message, device, what felt good.

## Verification recipe

Use a fresh `/tmp/hermes-verify-*` ad-hoc verifier when Hermes requests proof. It should:

1. `py_compile` the monitor script.
2. Run the monitor with staging `PYTHONPATH` and `--stdout`.
3. Parse generated JSON and verify `raw_transcript_content_included == false`.
4. Verify tester rows include `waiting_reasons` and `stuck_reasons`.
5. Verify monitor HTML includes the privacy statement.
6. Verify guide HTML/PDF contains the test card, Telegram steps, HDE branding, and guide names.
7. Secret-scan generated artifacts for token/API-key/DB-URL shaped strings while allowing the public Stripe test card.
8. Remove the verifier script.

## Pitfalls

- Do not mark every unused invite as “stuck.” For family testing, unused active invites are usually waiting/not-started, not broken.
- Do not expose raw Telegram transcript content in the operational monitor. Keep content review explicitly consent-gated.
- Do not conflate the coach dashboard with the family-test monitor. Coach dashboard = client review; family monitor = staging test operations.
- If the coach dashboard exists only in canonical paths while staging serves it, report that as untidy path coupling, not absence.
- Keep the tester PDF simple enough for non-technical family members; do not include internal service names or secrets.
