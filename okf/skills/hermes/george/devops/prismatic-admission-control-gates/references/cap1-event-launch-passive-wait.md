# Cap-1 event launch and passive wait pattern

Use after a reviewed Prismatic admission envelope is independently accepted and Michael explicitly authorizes the operational gate.

## Scope discipline

Authorization should be interpreted narrowly unless Michael expands it:

- one authenticated event POST;
- one ordinary consumer invocation;
- one cap-1 producer launch;
- temporary admission policy/control writes only if the launcher restores them in `finally`;
- no retry after any durable admission row exists;
- no source edit, commit, push, PR, merge, deploy/restart, timer/cron mutation, production DB mutation, or Linear write.

## Execution sequence

1. Run the accepted launcher in zero-mutation preflight mode first.
   - Confirm deployed validation passes.
   - Confirm pre/post live row counts remain zero.
   - Confirm `policy_restored=true`, `control_restored=true`, and temp configs removed.

2. Execute the launcher once.
   - Capture HTTP status and response.
   - Require `replayed=false` for the first live event unless the explicitly intended gate is an idempotency replay proof.
   - Capture consumer exit/stdout/stderr and parsed response.
   - Confirm `status=processed`, `attempt=1`, one claim row, one outbox row, expected lifecycle sequence, writer lease count zero, and selectable outbox zero.

3. Reconcile launch receipts immediately.
   - Read final-result, launch-receipt, harness-run, activity, admission-receipt, and active-slot files.
   - Bind `launch_id`, `event_id`, `claim_id`, producer identity, task SHA, workflow version, `pane_pid`, and `pane_start_ticks`.
   - Confirm the active slot count is exactly the expected cap and belongs to the launched run by `run_id`.
   - Do **not** require `active-slots/slot-*.json.owner_pid` to equal `pane_pid`; slot ownership may point at the harness/supervisor while the receipt-bound wait must target the receipt `pane_pid`.
   - If artifact filenames do not include the event/launch id, search receipt contents for the exact event id or launch id rather than guessing absence from filename shape.

4. Bind process identity before waiting.
   - Compare `/proc/<pane_pid>/stat` start ticks to `pane_start_ticks` in both `harness-run.json` and `launch-receipt.json`.
   - Confirm the active slot `run_id` matches the launch id and the DB claim/outbox rows remain terminal (`completed`/`processed`) with no writer lease or selectable outbox.
   - If identity mismatches, do not attach a wait to that PID; freeze a blocker.

5. Attach passive wait only.
   - Use `tail --pid=<pane_pid> -f /dev/null` in a managed background process with notify-on-complete.
   - After attaching, a single bounded read of harness/result paths is OK to establish `RUNNING` vs already-finished; do not poll activity in a loop, impose a wall-clock deadline, or kill for inactivity unless the task contract explicitly authorizes it.
   - Record the managed process id/session id in the handoff next to the launch id, pane pid, and start ticks.

## Proof block

```text
COMMAND=one authenticated POST plus one ordinary consumer plus one cap-1 AGY launch plus receipt-bound passive wait
RESULT=PASS_RUNNING
SCOPE=<task id> live admission and launch
AD_HOC_OR_CANONICAL=ad-hoc targeted admission and live receipt proof
NOT_CLAIMING=producer completion,implementation correctness,candidate acceptance,canonical suite green,push,PR,merge,deployment,cron/timer mutation,production DB mutation,or Linear write
MARKER=<TASK>_CAP1_RUNNING_RECEIPT_BOUND
```

## Pitfalls

- A successful POST is not producer completion. Report `RUNNING` and stop at the passive wait gate.
- A preflight setup failure, such as unsafe temporary policy mode, is not task incompatibility; correct setup and rerun the whole preflight.
- Do not summarize the launched task as accepted or complete until terminal artifacts and exact candidate state have been reconciled after producer exit.
