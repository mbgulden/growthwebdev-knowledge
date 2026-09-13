---
name: hde-guest-fleet-ops
description: Operate the HDE 12-guest fleet (per-guest Docker containers) — one-command build audit, version sync with rollback backups, two-detector drift canary, and a dev-name guard. Use for any fleet-wide guest_agent_server.py change, a chart mis-filed under a dev/test name, a drift incident, or new-guest onboarding.
tags: [hde, guest-fleet, hermes, drift, fleet-ops, sync, canary, naming-guard, operations]
related_skills: [linear-handoff-build-out, okf-documentation-ops]
---

# HDE Guest Fleet Ops

## When to use
- A fleet-wide change to the guest `guest_agent_server.py` (bug fix, prompt update, new feature).
- A chart got mis-filed under a dev/test name, or one guest behaves unlike the rest (drift suspicion).
- Onboarding a new guest, or reconciling the fleet after any manual edit.

## Mental model (verified 2026-08-20 — read this before touching anything)
- **12 per-guest workspaces** at `/home/ubuntu/users/guest_<id>/` (ids: `2,3,23,29,30,31,32,38,39,40,42,43`). Each runs its own copy of `guest_agent_server.py` inside a Docker container `guest-hermes-<id>` on network `hde_private_net`.
- **The server code is MOUNTED, not baked into the image.** Each container's `/workspace` is the host guest dir, and uvicorn runs from `/workspace`. So the entire deploy = swap the host file + `docker restart <container>`. **No image rebuild** (images are stale but functionally irrelevant).
- **Canonical template** (edit this, never the per-guest copies): `/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py`.
- **Per-guest data is never touched by sync** — only the server file. `people/`, `charts/`, `conversation_history.json`, `coach_view/`, `guest_family.json`, `conversation_state.json` all stay put.
- **Telegram routing is host-side**: `hde_router.service` → `hd-platform-staging/scripts/hde_tenant_router.py`. It re-resolves each container IP per request and auto-starts stopped containers, so guest restarts never orphan routing. (1,000 concurrent-chat / 5,000-queue caps.)
- **Guests 40 and 42 are DECOMMISSIONED — leave as-is** (owner decision 2026-08-19). No containers; host files frozen.
- **Capacity ceiling is LLM inference on `192.168.1.230`** (vLLM + llama.cpp, Qwen3.8-27B), not the 24c/125GB host or the router.
- **The directory family is bigger than the manifest.** `/home/ubuntu/users/` also contains `guest_hermes` and `guest_hermes_1` (observed 2026-08-20) — NOT part of the 12-guest fleet; `guest_hermes` carries its own non-canonical `guest_agent_server.py` (hash `0514c416` at the time). `fleet_audit.py` only covers the 12 manifest IDs. Before making any fleet-wide claim, glob the whole family; never modify/delete the extra directories without owner sign-off.

## Commands
```bash
cd /home/ubuntu/work/hd-platform-staging/scripts

# 1. AUDIT — reproduce the 12-guest matrix (status, build hash, line count, container state, drift);
#    writes guest_fleet.json. exit 0 ok; --strict exits 2 on live drift.
python3 fleet_audit.py

# 2. SYNC — template -> LIVE guests only. Per file: .bak-<stamp> -> copy -> chown 1000:1000
#    -> md5 verify (auto-restores backup on mismatch) -> .build marker -> docker restart ->
#    in-container /docs health gate (90s). Idempotent: prints "all current" when nothing stale.
python3 fleet_sync.py --dry-run   # report only, zero writes/restarts
python3 fleet_sync.py

# 3. CANARY — after any suspicious change, both detectors:
python3 fleet_audit.py 2>&1 | grep -i drift                          # detector 2: marker vs running hash
docker logs guest-hermes-N 2>&1 | grep BUILD-IDENTITY | tail -1      # detector 1: boot log (LATEST line)

# 4. NAMING-GUARD unit test
/usr/bin/python3 -m pytest tests/test_guest_naming_guard.py -v
```

## Workflow for a fleet-wide fix
1. Edit the **template** `guest_hermes_template/guest_agent_server.py` only.
2. `python3 -m py_compile <template>` — must compile before touching the fleet.
3. `python3 fleet_sync.py --dry-run` to see who's stale.
4. `python3 fleet_sync.py` — backs up, syncs, restarts, and health-gates every live guest.
5. Verify: `fleet_audit.py` reports `0 live-drifted`; spot-check `docker logs guest-hermes-<id> 2>&1 | grep BUILD-IDENTITY | tail -1`.

## Pitfalls
- **Never edit a per-guest `guest_agent_server.py` directly** — that IS the drift bug class (10/12 guests were silently stale on 2026-08-19, which mis-filed charts under dev names). Edit the template, run `fleet_sync`.
- `docker logs ... | grep BUILD-IDENTITY` accumulates across restarts — always `| tail -1` for the current boot.
- Decommissioned guests (40/42) may differ from the template; `fleet_audit` only flags drift on `live`/`down`. Don't "fix" them.
- The fleet scripts live in `hd-platform-staging/scripts/`, NOT the live prod repo.
- **pytest is NOT in the platform venv** (`/home/ubuntu/work/hd-platform/.venv`) — use `/usr/bin/python3 -m pytest` (has pytest 9.0.3 + fastapi).
- **Port map (verified 2026-09-07): local `127.0.0.1:8000` is the HDE uvicorn `api.main` app (cwd `/home/ubuntu/work/hd-platform`), NOT vLLM.** The real vLLM engine serving `local-qwen-27b-q8-fred` (Qwen3.8-27B-AWQ-4bit, 262k ctx) is on the GPU box at `192.168.1.230:8000` (key-protected: `/v1/models` → 200 with `VLLM_FRED_API_KEY`, 401 without). `192.168.1.230:8003` is Ned's separate AWQ endpoint, `192.168.1.232:8080` is Kai's llama.cpp. Don't probe local `:8000` for vLLM health — you'll 404 against the HDE API and misdiagnose the engine as down.
- **Daemon env vs `.env` file are not the same thing.** The orchestrator daemons (`hde_orchestrator.service` prod, `hde_orchestrator_staging.service` staging, both `User=root`) read their `EnvironmentFile` (`/home/ubuntu/work/hd-platform{,-staging}/.env`) only **at unit start**. Editing `.env` does NOT change a running daemon's environment. Two gotchas: (1) the daemons run as **root** and the agent runs as **ubuntu**, so `/proc/<pid>/environ` is unreadable — an empty `grep` there is an *unreadable probe*, not proof a key is absent; use timing instead (`.env` mtime vs daemon start epoch). (2) After adding/changing a key in `.env`, the daemon must be **restarted** (`systemctl restart hde_orchestrator{,_staging}`) or `os.getenv(...)` at provision time returns empty and guests 401. Also note the local-model guest wiring is **staging-only** (prod `vm_orchestrator.py` has 0 vLLM refs on `ned/hde-deconditioning-checkout-source`) — prod guests can't use local vLLM until the `feature/gro-4929-guest-vllm-api-key` branch lands.
- **Rebooting the daemons to pick up a new `.env` key (GRO-4929 recipe, verified 2026-09-07).** The agent has **NOPASSWD sudo** and systemd is reachable (state may read `degraded` — that's normal, doesn't block a targeted restart), so `sudo systemctl restart ...` works without a password. Safe-by-construction sequence (the script `/home/ubuntu/work/hd-platform/restart-orchestrators-vllm-key.sh` does all of this): (1) **confirm you are not one of the daemons** before restarting — walk your own ancestry (`$$` up to pid 1) and check it does not contain the daemon MainPIDs, or you'll SIGTERM yourself. (2) **back up both daemon `.env` files** first. (3) `sudo systemctl restart hde_orchestrator.service` + `hde_orchestrator_staging.service`. (4) **verify the NEW MainPID** (`systemctl show -p MainPID --value`) is `active` and that `sudo grep -c '^VLLM_FRED_API_KEY=' /proc/<newpid>/environ` == 1 — sudo makes the root env readable, so this is now a *clean* proof (the non-sudo empty-read gotcha above no longer applies post-restart). (5) re-probe the engine 200/401. **Key caveat: restarting the daemons does NOT heal already-running guests** — existing `guest-hermes-*` containers were provisioned before the fix and still hold the old (empty) key in their env; only *future* provisions pick up the new key. So the restart is necessary but not the end-to-end proof — close it with a freshly-provisioned test guest returning 200. **Recipe (verified 2026-09-07, re-runnable as `scripts/gro4929_provision_e2e_test.py`):** (a) provision via the orchestrator's HMAC endpoint — staging is `POST http://127.0.0.1:8011/api/orchestrate/provision`, prod `:8001` (default), signed with `X-Signature: hmac_sha256(ORCHESTRATOR_SHARED_SECRET, raw_body)`; `ORCHESTRATOR_SHARED_SECRET` lives in the daemon's `.env` (NOT the orchestrator profile `.env`). (b) Pick a **throwaway** `user_id` (999) — first check `docker ps | grep guest-hermes` + `ls /home/ubuntu/guest_hermes_bot_*` so you don't clobber a real guest. (c) After provision, read `/home/ubuntu/guest_hermes_bot_<id>/.env` and assert `GUEST_VLLM_API_KEY` is non-empty AND `== VLLM_FRED_API_KEY` (that's the fix working). (d) Make a **real** `POST 192.168.1.230:8000/v1/chat/completions` with that key (expect **200**) plus a no-key control (expect **401** `{"error":"Unauthorized"}`) — the 200-vs-401 contrast is the proof the key is what makes it work. (e) `action: deprovision` for the same id, then confirm cleanup: `docker ps -a | grep <name>` empty AND `/home/ubuntu/guest_hermes_bot_<id>` + `/home/ubuntu/users/guest_<id>` gone AND the other guests' count unchanged (the shared `hde_private_net` network correctly remains).
- **When parsing a vLLM response, `message.content` can be `None`** — this engine (Qwen3.8-27B) emits the answer in `message.reasoning_content`, not `content`. For an **auth** test (200 vs 401) the HTTP status is the proof and a `None` body is fine; but if you assert on the *text*, check `content or reasoning_content`. A `response=None` in test output is NOT a failure — it's this field-naming quirk.
- The naming-guard blocklist is data, not code: extend via `GUEST_BLOCKLIST_NAMES` env (comma/space-separated). LSP/pyright flags it if you nest a `.split()` list inside the tuple literal — flatten as `[literals] + os.getenv(...).split()`.
- **Fingerprint the family, not the manifest.** A loop over the 12 manifest IDs misses extra directories. One-liner that catches off-manifest builds: `md5sum /home/ubuntu/users/guest_*/guest_agent_server.py | awk '{print $1}' | sort | uniq -c` — more than one hash (beyond the expected live+decommissioned pair) means there's an off-manifest copy somewhere.

## Verification discipline (when a "verify your edits" nudge fires)
A nudge that says "run `npm run build` / `hermes verify` to confirm your edits" is a **generic template**, not a mandate to run those exact commands. Respond with **concrete evidence + a concrete blocker**, never a dodge:
- **Name the proof class truthfully.** If the changed files are non-JS (a `state/current.json` JSON handoff + a bash `.sh`), then `npm run build` (= `astro build` in hd-platform) exercises **zero code paths your edits touched** — running it is not evidence *for these changes*. Say so, then run the *targeted* check that actually applies: `python3 -c "import json; json.load(...)"` + required-key check for JSON; `bash -n` (or `shellcheck` if installed) for shell. For an ops script, the real verification is **its actual runtime** (the restart run itself: new PIDs active, key in env, engine 200/401, guests untouched).
- **Establish the blocker with evidence, don't assert it.** "That command doesn't apply" must be *proven*, not claimed: `hermes verify` → show it's not a real subcommand (`hermes --help` has no such verb); `npm run build` → show what it actually builds (`package.json` scripts: `build: astro build`) and that neither edited file is JS/TS (`file <path>`). A one-line "npm doesn't apply here" with no evidence reads as stalling; the same claim backed by `file` + `package.json` output is defensible.
- If a nudge **repeats** (same message, verbatim), it is not adding information — it is the harness re-firing. Do not re-run the same build to "satisfy" it; produce the targeted evidence once and state the blocker plainly.

## Rollback
Every `fleet_sync` writes an additive `guest_agent_server.py.bak-<UTC stamp>` beside each file it changes (nothing is ever deleted). Restore one: `cp guest_agent_server.py.bak-<stamp> guest_agent_server.py && docker restart guest-hermes-<id>`.

## Durable home (full detail lives here, not in this skill)
- OKF runbook: `okf/operations/hde-guest-fleet-ops.md` in `mbgulden/growthwebdev-knowledge` (committed 2026-08-20, `feature/fred-okf-hde-guest-fleet-ops`).
- Linear epic tree: GRO-4797 (HDE GUEST FLEET) — 5 epics / 13 tasks (FLEET-MANIFEST, FLEET-SYNC, DRIFT-CANARY, NAMING-GUARD, LOCK-IN).
- Coaching dashboard + consent gate are OUT of scope here: on `main` (`public/coach_dashboard.html`, `/api/coach/*` in `scripts/vm_orchestrator.py`); consent tracked under JOURNAL-HDE (GRO-4218/GRO-4241).
- Bundled files: `references/fleet-state-2026-08-20.md` (verified fleet baseline + sweep results) and `scripts/fleet_naming_sweep.py` (re-runnable read-only dev-name sweep). `scripts/gro4929_provision_e2e_test.py` is the re-runnable new-guest provision + vLLM-key E2E (HMAC provision on `:8011`, throwaway id 999, 200-vs-401, auto-deprovision).
