---
type: Audit
title: Prismatic Cron Runner — Full Status Audit (2026-09-12)
description: End-to-end audit of the Prismatic Engine cron subsystem (cron_runner, cron_authority, cron_receipts, swarmcron) and its integration state. Documents what's built, what's wired, what's missing, and the migration path from Hermes native cron to the portable prismatic cron runner.
tags: [cron, prismatic, swarmcron, audit, scheduler, migration, infra]
status: current
owner: fred
last_verified: 2026-09-12
verified_by: fred
related:
  - audits/journal-system-and-mcp-audit-2026-08-21.md
  - standards/cron-alert-output-contract.md
  - skills/hermes/orchestrator/operations/scheduled-journal-recaps/SKILL.md
linear_issue: null
git_path: okf/audits/prismatic-cron-runner-status-audit-2026-09-12.md
---

# Prismatic Cron Runner — Full Status Audit

**Auditor:** Fred (Hermes profile `orchestrator`) · **Date:** 2026-09-12 · **Method:** live verification — source code read, test suite executed, process/state inspection.

## 1. System Architecture (what exists)

The prismatic cron subsystem has **three layers**, each at a different maturity:

```
┌─────────────────────────────────────────────────────────────────────┐
│  LAYER 3: HERMES NATIVE CRON (what's actually running)              │
│  ~/.hermes/profiles/<name>/cron/jobs.json                           │
│  Scheduler: hermes-agent gateway cron loop                          │
│  Jobs: per-profile, LLM agent or no_agent script                    │
│  Status: LIVE but fragile (import bugs break agent-mode jobs)       │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 2: SWARMCRON (portable scheduler package)                    │
│  ~/Github/swarmcron/  (v0.3.0, zero-dep, JSON store)               │
│  Scheduler: croniter-based evaluator, DAG dependencies              │
│  Status: BUILT, TESTED, but NOT INSTALLED in any venv               │
├─────────────────────────────────────────────────────────────────────┤
│  LAYER 1: PRISMATIC CRON AUTHORITY (GRO-4317 / CRONRUNNER-1)       │
│  prismatic/cron_runner.py      (1,814 lines)                       │
│  prismatic/cron_authority.py   (3,155 lines)                       │
│  prismatic/cron_receipts/      (schema + validation)               │
│  Scheduler: none — run_once() is a one-shot executor               │
│  Status: BUILT, TESTED (97 tests pass), but ZERO callers            │
└─────────────────────────────────────────────────────────────────────┘
```

### Layer 1: Prismatic Cron Authority (the "canonical" core)

**Files:**
- `prismatic/cron_runner.py` (1,814 lines) — trigger envelope, registry snapshot, `run_once()`, `reconcile_expired_attempts()`
- `prismatic/cron_authority.py` (3,155 lines) — SQLite schema v3, `CronAuthorityStore`, migration engine, DB triggers
- `prismatic/cron_receipts/schema.py` — `CronRunReceipt` dataclass + JSON schema validation

**Key API surface:**
- `CronTriggerEnvelope` — frozen dataclass: trigger_event_id, trigger_kind (scheduled/manual/retry/hook/recovery), transport_kind (http/hook/recovery/internal), cron_id, registry_generation, schedule_bucket, command_digest, release_digest, submitted_at
- `CronRegistrySnapshot` — frozen dataclass: cron_id, command_digest, release_digest, argv, cwd, state, depends_on, catch_up_policy
- `run_once()` — the main entry point: validates envelope → migrates DB → delivers trigger → resolves aggregate → claims execution → invokes adapter → finalizes
- `reconcile_expired_attempts()` — cleanup for orphaned claims
- `CronAuthorityStore` — SQLite-backed store with lease management, projection reads, sweep cursors

**Design intent:** This is the *transaction-safe execution authority* — it manages the lifecycle of a single cron execution (claim → run → finalize → receipt) with idempotency, collision detection, and dependency gating. It is NOT a scheduler. It has no tick loop, no daemon, no "find due jobs and fire them" logic.

**Caller count: ZERO.** No code outside `tests/` and `cron_runner.py` itself imports `cron_runner` or `cron_authority`. The `prismatic/cron_receipts/` module is imported only by `cron_runner.py`.

**Test status:** 97 tests pass (`test_cron_runner.py`, `test_cron_authority.py`, `test_cron_receipts.py`, `test_native_crons.py`, `test_seo_cron_extensions.py`). The core logic is verified.

### Layer 2: SwarmCron (the portable scheduler)

**Location:** `~/Github/swarmcron/` (v0.3.0, MIT, zero external dependencies)

**What it provides:**
- `SwarmCronRegistry` — JSON file store (`~/.swarmcron/tasks.json`) with file-locking, atomic writes, DAG cycle detection
- `SwarmCronTask` — dataclass: id, name, schedule (5-field cron or "manual"), command, cwd, group, state, depends_on, last_run_at, last_status, last_exit_code, last_stdout, last_stderr, concurrency_policy, timeout_seconds
- `CronScheduleEvaluator` — pure-Python 5-field cron parser (no croniter dependency)
- `registry.mutate()` — lifecycle actions: run, recover, pause, resume, activate, deactivate, delete
- `registry.check_dependencies()` — fail-closed upstream state verification
- `CronRunReceipt` — machine receipt: status, exit_code, duration_ms, stdout, stderr
- `SwarmcronDaemon` — background hypervisor reaper + GC + ledger auditor (asyncio)
- CLI: `swarmcron list|register|run|recover|mutate|export-crontab`
- FastAPI router (optional dep)

**Design intent:** This is the *portable, zero-dependency cron scheduler* — the thing that actually finds due jobs and fires them. It's designed to be dropped into any Python project or microservice.

**Install status:** NOT INSTALLED in the hermes-agent venv. Declared as a git dep in `prismatic-engine/pyproject.toml` (both main and `primitives` extras) but never `pip install`ed. Local clone exists at `~/Github/swarmcron/` with egg-info (was installed at some point, but not in the current venv).

**Integration gap:** SwarmCron is the *scheduling engine* but it's not connected to:
1. The prismatic cron authority (Layer 1) — no bridge between swarmcron's `mutate()` and prismatic's `run_once()`
2. The Hermes gateway cron loop — no adapter that translates Hermes `jobs.json` entries into swarmcron tasks
3. Any daemon or tick loop — swarmcron has a `SwarmcronDaemon` for GC/audit but no "tick every N seconds, check which tasks are due, fire them" loop in the core

### Layer 3: Hermes Native Cron (what's actually running)

**Location:** `~/.hermes/profiles/<name>/cron/jobs.json` (per-profile)

**Scheduler:** The hermes-agent gateway's built-in cron loop (in `hermes-agent-fork/cron/scheduler.py`). Ticks periodically, checks `jobs.json` for due jobs, fires them.

**Job types:**
- `no_agent: true` — runs a script, captures stdout, done (fast, no LLM)
- `no_agent: false` — spawns a full agent session with a prompt (LLM, tools, delivery)

**Current journal jobs (orchestrator profile):**

| Job | Type | Schedule | Last Status | Error |
|-----|------|----------|-------------|-------|
| Hermes daily journal snapshot | no_agent | every 60m | ❌ error | `ModuleNotFoundError: No module named 'swarmlock'` (fixed: shebang) |
| Hermes daily journal recap | agent | 23:59 UTC | ❌ error | `cannot import name 'is_job_runnable' from 'cron.jobs'` (fixed: patch) |
| Becca Journal Recap | agent | 23:59 UTC | ❌ error | same `is_job_runnable` import (fixed by same patch) |
| Becca Journal Snapshot | no_agent | every 60m | ✅ ok | — |
| Weekly Journal Rollup | agent | Sun 10:00 | ❌ error | same `is_job_runnable` import (fixed by same patch) |
| Monthly Journal Continuity Audit | no_agent | 1st 09:00 | ✅ ok | — |

**Root cause of agent-mode failures:** `cron/jobs.py` in the hermes-agent-fork was missing `is_job_runnable()` — a function added in upstream commit `c7a5de7d6e` that only exists on feature branches, not on `main`. The fork's `cronjob_tools.py` and `hermes_cli/config.py` import it, but `cron/jobs.py` never had it. Fixed 2026-09-12 by adding the function (backport from upstream).

## 2. What's actually running vs. what's designed

| Component | Designed | Built | Tested | Wired | Running |
|-----------|----------|-------|--------|-------|---------|
| Prismatic cron authority (Layer 1) | ✅ | ✅ | ✅ (97 tests) | ❌ (0 callers) | ❌ |
| SwarmCron scheduler (Layer 2) | ✅ | ✅ | ✅ (local) | ❌ (not installed) | ❌ |
| Hermes native cron (Layer 3) | n/a | ✅ | n/a | ✅ | ⚠️ (fragile) |
| Journal pipeline | ✅ | ✅ | ✅ | ✅ | ⚠️ (2/6 jobs broken, now fixed) |
| Cron daemon/tick loop | ❌ | ❌ | — | — | — |
| Hermes → prismatic bridge | ❌ | ❌ | — | — | — |

## 3. Gap Analysis

### G1 — No tick loop / scheduler daemon — **CRITICAL**
Neither Layer 1 nor Layer 2 has a "check every N seconds which jobs are due and fire them" loop. Layer 1's `run_once()` is a one-shot executor that requires a pre-built envelope. Layer 2 has `CronScheduleEvaluator.get_next_run()` and `is_missed()` but no loop that calls them. The only thing actually scheduling jobs is the Hermes gateway's native cron loop (Layer 3).

**Fill:** Build a tick loop (daemon or gateway-integrated) that:
1. Loads the swarmcron registry (or prismatic authority registry)
2. Evaluates which tasks are due (using `CronScheduleEvaluator`)
3. For each due task, builds a `CronTriggerEnvelope` and calls `run_once()`
4. Handles catch-up policies (skip, run_once, bounded_replay)

### G2 — No bridge between swarmcron and prismatic authority — **CRITICAL**
SwarmCron's `SwarmCronTask` and `registry.mutate()` are the *scheduling* layer. Prismatic's `CronTriggerEnvelope` and `run_once()` are the *execution authority* layer. They speak different languages:
- SwarmCron: `task.id`, `task.command`, `task.schedule` → `registry.mutate(task_id, "run")`
- Prismatic: `envelope.cron_id`, `envelope.command_digest`, `envelope.trigger_event_id` → `run_once(envelope=...)`

No adapter translates between them. A swarmcron task fire doesn't produce a prismatic trigger envelope, and a prismatic execution doesn't update a swarmcron task's `last_run_at`/`last_status`.

**Fill:** Build an adapter class (e.g. `SwarmCronPrismaticAdapter`) that implements the prismatic `BoundedProcessAdapter` protocol and bridges the two: swarmcron fires → adapter builds envelope → `run_once()` executes → adapter updates swarmcron task receipt.

### G3 — SwarmCron not installed — **HIGH**
Declared in `pyproject.toml` but never installed in the hermes-agent venv. The local clone at `~/Github/swarmcron/` has egg-info (was installed at some point) but the current venv doesn't have it.

**Fill:** `pip install -e ~/Github/swarmcron/` in the hermes-agent venv (editable install, so local changes are live). Or: `pip install git+https://github.com/mbgulden/swarmcron.git@main`.

### G4 — No cron daemon in the Hermes gateway — **HIGH**
The Hermes gateway runs its own cron loop (Layer 3) but has no awareness of the prismatic cron subsystem. There's no gateway module that:
- Loads the prismatic cron registry
- Participates in the tick loop
- Reports cron execution status to the dashboard

**Fill:** Either (a) add a gateway module that integrates the prismatic tick loop, or (b) run the prismatic cron daemon as a separate systemd service that communicates with the gateway via the FastAPI router.

### G5 — Journal jobs are still on Hermes native cron — **MEDIUM**
The journal pipeline (snapshot, recap, weekly rollup, monthly audit) runs as Hermes native cron jobs in the orchestrator profile. This is fragile because:
1. Agent-mode jobs depend on the hermes-agent-fork's cron scheduler (which just broke from the `is_job_runnable` import bug)
2. No LLM involvement is needed for the snapshot job (no_agent), but the recap job does use an LLM
3. The migration to prismatic cron (GRO-4214..4260) is planned but not started

**Fill:** Migrate journal jobs to swarmcron tasks (deterministic, no LLM for snapshot; LLM agent for recap). This is the first concrete use case for the prismatic cron runner.

### G6 — No CLI entry point for prismatic cron — **LOW**
The prismatic cron subsystem has no `prismatic cron` CLI command. The swarmcron CLI (`swarmcron list|register|run|...`) exists but operates on swarmcron's own store, not the prismatic authority.

**Fill:** Add a `prismatic cron` subcommand that wraps the prismatic cron runner (list, run, status, reconcile).

### G7 — 17 swarm* packages declared, only 5 installed — **LOW**
`pyproject.toml` declares 17 swarm* packages (swarmcron, swarmcurator, swarmlock, swarmrouter, swarmledger, swarmsaga, swarmgate, swarmproof, swarmcas, swarmconsensus, swarmmemory, swarmmerge, swarmmesh, swarmmeter, swarmsandbox, swarmvault). Only 5 are installed in the venv (swarmlock, swarmledger, swarmsaga, swarmgate, swarmproof). The rest are declared but not installed.

**Fill:** Not a blocker for cron, but worth tracking. The cron subsystem only needs swarmcron (plus swarmlock which is already installed).

## 4. What was fixed today (2026-09-12)

1. **`is_job_runnable` import error** — Backported from upstream commit `c7a5de7d6e` into `hermes-agent-fork/cron/jobs.py`. Added `is_job_runnable()`, `_has_pause_marker()`, and rewrote `effective_job_state()` to match the upstream semantics (enabled flag is authoritative, pause markers are a second gate). 302 cron tests pass.

2. **`prismatic-journal-snapshot` shebang** — Changed from `#!/usr/bin/python3` (system Python, missing swarmlock) to `#!/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python` (venv Python, has all deps). Verified: `prismatic-journal-snapshot --force` exits 0 and writes to the inbox.

3. **Gateway restart** — Killed the stale gateway process (running since Sep 9) and restarted via systemd. The new gateway picks up the `is_job_runnable` fix.

## 5. Recommended path to "fully functional"

### Phase 1: Unblock (this session) ✅
- [x] Fix `is_job_runnable` import (unblocks all agent-mode cron jobs)
- [x] Fix snapshot shebang (unblocks journal snapshot)
- [x] Restart gateway
- [ ] Verify journal recap runs tonight (23:59 UTC) — first run with the fix

### Phase 2: Install swarmcron (next session)
- [ ] `pip install -e ~/Github/swarmcron/` in hermes-agent venv
- [ ] Verify `swarmcron list` works
- [ ] Register the journal snapshot task in swarmcron
- [ ] Verify `swarmcron run journal-snapshot` works

### Phase 3: Build the tick loop (the big one)
- [ ] Design the tick loop (daemon vs gateway-integrated)
- [ ] Implement: load registry → evaluate due tasks → build envelope → `run_once()` → update receipt
- [ ] Handle catch-up policies
- [ ] Integration test: register a task, let it fire, verify receipt

### Phase 4: Bridge swarmcron ↔ prismatic authority
- [ ] Build `SwarmCronPrismaticAdapter` (implements `BoundedProcessAdapter`)
- [ ] Wire: swarmcron fire → adapter → `run_once()` → adapter updates swarmcron receipt
- [ ] Integration test: full round-trip

### Phase 5: Migrate journal jobs
- [ ] Move journal snapshot to swarmcron (deterministic, no_agent)
- [ ] Move journal recap to swarmcron (LLM agent)
- [ ] Move weekly rollup to swarmcron
- [ ] Move monthly audit to swarmcron
- [ ] Decommission Hermes native cron jobs for journal

### Phase 6: Generalize
- [ ] Migrate other Hermes native cron jobs to prismatic cron runner
- [ ] Add `prismatic cron` CLI
- [ ] Dashboard integration (Logs → Cron tab)
- [ ] PE SQLite migration (GRO-4189) for events

## 6. Key files and paths

| Component | Path |
|-----------|------|
| Prismatic cron runner | `/home/ubuntu/work/prismatic-engine/prismatic/cron_runner.py` |
| Prismatic cron authority | `/home/ubuntu/work/prismatic-engine/prismatic/cron_authority.py` |
| Prismatic cron receipts | `/home/ubuntu/work/prismatic-engine/prismatic/cron_receipts/` |
| Prismatic cron tests | `/home/ubuntu/work/prismatic-engine/tests/test_cron_*.py` |
| SwarmCron package | `/home/ubuntu/Github/swarmcron/` |
| SwarmCron core | `/home/ubuntu/Github/swarmcron/swarmcron/core.py` |
| SwarmCron scheduler | `/home/ubuntu/Github/swarmcron/swarmcron/scheduler.py` |
| SwarmCron daemon | `/home/ubuntu/Github/swarmcron/swarmcron/daemon.py` |
| SwarmCron CLI | `/home/ubuntu/Github/swarmcron/swarmcron/cli.py` |
| Hermes native cron (orchestrator) | `~/.hermes/profiles/orchestrator/cron/jobs.json` |
| Hermes fork cron/jobs.py | `/home/ubuntu/work/hermes-agent-fork/cron/jobs.py` |
| Journal corpus | `~/work/Hermes-Research/journals/` |
| Journal MCP server | `/home/ubuntu/work/journal-mcp-server/server.py` |
| Cron job templates | `/home/ubuntu/work/prismatic-engine/templates/cron/cron-job-templates.md` |

---
*All timestamps UTC. Test counts from 2026-09-12 live run. Re-run this audit after Phase 2 (swarmcron install) — the "Wired" and "Running" columns will change.*
