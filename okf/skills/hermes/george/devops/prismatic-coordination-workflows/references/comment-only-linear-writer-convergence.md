# Comment-only Linear writer convergence and rollback pattern

Use this when Prismatic needs a bounded Linear comment/status write after a reviewed merge or acceptance event, but state/label/relation mutations remain explicitly unauthorized.

## Class of problem

Linear writes can have ambiguous outcomes:

- `commentCreate` may apply but the request times out.
- immediate reads after a successful/ambiguous create can be stale and temporarily omit the new comment.
- postcondition checks can detect issue-field drift after a comment was created.
- `commentDelete` rollback may apply but time out.
- immediate reads after an ambiguous delete can be stale and temporarily still show the deleted comment.

A safe writer must reconcile the live target state before claiming success/failure. One immediate read is not enough.

## Required writer properties

1. **Narrow mutation surface** — only `commentCreate` and `commentDelete`; no issue update/state/label/parent/relation/assignment/description mutation strings in the writer.
2. **Frozen packet** — fixed issue UUID, fixed marker, fixed expected issue fields, fixed comment body, and private bundle file. The approved bundle SHA-256 must be compiled or embedded into the reviewed writer; do **not** let the caller supply both a modified bundle and its matching modified hash as the authority check.
3. **Dry-run default** — live mutation requires an explicit execute authorization hash bound to the reviewed writer/test/bundle bytes; dry-run must read Linear and prove it would not mutate.
4. **Preflight drift guard** — before create, assert title/state/completedAt/updatedAt/labels/parent/relation expectations. If drifted, block before mutation.
5. **Pagination fail-closed** — bounded comment pagination must fail closed if the marker search cannot prove completeness.
6. **Duplicate/idempotency guard** — if the exact comment already exists, return idempotent success with `linear_mutated=false`.
7. **Durable forward intent** — write a private receipt/intent before `commentCreate` so an ambiguous apply can be reconciled later.
8. **Create convergence loop** — after create success or timeout, poll bounded reads until either the exact marker/body appears, a no-apply timeout is reached, or a read error blocks.
9. **Postcondition drift guard** — after observed create, re-check issue fields; if drifted, rollback the exact created/returned/matched IDs.
10. **Durable rollback intent** — before each `commentDelete`, write the exact IDs/body/marker being removed.
11. **Delete convergence loop** — if delete returns false or times out, do not immediately claim residual mutation. Re-read until the exact marker/body is absent or residual remains at timeout.
12. **Secret-safe errors** — receipts should record exception types/classes, not raw credential-bearing exception strings.

## Local proof expectations

Write failure-injection tests for at least:

- dry-run no mutation;
- normal success;
- create applies then times out, followed by stale reads before convergence;
- create timeout with no apply;
- postcondition drift causing rollback;
- delete applies then times out, followed by stale reads before absence converges;
- existing exact comment idempotency;
- adversarial bundle/hash substitution: a modified bundle must be rejected even when the caller supplies that modified bundle's matching SHA-256.

Then run a live dry-run against Linear with no mutation flag and bind:

```text
WRITER_SHA256=<sha>
TEST_SHA256=<sha>
BUNDLE_SHA256=<sha>
LIVE_DRY_RUN=PASS
LINEAR_MUTATED=false
FAILURE_INJECTION=<n>/<n> PASS
MUTATIONS=commentCreate,commentDelete
NOT_CLAIMING=live write, issue update, label/state/relation mutation
```

## Review/execution gate

Do not execute the live comment merely because local tests pass. Dispatch exact-byte independent review bound to the writer/test/bundle SHA-256 values. Older writer reviews become stale after any safety repair. Live execution is allowed only after the exact current writer SHA receives `CLEAN/PASS`.

## Pitfalls

- Treat a single immediate post-write read as unsafe; Linear reads can be stale.
- Treat ambiguous delete like ambiguous create: reconcile absence before deciding whether manual intervention is needed.
- If rollback eventually proves the marker absent, `delete_error_types` can be preserved as evidence without treating the rollback as failed.
- A caller-controlled bundle hash is not an authority boundary. Compile/embed the approved bundle hash into the reviewed writer (or equivalent reviewed constant) and add an adversarial test proving a modified bundle plus matching modified hash is rejected.
- Do not include the Linear API key or raw GraphQL error body in receipts or chat.
- Do not conflate a comment-only write-back with permission to change issue state; state may already be projected by an integration, but George should still prove live fields before commenting.
