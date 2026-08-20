---
name: hd-guest-fleet-ops
description: Audit, sync, and deploy the HD Engine guest Hermes bot fleet (guest-hermes-* containers). Use for fleet-wide server updates, build-drift diagnosis, chart-filing/naming-fallback bugs, adding or decommissioning guests.
---

# HD Guest Fleet Ops

Class-level ops for the HD Engine guest bot fleet: ~12 guest workspaces, one docker container each (some guests are dead tests), all serving the same `guest_agent_server.py` from a host mount.

## When to use
- "Update the guest server" / "why is guest X behaving differently from guest Y"
- A bug fix or prompt change that must land on EVERY guest
- Suspected version drift across the fleet
- Adding a new guest or decommissioning a test guest

## Architecture (verified 2026-08-19)
- **Live server code** = per-guest host file `/home/ubuntu/users/guest_<id>/guest_agent_server.py`, mounted at `/workspace` in the container. uvicorn's cwd is `/workspace`, so that file is what serves.
- **Deploy = host file swap + `docker restart`.** No image rebuild — the images are stale (2.85–2.89GB, built weeks old) but only carry dependencies; code comes from the mount.
- **Per-bot dir** `/home/ubuntu/guest_hermes_bot_<id>/`: `docker-compose.yml`, `.env` (`GUEST_CONTAINER_NAME`, `GUEST_WORKSPACE_PATH`, `OHDMCP_SOURCE_PATH`, bot tokens), `config.yaml`, `soul.md`, `active_soul.md`, `skills/`.
- **Canonical template**: `/home/ubuntu/work/hd-platform-staging/scripts/guest_hermes_template/` (server + `deploy.sh` + MCP scripts + `guest_family.json`).
- **Top-level `/home/ubuntu/guest_hermes_bot*` dirs are stale scaffolding** — not the live source. Do not audit or edit them.
- Container user = UID 1000 (`pn`). Per-guest state (`charts/`, `conversation_history.json`, `coach_view/`, `greeting_state.json`) lives next to the server file in the workspace — **never overwrite the whole workspace**, only the files being distributed.
- Not every workspace has a running container (dead tests). Always cross-check `docker ps` against the workspace list before concluding a guest is live.

## Fleet audit
**Canonical (2026-08-20+):** `python3 /home/ubuntu/work/hd-platform-staging/scripts/fleet_audit.py` — one command prints the 12-guest matrix (status / build md5 / lines / container / drift) and writes `guest_fleet.json` beside it. Status is derived, never hardcoded per guest: `live` (container running), `decommissioned` (in the script's `DECOMMISSIONED` set — 40/42, owner decision 2026-08-19), `down` (no container, not known → human decides). The drift flag applies to `live`/`down` only — decommissioned workspaces are frozen by owner decision and may legitimately differ from the template (flagging them is a false positive). `--strict` exits 2 on live drift. Guest detection is `fullmatch guest_(\d+)` — legacy scaffolds are excluded.
Manual / pre-tooling fallback: `bash <skill_dir>/scripts/fleet_audit.sh` (prints host matrix, live matrix, in-container truth) or by hand:
1. Host matrix: per workspace — `wc -l` + `md5sum` + mtime of `guest_agent_server.py`, plus the template's md5.
2. Live matrix: `docker ps --format '{{.Names}}\t{{.Status}}' | grep guest-hermes`. Map container → workspace via the bot dir's `.env` `GUEST_WORKSPACE_PATH` (naming convention: `guest-hermes-<id>` ↔ `guest_<id>`).
3. **Diff at feature level first** — line counts alone mislead (2594 vs 2656 was pure prompt drift, zero missing routes):
   `diff <(grep -oE '^(class |def |    def |@app\.(get|post|put|delete|websocket)) [A-Za-z_]+' OLD) <(grep -oE '^(class |def |    def |@app\.(get|post|put|delete|websocket)) [A-Za-z_]+' TEMPLATE)`
4. Before overwriting, quantify what would vanish: `diff TEMPLATE OLD | grep -c '^>'`, eyeball the `^>` lines, and check for per-guest hardcoded identifiers (`grep -lE "guest_[0-9]+"`). If zero feature-level delta and no per-guest code, overwrite is safe.

## Fleet sync (bug fix / prompt update)
**Canonical (2026-08-20+):** edit the template, then `python3 /home/ubuntu/work/hd-platform-staging/scripts/fleet_sync.py` (`--dry-run` first). It touches `live` guests only; per guest: `.bak-<UTC stamp>` → copy template → `chown 1000:1000` → md5 verify (auto-restores the backup on mismatch) → writes the `.build` marker (canary input) → `docker restart` → polls in-container `/docs` until 200 (90s budget). Idempotent: on a clean fleet it prints `all current — nothing to do` and touches nothing. Exit 0 ok / 1 hard failure / 2 partial.
Manual / pre-tooling path:
1. Fix lands in the **template first**. Verify no dev/test-name fallbacks remain (`grep -n "Gulden"` — the only intentional match is `Becca Gulden` in the Becca-naming branch).
2. Per behind workspace: `cp file file.bak-<UTCSTAMP>` → `cp TEMPLATE file` → `chown 1000:1000 file`.
3. `docker restart` every stale live container (for-loop is fine; ~10s each).
4. **Verify in-container, not just on host.** Wait ~20s (healthcheck start_period is 15s), then per container: `wc -l < /workspace/guest_agent_server.py` (expect template line count) and the `/docs` probe:
   `docker exec <c> python3 -c "import urllib.request;urllib.request.urlopen('http://localhost:8000/docs')"`
5. Final sweep: all live containers `healthy` in `docker ps`; all workspace md5s == template md5; dev-name grep zero across the fleet.
6. Report the build matrix (build → guests → drift), what was synced, and what was verified in-container.

## Drift canary (in template since 2026-08-20, build `baf3887b…`, 2725 lines)
Two independent detectors — a fleet build change that bypasses `fleet_sync` must trip at least one:
1. **Boot log (detector 1).** The template calls `_log_build_identity()` at startup, logging
   `BUILD-IDENTITY path=/workspace/guest_agent_server.py md5=<h> lines=<n> marker=<h> <n>`.
   Read the **latest** line: `docker logs <c> 2>&1 | grep BUILD-IDENTITY | tail -1` — logs
   accumulate across restarts, `head`/first match gives you the stale build. The line is on
   **stderr** (python logging default), so always `2>&1` before grepping. Best-effort by design:
   any failure logs a warning and never blocks boot.
2. **Audit marker (detector 2).** `fleet_sync` writes a `.build` marker (`<template_md5> <lines>`)
   into each workspace. `fleet_audit.py` compares the running hash to the marker and prints a
   named `DRIFT-MARKER: guest_N running hash X != marker Y` line to stderr + sets `marker_stale: true`
   in the manifest. This catches file edits made outside the sync path (hand-edits, failed syncs).

Negative-proof recipe (test guest 3): append one line to the workspace file → both detectors fire
(audit DRIFT-MARKER; boot log md5 ≠ marker after restart) → `fleet_sync.py` restores (backup,
verify, restart, healthy) → audit back to 0 live-drifted. Run it after changing the canary code
itself, or whenever a guest "should" be drifted but nothing reports it.

## Naming guard (in template since 2026-08-20)
`BLOCKED_PERSON_NAMES` (exact-match, case/punctuation-insensitive, applied to the **cleaned**
name): michael gulden, michael, becca, becca gulden, test, tester, test guest, guest test, qa,
dev. Extensible via `GUEST_BLOCKLIST_NAMES` env (comma/space separated) — **extend via data, never
by code** (a per-guest code edit re-creates the drift bug). Guarded at both chart-creation entry
points: chart-intent with explicit name, and compare-mode `person_name` capture. Blocked →
`NAMING-GUARD` warning log + user-facing refusal, nothing filed.
- Unit proof: `tests/test_guest_naming_guard.py` (10 tests; `/usr/bin/python3 -m pytest` — the
  platform venv lacks pytest, system python has 9.0.3 + fastapi). Imports the canonical template
  module directly so it proves what ships.
- Existing mis-files (read-only sweep 2026-08-20): only guests 2 & 23 hold `michael gulden` /
  `becca gulden` records (`people/index.json` + `charts/personal/*_gulden/`). Deletion is
  Michael's call — sweep was strictly read-only.

## Scope discipline
- Default to the **entire fleet, test guests included.** When 4 of 12 guests were flagged as stale, Michael said "continue and widen it to all 12 guests. Most of those are tests that I made." Test guests are part of the fleet and get the same build.
- Keep a timestamped `.bak-<stamp>` next to every replaced file. Prune only after ~1 week of clean operation, and only with Michael's OK — he is cautious about deletions.
- Dead workspaces (no container) get the file update too — they may be restarted later and it costs nothing.

## Pitfalls
- **`/app/guest_agent_server.py` inside some images is a stale decoy** (e.g. 2281 lines). The served file is `/workspace/guest_agent_server.py`. Never audit or fix the `/app` copy.
- A bug "already fixed in the template" can still be live in stale guests (the Michael-Gulden misfiled charts were produced by the 2286 build even though the template was clean). Verify the fix in the **running copy**, not the template.
- `docker exec` against a dead container hangs — wrap every exec in `timeout 15`.
- Ownership: files copied as `ubuntu` (mode 664) are readable by the container, but normalize to `1000:1000` to match workspace ownership. EACCES bites the moment the container rewrites anything in its workspace.
- Don't rebuild images to ship code — the mount makes it moot.
- Checking `/docs` immediately after restart reads stale state; the healthcheck has a 15s start period.

## Verification (what "done" means)
- `fleet_audit.py` exit 0: 12 records, 10 live / 2 decommissioned (40, 42), **0 live-drifted**
- Every workspace server file md5 == template md5; in-container `wc -l` == template line count on all live guests
- Latest `BUILD-IDENTITY` boot log line: md5 == marker, lines == template (all live guests)
- `/docs` returns OK in every live container; `docker ps` shows all healthy
- Naming guard: `pytest tests/test_guest_naming_guard.py` green + `grep -c is_blocked_person_name /workspace/guest_agent_server.py` ≥ 3 in a live container
- Handoff state (`state/current.json`) updated with the new matrix and backup stamp

## Pitfalls
- **`docker logs` grep for BUILD-IDENTITY needs `2>&1` + `tail -1`.** The line is on stderr and logs
  accumulate across restarts — a first-match or stdout-only grep reports the previous build's identity
  (this produced a false canary failure on 2026-08-20).

## Session detail
- `references/build-drift-2026-08-19.md` — the 2286/2594/2593/2656 matrix, the Michael-Gulden incident, and what the feature-level diff proved.
- `references/fleet-hardening-2026-08-20.md` — fleet_audit.py/fleet_sync.py tooling, the two-detector drift canary, the naming guard, the Linear HFG tree (GRO-4797), the review-packet handoff, and the naming-sweep findings on guests 2/23.
