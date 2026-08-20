# Operator-exception candidate blocked by trust-boundary review

Use this reference when a reviewed dirty same-worktree checkpoint was committed under an explicit exact-byte operator exception, then fresh exact-head review finds a candidate-specific authority/security defect.

## Pattern

A human-authorized operator exception may convert already-reviewed dirty bytes into one normal descendant commit so deployed admission no longer blocks on `worktree_dirty`. That commit is still only a **candidate**. Fresh exact-head review can block it even when:

- the worktree is tracked-clean;
- the focused suite passes;
- canonical failures are identical to the parent/baseline;
- the operator exception itself was correctly scoped.

Do not let the exception or focused green become acceptance.

## Review signals that block acceptance

For registry/authority/process-runner repairs, inspect the real execution path rather than only fixtures or helper methods. Block when trust-critical fields are declared but not consumed by the actual admissibility/spawn/finalization path.

Concrete example pattern:

```text
DECLARED_TRUST_FIELDS=trusted_runner_identity,release_root,release_root_evidence,executable_evidence,cwd_evidence
REAL_RUNNER_RETRIEVAL_CALLS=0
CALLER_SUPPLIED_SNAPSHOT_ACCEPTED=true
PRESPAWN_ONLY_CHECKS=scalars/deps/attempt_state
ADAPTER_INPUT=untrusted argv/cwd strings
NEGATIVE_FIXTURES_EXPECT_ADAPTER_CALL=true
```

A valid repair contract should require all of the following before a future producer/source edit:

1. Retrieve canonical snapshot bytes from the existing pinned authority store, not caller-provided snapshot content.
2. Use the same pinned database/object/connection across claim, immediate pre-spawn retrieval, and finalization.
3. Persist and recompare source/schema/version/canonical bytes/snapshot digest at every decision/finalization boundary.
4. Require trusted runner identity binding (`runner_id == trusted_runner_identity`).
5. Validate release root, cwd, executable, and parents with no-follow/pinned object evidence.
6. Ensure the adapter consumes the same pinned objects validated immediately before spawn.
7. Make every trust failure durable, reason-coded, idempotent, and zero-spawn/zero-adapter-call.
8. Add adversarial replacement tests that fail closed on registry row, release root, cwd, executable, and parent substitution.
9. For locator-based APIs such as `run_once()`, accept exactly the bounded locator fields needed to re-read the canonical row (for the cron-runner case: `source_id`, `registry_generation`, and `snapshot_digest`) and reject every caller-supplied snapshot object, canonical byte/mapping, evidence dictionary, reconstructed path set, path string, alias, detached helper result, or extra authority-bearing field at the API boundary. No locator value may be derived from caller snapshot content.

## Contract wording pitfall

Do **not** write authority contracts with soft phrases such as:

```text
accept or derive a locator
caller may provide a locator/assertion
caller snapshot content cannot override canonical bytes
```

Those phrases still leave room for caller-derived authority. Instead, name the exact accepted locator fields, state that all other authority-bearing inputs are rejected, and require a negative test proving the former caller-supplied snapshot/content/evidence/path arguments fail before any adapter call.

## Required handling

When this happens:

1. Preserve the blocked candidate commit and tree exactly.
2. Record the review verdict as candidate-specific BLOCKED, not producer failure rewrite and not canonical regression.
3. Freeze a new versioned repair contract based on the blocked head/tree.
4. Prove the future task/event count is zero.
5. Dispatch fresh artifact review of the new contract.
6. Update the handoff to `review pending` and stop.

## Nonclaims

The blocked-candidate repair contract authorizes no task copies, envelope, event, producer, source edit, new commit, push, PR, merge, deploy/restart, timer, production database mutation, or Linear write.

## Minimal proof fields

```text
BLOCKED_HEAD=<sha>
BLOCKED_TREE=<tree>
TRACKED_STATUS=clean
REVIEW=<delegation>:BLOCKED
CLASSIFICATION=BLOCKED_CANONICAL_BASELINE_NO_REPAIR_REGRESSIONS_WITH_CANDIDATE_SPECIFIC_TRUST_DEFECT
REPAIR_CONTRACT=<path>
REPAIR_CONTRACT_SHA256=<sha256>
FUTURE_EVENT_COUNT=0
NEXT_GATE=await fresh repair-contract review
NOT_CLAIMING=contract acceptance,task copies,envelope,event,producer,source edit,new commit,candidate acceptance,canonical green,push,PR,merge,deployment,cron/timer,DB,Linear
```
