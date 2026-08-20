# Runtime recovery/reconciliation gate

Use this reference after completed-work persistence has been integrated and merge-SHA release proof has passed, but before any production supervisor switch or historical replay.

## Trigger

- Completed-work integration gate is merged/release-verified.
- Next proposed slice is crash-safe raw-output/result-packet to completed-work recovery, reconciliation, or replay.
- Goal is to repair internal recovery ordering, not to perform public completion side effects.

## Read-only analysis before producer admission

Verify from the immutable current-main release:

1. **Raw queue retrieval** — identify the API that returns durable raw outputs, durable `raw_output_id`, issue/task/attempt identity, source path, classification, and evidence/repair markers.
2. **Delivery state** — map pending/in-progress/delivered/rejected/retryable states and how crash recovery distinguishes never-processed from partially processed packets.
3. **Strict replay eligibility** — require active issue binding, task/attempt/source identity match, safe source path, nonempty durable IDs, and completed-work dialect validation/adaptation before any completion-visible transition.
4. **Completed-work idempotency** — repeated recovery of the same valid packet must resolve to the same logical completed-work row; conflicting packets must hold/reject without public completion.
5. **Locking/concurrency** — prove two recovery workers cannot publish the same packet twice or race one worker past ledger failure.
6. **Oldest-first ordering** — recovery should process durable raw records deterministically so older eligible records do not starve behind newer ones.
7. **No external side effects** — read-only design and failed/ineligible replay may not emit `agent.completed`, Linear Done/comment/labels, GitHub/PR/promotion/quality launch, scheduler completion, or circuit success/reset.

## Bounded producer contract shape

- Exact base: current immutable main merge SHA from the previous completed-work closeout.
- Scope: prefer <=4 paths; split if raw retrieval, delivery-state schema, worker replay, and scheduler/circuit publication cannot fit safely.
- For raw-to-completed-work recovery, require a delivery-state table in the existing raw SQLite database, not a side ledger detached from raw rows.
- Migration/backfill must be atomic: legacy rows become pending without data loss, and all new raw rows receive pending delivery state at insert time.
- Recovery claims should be bounded, deterministic oldest-first leases with token-based compare-and-set so duplicate workers cannot both finalize one row.
- Retention must be lossless for pending, retryable, and in-progress rows; cleanup may not delete undelivered work just because it is old.
- Use one coordinator for immediate capture, startup recovery, and watchdog recovery so classification, eligibility, idempotency, and no-side-effect behavior cannot diverge across call sites.
- Public recovery results must stay metadata-only: never expose raw packet text or secret-bearing output through result serialization.
- Required tests:
  - valid durable raw packet recovers exactly once;
  - repeat recovery is idempotent;
  - missing/empty durable IDs fail closed;
  - issue/task/attempt/source mismatch holds/rejects;
  - completed-work ledger failure remains requeueable and emits no public completion;
  - sandbox/quota/error early exits cannot reuse stale success state;
  - concurrent recovery workers fence duplicate delivery;
  - legacy/unvalidated Markdown remains evidence only, not completion authority.

## Admission/state consistency verifier

After admitting the producer and editing control/handoff records, run a small ad-hoc verifier that binds:

- workspace HEAD and branch;
- frozen `AGY_TASK.md` SHA-256;
- changed-path allowlist is not exceeded, while allowing producer edits already in progress;
- control JSON `active_ids` and active task metadata;
- handoff marker such as `RUNTIME_CONVERGENCE_5_ONE_BOUNDED_PRODUCER_ACTIVE`.

Label this `AD_HOC_OR_CANONICAL=ad-hoc targeted`; it proves coordination/admission consistency only, not product behavior or canonical suite green.

## Proof packet

```text
COMMAND=<read-only API probes + focused recovery regressions + canonical suite>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<path>
SCOPE=raw-output-to-completed-work recovery/reconciliation
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite|GitHub CI|immutable release>
NOT_CLAIMING=historical replay performed; external writeback; production supervisor switch; deploy/restart; exactly-once global delivery
MARKER=AGY_COMPLETED_WORK_RECOVERY_RECONCILIATION_OK
```

## Pitfalls

- Do not treat a rejected completed-work row as completion authority just because it exists durably.
- Do not replay from raw Markdown alone; strict raw packet identity and completed-work adapter validation remain the authority.
- Do not count scheduler completion, circuit success, or Linear/quality/promotion as part of recovery until ledger persistence is already proven or idempotently confirmed.
- After product proof, update handoff/control state with a separate targeted consistency verifier so edited coordination files do not obscure the product evidence class.
