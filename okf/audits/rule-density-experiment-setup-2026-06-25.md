---
type: Audit
title: Rule-density experiment setup — Window B (stripped prompt) registered
description: Records the Window B cron job, the stripped prompt used, and the Window A completion status that allowed Window B to start. Feeds GRO-2277's measurement.
resource: https://github.com/mbgulden/growthwebdev-knowledge
tags: [audit, experiment, ned, prompt-engineering, rule-density, autonomous-task-loop]
timestamp: 2026-06-25T11:55:00Z
linear_issue: GRO-2278
linear_parent: GRO-2277
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/audits/rule-density-experiment-setup-2026-06-25.md
last_verified: 2026-06-25
verified_by: ned
status: current
---

# Rule-density experiment setup — 2026-06-25

Part of GRO-2277 ("Decide: does adding more rules to autonomous prompts help or hurt?"). This document records the **Window B** registration so the parent measurement task can later compare it to **Window A**.

## Window A — baseline (UNCHANGED)

| Field | Value |
|---|---|
| Cron Job ID | `a9374c15f022` |
| Name | "Prismatic Engine — Ned autonomous task loop" |
| Schedule | every 15 minutes (interval) |
| Script | `prismatic/lanes/ned/scan_tasks.py` |
| Prompt length | 2,311 chars |
| Hard rules count | 8 (see `~/.hermes/profiles/ned/scripts/autonomous-task-skeleton.md`) |
| Reference | Skeleton doc + hard rules + anti-patterns + commit-early pattern |
| Modified by this work | **NO** — left untouched for valid comparison |

### Window A completed tasks (5 — gate cleared)

| # | Issue | Date (UTC) | Outcome |
|---|---|---|---|
| 1 | GRO-2087 | 2026-06-24 04:28 | In Review (verification report) |
| 2 | GRO-2131 | 2026-06-24 02:53 | In Review (drift detector + tests, 36/36 passing) |
| 3 | GRO-2351 | 2026-06-25 10:37 | In Review (PWP file classification) |
| 4 | GRO-2312 | 2026-06-25 11:02 | In Review (autonomous-task-loop-pattern doc) |
| 5 | GRO-2267 | 2026-06-25 11:25 | In Review (publisher symlink fix) |

**Gate:** "5 tasks in Window A" — **MET 2026-06-25 11:25**.

## Window B — stripped prompt (NEW)

| Field | Value |
|---|---|
| Cron Job ID | **`20759afd096b`** |
| Name | "Window B — Ned stripped-prompt variant (rule-density experiment)" |
| Schedule | every 15 minutes (interval) — same as Window A |
| Script | `prismatic/lanes/ned/scan_tasks.py` — same scanner injection as Window A |
| Prompt length | **178 chars** (target was ≤200) |
| Hard rules count | 3 (implicit: read issue, execute, run finalize) |
| Profile | ned — same Hermes gateway as Window A |
| First run | 2026-06-25 12:10:40 UTC |
| Repeat | ∞ until parent task pauses or 5 tasks completed |

### Stripped prompt (verbatim, as registered)

```
You are Ned. Read the Linear issue from the script output above. Execute it fully. Last action: bash ~/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE_ID> ned/<ISSUE_ID> ned
```

Three implicit rules:

1. **Read** — the scan script output is in the prompt context
2. **Execute** — do the work
3. **Run finalize** — `bash ~/.hermes/profiles/ned/scripts/finalize_task.sh <ISSUE_ID> ned/<ISSUE_ID> ned`

No skeleton reference. No anti-patterns section. No hard rules listing. No doc-loading instruction.

## Constraint compliance

| Constraint from GRO-2278 | Status |
|---|---|
| DO NOT modify `a9374c15f022` | ✅ Untouched (verified 2,311-char prompt unchanged) |
| DO NOT touch `finalize_task.sh` | ✅ Untouched (shared between windows) |
| Same agent profile (ned) | ✅ Same Hermes gateway, same jobs.json |
| Same schedule (every 15m) | ✅ Both interval-based, same cadence |
| Different Job ID | ✅ New ID `20759afd096b` |
| Stripped prompt ≤200 chars | ✅ 178 chars |
| Window B starts after Window A 5 tasks OR 5 days | ✅ Window A completed 5 tasks at 2026-06-25 11:25 UTC |

## Measurement plan

For each of the next 5 tasks picked up by `20759afd096b`, capture:

1. **Completion rate** — In Review state reached, or stuck in Backlog?
2. **Tool calls** — count from cron output
3. **Wall time** — `last_run_at - next_run_at` deltas
4. **Budget exhaustion** — did it hit `max_iterations_reached`?
5. **Subjective quality** — Michael rates the final report 1-5

Compare against the 5 Window A data points above (already in commit history + session_search).

## Disable plan

After 5 tasks:

```bash
hermes cron pause 20759afd096b
hermes cron edit 20759afd096b --name "Window B — paused (5 tasks complete)"
```

Parent task GRO-2277 owns the comparison report at `okf/audits/rule-density-impact-2026-XX-XX.md`.

## Acceptance criteria status (GRO-2278)

- [x] New cron job (separate from `a9374c15f022`)
- [x] Job ID recorded for parent measurement (`20759afd096b`)
- [x] Schedule: every 15 minutes (same as `a9374c15f022`)
- [x] Same agent profile (ned) — runs through same Hermes gateway
- [ ] Run for 5 tasks then disable — **in progress**
- [ ] Data feeds into parent task's report — pending GRO-2277

## Files

- Cron job registered at `/home/ubuntu/.hermes/profiles/ned/cron/jobs.json` (key `20759afd096b`)
- This document at `okf/audits/rule-density-experiment-setup-2026-06-25.md`
- Branch: `ned/GRO-2278`
- Linear issue: GRO-2278 → will transition to **In Review** via `finalize_task.sh`
