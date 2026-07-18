---
type: Incident
title: Dispatcher fix incident — 2026-06-23
description: Incident report for the dispatcher fix and recovery path. Promoted selectively from conflicting PR #5.
resource: okf/incidents/2026-06-23-dispatcher-fix.md
tags: [incident, dispatcher, prismatic, webhook, recovery]
timestamp: 2026-07-18T00:00:00Z
linear_issue: null
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/incidents/2026-06-23-dispatcher-fix.md
last_verified: 2026-07-18
verified_by: fred
status: current
---

# AGY/Ned/Kai dispatcher fix — 2026-06-23

## The bug

The Ned + Kai dispatchers were invoking AGY as a single subprocess with a "process these N issues" prompt and a 5-min timeout. That can't possibly work for 20+ issues since AGY is meant for individual task execution, not batch processing.

Symptom: every dispatcher run ended with "AGY timed out after 5 min" → 0 work done.

## The root cause

Architectural mistake. The right design is:
- **Dispatcher** = queue producer (writes task spec to `/tmp/issue-batches/{iid}.txt`)
- **AGY supervisor** = queue consumer (polls every 90s, spawns workers per spec, monitors progress, validates RESULT.md)

The dispatchers were trying to BE the queue consumer + worker + validator all at once, with a 5-min hard cap. Of course it timed out.

## The fix

Commit `e0b3b8a` (in `~/.hermes/profiles/orchestrator/scripts/`):

1. **Ned dispatcher** (`ned_delta_dispatcher.py`): `invoke_agy()` now writes task specs to `/tmp/issue-batches/{iid}.txt` for each open Ned issue, with the issue description + an execution contract.

2. **Kai dispatcher** (`kai_delta_dispatcher.py`): same fix, with `WORKDIR: active-oahu-tours` for Kai-specific issues.

3. **Reset 23 stuck In Progress issues back to Todo** so the supervisor picks them up.

4. **Wrote 46 task specs** to `/tmp/issue-batches/` (one per open AGY/Ned/Kai issue).

5. **Started the AGY supervisor manually** — it picked up 35 issues in 2 polls, 3 workers are now actively running.

## The result (after 5 min)

| Agent | Before | After |
|---|---|---|
| AGY | 0 Done, 21 In Progress (stuck) | 1 Done, 4 In Progress (active), 13 Todo |
| Kai | 0 Done, 4 Todo | 3 Done, 4 Todo |
| Ned | 0 Done, 9 Todo | 4 Done, 7 Todo |
| Ned-infra | 0 Done, 5 Todo | 4 Done, 4 Todo |

The supervisor's 2-min heartbeat signals are firing: "🟢 healthy — sandbox activity recent".

## Anti-pattern rule

**Never batch-invoke AGY as a single subprocess.** Always write to `/tmp/issue-batches/` and let the supervisor handle distribution.

A batch of 20 issues can't be done in 5 minutes — it can take 30-60 minutes. The dispatcher's job is to queue, not to process.

## Related issues

- GRO-2237: [INFRA] Investigate 6 silent cron fails root cause (this is one of them)
- GRO-2229: [DONE] Refactor pipeline steps into library + thin CLI wrapper
- The process-overhaul doc (`okf/standards/prismatic-engine-process-overhaul.md`) should be updated to include this lesson

## Files changed

- `/home/ubuntu/.hermes/profiles/orchestrator/scripts/ned_delta_dispatcher.py` — invoke_agy() rewritten
- `/home/ubuntu/.hermes/profiles/orchestrator/scripts/kai_delta_dispatcher.py` — invoke_agy() rewritten
- `/tmp/issue-batches/` — 46 task specs written (auto-cleaned after consume)

## Change log

- 2026-06-23 17:00 UTC: Bug identified, fix applied, supervisor started, 3 workers running.
