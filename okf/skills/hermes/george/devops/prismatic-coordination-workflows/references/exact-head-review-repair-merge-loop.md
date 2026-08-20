# Exact-head review → repair → re-review → merge loop

Use this when a Prismatic assigned-agent candidate produces a good-but-not-yet-acceptable branch and independent review finds finite blockers.

## Pattern

1. **Freeze the reviewed identity.** Record base commit, candidate commit, tree, worktree path, and changed paths before acting on review findings.
2. **Do not approve stale failed heads.** If the review is BLOCKED but findings are valid, port each finding into a new frozen candidate commit. Preserve the old failed exact head as rejected evidence rather than mutating the acceptance verdict.
3. **Repair with narrow scope.** Keep the change set bounded to the contract/artifact path unless the review finding proves another path is required. If active reviewers or harnesses can touch the original worktree, perform same-task repairs in an isolated repair worktree branched from the blocked exact head; never let an uncommitted green repair sit in a shared worktree.
4. **Verify locally with explicit labels.** For doc/contract-only changes, run focused ad-hoc checks such as:
   - exact head/tree identity;
   - base ancestry;
   - clean worktree;
   - one-path scope;
   - `git diff --check BASE HEAD`;
   - required terms/canaries/forbidden markers;
   - no implementation authorization language.
   For code/data repairs, run the smallest focused behavior/regression/static bundle that exercises the finding, then `git add` and `git commit` immediately after the green run in the same bounded shell when possible. If `git commit` reports no tracked changes, stop and re-check identity/status before claiming preservation; a concurrent reset may have erased the repair.
   Label this as ad-hoc/focused proof, not canonical runtime suite green.
5. **Re-dispatch independent exact-head review.** The re-review brief must include the new commit/tree, base, path, prior blockers, and explicit read-only/no-mutation constraints.
6. **Accept only CLEAN/PASS on the newest exact head.** If the review finds more finite blockers, repeat the repair/re-review loop on a new commit.
7. **Create the PR after CLEAN/PASS.** Use a PR body that leads with Problem → Changed → Proof → Boundary.
8. **Merge only when authorized and head-bound.** Use a merge command that binds to the accepted head, e.g. `gh pr merge <PR> --merge --match-head-commit <ACCEPTED_COMMIT>`.
9. **Verify post-merge ancestry and tree.** Fetch remote `main`, verify accepted commit is an ancestor, and compare the remote merge tree to the accepted tree for doc-only merge commits.
10. **Write an acceptance/merge receipt.** Include accepted commit/tree, PR, merge commit, remote main tree, reviewer verdict, CI boundary, non-claims, and receipt hash.

## CI infrastructure boundary

If GitHub Actions jobs did not start because of billing/spending-limit/account infrastructure, report it separately:

```text
RESULT=INFRASTRUCTURE_NOT_STARTED
TEST_EXECUTION=none
CANDIDATE_FAILURE=false
```

Do not convert infrastructure non-execution into a candidate test failure, and do not claim CI green. If local exact-head independent review is the accepted provider-neutral proof for this slice, say so explicitly.

## Report shape

Use Michael's preferred order:

1. Problem
2. Changed
3. Why it matters
4. State
5. Next move
6. IDs/hashes/logs

For acceptance packets, keep the boundary prominent: contract-only acceptance does not authorize implementation, deployment, Linear mutation, runtime mutation, or successor admission unless separately authorized.
