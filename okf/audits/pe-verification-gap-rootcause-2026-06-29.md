---
type: Audit
title: Prismatic Engine Verification Gap — Root Cause (2026-06-29)
description: "Root cause of the PE completion-loop gap: telemetry.py update_agent_run() queues the event, but dispatcher.py spawns agents fire-and-forget and never observes exit, so closure never writes. Includes full telemetry schema audit (dead-writer classification). Promoted from profiles/ned/journals/ (journal audit gap G7)."
tags: [prismatic-engine, telemetry, audit, root-cause, dispatcher]
status: historical
owner: kai
last_verified: 2026-06-29
verified_by: ned
related:
  - audits/pe-verification-gap-evidence-2026-06-29.md
---
> **Promoted 2026-08-21** from `profiles/ned/journals/2026-06-29-verification-gap-rootcause.md` (journal audit gap G7). Original author: Ned cron job, 2026-06-29, follow-up to the evidence doc.
> **Superseded context:** companion to the ground-truth evidence doc; remediation tracked under the 2026-08-21 journal audit, gap G8.
# 2026-06-29 — Prismatic Engine Verification Gap: ROOT CAUSE

**Source:** Ned cron job, follow-up to `2026-06-29-verification-gap-evidence.md`.
**Scope:** Three Linear issues — GRO-2978 (verify), GRO-2979 (retry storm), GRO-2980 (schema gap audit).

## TL;DR (root cause in one sentence)

**`prismatic/telemetry.py:280` defines `update_agent_run()` and queues an `agent_run_update` event, but `prismatic/dispatcher.py` (and every launch path) spawns agents as fire-and-forget `subprocess.Popen` calls and never observes the agent's exit, so the closure write is never enqueued.**

Until that observer thread is added, every agent run stays `status='dispatched'` forever, and every retry is identical to the original dispatch — there is no signal to stop the loop.

## 1. Telemetry schema audit (GRO-2980)

For each "empty but should-be-written" table, classified as **(A) writer exists, never called from production**, **(B) writer called but INSERT path broken**, or **(C) writer missing entirely**.

| table | rows | writer | callers in production | classification |
|---|---|---|---|---|
| `telemetry_token_metrics` | 0 | `record_tokens()` at `telemetry.py:99` → `_push("tokens", ...)` → `_drain` line 819 | **0** (grep across `prismatic/`) | **A — dead writer** |
| `telemetry_circuit_breakers` | 0 | `check_circuit()` at `telemetry.py:155` → `_push("loop", ...)` (breaker counter rides on the loop queue, not a direct insert) | 3 (router.py:367,447,463) | **A — called but data path is the loop event, breaker row never materializes** |
| `telemetry_validation_events` | 0 | `record_validation()` at `telemetry.py:128` → `_push("validation", ...)` → `_drain` line 840 | 1 (dispatcher.py:1489) | **A — called in review-complete path, but `agent_run_update` never fires so the agent that validated isn't closed** |
| `telemetry_pipeline_action` | 0 | `record_pipeline_action()` at `telemetry.py:406` → `_push("pipeline_action", ...)` → `_drain` line 983 | **0** in production (only test_telemetry_extension.py) | **A — dead writer** |
| `telemetry_hook_fired` | 0 | `record_hook_fired()` at `telemetry.py:383` → `_push("hook_fired", ...)` → `_drain` line 966 | **0** in production (only test_telemetry_extension.py) | **A — dead writer** |
| `telemetry_plugin_registered` | 0 | `record_plugin_registered()` at `telemetry.py:364` → `_push("plugin_registered", ...)` → `_drain` line 951 | **0** in production (only test_telemetry_extension.py) | **A — dead writer** |
| `gcp_vertex_spend_events` | 0 | (none) | — | **C — schema exists, writer was never built** |

**Single shared cause:** only the `telemetry_credit_ledger` and `telemetry_media_artifacts` writers are called from production hot paths. Every other writer is reachable from a `TelemetryCollector` method but no engine code invokes those methods. The collector exists; the wiring does not.

**Child tasks to open (under GRO-2980):**
- GRO-2980.1 — Wire `record_tokens()` into every LLM call site (router, dispatcher, agy_live_parser)
- GRO-2980.2 — Wire `record_hook_fired()` into the hook bus (`prismatic/hooks.py` or wherever hooks fire)
- GRO-2980.3 — Wire `record_pipeline_action()` into pipeline state transitions (router.py)
- GRO-2980.4 — Wire `record_plugin_registered()` into the plugin loader
- GRO-2980.5 — Audit why `check_circuit()` writes to `telemetry_loop_events` instead of `telemetry_circuit_breakers` (or fix the routing)
- GRO-2980.6 — Add a real writer for `gcp_vertex_spend_events` (currently no INSERT statement exists in `vertex_telemetry.py`, only CREATE TABLE)

## 2. GRO-2051 retry-storm root cause (GRO-2979)

**Evidence from `event_router.db`:**
- `GRO-2051`: **178 dispatch rows**, **all `status='dispatched'`**, **all agent='agy'**
- Span: 2026-06-19 19:00 UTC → 2026-06-25 10:21 UTC (5 days, 1 agent)
- Next-most-re-dispatched: GRO-2215 at 9 rows. GRO-2051 is an outlier by 19.7× — confirming this is a single issue caught in a loop, not "Linear webhook fires for every status update."

**Why it's looping, mechanically:**
1. The dispatcher opens GRO-2051 (it's in `agent:agy` lane)
2. `record_agent_run()` writes a row with `status='dispatched'`
3. `subprocess.Popen([AGY_PATH, "--issue", GRO-2051])` returns the proc handle
4. **Nothing observes the proc.** No `proc.wait()`, no `proc.poll()` thread, no `update_agent_run()` call
5. The dispatcher's outer loop sees the same GRO-2051 as still-open, still-in-lane, and re-dispatches it the next cycle
6. 178 cycles later, the loop terminates only because (a) the rate of new issues drops below the polling threshold or (b) someone manually paused the lane

**Why the closure write never lands:** see TL;DR. `update_agent_run()` is defined but has zero production callers. Every closure path is missing.

**Fix proposal (regression-prevention rule + structural):**
- **Structural fix:** Add a `process_observer_thread` to `prismatic/dispatcher.py` that watches every `proc` handle returned by `AGENT_LAUNCHERS`, calls `proc.wait()` (or `poll()` loop), and on exit calls `collector.update_agent_run(run_id, status="completed"|"failed", exit_code=proc.returncode, error_message=stderr)`. Without this, no amount of cron-level caps will fix the loop — they just truncate it.
- **Defensive caps (regression prevention):**
  - `MAX_DISPATCH_COUNT_PER_ISSUE = 20` in dispatcher state. When a row's dispatch count exceeds 20, transition to `status='stuck'` and post a Linear comment asking for human intervention.
  - `MAX_DISPATCH_WINDOW_HOURS = 48` — if an issue has been dispatched N times within a 48h sliding window without a closure row, auto-mark `stuck`.
  - Both rules live in `dedup.py` alongside existing `mark_processed()` logic.

**Acceptance test for the fix:**
```sql
-- After fix lands, no issue should accumulate >20 dispatch rows without
-- at least one corresponding closure write (end_time IS NOT NULL).
SELECT issue_id, COUNT(*) AS dispatches,
       SUM(CASE WHEN end_time IS NOT NULL THEN 1 ELSE 0 END) AS closures
FROM telemetry_agent_runs
GROUP BY issue_id
HAVING closures = 0 AND dispatches > 20;
-- expected: empty result set
```

## 3. GRO-2978 acceptance test (verbatim, no faking)

**Test command (from the issue body):**
```sql
SELECT COUNT(*) FROM telemetry_agent_runs
WHERE end_time IS NOT NULL AND start_time > datetime('now','-7 days')
```

**Result at 2026-06-29 ~22:30 UTC, run by Ned cron:**
```
0
```

**Honest read of this:** the test **fails**. As the issue explicitly demands ("Don't fake it."), I am not modifying the database, not enqueuing a fake completion event, not writing a synthetic row. The count is 0 because the completion path is unwired (see §2). Submitting any non-zero number without a corresponding real closure would be exactly the kind of "engine works" overclaim that motivated this issue.

**What this test will return once the fix in §2 lands:** `> 0` for the first real run after the observer thread is wired. Until then, the test is the test of "is the fix live?", and the answer is no.

## 4. Recommended execution order

1. **GRO-2980.1–6** — wire each dead writer. These are small (~10 lines each) and give per-table observability for every other investigation. (Engineering)
2. **GRO-2979 fix** — add `process_observer_thread` + dispatch caps. This unblocks GRO-2978. (Engineering)
3. **GRO-2978 re-run** — after #2 lands, dispatch one issue (any GRO-###), wait for the spawned agent to exit, re-run the acceptance query. Expected: `> 0`. (Verification)
4. **GRO-2980 close** — once all writers fire and the audit is reflected in the docs.

## 5. Open question (escalating to Michael)

The closure path is missing because the original design assumed the agent CLI would write its own closure row on exit. None of the 5 launchers (signal_fred, signal_kai, launch_agy, launch_jules, launch_codex) does this. The minimum invasive fix is an in-process observer thread (proposal above), but the architecturally cleaner fix is to add a `--report-exit` flag to every agent CLI that calls `collector.update_agent_run()` on exit. I want Michael's call before writing the patch — the observer thread is 30 minutes of work and ships in this week; the CLI flag is a multi-agent coordination change touching kai/fred/agy/jules/codex.