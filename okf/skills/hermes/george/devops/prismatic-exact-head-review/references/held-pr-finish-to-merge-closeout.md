# Held PR finish-to-merge closeout pattern

Use this when Michael authorizes finishing an older/held Prismatic PR through publication and merge after it has drifted behind current `main`.

## Pattern

1. **Preserve and isolate.** Preserve the held PR head and create a clean isolated worktree from current base. Do not normalize or rewrite useful historic branches blindly.
2. **Integrate current main deliberately.** Merge or rebase only after proving the held PR's textual/semantic drift against `origin/main`; record base/head/tree separately.
3. **Review the contract, not just tests.** For bounded-output/recap/receipt features, independent exact-head review should trace semantic invariants through the real output path: ordering, ID ambiguity, redaction, byte bounds, rollback/transaction semantics, symlink containment, and platform portability.
4. **Repair on the same task until CLEAN.** If reviewers find blockers, preserve the blocked commit/tree and review verdicts, repair in the same isolated worktree, commit a new candidate, rerun canonical/local proof, and launch fresh independent exact-head review bound to the new commit.
5. **Classify setup failures as non-evidence.** Wrong venv/import path, empty-CWD fixture mismatch, missing optional dependency in a reused verifier venv, or GitHub CI jobs with `steps=[]` are setup/no-execution evidence. Fix verifier binding and rerun; do not call them candidate failure or candidate pass.
6. **Publish only after accepted exact head.** Before push, assert remote PR head, reviewed base, `origin/main`, ancestry, expected merge tree, and clean status. Update PR body/comments with exact head/tree/proof/non-claims.
7. **Merge under explicit authorization.** If GitHub CI did not execute but Michael authorized provider-neutral merge, record that boundary, merge, and immediately prove remote `main`, merge commit, ordered parents, merge tree, PR state, and changed-path set.
8. **Close out without redundant writes.** If Linear or another tracker is already in the intended final state after merge, read it back through the bounded broker and write a local reconciliation receipt with `mutation_sent=false` rather than sending a redundant state mutation.
9. **Update handoff last.** Add a compact marker with merge commit/tree, accepted head, review handle, canonical proof class, no-run CI boundary, Linear reconciliation, receipt path/hash, and non-claims.

## Proof packet fields

```text
HELD_HEAD=<original-pr-head>
ACCEPTED_HEAD=<final-reviewed-head>
ACCEPTED_TREE=<tree>
BASE=<reviewed-origin-main>
MERGE_COMMIT=<merge-sha>
MERGE_TREE=<tree; should match accepted tree unless intentionally advanced>
PARENT1=<base>
PARENT2=<accepted-head>
INDEPENDENT_REVIEW=<handle:CLEAN/PASS>
LOCAL_CANONICAL=<counts or log>
GITHUB_CI=<executed|no-execution-infra + run id>
TRACKER_STATE=<Done/other readback>
MUTATION_SENT=<true|false>
NOT_CLAIMING=<deployment,runtime restart,release publication,branch deletion unless proven>
MARKER=<handoff marker>
```

## Pitfalls

- Do not let an old PR `PASS` or greenish historic checks carry across repairs or a current-main integration commit.
- Do not call no-run GitHub CI either red or green product evidence; it is a publication/merge-policy boundary.
- Do not send tracker mutations just because the closeout workflow expected one; first read the live state and no-op when it is already satisfied.
- Do not delete branches/worktrees as part of closeout unless Michael explicitly authorizes deletion.
