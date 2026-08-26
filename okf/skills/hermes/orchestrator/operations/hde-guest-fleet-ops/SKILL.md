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
- The naming-guard blocklist is data, not code: extend via `GUEST_BLOCKLIST_NAMES` env (comma/space-separated). LSP/pyright flags it if you nest a `.split()` list inside the tuple literal — flatten as `[literals] + os.getenv(...).split()`.
- **Fingerprint the family, not the manifest.** A loop over the 12 manifest IDs misses extra directories. One-liner that catches off-manifest builds: `md5sum /home/ubuntu/users/guest_*/guest_agent_server.py | awk '{print $1}' | sort | uniq -c` — more than one hash (beyond the expected live+decommissioned pair) means there's an off-manifest copy somewhere.

## Rollback
Every `fleet_sync` writes an additive `guest_agent_server.py.bak-<UTC stamp>` beside each file it changes (nothing is ever deleted). Restore one: `cp guest_agent_server.py.bak-<stamp> guest_agent_server.py && docker restart guest-hermes-<id>`.

## Durable home (full detail lives here, not in this skill)
- OKF runbook: `okf/operations/hde-guest-fleet-ops.md` in `mbgulden/growthwebdev-knowledge` (committed 2026-08-20, `feature/fred-okf-hde-guest-fleet-ops`).
- Linear epic tree: GRO-4797 (HDE GUEST FLEET) — 5 epics / 13 tasks (FLEET-MANIFEST, FLEET-SYNC, DRIFT-CANARY, NAMING-GUARD, LOCK-IN).
- Coaching dashboard + consent gate are OUT of scope here: on `main` (`public/coach_dashboard.html`, `/api/coach/*` in `scripts/vm_orchestrator.py`); consent tracked under JOURNAL-HDE (GRO-4218/GRO-4241).
- Bundled files: `references/fleet-state-2026-08-20.md` (verified fleet baseline + sweep results) and `scripts/fleet_naming_sweep.py` (re-runnable read-only dev-name sweep).
