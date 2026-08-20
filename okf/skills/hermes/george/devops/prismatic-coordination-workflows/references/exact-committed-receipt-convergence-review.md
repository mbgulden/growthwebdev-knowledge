# Exact committed receipt convergence review

## Trigger

Use this reference when reviewing a Prismatic repair that changes receipt/idempotency convergence semantics, especially `CronAuthorityStore.finalize_execution_receipt()` or any producer that may retry a terminal receipt after the attempt lease has expired.

## Durable lesson

A late retry returning `status="converged"` is safe only when the already-committed record and the incoming receipt are semantically identical across the complete persisted receipt payload. Comparing only a few identity/result fields can let altered timestamps, signatures, schema, runner identity, or error metadata be falsely accepted as convergence.

## Exact convergence contract

For a committed `CronRunReceipt`, verify the convergence path checks all persisted semantic fields before returning `converged`:

```text
receipt_id
cron_id
execution_id
outcome
attempt
runner_id
runner_release_digest
started_at
finished_at
signing_key_id
signature
schema_version
error_classification
evidence_digest
```

Preferred implementation proof: reconstruct the committed dataclass/object from the database row, serialize through the same canonical JSON path as the incoming receipt, and compare canonical bytes. If the code instead compares fields manually, enumerate every persisted field in the review.

## Evidence-byte ordering

If `evidence_bytes` are supplied on a convergence retry, validate `sha256(evidence_bytes) == receipt.evidence_digest` before returning any read-only convergence decision. A mismatched evidence body must fail closed with a structured error such as `evidence_digest_mismatch`, even when the receipt row itself otherwise matches.

When evidence may already exist, `SELECT` before insert can be acceptable under the same transaction/lock discipline, but the review must verify existing evidence bytes are not overwritten and mismatch does not mutate receipt, attempt, evidence, or fence state.

## Review recipe

1. Bind exact commit, tree, parent/base, task bytes/hash, result artifact, and finite changed paths.
2. Reproduce targeted tests locally and save logs to `/tmp/hermes-verify-*`.
3. Read the complete finite diff, not only the producer summary.
4. Prove exact late convergence after terminalization/lease expiry is read-only.
5. Mutate each persisted field above one at a time; no changed field may return `converged`.
6. Mutate supplied evidence bytes with the same receipt; it must fail before convergence.
7. Snapshot receipt/attempt/evidence/fence rows before and after failed convergence attempts; they must be unchanged.
8. Check ordering against cross-binding, fence/active mutation guards, and database transaction boundaries.
9. Separate targeted/ad-hoc proof from canonical full-suite green, public proof, PR, merge, deploy, or Linear closure.

## Proof packet

```text
COMMAND=<pytest/ruff/compile/diff/adversarial verifier commands>
RESULT=<PASS|FAIL|BLOCKED>
LOG=<paths>
SCOPE=exact-head receipt convergence repair
AD_HOC_OR_CANONICAL=ad-hoc targeted
FIELDS_PROVED=14_persisted_receipt_fields
READ_ONLY_CONVERGENCE=<true|false>
EVIDENCE_MISMATCH_FAILS_CLOSED=<true|false>
MUTATION_ON_FAILURE=<none|details>
NOT_CLAIMING=canonical_suite,PR,merge,deployment,production_proof,Linear_write,parent_completion
MARKER=EXACT_COMMITTED_RECEIPT_CONVERGENCE_REVIEW
```
