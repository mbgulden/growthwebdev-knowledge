# GRO-2978 post-child-In-Review acceptance re-check

Use this when GRO-2978 resurfaces after the child fix issue (currently GRO-3617) has been implemented/finalized and is already `In Review`, but the parent acceptance criterion must be measured against the live DB.

## Decision rule

GRO-2978 is still an acceptance check against the live runtime DB, not a proxy for whether the child PR looks good.

1. Re-run the live acceptance query against `/home/ubuntu/work/prismatic-engine/prismatic_state/event_router.db`:
   ```sql
   SELECT COUNT(*)
   FROM telemetry_agent_runs
   WHERE end_time IS NOT NULL
     AND start_time > datetime('now','-7 days');
   ```
2. Confirm real AGY/GRO activity exists before measurement (e.g. `/tmp/.agy_long_runner_seen.json`, `/tmp/.agy_completion_seen.json`, `/tmp/agy-dispatch-GRO-*.txt`, or Linear `Started:` comments).
3. Inspect the child fix state (GRO-3617 unless superseded): Linear state, branch, PR URL, merge state, head SHA, changed paths.
4. Re-run the child’s focused verification from its isolated worktree (e.g. `/tmp/prismatic-gro3617`) to distinguish “fix branch is healthy” from “live DB acceptance has passed.”
5. Compare live checkout vs child worktree for the observer symbols (`register_proc_for_observation`, `_observer_loop`, `_PENDING_PROCS`, `update_agent_run` caller) so the report explains why the live DB can still be 0 while the child PR is green.

## Outcomes

### Count > 0

Acceptance is met. Finalize/close per the current cron contract.

### Count == 0 and child PR is healthy/In Review

Do **not** run `finalize_task.sh` on GRO-2978. Leave the parent in `Todo`; finalizing would be theater because the parent’s explicit close condition is still false.

Do post/update evidence if the state has materially advanced since the prior parent comment (for example, the child is now In Review with a clean PR and passing focused tests but live DB remains 0). Include:

- live acceptance query result and DB summary,
- proof of recent real activity,
- child issue state, PR URL, merge state, head SHA,
- focused child verification output,
- live-checkout-vs-child-worktree symbol comparison,
- close condition: merge/deploy child PR, run one real Popen-backed GRO agent cycle, then require query `> 0`.

Update `/tmp/issue-batches/GRO-2978_RESULT.md` with the same evidence.

## Pitfalls

- A clean child PR is not enough to close GRO-2978; the parent tests the live measured DB.
- Do not duplicate old failing-evidence comments unless the state materially changed. Child-In-Review + clean PR is a material change worth recording once.
- Do not mutate the DB or synthesize rows. The point is to prove live completion-loop behavior.
- Do not use the dirty shared checkout for child verification if an isolated child worktree exists; verify the child branch in its own worktree and keep the live checkout measurement separate.
