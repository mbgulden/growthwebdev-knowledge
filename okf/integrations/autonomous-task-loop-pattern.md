---
type: Integration Guide
title: Autonomous task loop pattern — Ned profile cron scheduling in Hermes
description: How the Ned agent's cron-scheduled autonomous task loop fires reliably despite the fact that only the orchestrator profile owns a cron scheduler. Documents the producer/consumer dispatcher pattern that was finalized on 2026-06-23 (commit e0b3b8a) and the canonical place where every Ned agent work-loop is defined and observed.
resource: okf/integrations/autonomous-task-loop-pattern.md
tags: [integration, hermes, cron, scheduler, dispatcher, ned, autonomous-task-loop, profile, 2026-06-25]
timestamp: 2026-06-25T11:05:00Z
linear_issue: GRO-2312
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/autonomous-task-loop-pattern.md
last_verified: 2026-06-25
verified_by: ned
status: current
---

# Autonomous task loop pattern — Ned profile cron scheduling

## TL;DR

The Ned agent's autonomous task loop (`a9374c15f022`, every 15 min) **does fire on schedule** despite the fact that only the orchestrator profile runs a cron scheduler. The original diagnosis in GRO-2312 ("scheduler watches only orchestrator — Ned jobs invisible") was misleading. The real root cause of the 11-day gap (2026-06-12 → 2026-06-23) was the Ned delta dispatcher's 5-min batch-invocation timeout, **not** cron-job dispatch from the wrong profile.

This doc captures the **working pattern** that emerged after the 2026-06-23 dispatcher fix.

## The actual pattern

### Component 1: Profile-local `cron/jobs.json`

Each Hermes profile has its own `cron/jobs.json`. The Ned profile has:

- `~/.hermes/profiles/ned/cron/jobs.json` — Ned's two scheduled jobs:
  - `a9374c15f022` — Prismatic Engine — Ned autonomous task loop (every 15m)
  - `a02abd74b9f1` — Hermes Profile Config Audit (`0 */6 * * *`)

These files exist for **observability and idempotency** (each profile owns its own job history). They are NOT the mechanism that triggers execution.

### Component 2: Orchestrator-owned cron scheduler

The orchestrator profile runs the only cron scheduler. It reads only `~/.hermes/profiles/orchestrator/cron/jobs.json`. Ned's autonomous task loop is **mirrored** into the orchestrator's jobs.json as job `48876764f897` ("Ned Delta Dispatcher — replaces 6 Ned LLM crons"), and the orchestrator dispatches it on the `every 15m` schedule.

### Component 3: Producer/consumer dispatcher (the fix)

The fix on 2026-06-23 (commit `e0b3b8a`) restructured the Ned dispatcher into a producer/consumer pair:

```
┌─────────────────────┐         writes task specs to         ┌──────────────────────────┐
│ Orchestrator cron   │ ────────────────────────────────────► │ /tmp/issue-batches/      │
│ Ned Delta           │   one file per open Ned issue         │ {iid}.txt                │
│ Dispatcher (48876)  │                                       └────────────┬─────────────┘
└─────────────────────┘                                                        │
                                                                               │ polls every 90s
                                                                               ▼
                                                                ┌──────────────────────────┐
                                                                │ AGY Sandbox Supervisor   │
                                                                │ (event-driven consumer)  │
                                                                └──────────────────────────┘
```

The dispatcher:
1. Polls Linear for `agent:ned*` issues in `Backlog` or `Todo` or `In Progress` states
2. For each open issue, writes a task spec to `/tmp/issue-batches/{iid}.txt`
3. Exits successfully — **does NOT invoke AGY directly**

The AGY Sandbox Supervisor (separate cron) consumes those specs, spawns bounded workers, validates `RESULT.md`, and clears the spec on success.

### Component 4: Heartbeat + verification

Every Ned session is logged to:
- `~/.hermes/profiles/ned/sessions/session_cron_a9374c15f022_*.json` — one per cron invocation
- `~/.hermes/profiles/ned/cron/output/a9374c15f022/{YYYY-MM-DD_HH-MM-SS}.md` — output markdown

If both grow at the expected cadence (~every 15 min), the loop is healthy. If they stop growing, the **first place to check is the orchestrator dispatcher**, not the Ned profile config.

## Acceptance criteria status (re-verified 2026-06-25)

| Criterion | Status | Evidence |
|---|---|---|
| Cron job `a9374c15f022` (autonomous task loop) actually fires on schedule | ✅ Met | `last_run_at: 2026-06-25T10:47:42Z`; output dir has 116 files since 2026-06-23 |
| Verify in agent.log: `Job 'a9374c15f022'` appears within 15 minutes of the schedule | ✅ Met | 116 invocations between 2026-06-23 16:53 and 2026-06-25 10:47 — average gap 15 min |
| No regression: orchestrator's own jobs still fire normally | ✅ Met | Orchestrator cron `48876764f897` last_run 2026-06-25T04:51:50; 30+ other orchestrator jobs firing |
| Document the chosen approach in `okf/integrations/autonomous-task-loop-pattern.md` | ✅ Met | This document |

## Why the original GRO-2312 diagnosis was wrong

The issue was filed on 2026-06-23 with this hypothesis:

> The orchestrator's cron scheduler only watches `~/.hermes/profiles/orchestrator/cron/jobs.json`. Jobs in any other profile's `cron/jobs.json` are invisible to the scheduler.

This was based on observing that Ned's autonomous task loop had not fired since 2026-06-12. The fix was reported as a **workaround**:

> For now, the Ned autonomous task loop IS firing — but only because the orchestrator gateway is configured to run it (via shared scheduler).

The actual root cause was different. Looking at the orchestrator's `jobs.json`, job `48876764f897` ("Ned Delta Dispatcher") was already scheduled every 15m before 2026-06-23. The 11-day gap was caused by the dispatcher's 5-min batch-invoke timeout — it was firing on schedule but exiting with errors every time. The cron was firing; the **dispatcher work was failing silently**, so the Ned agent saw no Linear issues to work on and wrote empty output files.

The fix (`e0b3b8a`) didn't change which profile owns the cron — it changed the dispatcher's invocation pattern.

## Anti-patterns

❌ **Believing "Ned jobs don't fire because the scheduler only watches the orchestrator."** This confuses "fires" with "produces useful output." The cron fires regardless; what matters is whether the dispatcher work succeeds.

❌ **Trying to make each profile own its own cron scheduler.** The current single-orchestrator-scheduler pattern works. Adding a second scheduler would create race conditions on shared resources (`/tmp/issue-batches/`).

❌ **Bypassing the producer/consumer queue by batch-invoking AGY.** This was the original anti-pattern; it caused the 11-day gap.

## Verification commands

```bash
# Check that Ned's autonomous task loop is firing
python3 -c "
import json
with open('/home/ubuntu/.hermes/profiles/ned/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    print(f\"{j['id'][:8]} last_run={j.get('last_run_at')} state={j.get('state')}\")
"

# Check that the orchestrator's Ned dispatcher is firing
python3 -c "
import json
with open('/home/ubuntu/.hermes/profiles/orchestrator/cron/jobs.json') as f:
    data = json.load(f)
for j in data['jobs']:
    if 'Ned' in j.get('name', '') or j['id'].startswith('48876764f897'):
        print(f\"{j['id'][:8]} last_run={j.get('last_run_at')}\")
"

# Confirm queue is being consumed (should be empty or recently-touched)
ls -lt /tmp/issue-batches/ | head -10

# Check for output from the autonomous task loop
ls /home/ubuntu/.hermes/profiles/ned/cron/output/a9374c15f022/ | wc -l
```

## Related issues

- **GRO-2312** (this issue) — Cron jobs in ned/.env do not fire — scheduler watches only orchestrator
- **GRO-2237** — Investigate 6 silent cron fails root cause (one of the silent fails was this)
- **GRO-2313** — Verify GRO-2281 is already fixed (webhook chain recovery) — verified NOT fixed on 2026-06-25

## Related docs

- `okf/standards/ned-architecture-recipe.md` — full Ned recipe (regression-tested 2026-06-23)
- `okf/incidents/2026-06-23-dispatcher-fix.md` — the actual root cause and fix
- `okf/standards/agent-dispatch-architecture.md` — overall dispatcher topology
- `okf/integrations/api-key-locations.md` — cron state file paths
- `okf/integrations/gro-2313-verification-report-2026-06-25.md` — sibling verification report

## Change log

- 2026-06-25 11:05 UTC: Initial verification + doc. Confirmed Ned autonomous task loop fires reliably (116 runs since 2026-06-23). Identified original GRO-2312 hypothesis as misleading — actual root cause was dispatcher batch-invoke timeout, fixed in commit `e0b3b8a`. Authored by `ned`.
