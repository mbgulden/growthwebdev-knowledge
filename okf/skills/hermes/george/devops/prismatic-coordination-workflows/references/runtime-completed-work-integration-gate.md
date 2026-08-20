# Runtime Completed-Work Integration Gate

Use this reference after durable raw-output/result-packet boundary convergence has merged and the next slice is deciding how completed-work persistence should be called from the supervisor without switching live runtime paths.

## Trigger

- `agy_result_packet` strict validation and durable raw-output capture are source-owned and release-verified.
- The next known gap is `AGY_COMPLETED_WORK_INTEGRATION_GATE_OK`, completed-work publication, or recovery/replay ordering.
- Live supervisor/runtime topology remains split or external, so source changes cannot be claimed as production behavior.

## Read-only analysis first

Before admitting a producer, map actual immutable-release APIs and tests for:

1. `scripts/agy_sandbox_event_supervisor.py` completion/publication points.
2. `prismatic.agy_completed_work` function signatures, default ledger/state paths, idempotency keys, and failure modes.
3. `prismatic.assigned_agent_visible_stream` event publication and side-effect ordering.
4. `prismatic.agy_result_packet` required fields and whether those fields are enough authoritative input for completed-work persistence without synthesizing data.
5. Any recovery/replay modules/tests that can duplicate, reorder, or reprocess result packets.

Return `CLEAN_FOR_BOUNDED_PORT` only if a <=4-path source slice can persist completed-work after strict raw-packet validation and durable raw capture, with no live state mutation and no external writeback/promotion transaction mixed in.

## Ordering contract

The safe order is:

```text
child process exits
-> RESULT.md semantic assessment
-> durable raw queue write returns exact nonempty raw_output_id
-> strict agy_result_packet validation
-> active issue/attempt/source binding
-> completed-work ledger persist succeeds/idempotently confirms same record
-> ingestion/integration markers are emitted from durable completed-work state
-> visible stream/event publication
-> any later authorized external writeback/promotion gates
```

Side effects that imply completion must wait for ledger success. Do not publish `agent.completed`, visible completion stream rows, Linear Done/comments/labels, quality/promotion launches, scheduler completed disposition, or success/circuit accounting if completed-work persistence fails, returns an empty durable id, cannot prove idempotency, or lacks the integration marker (`AGY_COMPLETED_WORK_INTEGRATION_GATE_OK`). Treat recovery/replay as the next slice unless it is explicitly included in the current exact task contract.

## Dialect and adapter rules

- Keep strict raw AGY packet validation separate from completed-work normalized records unless current APIs prove they are one schema.
- If the completed-work ledger expects a different dialect, add a narrow adapter from the validated raw packet plus durable raw-output metadata. The adapter must not synthesize authoritative fields that are absent from the packet; missing required fields are a fail-closed blocker or prior-slice requirement.
- Validate the artifact/source-path semantics with the real ledger: a relative `RESULT.md`-style artifact may correctly persist as `invalid_repairable`/rejected classification, while an absolute safe source path can be merge-ready. Do not “fix” this by synthesizing a safe path or treating rejected durable rows as completion authority.
- Preserve queue-normalizer/completed-work rejection evidence in the supervisor boundary payload so review can distinguish dialect mismatch, invalid-repairable source material, and product failure.
- Keep completed-work durable persistence separate from authorized external writeback/promotion unless current APIs prove a single coherent transaction with rollback/idempotency semantics.

## Producer contract shape

- Source-only, <=4 exact changed paths.
- No live supervisor switch, deployment, restart, systemd edits, live cursor/state mutation, Linear/GitHub writeback, quality launch, promotion, or generic dispatch.
- Dedicated absolute state path for completed-work ledger if one is not already source-owned and secret-free; source-owned manifests should classify these as external mutable state, not immutable release code.
- Tests for successful ledger persist after durable raw capture, failure before visible completion, idempotent replay of same issue/attempt/raw_output_id, conflict on changed payload for same identity, missing packet fields, invalid packet, queue durable-id failure, and no external side effects from any held/rejected path.
- After admitting a producer, verification should not require a clean worktree; the correct invariant is exact base plus all dirty/changed paths restricted to the allowed contract. A clean-worktree assertion is valid only before dispatch or after candidate preservation/reset.

## Proof packet additions

```text
COMPLETED_WORK_LEDGER=<path or fixture>
LEDGER_IDEMPOTENCY=<PASS|FAIL|BLOCKED>
ORDERING_PROOF=<log + sha256>
REPLAY_PROOF=<log + sha256>
NOT_CLAIMING=live supervisor switch, production writeback, Linear Done, promotion, recovery completeness unless separately proven
MARKER=AGY_COMPLETED_WORK_INTEGRATION_GATE_OK
```

## Overclaim traps

- A valid result packet is not completed-work persistence.
- A completed-work unit test is not proof the supervisor waits for the ledger before publishing completion.
- Event publication before ledger success creates a recovery gap; replay may not know whether completion was durable.
- Idempotent duplicate success and conflicting duplicate rejection must both be tested; one without the other is incomplete replay proof.
- Live runtime parity, production state, and external writeback remain separate gates after the source slice merges.
