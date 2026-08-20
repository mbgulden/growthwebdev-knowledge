# HDE live canary fixes after Postgres cutover — 2026-07

## Trigger

After HDE staging metadata moved to local Postgres and the Human Design Companion token was rotated, the real Telegram canary still failed:

- `/start <token>` returned user-facing `❌ Error: Database connection issue. Please try again.`
- A normal question returned the stock Hermes Agent self-description instead of the Human Design Companion / chosen guide persona.

## Root causes

### 1. Duplicate Telegram user linkage after Postgres cutover

Postgres enforced `bot_instances.telegram_user_id` uniqueness. The tester's Telegram chat ID was already linked to an older test `bot_instances` row. A new `/start` invite tried to insert/link the same `telegram_user_id` to a new user and raised:

```text
UniqueViolationError: duplicate key value violates unique constraint "ix_bot_instances_telegram_user_id"
```

The router caught the DB exception and surfaced the misleading generic database message.

Durable fix pattern:

1. In `/start` processing, look up any existing `BotInstance` by `telegram_user_id == chat_id` before inserting/updating the invited user's bot instance.
2. If the existing row belongs to another user, clear that old row's `telegram_user_id` before assigning the chat ID to the new invited user.
3. Commit the old unlink, new link, `status='awaiting_guide_choice'`, and `invitation.is_used=True` in one transaction.

This is especially important for staging/canary flows where Michael reuses the same Telegram account across many invite tokens.

### 2. Guest Soul file mounted as a directory

The guest container answered as stock Hermes Agent because `/home/pn/.hermes/SOUL.md` inside the container was a directory, not a file. Docker created the directory when the compose bind source was missing.

The orchestrator was writing `soul.md` / `active_soul.md` under the workspace directory, while `docker-compose.guest.yml` mounted these paths from the per-container base directory:

```yaml
./soul.md:/home/pn/.hermes/SOUL.base.md:ro
./active_soul.md:/home/pn/.hermes/SOUL.md
```

Durable fix pattern:

1. Generate `soul.md` and `active_soul.md` in the guest workspace for human inspection.
2. Also copy both files into the per-container compose/base directory before `docker compose up`.
3. If the target path in the base directory is already a directory, remove it first. Docker may have created it during an earlier bad mount.
4. Verify inside the running container:

```bash
sudo docker exec guest-hermes-USER_ID sh -lc '
  test -f /home/pn/.hermes/SOUL.md &&
  ! test -d /home/pn/.hermes/SOUL.md &&
  sed -n "1,12p" /home/pn/.hermes/SOUL.md
'
```

Expected canary phrase for an Ember guide:

```text
# Ember — Human Design Companion Soul
You are Ember, the user's chosen Human Design Companion.
```

### 3. Staging router used wrong orchestrator port

Staging `hde_orchestrator_staging.service` listened on port `8011`, but router provisioning had a hardcoded `http://HOST:8001/api/orchestrate/provision`. That can call an older/non-staging orchestrator and provision with stale code/templates.

Durable fix pattern:

- Add `ORCHESTRATOR_URL` to the HDE env, e.g. `http://127.0.0.1:8011` for staging.
- Router provisioning and wake/start paths should use `ORCHESTRATOR_URL.rstrip('/') + '/api/orchestrate/provision'` rather than hardcoded `:8001`.

### 4. Normal chat interpreted as custom guide name

If status is `awaiting_guide_choice`, broad custom-name parsing can treat messages like `what can you do?` as the guide name. Tighten custom names so ordinary questions/full sentences return no guide name and re-prompt.

Suggested guard:

- Preserve presets: `Ember`, `Mira`, `1`, `2`.
- Preserve explicit custom trigger: `custom`, `choose my own`, etc.
- Reject raw text containing `?` or more than 3 words as an implicit custom guide name.

## Product voice follow-up

If the first real guest reply is an overwhelming wall of text, check guest logs for the exact response and patch the guest Soul/product voice contract. For HDE, greetings must be low-pressure: one warm sentence plus one gentle invitation; do not ask for birth date/time/location unless the user explicitly asks for a chart, reading, report, or calculation. Michael corrected that the product should be framed as Human Design Engine Sanctuary, not a fake companion or validation loop. It should provide a kind-but-backed practice space for real healing/change, help the user become strong enough to carry sanctuary internally, and never reward complacency or apathy. If the user wants to call the space/voice `George`, accept it as a working handle; do not resist with “I’m Ember.” After changing the Soul, archive/reset the guest Hermes session directory so `hermes -c` does not continue a bad prior session with the old style.

## Verification recipe

After fixing:

1. Compile:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 -m py_compile \
  scripts/hde_tenant_router.py scripts/vm_orchestrator.py
```

2. Restart affected services:

```bash
sudo systemctl restart hde_orchestrator_staging.service
sudo systemctl restart hde_router.service
```

3. Verify services:

```bash
systemctl is-active hde_orchestrator_staging.service hde_router.service
```

4. Verify guest Soul file inside the canary container (see command above).

5. Verify router-to-guest response, not only direct container response. The router must resolve the guest container IP and POST to `/api/message` successfully.

6. Verify metrics:

```bash
PYTHONPATH=/home/ubuntu/work/hd-platform-staging:/home/ubuntu/work/hd-platform-staging/scripts \
  /home/ubuntu/work/hd-platform/.venv/bin/python3 \
  scripts/hde_router_metrics.py --pretty
```

Expected:

```text
database.backend = postgres
Redis ok = true
chat/wake/media pending = 0
```

7. Run canonical build after code/docs edits:

```bash
cd /home/ubuntu/work/hd-platform-staging
npm run build
```

## Pitfalls

- `getUpdates` 200 only proves Telegram polling works. It does not prove `/start` DB mutation or guest routing works.
- Directly calling a guest container proves the guest can answer, but not that the head bot routes to the correct guest.
- If Docker socket access fails from the router process even though `ubuntu` is in the docker group, either restart the service/session after group changes or fall back to `sudo docker inspect` in the resolver.
- Do not call the final canary complete until a real Telegram `/start`, guide selection, guest route, and response all pass.
