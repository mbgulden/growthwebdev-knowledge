# AGY Orchestration Simplification Regression

Use this when Michael questions whether AGY dispatch/control has become over-complicated, or when AGY runtime state appears stale/inconsistent.

## Durable lesson

The AGY harness is useful as a thin adapter: exact executable hash, frozen task/admission binding, cap slot, durable launch, process/result receipts, logs, status, cancellation. The mistake is exposing too many internal layers to the operator and letting multiple projections disagree.

Do not solve AGY orchestration confusion by adding another wrapper, schema, ledger, or handoff ceremony. Collapse toward one canonical run state machine and automatic reconciliation.

## Target operator model

```text
ONE TASK
  -> ONE EVENT
  -> ONE RUN RECORD
  -> AGY
  -> AUTOMATIC TERMINAL RECONCILIATION
  -> ONE INDEPENDENT REVIEW
  -> ACCEPT / REPAIR / REJECT
```

Recommended canonical states:

```text
QUEUED
ADMITTED
RUNNING
PRODUCER_TERMINAL
REVIEW_PENDING
ACCEPTED | REPAIR_REQUIRED | REJECTED
PR_OPEN
MERGE_ELIGIBLE
MERGED
RELEASE_VERIFIED
```

Dashboard, Telegram, handoff files, and status reports must be projections of the same canonical run record—not competing sources of truth.

## Regression pattern from DASHQA-2

A completed AGY producer wrote `process-result.json` with exit code 0, result present, process tree cleanup verified, and no surviving process identities, but the top-level `harness-run.json`/handoff still projected `running` and the active slot file remained. Root cause: the harness reconciled completion/released the slot only when something explicitly called `status(run_id)`.

Treat this as an orchestration bug: a durable terminal process receipt must automatically finalize the run, release the slot, and update projections. Manual status polling should not be required for terminal reconciliation.

## Steering language for future prompts

```text
Simplify AGY orchestration. Stop adding wrappers, proof schemas, or manual dispatch ceremony. Preserve cap-1, exact task/executable binding, durable process/result receipts, independent review, and separate merge/deploy authorization. Refactor toward one canonical run state machine: event -> AGY adapter -> automatic terminal reconciliation -> independent review -> accept/repair/reject. A completed process-result.json must automatically finalize the run and release the slot; no manual status call should be required. Dashboard and handoff must project the same canonical state.
```

## What to preserve

- cap-1 / explicit writer slot;
- exact task and executable hashes;
- idempotent event/admission receipts;
- isolated worktree/runtime;
- durable process/result/log artifacts;
- explicit cancellation and cleanup proof;
- producer output remains a claim pending independent review;
- merge/deploy/restart remains separately authorized.

## Implementation invariants learned from the AGY reconciliation repair

Use these as review gates when simplifying AGY orchestration. They are class-level invariants, not one-off DASHQA rules.

- **Automatic reconciliation belongs in the existing adapter/supervisor path.** A durable terminal receipt must update the canonical run record and projections without requiring a later `status()` call, polling loop, wrapper, or manual dispatch ceremony.
- **Cap release must be cleanup-gated.** Release a slot only when the terminal/process receipt is exactly bound to the run and reports verified cleanup with an explicit empty survivor list. Missing, malformed, or non-empty survivor data fails closed and retains the slot.
- **Successful producer completion is not acceptance.** Terminal success should move to `review_pending`; only an independent reviewer can transition to `accepted`, `repair_required`, or `rejected`.
- **Review state must be non-downgradeable.** Compatibility/status readers must not overwrite a reviewed run back to `running` or `review_pending`.
- **Producer self-review is invalid.** Carry `producer_identity` from the admitted event and reject review decisions from the same identity.
- **Serialize state transitions per run.** Parent launch updates, supervisor reconciliation, cancellation, and review decisions should share a per-run lock to avoid lost updates.
- **Treat runtime files as attack surfaces.** Locks, slot files, terminal receipts, manifests, and process/result paths should be private regular files where applicable; reject symlink/hardlink substitution and exact-binding mismatches.
- **Launch failure containment must distinguish pre-spawn from post-spawn.** Pre-spawn failures may remove provisional records and release; post-spawn failures must kill/wait/reconcile the exact session and release only through verified cleanup, otherwise project failure with the slot retained.
- **Dashboard is a projection, not a reconciler.** If a stale `running` record has a terminal receipt but cannot be safely reconciled from the dashboard path, project `reconciliation_required` rather than falsely live or silently freeing capacity.
- **Legacy artifact reproduction should use isolated copies.** When validating an old runtime shape, copy it and adjust only relocation-bound absolute paths inside the copy; do not mutate live runtime until exact-head review is clean.

## Terminal reconciliation safety invariants

- Write the canonical run record before spawning tmux.
- Let the supervisor publish the process receipt and reconcile automatically; `status()` is projection plus legacy idempotent fallback, never the required terminal trigger.
- Serialize parent pane updates, supervisor finalization, and independent review decisions with one private per-run lock.
- Treat cleanup as proven only when `process_tree_cleanup_verified is True` and the survivor list is explicitly `[]`.
- Release cap-1 only after cleanup proof. Producer exit/result failure with proven cleanup still enters `review_pending`; unproven cleanup retains the slot and fails closed.
- Bind process/cancel receipts to the exact run, workflow, manifest, activity, result path/digest, admission event/attempt, session, and slot. Refuse symlinked receipts and symlink/hardlink lock or slot substitution.
- Record producer identity from the admitted event and reject producer self-review. Review decisions must be serialized, idempotent for exact replay, and non-overwritable.
- A dashboard stale `running` record plus terminal receipt must surface `reconciliation_required`, not live work.
- Configure `PRISMATIC_AGY_RUNTIME_DIR` to the canonical task-admission runtime in production; otherwise the dashboard activity endpoint is truthful but empty and cannot project canonical run state.
- Contain post-spawn failures before release: terminate the exact session, wait for cleanup receipt, reconcile if valid, otherwise retain the slot.

## What to eliminate or hide

- manual temp policy/credential edits for ordinary dispatch;
- manual one-shot consumer invocations;
- manual finalization required after durable terminal process receipts exist;
- duplicate state records that can disagree about producer liveness;
- handoff files as operational state;
- repeated Telegram hash ceremony when dashboard can show exact bound hashes;
- new harnesses/ledgers before the existing path is reconciled end-to-end.
