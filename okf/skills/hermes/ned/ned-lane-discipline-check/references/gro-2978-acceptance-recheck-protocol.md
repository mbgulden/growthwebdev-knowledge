# GRO-2978 acceptance re-check protocol

Use this when a task asks to verify `telemetry_agent_runs` has at least one non-null `end_time` in the last 7 days, or when a completion-loop verification issue resurfaces.

## Decision rule

This is an acceptance check, not an implementation task by default.

1. Re-run the acceptance query honestly against the live repo DB:
   ```sql
   SELECT COUNT(*)
   FROM telemetry_agent_runs
   WHERE end_time IS NOT NULL
     AND start_time > datetime('now','-7 days');
   ```
2. Confirm real GRO/agent activity happened before measuring. Acceptable evidence includes recent `/tmp/agy-dispatch-GRO-*.txt` artifacts, Linear `Started:` comments, or currently-running dispatcher/supervisor processes.
3. If the count is `> 0`, the acceptance criterion is met; finalize/close according to the current cron contract.
4. If the count is `0`, do **not** run `finalize_task.sh` and do **not** transition the parent to In Review/Done. That would be theater.
5. When the issue body says to open a child task on `0`, create a child with the actual stack/source-line evidence and leave the parent in `Todo`.
6. Post one evidence comment to the parent and write/update the local `*_RESULT.md` artifact.

## Evidence to include when result is 0

- Query result and DB summary: total rows, rows with non-null `end_time`, latest `start_time`, latest `end_time`.
- Proof that real activity occurred before the measurement.
- Source-line evidence for the missing closure path:
  - Popen launcher lines that return a proc without observing exit.
  - `record_agent_run(... status='dispatched')` caller line.
  - `update_agent_run(...)` definition line.
  - Search result showing no production callers for `update_agent_run(...)` in `prismatic/`.
- Prior fix branch/test evidence if known, clearly distinguished from what is deployed in the live checkout.

## Pitfalls

- **Do not backfill or synthesize rows.** The issue explicitly tests live completion-loop behavior.
- **Do not finalize a failing acceptance check.** The useful side effect is the child task + evidence comment, not a state transition.
- **Do not treat a prior fix branch as deployed evidence.** Verify the live checkout / live DB separately.
- **Do not claim no real run happened until checking dispatch artifacts and Linear start comments.** A real agent cycle can exist while this DB remains stale, which is itself evidence for the wiring gap.
