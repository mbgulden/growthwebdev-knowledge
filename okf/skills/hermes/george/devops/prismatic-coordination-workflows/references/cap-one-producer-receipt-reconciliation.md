# Cap-One Producer Receipt Reconciliation

Use this when a Prismatic task-admission consumer is authorized to start exactly one supervised producer and the launch path returns an exception or missing receipt while process/ledger evidence shows the producer is already running.

## Core rule

A consumer-side `LauncherError`, missing launch receipt, or pending outbox row is **not** authorization to invoke the consumer again when the supervised child is live. Treat it as a receipt/reconciliation exception until proven terminal.

## Required sequence

1. **Freeze the launch boundary**
   - Record admission event id, task id, accepted base commit/tree, task file hash, producer identity, writer cap, and token-discard state.
   - Preserve the consumer log and admission log paths/hashes.

2. **Prove whether a producer exists before retrying anything**
   - Inspect the launcher ledger for `event_id`, `launch_id`, `attempt_count`, `state`, supervisor pid/start ticks, child pid/start ticks, exit/failure, candidate sha/tree.
   - Verify live child identity with `/proc/<pid>/stat` start ticks when available.
   - Check active process command lines only to count the exact authorized producer; do not use process grep output as acceptance proof.

3. **Fail closed on duplicate risk**
   - If the ledger/process evidence shows a live producer for the event, do **not** rerun the consumer or start another producer.
   - Start only a bounded read-only watcher for terminal state if needed.
   - Classify the state explicitly as `RECEIPT_RECONCILIATION_PENDING`, not as a failed admission requiring retry.

4. **Reconcile after terminal state**
   - Use stable idempotent historical receipt behavior for the same event/launch, not a new producer start.
   - Bind the final receipt to the exact event id, launch id, candidate commit/tree, logs, and producer identity.

5. **Separate proof classes**
   - Admission proof: event accepted, exact tuple, cap/token discarded.
   - Launch proof: exactly one supervised producer exists or reached terminal state.
   - Candidate proof: AGY result, local tests, and independent review of exact artifact.
   - Do not claim merge/deploy/Linear updates unless those were explicitly authorized and executed.

## Pitfalls caught in session

- Wrong CLI option names can fail before consumer execution; capture this separately and do not count it as a producer attempt.
- A launcher can return nonzero after spawning the supervisor/child if receipt publication has a bug; retrying the consumer can violate cap-one even if the outbox still says pending.
- Missing supervisor start ticks plus live child ticks should be treated as a reconciliation defect and duplicate-launch risk, not as a reason to relaunch.
- Keep the report user-facing: Problem → Changed/Evidence → Why it matters → State → Next move → IDs/hashes/logs.

## Compact report marker

Use a marker like:

```text
MARKER=<TASK>_EXACT_ONE_PRODUCER_RUNNING_RECEIPT_RECONCILIATION_PENDING
NOT_CLAIMING=consumer outbox processed, producer completion, candidate acceptance, PR, merge, deployment, Linear update, second producer, or cap increase
```
