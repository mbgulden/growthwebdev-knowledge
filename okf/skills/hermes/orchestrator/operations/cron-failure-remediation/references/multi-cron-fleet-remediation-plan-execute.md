# Multi-cron fleet remediation: plan → execute → verify

Use this reference when Michael asks to turn a cron/digest queue into concrete fixes across several active jobs.

## Pattern

1. **Rank active jobs, suppress retired noise.**
   - Start from `cronjob(action="list")` and latest output artifacts.
   - Ignore disabled/paused/archive jobs unless explicitly revived.
   - Rank by user-visible trust/revenue/security impact: failed delivery, false security alert, noisy green digest, unbounded dispatcher, stale registry/digest copy, then lower-risk cleanup.

2. **For each cron, state the plan before editing, then execute the smallest load-bearing change.**
   - Digest/watchdog all-clear noise: make stdout empty on green/idleness; write local state/logs only.
   - Delivery target missing (`Chat not found`): switch to `deliver=local`, rerun to clear stale `last_delivery_error`, restore direct delivery only after the recipient handshakes with the bot.
   - Missing skill on a cron: route to the available class-level skill rather than leaving a missing-skill preamble in every output.
   - Unbounded dispatcher: add a batch cap and preview only the selected slice; report held count, never dump/dispatch the full backlog.
   - Stale digest/registry wording: remove old “completed/fixed today” copy and replace with source-health/read-only status; mutate registry only for exact stale rows with current reconciliation wording.
   - Human/editorial/approval rows: package a checklist or remediation packet; do not mark answered/resumed/done without explicit human approval/evidence.

3. **Run the affected scheduler jobs.**
   - `cronjob(action="run", job_id=...)` for each patched job.
   - Confirm `last_status=ok` and `last_delivery_error=null`.
   - Read latest output only as evidence; do not confuse scheduler ok with content-contract ok.

4. **Use one final focused `/tmp/hermes-verify-*` verifier for the batch.**
   Include:
   - `py_compile` for changed Python scripts.
   - Fixture checks for all-clear silence and alert preservation.
   - Dispatcher cap fixture proving only N specs are written and held count is correct.
   - Registry/digest wording assertions.
   - Existence/contents of generated remediation packets/specs.
   - Scheduler `last_status`/`last_delivery_error` readback.
   - Cleanup of the temp verifier and explicit `AD_HOC_OR_CANONICAL=ad-hoc targeted; not canonical suite green`.

## Compact proof keys

Use a final machine-readable block when detectors are sensitive:

```text
COMMAND=<compile + fixture + scheduler readback summary>
AD_HOC_VERIFICATION=PASS
RESULT=PASS
LOG=/tmp/<topic>-verify.log
SCOPE=cronN-cronM remediation producers and action artifacts
changed_paths_checked=<absolute paths>
<cron-specific-key>=true
scheduler_runs_ok=true
AD_HOC_OR_CANONICAL=ad-hoc targeted; not canonical suite green
cleanup=PASS
fresh_verifier_absent=true
```

## Pitfalls

- Do not call memory over-cap “fixed” if the groomer found zero safe auto-removable entries. Mark the non-lossy sweep/reporting complete and leave manual compaction as a caveat.
- Do not keep printing queue counts, zero-result summaries, or all-green messages from no-agent crons; non-empty stdout may become user-visible noise.
- Do not let a capped dispatcher still print the full backlog. The visible output should preview only the selected slice and the held count.
- Do not convert Michael/editorial/approval blockers into agent-completed work. Package the exact checklist and stop.
