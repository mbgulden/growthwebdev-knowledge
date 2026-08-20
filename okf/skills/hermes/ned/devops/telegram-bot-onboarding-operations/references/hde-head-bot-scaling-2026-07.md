# HDE Head Bot + Scaling Notes — 2026-07

## Durable pattern

Use one public Telegram head bot for Human Design Engine customers, then store per-user guide/persona state in the HDE database. Telegram's UI shows one BotFather display name/username for the bot; it cannot dynamically show a different official bot name per user. Per-user bot tokens are technically possible but should not be the default because they create token sprawl, webhook/polling lifecycle complexity, and support risk.

Recommended product shape:

```text
Human Design Companion Telegram bot
  -> HDE tenant router
  -> DB lookup by telegram_user_id
  -> BotInstance / guest profile
  -> guest Hermes container /api/message
  -> reply through same head bot
```

Inside the chat, ask the user to choose:

1. Ember
2. Mira
3. Custom guide name

Store the choice as user/account metadata, e.g. `guide_name` and `guide_name_source`, then pass it to guest provisioning so the guest soul prompt says it is the chosen guide inside that user's private companion space.

## Token-handling lesson

If Michael pastes a BotFather token and explicitly asks to wire it:

- Do not print it back.
- Use it only through env/config update paths.
- Verify identity with Telegram `getMe`, printing only safe fields: `ok`, `id`, `username`, `first_name`.
- Recommend rotation after verification because pasted bot tokens should be treated as exposed.

## DB lesson

In the HDE staging session, the router initially failed because it lacked an explicit `DATABASE_URL` and fell back to default local Postgres. The staging API/payment flow used the real SQLite staging DB with users/invitations. The correct repair was to point the router at the same DB as the API, not to create a new empty Postgres shadow DB.

Before claiming onboarding is fixed, verify under the same environment as systemd:

- `select 1`
- DB path/scheme is the intended shared DB
- active user count
- unused invitation count
- invitation lookup with joined user
- generated deep link uses the intended head bot username
- router service is active and polling the intended token

## First-layer backpressure

For a shared Telegram head bot, add in-process protections before durable queue work:

- async semaphore for max in-flight chat/onboarding tasks,
- bounded task queue limit,
- per-task timeout,
- larger but finite HTTP connection pool,
- safe drop/degrade behavior when overloaded.

Next layer implemented in the staging workflow: Redis-backed token buckets via `scripts/hde_rate_limits.py`, wired into `scripts/hde_tenant_router.py`. Relevant env knobs:

```text
HDE_REDIS_URL=redis://127.0.0.1:6379/0
HDE_ROUTER_PER_USER_MESSAGES_PER_MINUTE=12
HDE_ROUTER_GLOBAL_MESSAGES_PER_SECOND=150
HDE_ROUTER_MAX_CONCURRENT_CHATS=1000
HDE_ROUTER_TASK_QUEUE_LIMIT=5000
HDE_ROUTER_CHAT_TIMEOUT_SECONDS=45
```

Redis token buckets are rate controls, not a full durable work queue. Next concrete staging layer added `scripts/hde_job_queue.py` using Redis Streams/consumer groups and `HDE_ROUTER_USE_REDIS_QUEUE=true`. The queue was then split into `hde:router:chat-jobs` and `hde:router:wake-jobs` with separate worker pools, so onboarding/provision work cannot starve normal chat delivery. Wake-on-chat was also extracted: sleeping/stopped containers now enqueue a `wake` job and re-enqueue the original message after activation instead of blocking a chat worker. Do not call 1000-user readiness complete until production metadata is actually cut over to Postgres and load testing passes. Guest agent server templates emit standardized estimated `usage`/`model_usage` metadata on `/api/message`; the router reconciles those fields into Redis budgets. Router Redis Streams are split into chat, wake/provision, and media-upload lanes (`hde:router:chat-jobs`, `hde:router:wake-jobs`, `hde:router:media-jobs`). HDE staging metadata has been cut over from SQLite to local self-hosted PostgreSQL 16 (`127.0.0.1:5432/hde`, app role `hde_app`; connection secret only in env/private file). `scripts/hde_postgres_migration.py` exports/imports/verifies metadata tables (`users`, `api_keys`, `usage_logs`, `invitations`, `bot_instances`); `scripts/hde_postgres_cutover.py` performed guarded migration/env backup/service restart; `scripts/hde_postgres_smoke.py` verifies DB counts, checkout deep-link, expected head-bot username, safe Telegram getMe, and service activity. Latest cutover verified row parity (`users=23`, `invitations=32`, `bot_instances=1`, no mismatches), metrics backend=postgres, queues pending=0. Backups use `/home/ubuntu/.hermes/profiles/ned/scripts/hde_postgres_backup.py` with daily cron `de96b1a3f144` and quiet watchdog `7244203a53a0`; restore verifier passed. Live canary fixes: router must reassign a Telegram chat ID from an older test `bot_instances` row before inserting a new one, otherwise Postgres unique constraint `ix_bot_instances_telegram_user_id` produces the user-facing “Database connection issue”; router should use `ORCHESTRATOR_URL=http://127.0.0.1:8011` for staging; vm orchestrator must copy `soul.md` and `active_soul.md` into the per-container base dir, removing Docker-created directories first, or Hermes falls back to the stock persona. `scripts/hde_load_harness.py` exercises isolated Redis Streams for 1000-user synthetic queue fan-in without Telegram/MiniMax/live guest calls, and supports `--mock-guest-http` to route chat jobs through a local mock `/api/message` server with usage metadata reconciliation under controlled latency; use it before any live load test. `scripts/hde_router_metrics.py` snapshots DB counts/backend, Redis queue length/pending/consumers, rate/budget key counts, and guest container health in JSON or Prometheus text without printing secrets. Important import-order pitfall: scripts that import `shared.database` must load `.env` first because the SQLAlchemy engine/session factory bind at import time; otherwise metrics/probes can silently use a stale default DB URL even after cutover. Ned cron job `HDE head-bot router watchdog` runs `~/.hermes/profiles/ned/scripts/hde_router_metrics_watchdog.py` every 5 minutes and stays silent unless Redis/DB/Docker/queue health crosses thresholds. For Hermes `cronjob(no_agent=True)`, put arguments in a wrapper script (`hde_postgres_backup_daily.py`, `hde_postgres_backup_watchdog.py`); the `script` field is a script path, not a shell command with argv. Upgrade later to exact provider accounting when Hermes/MiniMax exposes authoritative input/output token counts.

## Live customer canary pattern

A real checkout → deep link → Telegram `/start` → guest chat reply canary cannot be fully simulated through the Telegram Bot API because bots cannot impersonate users or send `/start` to themselves. The safe pattern is:

1. Preflight metrics: Postgres backend, Redis ok, all queue pending counts `0`, router config sane, guest containers visible.
2. Generate or select a real unused invitation via `/api/checkout/session?email=...` and verify the deep link points to `https://t.me/Humandesigncompanionbot?start=<token>`.
3. Start a temporary watcher that polls Postgres for the selected invitation changing to `is_used=true` and `bot_instances.telegram_user_id` becoming non-null. The watcher may run in a background process and should print only token prefixes or redacted state.
4. Ask Michael/the tester to tap the deep link in Telegram and send a fixed canary message such as `Canary: give me one short grounding reflection.`
5. After watcher success, verify router logs show successful `getUpdates`, queue depths return to `0`, the guest reply was observed by the tester, and `scripts/hde_router_metrics.py --pretty` remains `status=ok` with `database.backend=postgres`.

Do not call the final canary complete at the checkout/deep-link stage; stop at Partial if the real Telegram user action has not happened yet.

## Production scaling checklist

For 1000 actively chatting users:

1. Move production metadata off SQLite to Postgres.
2. Add Redis-backed queues for chat jobs and wake/provision jobs.
3. Add per-user fairness: one active model request per user; coalesce or queue later messages.
4. Add global token buckets by minute/hour/day.
5. Add monthly token/message budgets by subscription tier.
6. Separate container wake/provision concurrency from chat-message concurrency.
7. Add circuit breakers around MiniMax/API calls.
8. Track p95/p99 latency, queue depth, active tasks, failed wakeups, and token spend per minute.
9. Load-test with synthetic Telegram-like updates before marketing heavy traffic.

## MiniMax cost-estimation pattern

Official docs observed in-session:

- Token Plan: Plus $20/mo, Max $50/mo, Ultra $120/mo.
- Docs show rolling 5-hour and weekly quota windows and agent-usage guidance, not exact public monthly token quantities.
- Pay-as-you-go pricing visible in docs:
  - MiniMax-M3 <=512k input: $0.30/M input and $1.20/M output after permanent 50% discount.
  - MiniMax-M3 >512k input: $0.60/M input and $2.40/M output after discount.
  - MiniMax-M2.7: $0.30/M input and $1.20/M output.
  - MiniMax-M2.7-highspeed: $0.60/M input and $2.40/M output.
- Third-party/search snippets gave estimates for M2 and M2.5; label these as estimates and verify in MiniMax console/docs before committing production pricing.

Useful planning formula:

```text
cost_per_turn = input_tokens/1_000_000 * input_price + output_tokens/1_000_000 * output_price
turns_per_budget = monthly_budget / cost_per_turn
users_supported = turns_per_budget / average_turns_per_user_per_month
```

Example assumption from the session: a normal HDE turn is ~3k input + 700 output. At M3/M2.7 standard paygo rates that is about $0.00174/turn, so a $50 budget is about 28.7k turns/month or ~287 users at 100 turns/user/month. Treat this as a planning estimate, not a provider quota guarantee.
