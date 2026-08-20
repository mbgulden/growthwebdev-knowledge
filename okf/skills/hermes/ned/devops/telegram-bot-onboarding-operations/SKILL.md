---
name: telegram-bot-onboarding-operations
description: Diagnose and operate Telegram bot onboarding flows, especially when a bot link opens but /start fails, messages do nothing, or branding/bot identity is confused with backend routing. Covers BotFather identity, Hermes gateways, standalone Python bots, HDE multi-tenant routers, database checks, and safe token handling.
---

# Telegram Bot Onboarding Operations

## When to use

Use this skill when Michael reports that a Telegram bot link, `/start`, or customer onboarding flow failed, especially symptoms like:

- Telegram opens a bot but messages do nothing.
- `/start` returns an application error.
- The displayed bot name/username looks wrong for the product.
- The question is whether to create a new BotFather bot/token.
- Multiple local services may share a bot token or similar names.
- A product router/proxy is involved, e.g. Human Design Engine sanctuary/onboarding.

## Core distinction

Do not collapse these into one thing:

1. **Telegram identity** — BotFather bot display name, username, and token.
2. **Process/service** — systemd service or Python/Hermes gateway currently polling that token.
3. **Application router** — code that handles `/start`, invitation tokens, DB lookup, provisioning, and message proxying.
4. **Backend dependencies** — Postgres/SQLite/Redis/Docker/orchestrator/container runtime.
5. **Brand fit** — whether the bot name/username is right for the customer-facing product.

A new BotFather bot fixes identity/branding and token ownership. It does **not** fix a broken database, router, provisioning service, or invitation-token state.

## Diagnostic sequence

### 1. Identify the Telegram bot actually answering

Use the configured tokens without printing them. Call Telegram `getMe` and report only safe fields:

- `ok`
- `id`
- `username`
- `first_name`

Compare every plausible token source:

- app `.env` files,
- Hermes profile `.env`,
- systemd `EnvironmentFile`,
- router service env,
- standalone bot service env.

Never paste bot tokens. Redact token-shaped strings in logs.

### 2. Identify the process/service using that identity

Check active services/processes for:

- standalone bot process, e.g. `python /path/to/bot.py`,
- Hermes gateway profile, e.g. `hermes --profile ... gateway run`,
- product router/proxy, e.g. `hde_tenant_router.py`,
- overlapping services using the same token.

Important pitfall: a service can be active but not connected to Telegram. For Hermes gateways, inspect `gateway_state.json` and gateway logs for platform state. `systemctl is-active` alone is not proof the bot is reachable.

### 3. Trace the `/start` path in code

Find the exact user-facing error string in source. This usually reveals the layer:

- invalid/used token → invitation lookup branch,
- subscription inactive → user/account branch,
- database connection issue → DB transaction branch,
- setup/provision failed → orchestrator/container branch,
- connection timeout → downstream container/proxy branch.

Read the surrounding code, not only the matched line.

### 4. Check backend dependencies before changing bot identity

For onboarding routers, verify:

- required env vars are set (`DATABASE_URL`, bot token, onboarding username, shared secret),
- DB service is active/listening,
- async/sync DB connection smoke test passes using the same environment as systemd,
- Redis/Docker/orchestrator ports are active if provisioning depends on them,
- invitation/user/bot-instance tables are reachable.

If the DB falls back to a default local Postgres URL and Postgres is down, root cause is backend configuration, not BotFather.

### 5. Answer the BotFather question precisely

Use this framing:

- **Need BotFather now?** Only if the product needs a new public identity/token or the current token is revoked/unowned.
- **Will BotFather fix this error?** Only if logs show invalid token or wrong token. Not if the application error comes after Telegram successfully delivers `/start` to the app.
- **Should product have a dedicated bot?** Usually yes for customer-facing products. Pick a clear display name and username, then wire app env and success/onboarding URLs to it.

## Human-facing report shape

Lead with the real issue in plain English:

```md
🔴 Real issue: <database/router/token/provisioning>, not <user action>.

**What happened**
- You clicked <bot identity>.
- That maps to <service/router>.
- The first error comes from <code branch/layer>.

**Evidence**
- Bot `getMe`: <username/display name>.
- Service: <active/dead/retrying>.
- Backend check: <DB/provisioner/token state>.

**Answer**
- Wrong bot? <yes/no/branding vs operational distinction>.
- Need BotFather? <yes/no and why>.
- Recommended bot name: <if asked>.

**Next Step**
- <one concrete fix in correct order>
```

Do not dump raw logs unless Michael asks. Translate evidence into the decision point: token, database, router, or provisioning.

## Safe commands/patterns

- Redact token-shaped strings: `sed -E 's/[0-9]+:[A-Za-z0-9_-]+/[REDACTED_TOKEN]/g'`.
- Compare bot identities with `getMe` via a small script that prints only safe JSON fields.
- Use the same env as systemd when smoke-testing DB/router code: source the service `EnvironmentFile` or run under equivalent `PYTHONPATH`.
- For Hermes gateways, inspect both `systemctl status` and profile `gateway_state.json` / gateway logs.

## HDE head-bot + personal guide workflow

For Human Design Engine, prefer **one customer-facing Telegram head bot** plus per-user guide/persona state. Telegram cannot make one shared bot display a different BotFather name per user, and per-user BotFather bots create token sprawl. Use this pattern instead:

1. Wire the public token into `HDE_COACH_BOT_TOKEN` and set `HDE_ONBOARDING_BOT_USERNAME` to the username from Telegram `getMe`.
2. Keep the head bot identity neutral/product-level, e.g. `Human Design Companion`.
3. During onboarding, ask the user to choose a guide name/persona such as `Ember`, `Mira`, or custom.
4. Store that choice per user (`guide_name`, `guide_name_source`) and pass it into guest profile/container provisioning.
5. Make chat copy/persona use the chosen guide name while the Telegram header remains the shared public bot.

If Michael pastes a BotFather token in chat, wire it only if explicitly requested, never print it back, and recommend rotating it after verification because pasted bot tokens should be treated as exposed.

## HDE progressive Sanctuary guest runtime

When the HDE guest bot feels rigid, generic, or overwhelming, inspect both the router and the guest container runtime. The desired architecture is not “prompt harder”; it is Soul-led conversation plus deterministic guardrails for structured work.

Use this checklist:

1. Verify the live mounted Soul inside the guest container, not just the template file. It should embody Sanctuary/George, “show, don’t tell,” one-question-at-a-time pacing, and American-facing chart intake.
2. Verify progressive skills are mounted into the guest Hermes profile as inspectable skill files: `collect-birth-details.md`, `deconditioning-coach.md`, `read-hd-context.md`, and `task-atomicizer.md`.
3. Verify generated `config.yaml` still points to MiniMax (`provider: minimax`, `default: MiniMax-M3`); do not overwrite it with stale OpenRouter template config while refreshing runtime files.
4. Put deterministic guest-server shortcuts in front of the LLM for structured flows that must never regress:
   - chart intent asks birth date only,
   - comparison intent asks Person 1 birth date only, then proceeds one field at a time,
   - journal commands write/search/list the journal DB directly.
5. Store chart artifacts where coaches and the router can inspect them: personal charts under `/workspace/charts/personal/`, comparison subjects under `/workspace/charts/friends/person_1/` and `person_2/`, with `chart_data.json` in each subject folder.
6. Treat direct guest API checks as focused ad-hoc verification only. A full live canary still requires Michael or another real tester to message the Telegram bot.

See `references/hde-progressive-sanctuary-runtime-2026-07.md` for the session-specific runtime wiring, verification probes, and pitfalls.

## HDE guide choice and provisioning timeout checks

When Human Design Companion says `Setup Failed` / `contact support` right after guide choice, do not assume the container failed. First check whether the router timed out while the orchestrator continued successfully. Cold guest builds can exceed a short router timeout.

Use this pattern:

1. Check router logs for `VM Orchestrator connection failed` / `ReadTimeout` around `provision_bot_instance`.
2. Check `hde_orchestrator_staging.service` logs for a later `POST /api/orchestrate/provision HTTP/1.1" 200 OK`.
3. Check Docker for the expected `guest-hermes-USER_ID` container and verify it is healthy.
4. Verify `/home/pn/.hermes/SOUL.md` inside the container is a file and has the intended guide name.
5. If the setup actually succeeded, correct the DB state: clean up `users.guide_name` if a natural phrase was stored, set `guide_name_source`, and set the bot instance back to `active` only after router-to-guest proof.
6. Patch/verify the router so natural preset phrases like `Let's do ember`, `use ember`, `pick Ember`, `choose mira`, and `go with mira` resolve to presets, while questions like `what can you do?` are rejected as names.
7. Keep provisioning timeout configurable and long enough for cold builds, e.g. `HDE_ORCHESTRATOR_PROVISION_TIMEOUT_SECONDS` defaulting to `180`.

See `references/hde-guide-choice-provisioning-timeout-2026-07-16.md` for the session-specific root cause, code shape, and verification recipe.

## HDE family/beta test monitor and log triage mode

When Michael has family/siblings/beta testers run the HDE staging checkout + Telegram bot flow, start with a lightweight **health + stuck-state monitor** before any transcript review. This should be an operational cockpit, not surveillance:

1. Verify whether the coaching dashboard exists separately; it may live under canonical `hd-platform` paths while staging serves `/coach/dashboard` from the orchestrator.
2. Build/run a family-test monitor that reports DB/backend status, Redis queue pending counts, Docker guest health, invite usage, Telegram linkage, guide name, bot status, workspace existence, and clear stuck reasons.
3. Separate `waiting` from `stuck`: unused active invitations are usually testers who have not opened the link yet, not failures.
4. Keep raw transcript content out of the default monitor. If transcript review is requested, require explicit tester consent and report summaries/artifact counts by default. Consent should be product-visible in the checkout/success/bot onboarding path, persisted on the user record, and distinguish staging/family improvement review from production customer privacy. For staging/family Solo checkouts, do not gate persistence on premium/sovereign status alone: if metadata includes `family_test_review_consent=true` and `coach_review_consent=true`, the webhook should preserve `coach_review_consent=true` with source `staging_family_test_checkout` so the monitor can distinguish consented testers from ordinary private bot users.
5. Produce a simple HDE-branded tester PDF/HTML with staging signup steps, Stripe sandbox card `4242 4242 4242 4242`, Telegram onboarding steps, guide-name choices, first-conversation prompts, explicit improvement-monitoring consent language, and a feedback checklist.
6. Verify generated monitor/PDF artifacts with a fresh `/tmp/hermes-verify-*` script that checks schema, privacy flags, required tester instructions, and secret-like patterns.
7. For final staging gate checks, use a real Stripe sandbox browser checkout to prove user/invitation/consent DB state, but be explicit about human boundaries: server-side checks can prove deep-link generation, bot identity, guest canary, and PDF generation; only a real phone tap can prove Telegram `/start`, and only an approved browser login can prove Cloudflare Access edge policy.

When Michael asks how specific tester conversations/logs look, do a multi-layer triage instead of only reading `journalctl`:

1. Confirm active services and recent errors for the tester window.
2. Read the **runtime** database URL from the running service env because an `EnvironmentFile` can override the unit’s displayed `DATABASE_URL`; inspect users/invitations/bot_instances for email, premium/consent, guide name, invitation use, Telegram linkage, workspace path, and status.
3. Inspect guest workspace artifacts: `conversation_history.json`, `people/<slug>/profile.json`, `latest_chart_data.json`, `coach_manifest.json`, and chart/report files.
4. QA generated PDFs/images with `pdfinfo`/`pdftotext` and targeted checks for placeholders (`Pending in engine`, `Not returned`), wrong display names, stale profile lines, missing `Gates + Planets`, and suspicious timezone/location labels.
5. Distinguish customer blockers from product-quality gaps: a user can onboard/chat successfully while artifacts remain stale, parser wording is brittle, identity propagation is wrong, or internal premium alerts fail.
6. When a tester is stuck under `Sanctuary Guest` or another generic profile, fix the identity propagation root cause before cosmetic artifact renames: capture explicit self-name statements before LLM fallback, migrate the people profile/index/chart directories to the real slug, update manifests/latest-chart paths, then regenerate media.
7. Treat `timezone: UTC` plus unknown/zero coordinates for a real birthplace as a geocoder failure, not acceptable chart input. Patch the resolver/gazetteer narrowly and regenerate rather than forcing chart mechanics.
8. Report per tester as `what worked` + `gap`, then list already-fixed historical errors separately from live gaps.

See `references/hde-family-test-monitor-and-tester-pdf-2026-07-16.md`, `references/hde-pdf-portal-consent-production-gate-2026-07-16.md`, `references/hde-staging-family-test-gate-2026-07-16.md`, `references/hde-family-tester-log-triage-2026-07.md`, and `references/hde-family-tester-identity-artifact-cleanup-2026-07.md` for the implementation pattern, artifact names, verification recipe, consent gate, tester-log triage workflow, identity/artifact cleanup, and pitfalls.

## HDE coach portal exposure behind Cloudflare Access

When Michael asks to make the coaching customer dashboard browser-accessible, expose the existing staging orchestrator dashboard through `staging.humandesignengine.com/coach/dashboard` rather than inventing a second admin app:

1. Confirm the dashboard exists internally first (`/coach/dashboard` on `hde_orchestrator_staging.service`) and that coach APIs remain consent-gated.
2. Add origin-side Nginx routes for `/coach/dashboard` and `/api/coach/` that require the Cloudflare Access JWT header before proxying to the staging orchestrator.
3. Forward `Cf-Access-Jwt-Assertion` and `Cf-Access-Authenticated-User-Email` to the orchestrator.
4. In the orchestrator, accept either the legacy `COACH_ACCESS_TOKEN` or a Cloudflare Access-authenticated email from an allowlist such as `mbgulden@gmail.com` and `becca.gulden@gmail.com`.
5. Add a session endpoint (`/api/coach/session`) and update the dashboard to try Cloudflare Access auth first, leaving the token prompt as a local fallback.
6. Verify both denial and success paths: no CF header returns `403`; allowed simulated CF headers return dashboard `200` and session `method=cloudflare_access`; disallowed emails return `401`; coach clients returns a JSON list only for allowed auth.

See `references/hde-coach-portal-cloudflare-access-2026-07-16.md` for the Nginx shape, backend auth pattern, verification recipe, and pitfalls. If the user reports the dashboard “doesn’t show up” or “won’t let me log in,” distinguish the HTML shell from protected data APIs: `/coach/dashboard` returning 200 only proves the shell loads. Also test `/api/coach/session` and `/api/coach/clients` in the browser/auth context. If Cloudflare Access is not injecting identity headers, the app should show a clear Access-not-detected/token-fallback state while data APIs remain gated. Do not claim the Zero Trust policy was changed unless a Cloudflare API/dashboard mutation was actually verified; otherwise report the exact policy paths needed. See `references/hde-pdf-portal-consent-production-gate-2026-07-16.md`.

## Scaling checks for shared head bots

For 100+ active users, confirm the architecture has:

- DB shared between checkout/API/router/orchestrator; no accidental fallback to a separate empty DB.
- Router backpressure: bounded async tasks, concurrency semaphore, task timeout.
- Per-user rate/budget controls before model calls.
- Queue separation for chat messages vs container wake/provision jobs.
- A Postgres migration plan for production metadata; SQLite is acceptable for staging but not 1000 actively chatting users.
- Redis or equivalent durable queue before calling the system resilient under burst load.
- For Redis Stream queue health, distinguish retained stream `length` from live backlog: alert primarily on `pending` entries, missing consumers, dependency failures, or very large retention/trim thresholds. A stream length like 121 with `pending=0` and active consumers is history, not a live queue backlog.
- Token/model spend estimates based on average input/output tokens per chat turn, not number of Telegram users alone.

## HDE head-bot watchdog false-alarm triage

When the HDE head-bot router watchdog reports broad dependency failures at once — DB zero users, Redis unknown, Docker unknown, no guest containers — first prove whether the **metrics command/runtime** failed before treating it as an outage. Inspect the cron job and watchdog script, run `scripts/hde_router_metrics.py` directly with the same `PYTHONPATH` and Python path the watchdog uses, then compare against live service state (`hde_router.service`, `hde_orchestrator_staging.service`, Docker `guest-hermes-*`, Redis queue pending/consumers, and DB counts). If services are active but metrics are empty/unknown, repair the metrics runtime/path/dependencies; do not restart live services just to silence a watchdog. Verification requires both a populated forced watchdog run and a normal cron-triggered run with empty stdout. See `references/hde-head-bot-watchdog-runtime-2026-07.md`.

## HDE progressive guest runtime checks

When George/HDE answers with generic, scripted, slow-to-engage, too-long, or overwhelming copy, do not stop at the head-bot/router layer. Inspect the guest template and the live guest container profile. The preferred architecture is **LLM-first conversation + deterministic tools + strict validators**: normal help/greeting/frustration/open conversation should go to the LLM with live profile/chart context, while code owns auth, DB writes, chart generation, journal write/search, rate limits, and Telegram media. Avoid putting rigid menu/profile/chart dialogue in front of the model; static handlers should behave like callable tools or continuation rails for already-pending structured work. For life-pattern or relationship threads, George should bring the relevant Human Design lens in early, not make the user fight through several generic coaching turns first.

Minimum HDE guest behavior to verify:

- Greeting does not ask for birth data, present a menu, overuse loaded/ceremonial words like “honest,” “fair,” “true,” “alive,” or “slice,” or recite internal philosophy. It should embody the Soul: one warm sentence plus one invitation. Use a soft relatable-language bias, not a blacklist: sound like a grounded, perceptive person rather than a mystical app, therapist, or coach performing brand voice. Verify the reset/greeting guard is actually wired before LLM fallback; otherwise MiniMax can still generate loaded first-impression wording despite the prompt rule. When changing this tone, patch future provisioning, router/head-bot copy, current guest `soul.md`/`active_soul.md` surfaces, dynamic `update_soul_profile.py` blocks, and the runtime `guest_agent_server.py` prompt where present; restart current containers after mounted prompt edits.
- Conversation continuity is a hard product requirement. Persist a small local recent-turn history in the guest runtime and inject it into LLM prompts; do not rely only on `hermes -c` continuation, which can lose the immediate thread and produce generic “what do you want?” resets for short replies like “the pump is silent” or “do this.”
- Search access is allowed as a secondary factual lookup tool only. Prefer a direct DDGS/search context injection over broad browser access. Search when the answer depends on current/external facts, exact model/manual/part details, safety/practical verification, or the user explicitly asks to look something up. Do not search for ordinary Sanctuary conversation, Human Design interpretation when MCP/chart data is enough, emotional processing, proving the user wrong, or replacing body authority. When search results are present, answer the factual request first and cite at least one source/title; do not detour into Human Design unless the current user asks for that blend. For `/new`, reset, and repeated simple greetings, use a deterministic rotating first-impression guard before the LLM fallback so George does not recycle the same line; favor simple this/that choice prompts because most guests are likely Generator/MG sacral-response types, while keeping wording usable for non-generators before chart data exists.
- Add a friction interrupt before structured flows: if the user says the bot is painful, rigid, repeating itself, asking again, or blocking them, clear pending state, summarize known profiles/chart status, and ask for the desired outcome rather than forcing the user to continue the wizard.
- The guide runtime prompt should use permission architecture, not a bigger prompt cage, and must not hardcode a specific guide name like George. Use configurable guide identity (`GUEST_GUIDE_NAME`/`HDE_GUIDE_NAME`) plus guide-neutral contract headings: Constitution (never fabricate, fake certainty, override body authority, coerce, leak private data, or claim medical/legal/financial authority), Culture (Sanctuary voice, warm/direct/not syrupy, one clean question by default), Freedoms (improvise, synthesize, reframe, challenge gently, take the swing when invited, offer experiments, choose the next useful move), Graceful Deconditioning + Belief Work (name loops without shame, identify protective beliefs, update them into practical testable working beliefs, and move the user toward needing the guide less), and Tool policy (the guide narrates; server owns mutations/artifacts). Broad pattern asks such as “what am I missing?”, “what belief is underneath this?”, or “how do I decondition this?” should trigger a grounded pattern/belief read when the live thread gives enough context, not a setup wizard. Use uncertainty etiquette: known data, strongest read, working hypothesis, exploration, or unknown. The reusable guest canary should include a static permission-architecture contract check so future prompt edits cannot quietly remove Constitution/Culture/Freedoms, permission-to-improvise, take-the-swing, consentful depth, uncertainty etiquette, graceful belief work/deconditioning, guide-name neutrality, or creative prompt-native tool handles.
- Polyvagal/somatic cues belong in both wake latency and George’s journey language. Keep the cue JSON in the active staging repo (`scripts/somatic_cues.json`) instead of relying on another checkout. Router wake messages should infer a light state from the user text (`sympathetic` wired/urgent/angry, `dorsal` numb/frozen/tired, `ventral` clear/curious/grounded), choose a cue, and strip generator artifacts like `i=17`, `Preparing bot`, or `Activating sanctuary`. George may use the same cue library as prompt-native micro-practices, but should frame state as a working read, never diagnosis, and offer one small orientation/breath/body practice — no woo sludge.
- Missing birth time must never silently become a “better” 12:00 default. Offer three paths: explore likely windows with chart-pattern anchors, build a clearly labeled unknown-time/rough chart, or wait for exact records. Static chart intake should shrink into a slot clipboard: if the initial chart request already includes date/time/location/name, extract and validate those slots, ask only for what is missing, and let deterministic chart generation run once required slots are present. If a stored profile already has complete birth details and the user asks to build/rebuild/generate that chart, George should operate the system and generate it instead of asking “use those details?” Store birth-field confidence (`exact`, `natural-clue`, `approximate`, `explored`, `unknown-placeholder`) in the person profile so future readings can calibrate certainty.
- Personal chart requests collect one field at a time only when slots are truly missing; otherwise use a slot clipboard and operate the system. Name capture must be strict: do not turn ordinary phrases after `for`/`under` into fake profiles. New chart labels should require a real-looking first + last name (or an already stored known single-name profile); if the text has a loose phrase where a name should be, ask for the person’s first and last name or “my chart.” User-facing dates should be `MM/DD/YYYY` or natural language; ISO is internal only. Birth-date intake must accept a wide net: American numeric, ISO for backwards compatibility, month-first English (`June 14, 1990`), day-first English (`14 June 1990`), ordinals (`14th June 1990`), and short surrounding phrases. Birth-time intake must be wide: accept exact times, unknown, dayparts, and natural-light phrases like “around sunrise/dawn/sunset”; resolve sunrise/sunset-style phrases after location is collected instead of rejecting them. Chart responses should include useful interpretive first-read insights (conditioning pressure, reliable centers, profile learning style, one concrete channel/cross clue, best next practical step), not only the stock Type/Strategy/Authority/Profile anchors. Progressive retry prompts should rotate so the guide does not repeat the same line across adjacent turns.
- Comparison requests handle plural/natural phrases like “compare two charts,” then gather Person 1 and Person 2 progressively before summarizing the relationship in ordinary language. If both named/stored profiles are complete (for example “compare me and Becca” or “compare Canary Guest and Canary Friend”), resolve names from the people index, use the stored profiles, regenerate missing chart summaries if needed, compare them, and return plural PDFs instead of asking the user to rebuild or confirm known details.
- Continuity asks are deterministic lookup rails, not user homework. Treat “Do you remember?”, “what did we talk about yesterday?”, and similar cross-session asks as a trigger to search saved journal plus retained recent session history first. Answer from what is actually found, and say plainly when the earlier conversation was not saved/retained instead of asking Michael for a keyword or reconstructing the thread from vibes.
- Coach dashboard endpoints must enforce consent at every read/write path. A coach token alone is not enough: `/api/coach/clients`, `/api/coach/review`, and `/api/coach/update_steps` should all require active premium status, `coach_review_consent=true`, no revoked consent timestamp, and a non-expired coaching window before reading or mutating any `/home/ubuntu/users/...` workspace files.
- Generated charts leave coach-visible artifacts: `chart_data.json`, `coach_manifest.json`, PDFs, and `/workspace/coach_view/events.jsonl` chart/journal events. Birth details must also persist by individual under `/workspace/people/<person_slug>/profile.json` with `birth_input`, latest chart links, and `/workspace/people/index.json` so later chart requests can recall/confirm existing details instead of asking again. If only one profile exists, edit requests like “edit the time” should target that profile automatically; support single-field date/time/location updates without restarting full intake. When a single-field edit leaves a complete profile, rebuild the chart immediately and return PDF metadata instead of asking “want me to rebuild?” Chart mechanics must come from the real Human Design calculation engine/API: never force a profile, line, Type, Authority, or Cross with per-person exception rules or `chart_overrides`; debug birth input, AM/PM, location resolution, timezone/DST conversion, and Personality/Design Sun lines instead. Add deterministic-but-natural workflow navigation before LLM fallback for help/what-can-you-do, what-next, explain-my-chart, rebuild/regenerate, compare stored profiles, journal/search/list journal, edit details, start/update chart, and short report follow-ups like `yes pdf report`; each handler should state what is known, operate available stored details, return media metadata, offer a few useful doors, and ask one next question only when needed.
- HDE report-generation “auth errors” can be LLM fallback/routing failures rather than bad credentials. Before rotating keys, prove guest-to-report auth from inside the affected container with `/api/compute` and the container env key. If direct auth succeeds, add/repair deterministic PDF/report follow-up handling before LLM fallback, recover birth details from stored profiles or recent history, and ensure the running container imports the patched file path. Do not treat PDF size/existence as quality proof: inspect the source HTML, run `pdftotext` for real headings, render pages to PNG for visual QA, and fix renderer/font/emoji/page-flow problems when HTML is correct but PDF text/visual output is bad. Also verify that one-shot birth-detail messages create artifacts, not just LLM summaries: if a tester pastes name/date/time/place in one sentence, the runtime should deterministically generate `chart_data.json`, bodygraph PNG, PDF, coach manifest, and router media metadata before LLM fallback. Accept terse family-test shorthand where the place trails the clock without `in`/`birth place` (for example `August 2 1952 6:46pm Glendale California`); once date/time are parsed, trailing city/state words should become the birth place instead of falling through to LLM-only output. Also handle the multi-turn version: if recent user turns contain birth/chart context with date/time and the current reply is a short city/state such as `Provo, UT`, combine the recent context, treat the current location as authoritative, and run deterministic chart/PDF generation before LLM fallback. Beware parser traps where `parse_birth_time('Provo, UT')` returns `UNKNOWN`; `UNKNOWN` is not a real time and must not block location-only recovery. For new HDE bots, permission failures can masquerade as PDF/runtime issues: the orchestrator must `chown -R 1000:1000` both the user workspace and the per-container base directory because `active_soul.md`/`SOUL.md` are bind-mounted from the base dir into `/home/pn/.hermes` and must remain writable after chart generation. If Michael or a domain expert says a generated chart field is wrong, do **not** force the expected answer with `chart_overrides`; verify the source birth data first (image/OCR if supplied), then debug year/date, AM/PM, local-vs-UTC normalization, geocoding, DST/timezone, and Personality/Design Sun lines until the real engine explains the discrepancy. If reports were generated before a placeholder/geocoder/name fix, regenerate them; stale PDFs remain stale even after code is patched. See `references/hde-report-generation-auth-recovery-2026-07-16.md`, `references/hde-pdf-portal-consent-production-gate-2026-07-16.md`, `references/hde-one-shot-chart-artifact-generation-2026-07.md`, `references/hde-terse-birth-details-profile-override-2026-07.md`, `references/hde-ruth-source-image-year-correction-2026-07.md`, `references/hde-family-tester-identity-artifact-cleanup-2026-07.md`, and `references/hde-location-only-pdf-permission-recovery-2026-07.md`.
- For personalized recurring HDE tester messages such as daily transit briefings, resolve recipients from `users` + `bot_instances` and send to `BotInstance.telegram_user_id`; `User.telegram_user_id` can remain null after linking. Generate copy from actual daily transits plus each stored chart/profile/guide name, include direct gate hits where possible, and explicitly ask for one current-life sentence when recent situational context is thin instead of inventing personalization. Script-only cron senders should be idempotent by Pacific date, run frequently but send only inside the requested America/Los_Angeles window, stay silent on healthy/out-of-window runs, and re-exec into the HDE service venv before importing runtime dependencies. See `references/hde-personalized-daily-transit-cron-2026-07.md`.
- For HDE Stripe/report checkout work, treat checkout URL creation, browser form handoff, and fulfillment as three separate proofs. Inventory every route family and surface first (`src/pages/buy-report.astro`, legacy HTML mirrors, `payment/static/hd-checkout.js`, `payment/server.py`, `api/routes/stripe_webhook.py`, `api/routes/payment.py`, and `reports/server.py`). When lowering report prices, update displayed prices and server-side `unit_amount` together; in staging/test mode prefer `price_data` over stale live Stripe Price IDs so sandbox checkout matches the page. Verify product fulfillment mapping (`natal` -> natal PDF, `transit` -> transit PDF, `synastry` -> relationship PDF, `bundle` -> natal + transit + relationship when partner data exists), generate real PDFs, and browser-smoke at least one staging form click to Stripe sandbox. If Cloudflare Access returns 302 login for public checkout/static routes, report that as a production-readiness blocker rather than calling checkout live. See `references/hde-stripe-report-checkout-cta-proof-2026-07.md`.
- When checkpointing HDE staging for family handoff, durability is not just `git commit` in the staging worktree. Inspect external runtime dependencies too. If the orchestrator provisions guests from `/home/ubuntu/guest_hermes_bot`, snapshot that template into the repo (excluding `.env`, backups, and caches), patch the orchestrator to prefer the repo-local template, ignore regenerated monitor/runtime artifacts, run a `/tmp/hermes-verify-*` verifier, then commit and push the `ned/` branch. See `references/hde-staging-durable-handoff-checkpoint-2026-07-16.md`.
- HDE staging schema drift can look like the user broke onboarding when a second checkout/Telegram conversation exposes stale state. If router logs show `AttributeError` on a user field such as `guide_name`, inspect both DB columns and `shared/database.py`; add missing ORM mappings when the DB already has the columns, restart the router, then inspect the new MainPID logs. If a chat is stuck in `waking` with no matching `guest-hermes-<user_id>` container, reset only that bot instance to `awaiting_guide_choice` so onboarding can resume. See `references/hde-staging-schema-breathing-success-2026-07-16.md`.
- HDE success-page breathing UI must be real box breathing: 4s inhale, 4s hold, 4s exhale, 4s hold. Avoid lumped copy like `Hold... Exhale...`; use phase classes plus smooth cubic-bezier transform/opacity. For mandala assets, remove checkered/white backgrounds by converting edge-connected neutral pixels to alpha 0, use normal blend mode, cache-bust the PNG URL, and verify alpha extrema/corners. See `references/hde-staging-schema-breathing-success-2026-07-16.md`.
- Natal chart/report/bodygraph surfaces should include the full coaching-ready field standard, not just Type/Strategy/Authority/Profile/Cross. Include compact descriptions for Profile, Type, Definition, Environment, View/Perspective, Signature, Variables, Distraction, Strategy, Not-Self Theme, Sense, Trajectory, Authority, Cognition, Motivation, Transference, Determination, Incarnation Cross, Bridging Gates, Melancholy, Fears, Penta Qualities, Genetic Trauma, AstroHD Star Archetype, timing fields, location, and timezone. Add a professional planet+gate activation map (Personality/Design side, Planet, Gate.Line, Center, Gate theme, planet significance) because Becca uses those combinations for deeper coaching calls and education content. Repair mojibake/wrong characters before display; do not preserve corrupted rich-text examples in persistent docs. Guest chart generation must use `calculate_chart_detailed` (not simplified `calculate_chart`) so `chart_data.json` keeps personality/design planet maps; normalize string `defined_channels` into `{gates,name}` dicts before calling `render_bodygraph`. If a known customer has corrected chart fields from an expert, treat the correction as a source-data discrepancy to investigate, not as permission to override mechanics. Preserve the expert/reference chart as evidence in notes if needed, but make chart JSON/PDF agree by fixing the real inputs/calculation path: exact year, date, AM/PM, birthplace, timezone/DST, local→UTC conversion, geocoder, and Personality/Design Sun line calculations. When a user reports `Pending in engine` or similar placeholders in PDFs, do not hide sections or leave tombstones: derive transparent secondary fields from existing engine activations where possible (bridging gates, melancholy, Spleen fear gates, Penta gates, cycle windows) and verify generated HTML plus `pdftotext` output contains no placeholders. See `references/hde-natal-field-standard-2026-07-16.md`, `references/hde-chart-report-split-brain-2026-07-16.md`, `references/hde-ruth-source-image-year-correction-2026-07.md`, and `references/hde-report-pending-engine-field-fill-2026-07.md`.
See `references/hde-real-calculation-discipline-2026-07.md` for the no-exceptions calculation discipline: debug geocoding/timezone/AM-PM/Profile Sun lines and remove `chart_overrides` rather than forcing expected profile results.
- Comparison flows return all generated documents, not just the last chart: the guest API should expose plural `pdf_paths`/`image_paths` while preserving legacy `pdf_path`/`image_path`, and the router should enqueue each unique media path.
- When Michael asks to restore an older/better HDE bodygraph — especially if he mentions Fred, Personality/Design channels, red/black activations, or better colors — search the Fred-era bodygraph branches/commits before rebuilding. Prefer the professional `hd-bodygraph/render-pro.mjs` SVG renderer through `/api/public/bodygraph?format=png` for Telegram previews; keep the local Pillow `image_generator.render_bodygraph()` path as fallback only. Verify by checking SVG Personality/Design tokens/colors and a real PNG conversion, not just file existence. See `references/hde-fred-bodygraph-renderer-recovery-2026-07.md`.
- Canary runs clean up fake chart/journal/coach-view artifacts and transient `conversation_state.json` afterward so live guest context is not poisoned. Prefer the reusable repo canary `python3 scripts/hde_guest_canary.py --guest-id 23 --pretty` for server-side guest-runtime proof before asking Michael for another live Telegram media canary.

See `references/hde-progressive-guest-runtime-wiring-2026-07.md` for the focused verification recipe and artifact expectations.
See `references/hde-llm-first-static-layer-reduction-2026-07.md` for the LLM-first/static-layer reduction pattern: frustration repair interrupt, LLM-managed profile/chart slots, known-state prompt primitive, use-what-you-have behavior, and transcript replay harness.
See `references/hde-george-permission-polyvagal-consent-2026-07.md` for the older George-named permission-architecture pattern, creative prompt-native tool handles, missing-time confidence rules, Polyvagal cue consent, router wake-cue cleanup, and focused ad-hoc verification recipe.
See `references/hde-guide-neutral-deconditioning-runtime-2026-07-15.md` for the follow-up correction: guide-neutral naming, Graceful Deconditioning + Belief Work, the `belief_work` prompt-native tool, canary contract coverage, and OKF/HDE documentation destinations.
See `references/hde-live-launch-gap-2026-07-15.md` for the HDE go-live gap audit pattern: server-side runtime proof, router/queue health, safe Telegram identity check, public conversion path checks, live Telegram media watcher, and launch hygiene.
See `references/hde-launch-report-refresh-2026-07.md` for the launch-report refresh pattern: supersede stale RED reports with dated JSON/Markdown evidence, keep reports YELLOW while live Telegram proof is pending, handle deploy-fresh branch-shape caveats, and verify report artifacts/secrets with a `/tmp/hermes-verify-*` script when Hermes asks for fresh proof.
See `references/hde-live-canary-postgres-soul-fixes-2026-07.md` for the final live-proof-to-GREEN pattern: widen the watcher `--since` window when needed, verify two redacted `sendDocument` 200 calls, ensure queues drain, and only then mark the launch report GREEN.
See `references/hde-guide-choice-provisioning-timeout-2026-07-16.md` for the guide-choice preset parsing and cold-provisioning timeout pitfall that can produce a false “contact support” message even when the orchestrator later succeeds.
See `references/hde-controlled-public-traffic-2026-07-15.md` for the post-GREEN controlled public traffic ramp: verify services/metrics/identity/canary/watchdogs/backups, create PROCEED/HOLD rollout artifacts, define 3–5 user cohort gates, and keep rollback criteria explicit.

See `references/hde-phase1-phase2-staging-funnel-fix-2026-07-15.md` for the HDE Phase 1/2 staging funnel fix pattern: canonical staging `/deconditioning/` route, staging Stripe `price_data` fallback instead of live Price IDs with test keys, checkout router mounting, route/API/browser handoff proof, and mechanical/OCR PDF QA fallback.
See `references/hde-phase3-phase4-paid-onboarding-proof-2026-07-15.md` for the Phase 3/4 paid onboarding proof pattern: Stripe test checkout completion, webhook/user/invitation verification, success-page Telegram deep-link redaction, human `/start` proof boundary, paid bot quality canary, coach consent gate checks, and controlled-staging PDF proof labeling.
See `references/hde-phase3-stripe-telegram-proof-2026-07-15.md` for the HDE Phase 3 proof pattern: real Stripe test checkout completion, signed webhook replay when automatic delivery previously failed, user/invitation/success-link checks, consent-field schema drift fix, report status rules, and the human Telegram `/start` gate before GREEN.
See `references/hde-name-capture-chart-insights-router-markdown-2026-07.md` for the strict name-capture fix, richer chart insight layer, natural profile-edit regression, canary profile-pollution guard, and Telegram Markdown parse fallback.
See `references/hde-dirty-staging-checkpoint-2026-07.md` for the HDE dirty staging checkpoint pattern: safe `ned/` branch, staged secret scan, excluding `.env` backups/runtime state, verification before commit, and bundle fallback when lane guard blocks push.
For post-launch-report cleanup, pair this with `worktree-hygiene-and-cleanup-safety/references/2026-07-hde-workspace-branch-cleanup.md`: archive ambiguous/runtime artifacts, move secret `.env` backups to a private archive, prune only local superseded branches, leave remote review branches intact, and commit a workflow map so app/docs/site readers can find the launch report, runbooks, router, canary, media watcher, and coach gate.
See `references/hde-comparison-multi-pdf-telegram-2026-07.md` for the comparison multi-PDF Telegram delivery pitfall and verification recipe.
See `references/hde-first-impression-rotation-2026-07.md` for the `/new`/greeting repetition pitfall, this/that prompt pattern, and verification recipe.
See `references/hde-relatable-language-soft-bias-2026-07.md` for the Sanctuary relatable-language pattern: soft style bias instead of hard blacklist, patch future provisioning plus current live guest prompt surfaces, restart containers, and verify old anchor phrases are gone.

## Rogue external poller on a shared bot token ("terminated by other getUpdates request")

When a Hermes gateway's Telegram adapter logs repeated `polling conflict ... terminated by other getUpdates request; make sure that only one bot instance is running`, another process somewhere is polling the same bot token. This is a *shared-token* problem, often off-host — not a local one.

### Diagnostic sequence
1. **Confirm it's live, not stale**: `grep -c "polling conflict" <gateway log>` at two timestamps ~60s apart. Delta > 0 = actively contended.
2. **Rule out local pollers** before assuming off-host:
   - `ss -tnp | grep -E "149.154|185.73"` → every ESTAB to Telegram; map each pid to `ps -o args` + `readlink /proc/<pid>/cwd`.
   - For each candidate pid, `tr '\0' '\n' < /proc/<pid>/environ | grep TELEGRAM_BOT_TOKEN` and compare token *prefixes* (first ~6 chars) against the victim bot. Standalone bots in `~/work/next-step-*`/`beyondsaas-bot` usually carry their own distinct tokens — not the culprit.
   - Scan Docker: for each running container, check whether its `env` carries the victim token prefix.
   - Scan config files for the full token — OpenClaw-style agents store the token in a *config file*, not an env var: `grep -rl '<full token>' <profile dirs> <work dirs>` (scope to likely trees; a whole-home grep can time out).
3. **If no local process holds the token, it's off-host.** Correlate with which Tailscale/LAN peer is actually up and talking (`tailscale ping`, direct LAN reachability).

### Fix (when you can't reach the rogue host)
- **Rotate the victim to a new BotFather bot/token** and repoint the gateway + every profile that shares it. This is the fast unblock: the rogue keeps polling the now-orphaned old bot and can no longer contend the live one.
- **Then scrub the old token from every profile/script that still carries it** — otherwise starting any of those gateways re-ignites the conflict. `grep -rl '<old token prefix>' ~/.hermes/profiles/*/` scoped to `.env` + `config.yaml` (a whole-tree grep over big profiles can time out).
- **Killing the rogue at the source** (the real fix) usually needs RDP/PowerShell on a Windows box or shell access the firewall denies; report it as a follow-up, not a blocker, once rotation unblocks the live bot.
- **Fleet prune after rotation:** Michael usually follows up with "delete the unused profiles". Audit before deleting — identity symlinks (e.g. `fred -> orchestrator`), prismatic bus workers, and ops scripts may reference them. Use the `hermes-profile-audit-and-prune` skill (class-level procedure + session detail in its references/).

### Pitfalls
- Token rotation does **not** stop the rogue poller — it just orphans its target. The rogue keeps hammering `getUpdates` for a bot that serves nothing; harmless, but it will ambush any profile left on the old token.
- `systemctl is-active` = `active` does **not** mean the gateway won the poll — it may be stuck in a 20s retry loop. Only a zero conflict delta over a real window proves the session is clean.
- A Hermes profile that is a **symlink** to another profile (e.g. `profiles/fred -> profiles/orchestrator`) shares that profile's token *and* `gateway.lock`; starting its own gateway unit recreates the exact contention + lock collision. A profile needs a real dir + its own token before it can run its own gateway.

## Pitfalls

- Do not tell Michael to create a new bot before proving whether the current failure is token identity or backend state.
- Do not treat bot display name as proof of which service handled the message.
- Do not restart or swap customer-facing bot tokens without preserving the old env and explaining impact.
- Do not print tokens, webhook URLs containing tokens, connection strings, or secrets.
- Do not call a bot “working” because `getUpdates` returns 200; the application handler may still be failing after receiving updates.
- Do not claim a real Telegram customer canary is complete from server-side checks alone. Bots cannot send `/start` to themselves through the Bot API; require a real tester/user to tap the deep link and send a canary message, while a watcher verifies invitation usage and Telegram user linkage in DB.
- When Michael asks to “apply as many fixes as you can” before the human tap exists, run a bounded server-side walkthrough instead of stalling: create a staging demo, pass its `hde_demo_` token into the router’s `/start` handler with mocked Telegram sends, select a guide, let the real orchestrator provision Docker, inspect the generated guest `.env`/workspace/container state, then safely simulate paid upgrade continuity without completing Stripe payment. Label this as server-side proof, not human Telegram proof.
- Do not redesign HDE onboarding/payment/email/PDF surfaces against production/live styling when the goal names staging. Treat `staging.humandesignengine.com/deconditioning/` as the source of truth for staging launch work, extract its actual style tokens, and keep production/source services untouched unless explicitly asked. Before restarting or claiming a staging workflow is live, inspect systemd `WorkingDirectory`/`ExecStart`; `hde-payment.service` or `hde-reports.service` may point at `/home/ubuntu/work/hd-platform` rather than `/home/ubuntu/work/hd-platform-staging`.
- Do not confuse a Hermes profile gateway with a standalone product bot if both reference the same token/branding.
- Do not claim 1000-user readiness from an in-process semaphore alone; report it as first-layer backpressure until Postgres, Redis queues, rate limits, and load tests exist.
- For HDE head-bot scaling work, treat the real `POSTGRES_DATABASE_URL` as a hard cutover boundary. Build/rehearse migration tooling with ephemeral Postgres if needed, but do not silently invent credentials or repoint live services without the actual intended target and an explicit smoke-test window.
- When refreshing HDE guest runtime files, do not overwrite a working generated `config.yaml` with the stale generic template (`openrouter`/`gpt-4o-mini`/empty providers). Existing guest containers need the orchestrator-generated MiniMax config (`provider: minimax`, `default: MiniMax-M3`) plus the MiniMax env key, or Hermes returns “No LLM provider configured.”
- For HDE chart canaries, clean up fake guest artifacts afterward: remove test `charts/personal` outputs, delete test journal rows, clear `conversation_state.json`, reset `active_soul.md` to the user’s real base Soul, and archive Hermes sessions so the fake chart context does not poison the live guest persona.
- For HDE comparison canaries, do not stop after seeing one Telegram `sendDocument 200 OK`; comparison should upload both generated PDFs. Verify `pdf_paths` has two entries and router media upload handles plural paths without duplicate sends.

## References

- `references/hde-sanctuary-jeff-sage-debug-2026-07.md` — HDE sanctuary debugging pattern: Jeff/TheNextNextStepBot was answering via the HDE router, but onboarding failed because DB configuration/listener was missing; BotFather would fix branding, not the DB failure.
- `references/hde-head-bot-scaling-2026-07.md` — Head-bot wiring, per-user guide naming, and 1000-user scaling notes including MiniMax cost-estimation pattern.
- `references/hde-live-canary-postgres-soul-fixes-2026-07.md` — Live canary postmortem after Postgres cutover: duplicate Telegram user linkage, Docker-created `SOUL.md` directory/persona fallback, staging orchestrator port mismatch, and verification recipe.
