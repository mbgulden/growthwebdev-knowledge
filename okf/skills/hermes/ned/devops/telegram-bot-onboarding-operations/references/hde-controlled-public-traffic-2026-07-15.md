# HDE controlled public bot traffic ramp — 2026-07-15

## When this applies

Use this pattern after HDE has a GREEN launch report and live Telegram proof, but before opening broad public bot traffic. The goal is to move from “verified live proof” to a controlled cohort without losing observability or rollback discipline.

## Required evidence before PROCEED

Freshly verify and record:

- `hde_router.service` is `active`.
- `hde_api_staging.service` is `active` or explicitly not applicable.
- `guest-hermes-<id>` is `healthy`.
- `scripts/hde_router_metrics.py --pretty` returns `status: ok`.
- Redis stream **pending** counts for chat/media/wake are `0` or clearly draining.
- Telegram identity from safe `getMe` fields is the expected public bot, e.g. `@Humandesigncompanionbot`; never print the token.
- `scripts/hde_guest_canary.py --guest-id <id> --pretty` passes.
- The launch report says `GREEN` and live Telegram media proof says `pass`.
- HDE router watchdog, Postgres daily backup, and backup watchdog cron jobs are enabled and `last_status: ok`.
- A recent Postgres backup exists.
- Recent router logs have no critical errors after redaction.

## Report artifacts

Create dated report artifacts under `reports/`, for example:

- `reports/hde_controlled_public_bot_traffic_YYYYMMDD.md`
- `reports/hde_controlled_public_bot_traffic_YYYYMMDD.json`

Include:

- timestamp, branch, and commit checked;
- launch report link/status and live-proof status;
- service health;
- router metrics summary including Redis pending counts and consumers;
- Telegram identity summary with token redacted;
- guest canary result;
- watchdog/backup status and latest backup metadata;
- proposed cohort size;
- rollout gates;
- hold conditions;
- rollback criteria;
- monitoring commands;
- remaining risks;
- recommendation: `PROCEED` or `HOLD`.

## Controlled traffic posture

Use a conservative ramp:

1. **Phase 0:** Michael/internal testers only.
2. **Phase 1:** 3–5 external users.
3. **Phase 2:** broader public traffic only after Phase 1 completes without backlog, failed sends, unhealthy containers, restart loops, onboarding failures, or spend anomalies.

Do not treat GREEN launch proof as permission to broadcast broadly. GREEN means the door opens; it does not mean stampede.

## Hold / rollback criteria

Hold or stop adding users if any of these appear:

- router/API service down or restart-looping;
- guest container unhealthy;
- Redis pending backlog grows and does not drain;
- Telegram sends fail;
- wrong Telegram identity/token appears wired;
- DB connection errors;
- onboarding/invitation errors for test users;
- backup watchdog reports stale/missing backups;
- unexpected token/model spend spike.

Rollback posture:

1. Stop adding new users/invitations.
2. Keep existing sessions available if safe.
3. Capture redacted logs and router metrics.
4. Pause/disable public entry links rather than deleting data.
5. Do not rotate bot tokens or restart broad infrastructure without explicit approval unless service is already down and the safe fix is narrow/documented.

## Verification pattern

Before commit:

```bash
/home/ubuntu/work/hd-platform/.venv/bin/python3 -m py_compile scripts/hde_router_metrics.py scripts/hde_guest_canary.py scripts/hde_telegram_media_watch.py
python3 scripts/hde_guest_canary.py --guest-id 23 --pretty
systemctl is-active hde_router.service
sudo docker inspect -f '{{.State.Health.Status}}' guest-hermes-23
git diff --cached --check
```

Run a staged secret scan for token/API-key/DB-URL/Redis-URL shaped content. For report-only changes, also create a `/tmp/hermes-verify-*` artifact verifier that parses the JSON and Markdown, checks the PROCEED/HOLD semantics, validates the required evidence fields, scans for secret-shaped strings, runs it, and removes it. Report this as ad-hoc artifact verification, not suite green.

## Pitfalls

- Do not call controlled traffic “public launch complete”; it is a staged ramp.
- Do not ignore watchdog/backups just because runtime checks are green.
- Do not confuse Redis Stream `length` with live backlog; alert/ramp decisions should focus on `pending` counts, consumers, dependency failures, and sustained growth.
- Do not include raw Telegram logs or bot tokens in reports; use redacted evidence only.
- Do not claim frontend readiness from this HDE runtime branch when `package.json` is absent; keep it as a branch-shape caveat and verify frontend-bearing checkouts separately.
