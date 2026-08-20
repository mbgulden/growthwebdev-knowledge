---
name: ned-lane-discipline-check-telemetry-silence
description: Recipe for diagnosing telemetry-table silence in prismatic_state/event_router.db. Distinguishes writer-thread-dead vs call-path-bypassed-writer vs table-never-populated via cross-table correlation. Originated from GRO-2981 (2026-06-29).
---

# Telemetry-silence investigation recipe

Use this when a Ned-triage issue reports silence on one of the `telemetry_*` tables in `~/work/prismatic-engine/prismatic_state/event_router.db`. The recipe walks five diagnostic steps and lands on one of three root causes. Each cause maps to a specific cure-lane (infra / orchestrator / design).

## Why this is a Ned-lane investigation, not an orchestrator-lane one

Even though the underlying fix often lives in the orchestrator profile's scripts (`~/.hermes/profiles/orchestrator/scripts/`), the *diagnosis* is Ned infra work. The probe data lives in engine state; the cross-table correlation requires knowing the engine's write paths; the "is the writer thread alive?" question is a pure infra check. Fix handoff to orchestrator / Michael happens AFTER diagnosis is documented.

## The five diagnostic steps

### Step 1 — Confirm the silence scope (cheap, always start here)

```python
import sqlite3
conn = sqlite3.connect('/home/ubuntu/work/prismatic-engine/prismatic_state/event_router.db')
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute('SELECT COUNT(*) as total_rows, MAX(start_time) as latest_start, MAX(end_time) as latest_end FROM telemetry_agent_runs')
print(dict(cur.fetchone()))
```

Record: total_rows, latest_start, latest_end. The `latest_end IS NULL` for every row is itself a finding (separate completion-loop bug — see GRO-2978 family).

Also check daily distribution:

```python
cur.execute("""
SELECT date(start_time) as d, COUNT(*) as cnt
FROM telemetry_agent_runs
WHERE start_time >= date('now', '-7 days')
GROUP BY date(start_time) ORDER BY d
""")
```

The shape of the silence matters: monotonic drop-off vs cliff-edge vs gradual decline each point at different root causes.

### Step 2 — Verify the SQLite writer thread is alive

The non-blocking telemetry pipeline in `prismatic/telemetry.py` uses a daemon thread + 10K-slot queue. If the writer thread died, **all** tables stop growing. If only some tables stop, the writer is alive and a specific call path is bypassed.

```python
for table in ['telemetry_agent_runs', 'telemetry_credit_ledger',
              'telemetry_loop_events', 'telemetry_circuit_breakers',
              'telemetry_token_metrics', 'telemetry_plugin_metrics']:
    try:
        for col in ['start_time', 'recorded_at', 'created_at', 'ts']:
            cur.execute(f"SELECT MAX({col}) as latest FROM {table}")
            r = cur.fetchone()
            if r['latest']:
                print(f"  {table}.{col}: {r['latest']}")
                break
    except Exception as e:
        print(f"  {table}: ERROR {e}")
```

**Three distinct write-path categories emerge** (originated from GRO-2981, 2026-06-29):

| Category | Signal | Root cause |
|----------|--------|------------|
| **Still active** | `telemetry_credit_ledger` (86,105 rows, latest within minutes of now) | Writer alive. DB path healthy. |
| **Silent since a specific timestamp** | `telemetry_agent_runs` (latest 2026-06-25T10:21Z) | Call path bypassed writer. Orchestrator-side launch path is the live path, but it doesn't call `record_agent_run`. |
| **Always zero** | `telemetry_token_metrics` (0 rows), `telemetry_circuit_breakers` (0), `telemetry_validation_events` (0), `telemetry_hook_fired` (0), `telemetry_pipeline_action` (0) | Tables defined in `_ensure_tables` but no production write sites in current runtime. Either write sites were never wired or they were retired. Design-time gap, not runtime gap. |

The category determines the cure lane and the urgency. Category 1 means the table is healthy. Category 2 means the orchestrator-side call path needs telemetry wiring. Category 3 means a Michael / orchestrator design decision about whether to wire the missing paths or drop the tables.

### Step 3 — Map the call graph for the missing function

The two main `record_*` calls in `prismatic/telemetry.py` are `record_agent_run` (line 233) and `update_agent_run` (line 263). Grep for both across the engine and the orchestrator profile:

```bash
grep -rn "record_agent_run\|update_agent_run" \
  ~/work/prismatic-engine/prismatic/ \
  --include="*.py"
```

Expected engine-side hits (canonical call sites):
```
prismatic/telemetry.py:233:    def record_agent_run(...)
prismatic/dispatcher.py:628:    collector.record_agent_run(...)  # launch_kai
prismatic/dispatcher.py:1686:   collector.record_agent_run(...)  # process_queue_cycle
```

Now check the orchestrator profile (this is the bypass detector):
```bash
grep -rn "record_agent_run\|update_agent_run" \
  ~/.hermes/profiles/orchestrator/scripts/
```

**Expected: zero hits.** If you see hits here, the orchestrator already wires telemetry and the silence has a different cause.

### Step 4 — Confirm the orchestrator-side bypass

Find the currently-running orchestrator process and inspect its launch path:

```bash
ps aux | grep -E "agy_sandbox_event_supervisor|launch_agy" | grep -v grep
```

Then read the launch site in the supervisor script:

```bash
grep -n "cmd = \|subprocess.Popen\|AGY_BIN" \
  /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_event_supervisor.py
```

The bypass signature (confirmed in GRO-2981, 2026-06-29):
```python
# agy_sandbox_event_supervisor.py:615
cmd = [
    AGY_BIN,
    "--print", prompt,
    "--dangerously-skip-permissions",
    "--print-timeout", PRINT_TIMEOUT,
    "--sandbox",
    "--add-dir", str(sandbox),
    "--model", model,
]
proc = subprocess.Popen(cmd, ...)   # line 660 — direct AGY invocation
```

No `prismatic.dispatcher` import, no `record_agent_run` call, no telemetry wiring.

**Cross-check with launch artifacts**: AGY launches produce `/tmp/agy-dispatch-<issue>-*.txt` and `/tmp/agy-dispatch-<issue>-result.md` files. If these are being created daily but `telemetry_agent_runs` rows are not, the bypass is confirmed.

```bash
ls -lat /tmp/agy-dispatch-* 2>&1 | head -10
```

### Step 5 — Verify AGY is actually running, not silently dead

Before concluding "bypass confirmed", verify AGY is firing normally via other orchestrator-side signals:

```bash
# Last AGY completion-tracking file mtime
stat /tmp/.agy_completion_seen.json | grep Modify
stat /tmp/.agy_long_runner_seen.json | grep Modify

# Most recent AGY launch log
ls -lat /tmp/GRO-*-launch.log | head -3
```

If these are recent (within hours), AGY is alive and the orchestrator is just not writing telemetry.

## Architecture insight (durable fact, 2026-06-29)

The Prismatic Engine has **two AGY launch paths**:

1. **Engine-side** (`prismatic/dispatcher.py:launch_kai` and `process_queue_cycle`) — wires `collector.record_agent_run()` at dispatch and `collector.update_agent_run()` at completion. **This path is the source of all 635 `telemetry_agent_runs` rows.**
2. **Orchestrator-side** (`agy_sandbox_event_supervisor.py`) — the lane-aware dispatcher that handles `dispatch:ready` / `dispatch:backlog` / `dispatch:priority` labels. **This path is the live production path in the orchestrator profile but does NOT wire telemetry.**

The two paths diverged at some point in the engine's evolution (likely when the orchestrator switched from `prismatic.dispatcher` to lane-aware routing via the supervisor). The supervisor kept all the launch/sandbox/heartbeat/abandonment-guard machinery but never picked up the telemetry calls. **All AGY launches since 2026-06-25 10:21Z have been via the orchestrator-side path, hence the silence.**

**The cure is in the orchestrator profile.** Adding telemetry wiring to `agy_sandbox_event_supervisor.py` is an orchestrator/Michael task, not a Ned one. The Ned deliverable for the diagnostic issue is the audit doc + commit + handoff.

## Recommended fix (handoff to orchestrator / Michael)

Add three telemetry calls to `agy_sandbox_event_supervisor.py`:

1. **At launch** (around line 660, before `proc = subprocess.Popen(...)`):
   ```python
   from prismatic.telemetry import get_collector
   collector = get_collector()
   run_id = f"agy-{issue_id}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
   collector.record_agent_run(
       run_id=run_id,
       agent="agy",
       issue_id=issue_id,
       provider="antigravity",
       status="dispatched",
       credits_spent=0,
   )
   # Also stash run_id -> proc mapping so we can update it on exit.
   ```

2. **At exit** (after the `proc.poll()` loop and before `return`):
   ```python
   collector.update_agent_run(
       run_id=run_id,
       status="completed" if exit_code == 0 else "failed",
       exit_code=exit_code,
       error_message=error_msg if exit_code != 0 else None,
   )
   ```

3. **On stagnation_kill or abandonment-guard paths**, emit `status="killed"` or `status="abandoned"` respectively.

4. **Token metrics gap (related GRO-2980 territory)**: if Gemini token counts are accessible from the AGY CLI output (e.g. via the `--print` reply metadata), wire those into `record_token_metrics` here too. Otherwise a separate decision about scraping Gemini's quota endpoint.

## Disposition: Pass-12 protocol for in-lane investigations

GRO-2981 was a **fresh, in-lane Ned investigation** — not a recurring-batch misroute. The Pass-12 protocol (per the SKILL.md root) applies cleanly: audit-doc + commit on `ned/gro-485-triage-pass-1` (day's ratchet branch), no Linear comment, no `finalize_task.sh` state mutation. The Pass-12 protocol is NOT just for recurring-batch dispositions — it works for any no-op Ned pass where the deliverable is documentation.

## What to put in the audit doc

The audit doc for a telemetry-silence investigation should include:

1. **Confirmed silence scope** (total rows, latest timestamp, daily distribution table).
2. **Writer thread health** (which tables are still active, which are silent, which are always-zero).
3. **Call-graph map** for the missing function (`record_agent_run` call sites, or whichever `record_*` is missing).
4. **Orchestrator-side bypass evidence** (process inspection, launch artifacts, launch log mtimes).
5. **AGY-is-alive cross-check** (other orchestrator signals still updating).
6. **Architecture insight** (which paths diverged when, why the live path doesn't wire telemetry).
7. **Related issues** (the same root cause often drives multiple issues — e.g. GRO-2978 (completion loop), GRO-2979 (retry storm), GRO-2980 (token metrics) all share the orchestrator-side-bypass root cause from GRO-2981).
8. **Recommended fix** (specific patch for the orchestrator-side script, with exact line numbers and code snippets).
9. **Explicit non-actions** (what Ned did NOT do because it's out-of-lane — preserves the lane-discipline audit trail).
10. **Handoff statement** (this is in the orchestrator lane; Michael / orchestrator to action).

## Related issues (GRO-2981 family, all share the same root cause)

- **GRO-2978** (Verify completion-loop fix — assert >=1 row with non-null end_time in telemetry_agent_runs): same root cause from the completion side. All 635 rows have `end_time=NULL` because `update_agent_run` was never wired into the orchestrator's launch path either. Both halves of the loop are missing.
- **GRO-2979** (GRO-2051 retry-storm — 178 dispatches, 0 completions): the 178 dispatches are exactly the rows from the storm window in `telemetry_agent_runs`. The "0 completions" is the same `update_agent_run` gap.
- **GRO-2980** (telemetry_token_metrics empty if telemetry_credit_ledger has data): `telemetry_token_metrics` is one of the "always zero" tables. Likely related to `telemetry_circuit_breakers`, `telemetry_validation_events`, `telemetry_hook_fired`, `telemetry_pipeline_action` — all defined in `prismatic/telemetry.py:_ensure_tables` but with no live write sites in the orchestrator path. Same family of "defined-but-never-populated" gaps.

## Pitfalls

- **Concluding "writer is dead" from one silent table** — single-table silence is almost never a writer-thread issue. Cross-table correlation (Step 2) is mandatory before any writer-diagnosis conclusion.
- **Concluding "no work happening" from telemetry silence** — telemetry can be silent while AGY launches are firing 5+ times per day. Always cross-check `/tmp/agy-dispatch-*` artifacts and the supervisor process before declaring a dispatch outage.
- **Modifying `prismatic/telemetry.py` or `prismatic/dispatcher.py` as the "fix"** — the engine-side is correct. The fix lives in the orchestrator profile's scripts. Engine-side edits would be a workaround, not a cure, and would diverge the engine from production reality (the orchestrator-side path is what's actually used).
- **Calling `finalize_task.sh` after writing the audit doc** — the doc + commit IS the durable evidence. `finalize_task.sh` adds noise (Linear comment, state mutation attempt, lock release) for no incremental value. The script's auto-commit-on-budget-exhaustion path is the only legitimate reason to call it; otherwise skip.
- **Posting a Linear anchor comment** — the audit doc on `ned/gro-485-triage-pass-1` is the canonical record. The Pass-12 protocol's chatter-cooldown (no Ned-authored comment unless a new finding requires it) applies to investigation passes too.
- **Backfilling missing rows from `/tmp/agy-dispatch-*` artifacts** — backfilling telemetry retroactively is a non-trivial design decision (which `run_id` scheme? which `provider` value? do abandoned/silentcron/memcap-terminated launches count as runs?). That's a Michael / orchestrator call, not a Ned infra call. Document the backfill possibility in the audit doc's "What I did NOT do" section but do NOT attempt it.
- **Treating the orchestrator-side launch path as a Ned lane** — `~/.hermes/profiles/orchestrator/scripts/` is the orchestrator profile's territory. Ned can READ it for diagnosis but should not modify it. The handoff statement in the audit doc is the load-bearing piece.
- **Anchoring the audit doc on a recurring-batch branch** — investigations land on `ned/gro-485-triage-pass-1` (the day's ratchet), NOT on a fresh `ned/gro-2981-...` branch. Per the Pass-10 protocol the branch is the day's ratchet across all Ned dispositions regardless of signature.