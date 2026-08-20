---
name: hde-guest-ops-scripts
description: Rebuild, verify, and operate the HDE guest-container ops scripts (backup_guest_data.py, hibernate_inactive_containers.py, prune_suspended_users.py) in hd-platform. Use when a cron job fires at a missing script path, guest journals need backing up, or retention/scale-to-zero behavior must change.
---

# HDE Guest Ops Scripts (hd-platform)

The three retention/backup scripts run from the **root crontab** against
`/home/ubuntu/work/hd-platform/scripts/`:

| Script | Cron | Job |
|---|---|---|
| `backup_guest_data.py` | `0 2 * * *` | tar every `/home/ubuntu/users/guest_*` → `/home/ubuntu/backups/guest_backups/<name>_<stamp>.tar.gz`, 14-day retention |
| `prune_suspended_users.py` | `0 3 * * *` | finalize `users.deletion_scheduled_at` rows: HMAC deprovision + PII anonymize + workspace removal (only if backup exists) |
| `hibernate_inactive_containers.py` | `*/5 * * * *` | `docker compose stop` for non-active guests idle >7d (router auto-wakes on next message) |

Logs: `/home/ubuntu/hde_backup.log`, `/home/ubuntu/hde_prune.log`, `/home/ubuntu/hde_hibernate.log`.

## Critical pitfalls

1. **DATABASE_URL comes from the repo `.env`, not a hardcoded value.** The
   original scripts (2026) hardcoded user `hduser` which never authenticated —
   they crashed every run. Always `load_dotenv(REPO_ROOT/".env")` then import
   `shared.database.async_session_factory`. Working DB: `postgresql+asyncpg://hde_app:...@127.0.0.1:5432/hde`.
   Verify engine availability: `async_session_factory is not None`.
2. **These scripts were lost from disk in 2026-07-18 because they were never
   committed to git.** Any script referenced by crontab MUST be git-tracked in
   hd-platform before it is considered done. Verify with `git ls-files`.
3. **prune must never delete a workspace without a backup archive present.**
   Check `BACKUP_DIR.glob(f"guest_{user_id}_*.tar.gz")` before `shutil.rmtree`.
4. **`paid`/`demo`/`active` users are never pruned or hibernated.** Hibernatable
   statuses: `expired_demo`, `inactive`, `deactivated`, `deleted_demo`.
5. **`hde_trial_lifecycle.py` (live systemd timer) owns the `expired_demo`
   chain.** prune marks finalized rows `deleted_demo` (which trial-lifecycle
   ignores) to avoid double-processing.
6. **Orchestrator calls need HMAC**: `POST http://127.0.0.1:8001/api/orchestrate/provision`
   with `X-Signature: sha256 HMAC of the raw JSON body`, secret =
   `ORCHESTRATOR_SHARED_SECRET` from repo `.env`. Actions: `provision|deprovision|stop|start`.
7. Container names: `guest-hermes-{user_id}`, compose at
   `/home/ubuntu/guest_hermes_bot_{user_id}/docker-compose.yml`,
   project prefix `guest-hermes-{user_id}`.
8. Customer journals live in `/home/ubuntu/users/guest_{id}/guest_journal.db`
   (bind-mounted into containers as `/workspace`). File mtimes there are a
   trustworthy inactivity signal.

## Verification recipe (do all of this before claiming done)

```bash
cd /home/ubuntu/work/hd-platform
.venv/bin/python3 -m py_compile scripts/<script>.py
.venv/bin/python3 -c "import sys; sys.path.insert(0,'.'); import importlib; importlib.import_module('scripts.<script>'); print('OK')"
# dry runs against the LIVE db:
HDE_PRUNE_DRY_RUN=1 .venv/bin/python3 scripts/prune_suspended_users.py
HDE_HIBERNATE_DRY_RUN=1 .venv/bin/python3 scripts/hibernate_inactive_containers.py
# real backup run + integrity:
.venv/bin/python3 scripts/backup_guest_data.py
tar tzf <archive> | grep -c guest_journal.db   # must be >= 1 per active guest
ruff check scripts/backup_guest_data.py scripts/prune_suspended_users.py scripts/hibernate_inactive_containers.py
```

Then commit (docs update in the SAME commit — `scripts/README.md` ops section).

## Rebuild history

- 2026-08-19: all three rebuilt after originals vanished (32-day backup gap).
  Commit `[Ned] Rebuild guest data backup, hibernate, and prune ops scripts`.
  First verified backup run: 13 archives, byte-identical extract diff.
