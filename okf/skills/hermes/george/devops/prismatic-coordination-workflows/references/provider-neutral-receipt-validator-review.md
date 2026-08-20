# Provider-neutral receipt validator review pattern

Use this reference for Prismatic PNV receipt-validator / merge-gate slices where agent-produced candidates are repaired under exact-head review.

## Trigger

- A producer submits a provider-neutral verification receipt validator, merge eligibility gate, or clean-room policy enforcement change.
- Earlier candidates showed fail-open behavior, stale producer proof, or policy/receipt schema drift.
- George must decide whether to admit a focused PR, request same-task repair, or keep the queue paused.

## Durable review sequence

1. **Bind the candidate before reviewing.** Record base SHA/tree, candidate HEAD/tree, allowed paths, branch/worktree, and bundle path/hash before any admission or PR action.
2. **Treat producer packets as claims, not proof.** If an outbox/status packet was written before canonical completion, has stale counts, or has stale hashes, exclude it from authoritative evidence and rely on fresh local logs.
3. **Run adversarial checks before accepting local green.** For receipt validators, targeted tests should exercise fail-closed behavior around:
   - evidence digest policy algorithms (`sha256` vs `sha512` mismatches),
   - required digest evidence by kind/name,
   - optional command `argv` and `proof_class` binding,
   - unapproved receipt commands,
   - freshness/revocation/supersedes edge cases,
   - evidence path containment and symlink/traversal rejection,
   - timestamp precision and lifecycle containment at the schema boundary, including 7–9 digit RFC3339 fractions and one-nanosecond before/after escapes,
   - non-raising API behavior.
4. **Preserve timestamp precision exactly.** If the receipt schema allows nanosecond-style fractional timestamps, do not rely on Python `datetime` microsecond parsing/truncation for lifecycle gates. Parse canonical UTC RFC3339 timestamps into integer epoch nanoseconds (or an equivalent exact representation), normalize 1–9 fractional digits by right-padding, and perform receipt/command ordering, containment, and duration checks on the exact integer values.
5. **Use isolated repair worktrees when sibling mutation is possible.** If a prior repair worktree may have been reset or modified by another process/subagent, stop using it for the new candidate. Create a clean, named repair worktree/branch, bind HEAD/tree, and package a bundle from that isolated branch.
6. **Separate proof tiers in reporting.** Label focused/adversarial/package checks as ad-hoc targeted unless the full suite actually ran. Only claim canonical when the suite log is fresh and digest-bound.
7. **Same-task repair stays on the same gate.** Do not dispatch the next queued PNV slice while exact-head review is pending or a valid REPAIR finding exists.
8. **Update state artifacts immediately.** Keep `PRISMATIC_CURRENT_HANDOFF.md` and the Beyond North Star queue JSON aligned with the current exact-head review state, but avoid turning transient candidate history into memory.

## Acceptance packet minimum

```text
ISSUE=<GRO issue / PNV slice>
BASE=<sha/tree>
HEAD=<sha/tree>
BUNDLE=<path>
BUNDLE_SHA256=<sha256>
FOCUSED_LOG=<path/hash/result>
ADVERSARIAL_LOG=<path/hash/result>
CANONICAL_LOG=<path/hash/result or NOT_RUN>
WORKTREE_CLEAN=<true|false>
REVIEW=<delegation id and CLEAN|REPAIR|PENDING>
BOUNDARY=<not opened/not merged/not deployed/etc.>
```

## Pitfalls

- Do not accept a validator that returns eligible on schema-valid but policy-contradictory receipts.
- Do not let optional commands bypass policy binding just because they are not required.
- Do not treat a stale producer outbox packet as authoritative if George has fresher local logs.
- Do not advance to the next PNV producer while an exact-head independent review is still pending.
- Do not let RFC3339 fractional precision silently collapse through microsecond-only parsing; one-nanosecond lifecycle escapes are enough to fail the gate.
- Do not keep repairing in a shared/sibling-mutated worktree after detecting resets or unexpected file state; move to an isolated repair worktree and re-bind proof there.
