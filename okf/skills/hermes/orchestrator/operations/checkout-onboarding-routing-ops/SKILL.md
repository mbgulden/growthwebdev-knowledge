---
name: checkout-onboarding-routing-ops
description: Verify and remediate paid checkout → webhook → onboarding token → Telegram tenant routing flows, including Stripe test/live mode, guest profile seeding, and launch-gate evidence.
triggers:
  - Stripe checkout, payment, subscription, webhook, or test-card matrix work
  - Human Design Engine / deconditioning / sanctuary paid onboarding flows
  - Telegram onboarding links, guest profiles, tenant router, BotInstance, or guest container routing
  - Launch readiness checks where payment success must create a routable conversation lane
---

# Checkout → Onboarding → Routing Ops

Use this when a paid product needs to prove the full customer path, not just a build: **Checkout session created → card flow works → Stripe webhook arrives → user/invitation exists → Telegram start token binds chat → message routes to guest container**.

## Operating Principles

1. **Do not stop at env-file surface checks.** Before declaring Stripe unavailable, inspect all runtime sources safely/redacted:
   - project `.env` and staging `.env`
   - systemd `Environment=` / `EnvironmentFile=` for the active API service
   - published deployment/env snapshots, if present
   - Stripe CLI config, if installed
   - payment/link docs that may hold webhook or price IDs
2. **Never print secrets.** Report prefixes/lengths/status only. Redact `sk_*`, `rk_*`, `whsec_*`, `cs_*`, bot tokens, and HMAC secrets.
3. **Verify key type with Stripe.** A `whsec_...` webhook secret is not an API key; an `mk_...` key is not server-side auth. Validate `sk_test_...` / `rk_test_...` or `sk_live_...` against `/v1/account` before wiring it.
4. **Align code to the intended product model, not the current bad Stripe objects.** If Stripe prices are wrong, create/reuse correct Products/Prices and patch code to use those IDs.
5. **Label verification scope.** Distinguish:
   - canonical build/compile verification
   - ad-hoc endpoint/browser checks
   - Stripe-hosted Checkout/card matrix
   - manual-only SCA/3DS completion
6. **When a system prompt says verification is stale, rerun the relevant command in that turn** (`npm run build`, plus Python compile for changed Python) before claiming success.

## Stripe Checkout Verification Sequence

1. **Discover runtime credentials and service context.**
   - Check active service env (`systemctl show ... --property=Environment,WorkingDirectory,ExecStart,FragmentPath`).
   - Confirm which DB/API/service is actually serving staging.
   - Use redaction in logs and command output.
2. **Validate API key.**
   - Call `GET https://api.stripe.com/v1/account` using the key.
   - Record status, account id, livemode/test mode where available, prefix, and length — never the key.
3. **Verify/create Stripe objects.**
   - Confirm Product/Price names, amount, currency, recurring interval, and livemode.
   - For mixed product models, test Stripe session creation directly before patching app code.
4. **Patch checkout contract if needed.**
   - Support `price_id` for the upfront/primary line.
   - Support `recurring_price_id` for renewal lines.
   - Support `subscription_trial_days` where a paid container includes a delayed renewal.
5. **Run card matrix in test mode.**
   - Success: `4242 4242 4242 4242` → success redirect.
   - Decline: `4000 0000 0000 0002` → expected decline error.
   - SCA: `4000 0025 0000 3155` → hosted 3DS challenge. If headless browser reaches the `three-ds-2-challenge` iframe but cannot complete due to hosted iframe/anti-bot handling, mark as **branch reached, manual completion required in normal browser** — not full SCA success.
6. **Verify webhook and fulfillment.**
   - Prefer Stripe-delivered test webhook evidence after a success card.
   - Also use signed local webhook smoke only for signature-path verification.
   - Confirm `/api/checkout/session?email=...` returns token/deep link and tier flags.

## HDE Deconditioning Product Contract

Current intended model:

- **Solo Sanctuary**: `$29/month` recurring subscription.
- **Sovereign Container**: `$1,500` upfront 6-week container, includes 1 year, then renews at `$29/month` after 365 days.

Implementation pattern:

- Solo Checkout: `mode=subscription`, one recurring monthly price.
- Sovereign Checkout: `mode=subscription`, one upfront one-time line + one monthly recurring renewal line + `subscription_data.trial_period_days=365`.
- `is_premium` gates coach-review / Sovereign handling; it does **not** gate bot entitlement. Solo and Sovereign both get the sanctuary bot.
- Coach-review access requires explicit consent (`coach_review_consent=true`), even for Sovereign.

## Trauma/AuDHD-Safe Onboarding UX Contract

Paid onboarding is not done when checkout works; it is done when a distracted, overwhelmed, or interrupted user can return and see exactly one obvious next step.

1. **Expose one visible step at a time.** The success page should not show Telegram + calendar + support paths simultaneously. Primary visible CTA should be the next action only (for example, `Open Telegram`). Reveal optional follow-up steps only after the first action is taken.
2. **No punitive setup timeouts.** Paid active users should not lose onboarding because an invitation timestamp passed. Use durable/far-future invite timestamps for DB compatibility, but gate by subscription status and token usage rather than a short expiry.
3. **Email the recovery anchor.** After checkout, send a plain-language email containing the same one next step and durable Telegram link so ADHD/interrupted users can resume from inbox. If SMTP is incomplete, log/skip without breaking checkout. When provisioning Gmail/Google Workspace SMTP, normalize app passwords to the 16-character no-space form before writing `.env`; unquoted spaced passwords break shell/env sourcing.
4. **Use calm, non-alarming copy.** Avoid “do not close,” “expires,” “verification failed,” or multi-step instructions. Preferred language: “You’re in,” “Nothing else to figure out right now,” “The link does not expire,” and “come back whenever you need.”
5. **Verify UX as live text, not just source.** Browser/DOM proof should show one primary CTA and no timeout/scary language. For premium/Sovereign, ensure the coaching calendar is hidden until after the Telegram step.

See `references/hde-onboarding-ux-2026-07.md` for the session-specific implementation notes.

## Guest Profile / Telegram Routing Pattern

Use active users + invitation tokens as the source of truth; do **not** pre-bind launch profiles to fake Telegram IDs.

1. Seed `User` rows with:
   - `subscription_status='active'`
   - correct `is_premium`
   - correct `coach_review_consent`
   - container window dates for Sovereign if applicable
2. Create fresh unused `Invitation` rows with meaningful token prefixes and expiry.
3. Do **not** create `BotInstance` rows for launch guests in advance.
4. The tenant router should bind the real tester's Telegram `chat_id` during `/start <token>`:
   - `Invitation.token` → `User`
   - validate active subscription and expiry
   - set `Invitation.is_used=true`
   - create/update `BotInstance.telegram_user_id`
   - provision/wake `guest-hermes-{user_id}`
5. Runtime message routing is:
   - `telegram_user_id` lookup in `bot_instances`
   - resolve `guest-hermes-{user_id}` container IP
   - POST `{"text": ...}` to `/api/message`
   - forward returned `response`, `image_path`, or `pdf_path` back to Telegram.

## Guest Container Model, Egress & PDF Ops (HDE)

The tenant router is a **pure proxy** — it holds no model, skills, or MCP config. All customer-facing behavior (model, skills, MCP, soul) is per-guest-container, so "restart the gateway" never applies a model/config change. Find the config where the container actually reads it.

**Guest config has 4 sources of truth — change all 4 plus the live firewall:**
1. `hd-platform-staging/scripts/guest_hermes_template/` — staging provision template (config.yaml, block_egress.sh, Dockerfile, compose, guest_agent_server.py).
2. `/home/ubuntu/guest_hermes_bot/` — fallback template: the prod repo (`hd-platform/`) has **no** `guest_hermes_template/` dir, so the prod orchestrator falls back to this one (see `TEMPLATE_DIR` in vm_orchestrator.py). Easy to miss.
3. The `config_content` string embedded in `vm_orchestrator.py` (in **both** `hd-platform` and `hd-platform-staging` repos) — regenerates config.yaml at provision time.
4. Live per-user dirs `/home/ubuntu/guest_hermes_bot_{uid}/` (config.yaml, block_egress.sh, .env) + live workspaces `/home/ubuntu/users/guest_{uid}/` (guest_agent_server.py, soul/active_soul).

**Local-model rollout recipe:** replace the hardcoded `model: provider: minimax / default: MiniMax-M3` block with the local llama.cpp provider (`api: http://192.168.1.230:8000/v1`, `api_key: llama-local`, model `local-qwen-27b-q8-fred`, ctx 262144, `request_timeout_seconds: 600`) across all 4 sources + live dirs; patch `build_usage` env defaults in guest_agent_server.py; back everything up (`*.bak-prelocalmodel`). Guest dirs are chowned uid 1000 → edits need `sudo -n`.

**Egress firewall:** each guest's `block_egress.sh` DROPs all RFC1918 (`192.168.0.0/16`, `10.0.0.0/8`, `172.16.0.0/12`) in DOCKER-USER *before* the existing dport-8081 ACCEPT, so guests can never reach LAN services. To expose a LAN endpoint:
- Insert `sudo iptables -I DOCKER-USER -s "$SUBNET" -d <host> -p tcp --dport <port> -j ACCEPT` directly after the existing 8081 ACCEPT line — i.e. after `remove_rule()` is defined (script uses `set -e`; anchoring the insert earlier where `remove_rule` is called before definition aborts it).
- Also insert the same rule live on the host (`subnet` from `docker network inspect hde_private_net`), because running rules predate the script fix.
- Verify from inside: `docker exec guest-hermes-N sh -c 'curl -s http://<host>:<port>/v1/models'`.

**PDF/report 401 signature:** guest chart generation POSTs to the host reports server (`host.docker.internal:8081/api/compute`, `X-API-Key`). `{"error": "Unauthorized", "license": "AGPLv3"}` is an **API-key mismatch, not egress**. Diagnose by comparing (hash/length, never value) the key in the server's *running process* (it holds whatever was in env at process start), the unit file, `.env`, and the guest's `.env`. A service that started before a key rotation keeps 401ing on the stale in-memory key until restarted. Source fix: never hardcode keys in systemd units — use `EnvironmentFile=-<path/.env>` so rotation takes effect on next restart.

**Restart semantics:** guest `config.yaml` is bind-mounted and re-read on **every message** (`hermes -z` spawns a fresh process) → no container restart needed. Long-running code (guest_agent_server.py under uvicorn) → `docker restart guest-hermes-{uid}`.

**Model verification recipe:** `docker logs --since 3m guest-hermes-{uid} | grep "Usage metadata"` shows the provider/model that actually ran — but the ledger default can be stale (hardcoded fallback in `build_usage`), so patch the defaults *and* confirm via the log line. End-to-end proof: POST `{"text": ...}` to the container's `:8000/api/message` and check `usage.provider`/`usage.model` in the response JSON, plus the chart flow returning a real `pdf_path` whose file is a valid PDF on the host workspace.

**Onboarding copy & loop guard (2026-08-19):** the guide-choice greeting must offer two **named** presets (Ember, Mira) plus custom — not an abstract "what name should this space answer to". The ready message asks for name + birth details with an explicit "send them any time later" out. The `awaiting_guide_choice` state must never silently re-prompt forever: a message that isn't a guide name gets one soft re-prompt with an explicit escape ("if this is about something else, just say that and we'll start there"). Note the container is only provisioned *after* a name is chosen, so true free-chat adaptation belongs in the guest prompt/soul, not the router state. Welcome/startup phrasing must be **unique per user** — the pattern is a rotation pool + persisted last-shown dedupe (guest: `FIRST_IMPRESSION_PROMPTS` + `greeting_state.json`; router wake: `somatic_cues.json` 360 cues; router onboarding: `_WELCOME_POOL` + per-chat `_WELCOME_LAST`). Grep for these existing mechanisms before writing new ones — "we planned that in" features usually already exist.

## Guest Chat Quality: Names, Birth Data & Version Drift (HDE)

A customer-facing chart bot's core failure class is **birth data landing under the wrong person**.

- **Dev names in fallbacks**: `details.get("name") or "Michael Gulden"`-style fallbacks in the
  deterministic rails file a nameless chart under a developer test name. `grep` for known dev
  names across guest server files; fallback must be generic-aware (explicit → non-generic
  existing profile name → `"Sanctuary Guest"`, which onboarding migrates to the real name).
- **Third-party merge**: "Add my mother, Rosa Rivera. She was born ..." with no name parser for
  that shape falls back to the user's *default* profile and overwrites the customer's own chart
  with a family member's data, filed `personal`. Guard: `detect_third_party_name(text) ->
  (name, relationship)` before any default-profile write — relation words (family/friends lists)
  + a character-class name collector (capitalized first word; **periods only continue between
  initials**, so sentence periods stop the name), with a self-reference prefix guard
  (`my name is|my chart|for me|here are my...` → None). The safety property: a third party is
  **never** merged into the default profile, and self messages are **never** given a third-party
  name — safety beats recall. Verified 15/15 battery before wiring. Categorization
  (`relationship_type` personal/family/friends/other) is persisted via `write_person_profile`
  into `profile.json` + index (coaching-dashboard-ready) — pass it through, confirm in one human
  line, never a folder dump.
- **Guest server version drift (root-cause class)**: `guest_agent_server.py` is copied at
  provision time with **no auto-upgrade**; a customer on a stale build gets a mis-filed chart —
  not a model or soul problem. Diagnose: diff live guest server file vs template, but
  **line count alone misleads** — diff the feature inventory first (`grep -oE
  "^(class |def |    def |@app\.(get|post|put|delete|websocket)) [A-Za-z_]+"` on each build,
  sort, diff). On the HDE fleet (2026-08-19 full audit) every stale build had an *identical*
  feature inventory to the template — the drift was prompt text (6-7 lines/build), not missing
  subsystems. Safety gate before a blanket overwrite: per-build old-unique lines
  (`diff template live | grep '^>'`) are small and contain no guest-specific identifiers.
  Deploy mechanics: uvicorn serves from the bind-mounted `/workspace`
  (`GUEST_WORKSPACE_PATH=/home/ubuntu/users/guest_{uid}` in `guest_hermes_bot_{uid}/.env`) → host
  swap + `chown 1000:1000` + `docker restart guest-hermes-{uid}` IS the full deploy; no image
  rebuild needed (images are stale, code comes from the mount). Back up per guest
  (`*.bak-<UTCstamp>`), then verify md5 identity vs template + in-container line count + `/docs`
  200. Routing is restart-safe by design: `hde_router` re-resolves container IPs per request
  (docker inspect) and auto-starts stopped containers; confirm with `journalctl -u hde_router`
  (getUpdates 200s, no errors) — an outbound test message is not required for routing proof.
  See `references/hde-guest-chat-quality-name-association-2026-08.md` (fleet-wide sync section)
  for the executed 12-guest matrix, md5s, and the capacity model.
- **Vague input → option menu, never assumption.** Michael's product direction (2026-08-19):
  "Be careful with being too rigid with the rule. Opt for a **constitution** and **selectable
  telegram option menus with two choices and other** if the info is vague instead of assuming and
  breaking things." Behavior = principles the model flexes + two-choice + other menus, not rigid
  intake state machines. Applies to the guest bot (birth-detail/categorization prompts) **and to
  Fred's own workflow** on this platform.
- **Chat-log audit permission granted** (Michael + customers) for fiction/friction hunts; the
  only power user at this stage is Alicia Gouso. Recipe: `users` → `bot_instances` (Postgres
  `hde`) → `/home/ubuntu/users/guest_{uid}/` (`conversation_history.json`, `guest_journal.db`,
  `people/`, `charts/`) + `docker logs`. See the 2026-08-19 cont. reference.

## Router Pitfalls

- SQLite may return datetime columns as offset-naive while application code compares them to timezone-aware UTC. Normalize DB datetimes before expiry comparisons (for example, `as_aware_utc(value)`).
- Keep launch invitation tokens unused until a real Telegram tester claims them. If you need to test routing, use a disposable user/invitation and delete it afterward.
- For router tests without Telegram spam or Docker dependency, monkeypatch/fake:
  - Telegram `sendMessage` client responses
  - orchestrator provision endpoint response
  - container IP resolver
  - guest `/api/message` response
- Restart the active router service after routing code changes and verify it is active.

## Required Evidence Before Reporting Done

- Fresh canonical verification: `npm run build` for frontend/static changes.
- Python compile for changed router/API modules.
- Focused payment/onboarding tests for the exact flow touched; label them as ad hoc targeted verification unless the whole suite ran.
- Secret scan repo-safe files before commit/push, and remove generated caches such as `__pycache__` first so bytecode does not preserve token-like material.
- If the runtime target is a protected or non-prefix branch such as local `staging`, respect branch-prefix governance: keep the verified commit on the runtime branch locally, push a governance-compliant `feature/...` handoff branch if direct staging push is blocked, and record the exact blocker/evidence in Linear.
- If the user explicitly asks to repair staging-governor access, fix the governance layer instead of leaving a feature-branch workaround: ensure `PRISMATIC_ENGINE.yaml` names the real staging branch, make the hook’s staging-governor exception run before branch-prefix validation, and check `git config --show-origin --get core.hooksPath` because a global hooks path can override the repo-local fixed hook.
- For full run-through requests, include actual screenshots of the visible path:
  - product page
  - checkout email modal
  - Stripe hosted Checkout
  - post-payment success/recovery state if applicable
  - final one-step `Open Telegram` success state
- Public onboarding lookup for seeded or fresh paid profiles returns `HTTP 200`, token, deep link, tier flag, and consent flag.
- Direct `session_id` success-page lookup must work after webhook processing; the fallback email path is a recovery anchor, not the expected normal path.
- Disposable router simulation shows:
  - `bot_exists=true`
  - `bot_status=active`
  - `telegram_user_id` bound
  - `invite_used=true`
  - forwarded request to guest `/api/message`
  - Telegram reply payload contains the guest response
  - disposable records cleaned up

## HDE Staging Governor Push Repair Pattern

When HDE launch work is already verified on local `staging` but direct `git push origin staging` is blocked by branch-prefix governance, treat it as a governance contract bug if Fred is configured as staging governor. The durable repair sequence is:

1. Lock and patch `PRISMATIC_ENGINE.yaml` so `staging.branch` is the real branch name (`staging`, not stale `deploy-fresh`).
2. Patch the tracked pre-push hook so the staging-governor branch exception is evaluated **before** generic branch-prefix validation.
3. Install the tracked hook into the active hook path and verify `sha256sum` matches.
4. Check `git config --show-origin --get core.hooksPath`; if it points at a global/profile hook, set repo-local `core.hooksPath=.git/hooks` so Git actually uses the fixed hook.
5. Verify positive and negative cases with a temp verifier: Fred/non-empty `staging` push allowed, no-op staging push allowed, Ned-to-staging blocked, direct `main` push blocked.
6. Push `staging`, then read back `git ls-remote origin refs/heads/staging` equals local `HEAD`.

See `references/hde-staging-governor-push-governance-2026-07.md` for session-specific command details and verifier shape.

## Full Visual Run-through Pitfalls

- If Stripe retrieve logs `response_code=200` but `/api/checkout/session?session_id=...` returns `400 Invalid checkout session` with `Failed to retrieve Stripe session: get`, the failing layer is local Stripe-object access, not Stripe retrieval. Use attribute-safe access for Stripe Session objects instead of assuming `session.get(...)` exists.
- When creating temporary screenshot tooling, keep it as an evidence helper only: store screenshots outside the repo if they are not product assets, remove temporary helper scripts before final verification, then rerun build/compile.
- If the direct success page initially shows the email fallback, verify whether this is a webhook race or a persistent `session_id` lookup bug. After webhook completion, direct `session_id` lookup should show the Telegram CTA without requiring email entry.

## References

- See `references/hde-guest-chat-quality-name-association-2026-08.md` for the 2026-08-19 continuation: name-association bug (dev-name fallbacks + third-party merge), `detect_third_party_name` fix pattern, guest server version drift, unique-phrase rotation inventory, the constitution/option-menu product direction, chat-log audit recipe (Alicia Gouso), and open items.
- See `references/hde-local-model-egress-pdf-rollout-2026-08.md` for the 2026-08-19 local-model rollout across guest containers, the egress firewall exception sequence, the stale-systemd-key PDF 401 fix, and the secret-redaction workarounds for host-side scripting.
- See `references/hde-stripe-guest-routing-2026-07.md` for the session-specific Stripe/test-mode, guest profile, and tenant-router findings that informed this skill.
- See `references/hde-full-run-visual-verification-2026-07.md` for the screenshot evidence pattern and Stripe Session object-access bug found during a full staging run-through.
- See `references/hde-smtp-recovery-email-provisioning-2026-07.md` for provisioning the checkout recovery email path, including Google app-password normalization, service restarts, and send verification.
- See `references/hde-staging-stripe-pr-worktree-closeout-2026-07.md` for the staging-branch + feature-branch governance pattern, generated-cache secret-scan pitfall, and Ned/OpenHumanDesignMCP PR/worktree closeout workflow.
- See `references/hde-staging-governor-push-governance-2026-07.md` for repairing HDE repo governance when Fred, as staging governor, must push the actual `staging` branch: config branch drift, hook ordering, repo-local `core.hooksPath`, allow/block verifier cases, and remote readback.
