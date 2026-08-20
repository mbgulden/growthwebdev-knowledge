# Versioned precontract lineage: local fences, remote mutation ambiguity, and exact-review repair

Use this reference when a Prismatic precontract or blocker artifact governs downstream projection of canonical outcomes into an external system such as Linear.

## Session lesson

A local idempotency key, durable intended-delta bytes, and a database generation fence are not sufficient to claim exactly-once remote mutation when the transport call can already be in flight. A worker can pass final local validation, pause during/after transport invocation, lose its lease, and later commit while a second worker takes over after observing marker absence. Marker absence is not conclusive proof that the earlier request cannot still commit.

## Required contract shape

For any future contract that may write to a remote system:

1. Preserve every reviewed version byte-for-byte. Do not rewrite V1/V2/V3 after a blocker; copy forward to V(N+1), repair there, and record old/new hashes.
2. Bind the exact artifact under review by path, SHA-256, line count, and byte count before dispatching independent review.
3. Treat each independent BLOCKED finding as authoritative only for the first precise blocker; make the minimum artifact-only correction and request a fresh exact-hash review.
4. Separate these layers explicitly:
   - canonical intended delta bytes;
   - logical idempotency key / stable marker;
   - local ownership and monotonic generation fence;
   - linearizable dispatch guard held through adapter return;
   - provider-side idempotency or conclusive provider request-status evidence.
5. Require one linearizable per-idempotency-key dispatch guard held continuously from final fence validation through adapter return and durable classification.
6. Do not allow wall-clock lease expiry to revoke an active dispatch guard or authorize a second transport call.
7. If process death, timeout, connection loss, missing response, or guard loss leaves the prior request possibly in flight, enter non-writing ambiguity/reconciling/quarantine.
8. Never resend solely because the remote marker is absent. Automatic resend after ambiguity requires either accepted provider-side atomic idempotency/conditional-write for the same logical key or authoritative provider evidence that the prior request reached a terminal non-committing state.
9. If that provider proof/primitive is unavailable, the correct state is operator-visible, replay-disabled ambiguity hold; do not overclaim automatic recovery.
10. Add adversarial tests that pause the old holder immediately after final validation and simulate late remote commit after timeout; prove no second fake-adapter mutation.

## Review packet defaults

Use compact proof blocks that preserve boundaries:

```text
PREVIOUS_ARTIFACT=<path>
PREVIOUS_SHA256=<sha>
PREVIOUS_REVIEW=<delegation>:BLOCKED
FIRST_BLOCKER=<precise finding>
NEW_ARTIFACT=<path>
NEW_SHA256=<sha>
NEW_LINES=<n>
NEW_BYTES=<n>
REPAIR=<minimum correction summary>
REVIEW=<fresh delegation>:pending
EVENT_COUNTS=0/0/0 or exact bounded counts
WORKTREE_CREATED=false
LINEAR_WRITE_COUNT=0
NOT_CLAIMING=<acceptance, implementation, task, event, producer, PR, merge, deployment, credentials, network, mutation>
```

## Pitfalls

- Do not say a generation fence alone provides exactly-once remote mutation.
- Do not say marker absence proves safety to resend after an ambiguous in-flight request.
- Do not let a takeover both acquire a new fence and write unless the provider capability closes the remote ambiguity.
- Do not mutate runtime state, create a worktree, admit events, or write Linear while freezing a precontract blocker.
