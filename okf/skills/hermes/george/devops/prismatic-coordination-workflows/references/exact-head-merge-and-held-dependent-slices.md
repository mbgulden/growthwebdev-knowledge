# Exact-Head Merge and Held Dependent Slices

Use this when a Prismatic candidate has passed exact-head independent review, but GitHub Actions or downstream Linear state complicates the handoff.

## Pattern

1. **Bind merge to the reviewed head.** Before merge, verify the PR head OID equals the independently reviewed candidate commit. Merge with a head guard such as `gh pr merge <PR> --merge --match-head-commit <sha>` so a late push cannot silently change the accepted artifact.
2. **Verify post-merge ancestry and tree.** After merge, fetch `origin main`, record the merge commit/tree, and verify the accepted commit is an ancestor of `origin/main`. If the merge commit tree equals the accepted tree, state that explicitly.
3. **Classify GitHub CI non-starts separately.** If Actions jobs never start because of billing/spending-limit/account infrastructure, do not report this as test failure or suite proof. Mark it as `TEST_EXECUTION=none` and rely only on exact-head local/independent clean-checkout receipts that actually ran.
4. **Preserve branch deletion as a separate side effect.** If deletion was not authorized, merge without deleting and say so.
5. **Write a compact acceptance receipt.** Include task, accepted commit/tree, PR URL, merge commit/tree, merge time, review/test scope, CI boundary, non-claims, and a marker. Hash the receipt if it will be cited.
6. **Do not auto-admit dependent held work.** After a prerequisite merges, inspect the dependent Linear issue text/status. If it contains an operational hold such as “not dispatch-ready” or “does not authorize implementation,” stop at a contract/planning recommendation unless Michael explicitly authorizes lifting the hold for a bounded slice.

## Proof block

```text
COMMAND=gh pr merge <PR> --merge --match-head-commit <accepted_sha>
RESULT=PASS
SCOPE=merge bound to exact reviewed head
AD_HOC_OR_CANONICAL=governance/provenance check
NOT_CLAIMING=deployment, restart, downstream admission, branch deletion unless separately authorized
MARKER=<TASK>_ACCEPTED_MERGED
```

## Reporting boundary

Lead with behavior and impact before IDs: accepted candidate is now in `main`; exact reviewed tree preserved; CI infrastructure non-start did not execute tests; next issue remains held unless authorized.