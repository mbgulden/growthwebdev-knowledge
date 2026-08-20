# HDE personalized daily transit cron — 2026-07

Use this pattern when Michael asks for recurring personalized Telegram messages to HDE family/beta testers through the shared head bot.

## Trigger

Michael wanted Ruth, Jessica, and Alicia to receive a daily Human Design transit message at 9:00 AM Pacific, catered to their chart and current situation, and to be prompted for more context when the system lacks enough personal situational detail.

## Pattern that worked

1. **Resolve recipients from the HDE DB, not assumptions.** Query `users` by email and then `bot_instances` by `user_id`. The actual Telegram chat id lives on `BotInstance.telegram_user_id`, not `User.telegram_user_id`.
2. **Verify linkability before scheduling.** For each recipient, check: user exists, bot instance is `active`, `telegram_user_id` exists, workspace path exists, and the person profile/chart exists under `/home/ubuntu/users/guest_<id>/people/<slug>/profile.json` and `/charts/personal/<slug>/chart_data.json`.
3. **Build messages from actual chart data.** Use stored Type, Authority, Profile, active gates, guide name, and daily transit gates from the real HDE transit engine. Prefer chart-specific gate hits over generic transit copy.
4. **Prompt for missing live context.** If recent conversation history is absent/stale, include a direct prompt like: `Reply with “today I’m dealing with…” plus one real sentence.` This makes the next day’s message more situational without fabricating context.
5. **Schedule with a narrow send window and idempotent state.** A script-only cron can run every 5 minutes while the script sends only during `09:00–09:14 America/Los_Angeles`, with a per-Pacific-date sent ledger under the Ned profile state directory.
6. **Make script-only cron environment-safe.** Hermes no-agent Python scripts may launch under system Python. If the HDE script needs service dependencies, re-exec into `/home/ubuntu/work/hd-platform/.venv/bin/python3` before importing SQLAlchemy, Redis, Swiss Ephemeris, or HDE modules.
7. **Dry-run before live scheduling.** Run `python3 <script> --dry-run`, redact chat ids in reporting, and inspect generated copy for all recipients before creating/updating cron.
8. **Remove obsolete one-shots.** If a prior one-shot delivery job overlaps the new recurring flow, remove it first so testers do not receive duplicate or conflicting messages.

## Verification shape

- `--dry-run` prints one personalized message per target and does not send.
- Manual cron run outside the 9 AM Pacific window exits successfully with empty stdout.
- Recipient DB check reports `has_telegram_user_id=true`, `bot_status=active`, and `workspace_exists=true` for all intended recipients.
- The script keeps stdout quiet on healthy/out-of-window runs; non-empty stdout is reserved for failures or explicit dry-run output.

## Pitfalls

- Do not use `User.telegram_user_id`; it may be null even after the head bot is linked. Use `BotInstance.telegram_user_id`.
- Do not send “personalized” transits from only Type/Profile. Include at least direct daily transit gates and whether they hit the stored natal active gates.
- Do not invent situational context from family identity or vibes. If current context is thin, ask the tester for one current-life sentence.
- Do not schedule a cron at `9:00` without being explicit about timezone. Use America/Los_Angeles/Pacific for this request.
- Do not let a missing service venv become a recurring false failure. Script-only cron wrappers that depend on HDE runtime packages should self-select the service venv before imports.
