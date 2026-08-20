# 2026-08-18 — HDE walkback: operator profile vs product data layer

Context: after the fleet prune (see `2026-08-18-fleet-prune.md`), Michael believed the whole Human Design bot setup had been deleted. It had not — the customer-facing layer was untouched; only operator profiles were removed. **Corrected record: FIVE profiles were HDE-relevant — `hdengine`, `active-oahu`, `ai-consulting`, `google-ai-toolkit`, AND `jules`.** The first three-day impression said "four"; the full tarball sweep (`tar tzf | cut -d/ -f1 | sort -u` — the tarball held 19 top-level entries) exposed `jules`, which `hd-platform*/scripts/jules_session_manager.py` references. This file is the layer map that prevents the scare and the walkback recipe.

## HDE architecture map (the map that prevents the scare)

| Layer | Where | Notes |
|---|---|---|
| Customer "containers" | Docker `guest-hermes-{user_id}` | per-user Hermes-in-Docker on `hde_private_net`; NOT Hermes profiles |
| Customer journals | `/home/ubuntu/users/guest_{id}/` (`guest_journal.db`, `guest_family.json`, `next_step_mcp.py`, `active_soul.md`) | mounted into the container at `/workspace`; ~177M across 13 guests as of 2026-08-18 |
| Per-customer config | `/home/ubuntu/guest_hermes_bot_{id}/` (config.yaml, soul.md, active_soul.md, skills) | mounted into container at `/home/pn/.hermes/` |
| Core bot | `@Humandesigncompanionbot` via `hde_router` (systemd) | router code `~/work/hd-platform-staging/scripts/hde_tenant_router.py`; token env var `HDE_COACH_BOT_TOKEN` in `~/work/hd-platform-staging/.env` |
| Platform services | `hde-api`, `hde_orchestrator`, `hde_router`, `hde-payment`, `hde-reports`, `cloudflared-hde` (+ staging variants) | all systemd, fully independent of Hermes profiles |
| Operator assistant | `hdengine` Hermes profile (deleted, in tarball) | operator layer only; its `.env` still carries the old `865347…` token |

Router → customer path: user → container name `guest-hermes-{id}` → IP via `docker inspect` on `hde_private_net`; wakeup/provisioning goes through the orchestrator.

Mount inspection recipe:
```bash
docker inspect guest-hermes-39 --format '{{range .Mounts}}{{.Source}} -> {{.Destination}}{{"\n"}}{{end}}'
```

## Walkback recipe (token-scrubbed restore)

1. Prove the product layer is alive first:
   - `docker ps -a --format '{{.Names}}\t{{.Status}}' | grep guest-hermes` (expect all healthy)
   - `ls /home/ubuntu/users/` and `du -sh /home/ubuntu/users/`
   - `systemctl is-active hde_router hde_orchestrator hde-api`
2. Extract: `tar xzf /var/tmp/profiles-cleanup-20260818.tgz -C /home/ubuntu/.hermes/profiles hdengine` (one name at a time).
3. Scrub the old token from the restored `.env`/`config.yaml` before the profile is used again; scoped grep for the old prefix must return zero hits.
4. Identity check without printing the secret (Python; env-var name assembled by concatenation):

   ```python
   varname = "HDE_COACH" + "_BOT_" + "TOKEN"   # do NOT write the full name as one literal
   # read from /home/ubuntu/work/hd-platform-staging/.env
   # GET https://api.telegram.org/bot<token>/getMe via urllib
   # assert token not in stdout AND username == "Humandesigncompanionbot"
   ```
5. No gateway unit to recreate — `hdengine` was bus/on-demand driven, never had its own gateway unit.

## State at decision time (2026-08-18)

- Tarball: `/var/tmp/profiles-cleanup-20260818.tgz` (1.4M; ~14.7M uncompressed; `hdengine` = 40 files incl. `state.db`)
- 9 guest containers up/healthy: `guest-hermes-{2,3,23,29,30,31,32,38,39}`; data dirs `guest_40`, `guest_42` exist with no running container at that time
- `/home/ubuntu/users/` = 13 guest dirs, 177M
- `active-oahu` + `ai-consulting` are referenced by `hd-platform-staging/scripts/jules_session_manager.py`, `social_content_pipeline.py`, `tag_media.py` (Jules social pipeline) — restoring them is what keeps that pipeline functional
- `google-ai-toolkit` not referenced by the live HDE stack
- Old token `865347…` eradicated from all live profiles; the tarball copy of `hdengine/.env` still carries it (must be scrubbed on restore)
- OpenClaw on `lightbringer-windows` still polling the orphaned bot (separate infra issue, needs RDP)

## Executed restore (2026-08-18, same day — the "GO")

All five HDE-relevant profiles restored from `/var/tmp/profiles-cleanup-20260818.tgz`, then token-scrubbed. Verified byte-exact vs tarball: `hdengine` 24 files, `active-oahu` 24, `ai-consulting` 23, `google-ai-toolkit` 16, `jules` 14. Old token `865347…` scrubbed from the four that carried it (replaced with `__SCRUBBED_OLD_TOKEN__`); `jules` had zero occurrences. Proved the old token dead with one `getMe` → HTTP 401 (so log/bak/credentials residue in `orchestrator/` is inert, not a live poller). Post-restore the full HDE layer stayed green: 6 `hde-*`/`cloudflared-hde` units active, 9/9 `guest-hermes-*` containers healthy, `@Humandesigncompanionbot` live, postgres `hde` DB (44 users) up.

## Bonus finding (class-level, not HDE-specific): stale maintenance crons

While auditing the HDE blast radius, `crontab -l` showed three root cron entries pointing at scripts that no longer exist and had been failing silently since ~Jul 18 (~32 days):

| Cron (root) | Missing script | Impact |
|---|---|---|
| `2am backup_guest_data.py` | `hd-platform/scripts/backup_guest_data.py` | 🔴 guest journals `/home/ubuntu/users/` unbacked-up for 32 days (last good `guest_*_20260717_020001.tar.gz`, 354M in `/home/ubuntu/backups/guest_backups/`) |
| `3am prune_suspended_users.py` | `…/prune_suspended_users.py` | suspended users (40/42, deletion scheduled) not pruned — low urgency |
| `*/5 hibernate_inactive_containers.py` | `…/hibernate_inactive_containers.py` | containers not hibernating — cost/cosmetic |

Root cause: the three scripts were **never git-committed** (searched all branches, worktrees, NAS, even `__pycache__` — zero copies). They were plain files deleted by an earlier repo cleanup; the cron entries outlived them. Mitigating: the **separate postgres** backup (`/home/ubuntu/backups/hde-postgres/hde-postgres-20260817T030021Z.dump`) WAS current — only the file-level journal layer was exposed. Fix path: replace the dead cron with a **git-committed** tar script that archives `/home/ubuntu/users/` (don't silently re-add a cron pointing at a missing file). Lesson: a deletion scare is the right moment to also audit the product's own maintenance crons, because the same cleanup that lost the profiles often silently breaks the backups too.
