# Failed-producer recovery contracts

Session-derived pattern for Prismatic runs where an admitted producer terminates or overclaims but leaves an exact candidate artifact.

## Boundary to preserve

- Producer terminal state is independent from candidate review.
- Preserve `producer_completed=false`, run/event ids, exit code, cleanup, active slot state, and original event count.
- Candidate focused-test success or independent review evidence is not producer success.
- No second event/producer until a new task/envelope path is reviewed and explicitly authorized.

## Candidate review checklist

1. Freeze exact `HEAD`, tree, parent/base, changed paths, tracked cleanliness.
2. Reproduce from `git archive` in a disposable directory.
3. Run focused tests, compile, diff-check, lint, format, static no-spawn checks, and domain authority invariants.
4. If canonical suite fails, do not claim canonical green. Reproduce baseline under the same environment before classifying failures as baseline vs regression.
5. Return first blocking defects and minimum repair.

## Repair contract checklist

When candidate review is BLOCKED:

1. Write the repair contract before any source mutation.
2. Bind it to exact blocked `HEAD`/tree and same worktree.
3. Require descendant-only repair: no reset, rebase, amend, clean, force, or replacement.
4. Define tracked path allowlist plus `BLOCKED_OUT_OF_SCOPE` stop condition.
5. Turn every reviewed defect into a required repair with direct tests.
6. Include immutable-archive verification and state-invariance checks.
7. Reserve future repair identity only as a reservation; do not create task files, events, credentials, or producers.
8. Verify artifact SHA/lines/bytes and dispatch artifact-only independent review.
9. If review blocks the contract, preserve `Vn` byte-for-byte, write a `Vn -> Vn+1` proof packet, and freeze a new artifact with a new marker/hash. The old artifact's blocked status is part of the evidence chain, not a draft to be edited in place.
10. Before declaring a security/authority repair contract sufficient, search for any abstract authority phrase and replace it with concrete source/storage/schema/encoding/digest/provenance/retrieval semantics.

## Proof fields

```text
PRODUCER_COMPLETED=false
ORIGINAL_EVENT_COUNT=<n>
BLOCKED_HEAD=<sha>
BLOCKED_TREE=<tree>
CANDIDATE_REVIEW=<delegation>:BLOCKED|CLEAN/PASS
REPAIR_CONTRACT=<path>
REPAIR_CONTRACT_SHA256=<sha256>
FUTURE_EVENT_COUNT=0
SECOND_EVENT=false
SECOND_PRODUCER=false
NOT_CLAIMING=<producer success, candidate acceptance, canonical green, PR, merge, deploy>
```

## Pitfalls

- Do not call a review-pending candidate accepted.
- Do not collapse deep authority defects into "lint only" just because lint also failed.
- Do not retry admission to reconcile a race; reconcile terminal state and freeze next gate.
