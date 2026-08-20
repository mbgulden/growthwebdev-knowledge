---
type: Operations Plan
title: HDE Guest Fleet Ops — Audit / Sync / Canary / Naming Guard
description: Runbook for the 12-guest HDE guest_hermes fleet. One-command build audit, one-command version sync with rollback backups, a two-detector drift canary, and a dev/test naming guard. Ships the fix for silent build drift (10 of 12 guests on stale builds, 2026-08-19).
resource: okf/operations/hde-guest-fleet-ops.md
project: hd-engine
tags: [hde, guest-fleet, hermes, drift, fleet-ops, sync, canary, naming-guard, operations]
timestamp: 2026-08-20T05:00:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/operations/hde-guest-fleet-ops.md
last_verified: 2026-08-20
verified_by: fred
status: current
---

# HDE Guest Fleet Ops — Audit / Sync / Canary / Naming Guard

> **Verified 2026-08-20 by Fred** — all four phases exercised live: fleet unified
> (12/12 hash-identical), end-to-end sync proven on a test guest, both canary
> detectors fired in a deliberate desync, naming guard 10/10 unit-green and live
> on all 10 running guests.

## TL;DR

The HDE guest fleet is **12 per-guest workspaces**, each running its own copy of
`guest_agent_server.py` inside a Docker container. On 2026-08-19 an audit found
**10 of 12 copies had silently drifted** (three different stale builds), which is
what caused charts to be mis-filed under dev names. This runbook is the
post-incident fix: one command to **audit**, one command to **sync**, a
two-detector **drift canary**, and a **naming guard** at the chart-creation
boundary.

## Layout (verified paths)

| Piece | Path |
|---|---|
| Guest workspaces (12) | `/home/ubuntu/users/guest_<id>/` for id in 2,3,23,29,30,31,32,38,39,40,42,43 |
| Per-guest server copy | `/home/ubuntu/users/guest_<id>/guest_agent_server.py` (mounted at `/workspace/` in the container; uvicorn runs from `/workspace`, so host file + `docker restart` is the whole deploy — **no image rebuild**) |
| Canonical template | `/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/guest_agent_server.py` |
| Fleet scripts | `/home/ubuntu/work/hd-platform-staging/scripts/fleet_audit.py`, `fleet_sync.py`, `guest_fleet.json` (manifest) |
| Naming-guard test | `/home/ubuntu/work/hd-platform-staging/tests/test_guest_naming_guard.py` |
| Telegram routing | `hde_router.service` → `/home/ubuntu/work/hd-platform-staging/scripts/hde_tenant_router.py` (host-side; re-resolves container IPs per request — restarts never orphan routing) |
| Per-guest data (untouched by sync) | `people/`, `charts/`, `conversation_history.json`, `coach_view/`, `guest_family.json` |

## Commands

```bash
cd /home/ubuntu/work/hd-platform-staging/scripts

# 1. AUDIT — reproduce the fleet matrix (12 guests: status, build hash,
#    line count, container state, drift). Writes guest_fleet.json.
python3 fleet_audit.py            # exit 0 ok; --strict exits 2 on live drift

# 2. SYNC — template -> live guests only. .bak-<stamp> per file, md5 verify,
#    .build marker, docker restart, in-container /docs health gate.
python3 fleet_sync.py --dry-run   # report only, zero writes
python3 fleet_sync.py             # idempotent: "all current" when nothing stale

# 3. CANARY check — after any suspicious change:
python3 fleet_audit.py 2>&1 | grep -i drift        # detector 2 (marker vs running hash)
docker logs <guest-hermes-N> 2>&1 | grep BUILD-IDENTITY | tail -1   # detector 1 (boot log)

# 4. NAMING GUARD unit test:
/usr/bin/python3 -m pytest tests/test_guest_naming_guard.py -v
# (platform venv has no pytest; /usr/bin/python3 has pytest 9.0.3 + fastapi)
```

## The four mechanisms

### 1. Fleet manifest (`fleet_audit.py` → `guest_fleet.json`)
Status model is **derived, not hardcoded**: `live` (container running),
`decommissioned` (in the `DECOMMISSIONED = {40, 42}` set — Michael's decision
2026-08-19 "leave as is"), `down` (no container, not known decommissioned →
human decides). Drift flag applies to `live`/`down` only — decommissioned
workspaces are frozen by owner decision and may differ from the template
without being a problem. Guest detection is `fullmatch guest_(\d+)` so legacy
scaffolds (`guest_hermes`, `guest_hermes_1`) are excluded.

### 2. One-command sync (`fleet_sync.py`)
Order per guest: `.bak-<UTC stamp>` → copy template → `chown 1000:1000`
(container user) → md5 verify (auto-restore backup on mismatch) → write
`.build` marker → `docker restart` → poll in-container `/docs` until 200
(90 s budget). Never deletes, never touches decommissioned/down guests.

### 3. Drift canary (two independent detectors)
- **Detector 1 (boot log):** the template logs `BUILD-IDENTITY
  path=... md5=... lines=... marker=...` at startup (best-effort, never blocks
  boot). Read it with `docker logs <c> 2>&1 | grep BUILD-IDENTITY | tail -1`
  (the **latest** line — logs accumulate across restarts).
- **Detector 2 (audit):** `fleet_audit.py` compares each workspace's running
  hash against its `.build` marker (written by `fleet_sync`) and prints a named
  `DRIFT-MARKER: guest_N running hash X != marker Y` to stderr +
  `marker_stale: true` in the manifest.

Negative proof (done 2026-08-20): appending one line to test guest 3 outside
the sync path was caught by **both** detectors; `fleet_sync` restored it and
the fleet returned to 0 live-drifted.

### 4. Naming guard (template `guest_agent_server.py`)
`BLOCKED_PERSON_NAMES` (exact-match, case/punctuation-insensitive on the
**cleaned** name): michael gulden, michael, becca, becca gulden, test, tester,
test guest, guest test, qa, dev. Extensible via `GUEST_BLOCKLIST_NAMES` env
(comma- or space-separated) — extend via data, never by code. Guarded at both
chart-creation entry points: chart-intent with explicit name, and
compare-mode `person_name` capture. Blocked names get a `NAMING-GUARD` log
line + user-facing refusal; nothing is filed. Known tradeoff: a real client
whose name exactly matches a blocklist entry is a false positive — that is
accepted, the blocklist is dev-name protection by design.

**Sweep of existing mis-files (read-only, 2026-08-20):** 10 of 12 workspaces
clean. Mis-filed dev-name records exist only on test guests **2** and **23**
(`people/index.json` + `charts/personal/michael_gulden/` and
`charts/personal/becca_gulden/` — the "michael gulden" mis-filing class).
Deletion is Michael's call; nothing was deleted.

## Known state / decisions

- **Fleet build baseline 2026-08-20:** template md5 `baf3887bf391357d61294b369b12bed7`
  (2725 lines) — includes canary + naming guard. All 10 live guests on it,
  `.build` markers present. Rollback backups from the 08-19/08-20 rollout:
  `guest_agent_server.py.bak-20260819T2100Z` (original 12-way sync),
  `.bak-20260820T0402xxZ` (canary rollout), `.bak-20260820T0451xxZ` (guard
  rollout) — prune after ~1 week clean.
- **Guests 40/42: decommissioned, leave as-is** (no containers; host files
  updated but frozen).
- **Images are stale** (built Jul 10–16) but functionally irrelevant — code is
  mounted, not baked in.
- **Capacity:** host (24c/125GB) and router (1000-chat cap) are not the
  constraint; LLM inference on `192.168.1.230` (vLLM + llama.cpp, Qwen3.8-27B)
  is the ceiling (~8 comfortable / ~15 hard concurrent users per 3090).

## Related work

- Linear parent epic: [HDE GUEST FLEET](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-4797)
  (GRO-4797 + 5 epics + 13 tasks, all phases shipped to In Review 2026-08-20)
- Coaching dashboard + consent gate: on `main` (`public/coach_dashboard.html`,
  `/api/coach/*` in `scripts/vm_orchestrator.py`); consent flow tracked under
  JOURNAL-HDE (GRO-4218/GRO-4241) — out of scope here.
- HDE GREEN operational-reliability north star: GRO-4004.
