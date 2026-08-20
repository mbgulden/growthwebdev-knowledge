# Canonical AGY run state machine

Use this reference when simplifying or repairing AGY orchestration after a producer reaches a terminal process receipt but the dashboard/runtime projection remains stale.

## User preference / design constraint

Michael explicitly wants AGY orchestration simplified: do **not** add more wrappers, proof schemas, or manual dispatch ceremony. Preserve only the durable controls that matter:

- cap-1 producer limit;
- exact task/worktree/executable binding;
- durable process/result receipts;
- independent exact-artifact review;
- separate merge/deploy authorization.

## Correct state-machine shape

1. Launch through the ordinary event/consumer path only.
2. Create the canonical run record before starting the tmux/process.
3. The supervisor/harness owns terminal reconciliation; do not require a later manual `status()` call to finalize state.
4. On process exit, write `process-result.json` first, then atomically update the canonical run record.
5. Release the exact active slot only after process-tree cleanup is verified and the slot path is proven to belong to the same run.
6. A safely terminal producer result enters `review_pending` even when the result indicates product repair is needed. Independent review decides `accepted`, `repair_required`, or `rejected`.
7. If cleanup is unproven, survivors exist, the slot path is counterfeit, or identity binding fails, fail closed and do not release the slot.
8. Cancellation projects directly to rejected/cancelled state and should be durable/idempotent.
9. Dashboard APIs should project from the canonical run record, not stale tmux existence or ad-hoc wrappers.
10. `status()` remains compatibility/readback only; it must not be the only path that finalizes a terminal run and must never downgrade a reviewed state back to pending/running.

## Acceptance tests to add

- Fast producer exits with process-result written: canonical record finalizes and slot releases without calling `status()`.
- DASHQA-style stale `running` record plus terminal process receipt reconciles idempotently.
- Result path and SHA in the canonical record must match the process receipt.
- Hash mismatch with cleanup verified releases cap but remains `review_pending` for independent repair/reject decision; do not auto-accept.
- Cleanup failure or surviving process identity retains slot and fails closed.
- Counterfeit/symlink/out-of-runtime slot path is rejected before mutation.
- Existing live tmux session or live slot blocks launch.
- Cancellation record projects rejected/cancelled and does not leave cap stuck.
- `record_review_decision` is idempotent for the same reviewer/decision and blocks conflicting decisions.
- `status()` cannot downgrade `accepted`, `repair_required`, or `rejected` states.

## Reporting boundary

Report only exceptions and authorization points during this class of task. Do not over-report normal progress. Stop before push/PR/merge/deploy unless explicit authorization exists.
