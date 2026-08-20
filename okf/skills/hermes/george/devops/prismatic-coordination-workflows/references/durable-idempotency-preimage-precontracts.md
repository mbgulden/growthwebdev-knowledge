# Durable idempotency preimage precontracts

Use this reference when freezing or reviewing Prismatic contracts/precontracts for idempotent projection, remote mutation, replay, or retry paths.

## Trigger

Apply this when a contract derives an `idempotency_key`, request key, projection identity, or duplicate-suppression key from canonical inputs and then claims replay safety, collision detection, or idempotent remote writes.

## Lesson

Persisting a digest, selected fields, or a re-renderable input description is not enough to prove idempotency identity after restart, retry, schema drift, or collision. A future worker must be able to compare the exact canonical key preimage bytes that originally produced the key.

## Required contract shape

A durable send-eligible intent/projection row should include, before eligibility:

```text
idempotency_key
idempotency_preimage_canonical_bytes   # immutable, bounded, schema-versioned
projection_schema_version              # independently durable constituent
runner_outcome_schema_version           # independently durable constituent, when derived from runner outcome
intended_delta_canonical_bytes          # exact bytes to replay/send
intended_delta_digest
```

The same atomic pre-eligibility transaction must persist the exact preimage bytes and schema constituents from which the key is derived. Do not allow later re-rendering from current policy, registry, receipt, upstream issue state, or code defaults to stand in for the original preimage.

## Verification gates

Before eligibility, retry, or replay:

1. Recompute/verify `idempotency_key` from the persisted `idempotency_preimage_canonical_bytes`.
2. Verify the preimage schema versions are known and independently persisted.
3. Verify `intended_delta_digest` against the persisted intended-delta bytes.
4. Treat missing bytes, unknown versions, or any mismatch as durable quarantine with zero remote writes.
5. For same-key collisions, compare persisted preimage bytes byte-for-byte:
   - identical bytes = same logical intent;
   - different bytes = quarantine both identities with zero remote writes.

## Review pitfall

A review that accepts only `canonical_input_digest` or selected columns for collision handling is incomplete. The blocker is not just “need a digest”; it is “need exact durable key-preimage bytes plus schema constituents that can be byte-compared later.”

## Adversarial cases to require

- missing `idempotency_preimage_canonical_bytes`;
- unknown preimage schema version;
- stored key does not verify against persisted preimage bytes;
- same key with different persisted preimage bytes;
- retry/replay after schema/policy/registry drift;
- intended delta digest mismatch;
- remote mutation attempted from reconstructed rather than persisted bytes.

## Reporting boundary

If the precontract passes but upstream authority is still missing, report it as:

```text
PRECONTRACT=CLEAN/PASS
IMPLEMENTATION=BLOCKED_ON_UPSTREAM_AUTHORITY
NOT_CLAIMING=task, worktree, event, producer, implementation, PR, merge, deployment, or live mutation
```
