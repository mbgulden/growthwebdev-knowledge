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

## Fleet drift (HFG) + timeout/routing diagnosis

For the build-drift toolchain (`fleet_audit.py` / `fleet_sync.py` / `.build` markers / naming guard), the HFG scope boundary, and the two classic guest-bot failure modes ("Sanctuary container took too long" router timeouts, and a chat landing on the wrong guest container and showing someone else's chart), see `references/hfg-fleet-drift-and-timeout-diagnosis.md`. **Status (2026-08-21, final): both failure modes fully repaired AND committed. Prod rebind `8190664947`→user 2/guest-hermes-2 + user-43 suspension (access_status=inactive, +30d delete) executed against the prod DB. Router timeout fix + full router subsystem merged to main (PR #56, a13723b); the GRO-4823 rebind guard = PR #57 (7817c81). vLLM prefix caching ENABLED + verified (start_fred.sh). The staging branch `ned/hde-phase4-...` is DIVERGENT from main on the router — cherry-pick/rebase, never merge. Re-check the "2026-08-21 resolution" section before re-diagnosing or re-fixing.**

## Merged ≠ live: the HDE router runs from the diverged staging tree

The single most expensive trap in HDE "why isn't my fix live?" debugging:
**`hde_router.service` does NOT run from the prod checkout or from `main`.** Its
unit points at the **staging** tree:

```
WorkingDirectory=/home/ubuntu/work/hd-platform-staging
EnvironmentFile=/home/ubuntu/work/hd-platform-staging/.env
ExecStart=/home/ubuntu/work/hd-platform/.venv/bin/python3 scripts/hde_tenant_router.py
```

So the router that actually runs is
`/home/ubuntu/work/hd-platform-staging/scripts/hde_tenant_router.py` — and in that
tree it is **UNTRACKED** (`git status` shows `?? scripts/hde_tenant_router.py`
alongside `hde_trial_lifecycle.py`, `vm_orchestrator.py`, `.bak-*`). It is a
hand-maintained copy, not a git checkout of main. **Merging a PR to `main`
(PR #56 timeout chain, PR #57 rebind guard) changes nothing about the running
process** until the file is copied into the staging tree AND the service is
restarted. The `hd-platform` prod checkout is a red herring: its venv is shared,
but the *code path* is the staging tree. (Hit 2026-08-21: PR #57 merged + verified
on main, yet the live router — process up since 03:29, merge at 08:20 — still ran
the pre-guard claim path because the staging copy never received the guard file.)

**Diagnostic recipe (run before ever claiming a merged fix is "deployed"):**
1. `systemctl cat hde_router.service` → read `WorkingDirectory` + `EnvironmentFile`
   (these two name the tree that actually runs; do NOT assume the prod checkout).
2. `git -C <that tree> ls-files scripts/hde_tenant_router.py` → if it returns
   nothing, the running code is an untracked hand copy, not git state.
3. `git show origin/main:scripts/hde_tenant_router.py > /tmp/main.py && diff /tmp/main.py <that tree>/scripts/hde_tenant_router.py`
   → the real "what's missing from live" delta. Semantic-diff (strip comments/blank
   lines) and confirm the delta is ONLY your change — specifically that there are no
   local-only config constants (tokens/ports/paths) in the staging copy that a
   straight overwrite would clobber, and no staging-only imports that main lacks.
4. `ps -o lstart= -p $(systemctl show -p MainPID --value hde_router.service)` vs
   `git show -s --format=%ci <merge>` → if the process started BEFORE the merge, it
   holds the OLD code regardless of what's on disk now (Python doesn't hot-reload).

**Deploy (needs explicit owner GO — it is a prod bot restart):** sync the changed
files from `origin/main` into the staging tree's `scripts/`
(`git show origin/main:scripts/<f> > <staging>/scripts/<f>`), then `systemctl
restart hde_router`. Verify after: new `MainPID`/start time is after the merge, and
the on-disk file greps for the symbol you shipped (e.g. `grep -c hde_rebind_guard`).
State lives in Postgres/Redis, not the process, so the restart loses nothing — but
in-flight Telegram messages in the few-second window may drop, so this is still a
prod change that needs approval, not a silent auto-deploy.

**RESOLVED 2026-08-21 15:37 UTC — the guard is LIVE (owner GO).** Synced
`scripts/hde_tenant_router.py` + `scripts/hde_rebind_guard.py` from `origin/main`
(6625c74) into the staging tree (byte-identical, diff-verified), `sudo -n systemctl
restart hde_router` → PID 1701071. Post-verify: clean startup (somatic cues, Redis
rate limiter, job queues), Telegram polling resumed, zero journal errors, and 15/15
guard tests re-run against the *deployed* tree (symlink-scratch recipe, pitfall 10).
[GRO-4823](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4823) +
[GRO-4822](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4822) (epic) flipped
Done with verified closure comment. Do NOT re-diagnose "guard not live" — it is live
as of this date; re-run the diagnostic recipe above only if a FUTURE change lands.

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
9. **Plain `systemctl restart` fails with "Interactive authentication required"**
   for these user-facing services on this host — the Hermes `ubuntu` user lacks
   direct polkit rights on the unit. Use `sudo -n systemctl restart <service>`
   (passwordless sudo is available; hit 2026-08-21 during the hde_router guard
   deploy). The failure is silent-ish: the old process keeps running, so ALWAYS
   re-check `MainPID`/`ExecMainStartTimestamp` after a restart to prove a new
   process actually started.
10. **Guard/feature tests resolve sibling modules RELATIVE TO THE TEST FILE**, not
    via PYTHONPATH. `tests/test_rebind_guard.py` locates
    `../scripts/hde_rebind_guard.py` from its own path, so running a copy from
    `/tmp` dies with `FileNotFoundError: '/tmp/../scripts/hde_rebind_guard.py'`
    even though the import would otherwise work. To re-run a test suite against a
    DEPLOYED tree, mirror the layout in a scratch dir: `mkdir -p
    /tmp/verify/tests && ln -s <deployed>/scripts /tmp/verify/scripts && cp
    <test> /tmp/verify/tests/ && (cd /tmp/verify && python3 -m pytest tests/<test>
    -q -p no:cacheprovider)`. The symlink means the tests genuinely exercise the
    deployed code, not a copy.

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
# healthy: response self-reports michael_gulden, real time < ~60s (not 3-min)
```

## 2026-08-21 (final) closure + prod DB traps learned this session

- **Rebind + suspension executed on the PROD Postgres DB** (not staging) in one
  committed transaction (asyncpg): `bot_instances.id16`(user 43)→`telegram_user_id=NULL`;
  `bot_instances.id7`(user 2/mbgulden)→`telegram_user_id='8190664947'`; verified exactly
  one row holds the phone → user 2 / guest-hermes-2. (The rebind target state had already
  been reached by the router's claim path, so the write was idempotent.)
- **SUSPENSION TRAP (the one that bit):** for a LIVE (unexpired) demo, setting
  `users.subscription_status='inactive'` ALONE does NOT block the user — the
  `user_access_state()` demo branch still returns `allowed:True` while
  `trial_expires_at` is in the future. The app's own `mark_access_paused()` only
  forces a non-demo `access_status` on the `demo_expired` path. To suspend a live
  demo you MUST also set `access_status` to a non-demo value (`inactive`). Done:
  user 43 = `subscription_status=inactive, access_status=inactive, deactivated_at set,
  deletion_scheduled_at=+30d`, `bot_instances.id16.status=suspended`. **Proved** by running
  the router's real `user_access_state()` on the new row → `{allowed:False, kind:inactive}`,
  which is checked at the access gate (line ~591) BEFORE the status/wake path (~628), so the
  container is not even woken by the suspended user's messages.
- **DB access recipe that works:** Python `asyncpg`; parse `DATABASE_URL`
  (scheme `postgresql+asyncpg://`) by stripping the `+asyncpg` and `?…` then
  `urllib.parse.urlparse` — do NOT hand-roll a regex (the `***` in the password
  breaks it). Wrap multi-statement repairs in ONE `async with conn.transaction()` with
  BEFORE/AFTER snapshots + assertions, so any violated assertion rolls back. Never print
  the password.
- **`sqlite3` CLI is not installed** on this host — use Python (`asyncpg`/sqlalchemy).
- `:8002` llama.cpp zombie: STILL PENDING + untracked (GRO-4824 closed Done). Guests do
  NOT reference `:8002` (they call `:8000`) — quarantine needs owner GO.
- **Verification split (hd-platform worktrees):** `pytest` is NOT in
  `/home/ubuntu/work/hd-platform/.venv` — use **system `python3`** (has pytest 9.x) for
  tests; use the **venv python** for actual `import` probes that need httpx/sqlalchemy
  (and put `scripts/` on `sys.path` — sibling modules import by bare name). Router
  import is the real gate (catches missing `somatic_cues.json` → silent fallback),
  not py_compile.

### vLLM prefix caching — ENABLED + verified (2026-08-21)
The top item from the residual-risk list above was implemented. Owner gave explicit OK.

- **Change:** added `--enable-prefix-caching` to `/opt/vllm_bin/start_fred.sh` (the script behind `vllm-fred.service` — the service's `ExecStart` just calls this shell script, so the flag lives in the script, not the unit). Backed up to `start_fred.sh.bak-20260821`. Insert with `sed -i '/--enable-auto-tool-choice/i\  --enable-prefix-caching \\'` — NOT a `sed s/` substitution (replacement text containing backslashes/`&` breaks it; use insert-before). `bash -n` passed before restart. `systemctl restart vllm-fred.service`.
- **Restart is SLOW — don't misread it as failure:** the old TP=2 process drains on SIGTERM for several minutes before the unit goes `active`, and the new 27B load takes ~3+ more minutes during which `/health` returns `000`. Poll `systemctl is-active vllm-fred.service` + `curl -s -m 3 http://127.0.0.1:8000/health` in a loop up to ~6 min (observed: `deactivating` for 2+ min, then `active` with health `000` for ~3 min, then `200`).
- **Confirm live:** `ps -o args= -p $(systemctl show -p MainPID --value vllm-fred.service) | grep -o 'enable-prefix-caching'` → present.
- **GOTCHA — the log's `Prefix cache hit rate` is UNRELIABLE on this model:** vLLM logs `Mamba cache mode is set to 'align' for Qwen3_5ForConditionalGeneration by default when prefix caching is enabled`. The `Prefix cache hit rate: 0.0%` metric STAYS 0% even while the cache demonstrably works (hybrid Mamba+attention model — the counter doesn't track prefix reuse). **Never use the hit-rate% log line as proof the cache is off or on.**
- **Proof = the latency delta.** Same ~2000-token prompt to `:8000`: **cold 4.3s → warm 1.3s**, stable on repeats (3.3× prefill speedup). Through the real guest container (full ~5k prompt + history): turn 1 52.8s → turn 2 27.0s.
- **Re-verify recipe (no inference):**
```bash
ssh root@192.168.1.230 bash -lc '
  ps -o args= -p $(systemctl show -p MainPID --value vllm-fred.service) | grep -o enable-prefix-caching && echo FLAG_ACTIVE
  /usr/bin/python3 - <<"PY"
  import json,time,urllib.request
  p=("The Human Design system describes five energy types: Manifestor, Generator, "
     "Manifesting Generator, Projector, and Reflector. Each has a defining center, "
     "a strategy, and an authority. The Generator and Manifesting Generator have the "
     "sacral center defined and use the strategy of responding and the sacral authority. "
     "The Projector has no sacral center, uses the strategy of waiting for the "
     "invitation, and reads the situation with the self. The Reflector has no "
     "sacral or solar plexus and cycles roughly every twenty-eight days, so "
     "decisions should wait for a full cycle. The Manifestor initiates and must "
     "inform to avoid friction. The profile adds a hereditary cross and a "
     "personal cross that shape how the person engages with the world. ")*12
  body=json.dumps({"model":"local-qwen-27b-q8-fred",
     "messages":[{"role":"user","content":p+" In one word, what is the Reflector strategy?"}],
     "max_tokens":8,"temperature":0}).encode()
  for tag in ("cold","warm1","warm2"):
      req=urllib.request.Request("http://127.0.0.1:8000/v1/chat/completions",data=body,headers={"Content-Type":"application/json"})
      t=time.time()
      urllib.request.urlopen(req,timeout=120).read()
      print(f"{tag}: {time.time()-t:.2f}s")
  PY'
# healthy: warm1/warm2 >=2x faster than cold, and roughly equal to each other
```

**Commit status (final, 2026-08-21):** the router timeout fix + the whole router subsystem (`hde_tenant_router.py` + `hde_rate_limits/job_queue/usage_budgets` + `somatic_cues.json` + runtime doc) are **COMMITTED + MERGED to main via PR #56 (a13723b)**. The GRO-4823 rebind guard (`scripts/hde_rebind_guard.py` + claim path) is **PR #57 (7817c81), MERGED to main 2026-08-21 (merge commit 6625c74) AND DEPLOYED LIVE 2026-08-21 15:37 UTC** (the staging tree received both guard files byte-identical from origin/main and hde_router restarted, PID 1701071; see the RESOLVED note in "Merged ≠ live"; GRO-4822/4823 flipped Done). The host-side `.env` values (chat budget 240s) and the guest inner cap (240s) were applied on the staging host — confirm whether they are on main before assuming. The prefix-caching change lives on the GPU node (`/opt/vllm_bin/start_fred.sh`, backed up) and is not in any git repo. The staging branch `ned/hde-phase4-...` carries a stale divergent router copy + 7 unpushed commits — never merge it to main.

Then commit (docs update in the SAME commit — `scripts/README.md` ops section).

## Rebuild history

- 2026-08-19: all three rebuilt after originals vanished (32-day backup gap).
  Commit `[Ned] Rebuild guest data backup, hibernate, and prune ops scripts`.
  First verified backup run: 13 archives, byte-identical extract diff.
