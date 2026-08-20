# Uncommitted accepted-candidate reconciliation and merge

Use this when an exact-byte review accepted a candidate that still exists as uncommitted work in a clean/isolated worktree and Michael authorizes reconciliation + merge.

## Pattern

1. **Bind base before committing.** Fetch `origin --prune` and assert `origin/main` still equals the independently reviewed base commit. If remote main advanced, do not commit-and-merge as accepted; create a reconciled candidate and rerun exact-head verification/review.
2. **Stage only reviewed paths.** Recheck the accepted manifest/hash first, then `git add -- <allowlisted paths>`. Assert staged path count/name list equals the reviewed allowlist and run `git diff --cached --check` before commit.
3. **Commit with local repo identity only if needed.** If `git commit` fails because author identity is unset, derive the repository's established identity from recent commits and set `git config --local user.name/user.email` in that worktree only. Do not set global identity unless explicitly asked.
4. **Post-commit exact-head verifier.** After commit, run a fresh OS-safe `/tmp/hermes-verify-*` pytest probe that asserts exact `HEAD`, tree, changed path list, and clean worktree, plus focused tests/lint/build/compile/diff. This converts an accepted uncommitted byte set into an immutable commit-bound candidate.
5. **Push and open PR with boundaries.** Include reviewed manifest/hash, head/tree, focused proof, and explicit non-claims in the PR body. If GitHub reports empty `statusCheckRollup`, classify as no GitHub checks reported; do not claim CI execution.
6. **Final pre-merge fail-closed assertions.** Before `gh pr merge`, assert PR head OID equals the exact reviewed commit, PR base name is `main`, fetched `origin/main` still equals reviewed base, and the worktree is clean.
7. **After merge, bind the artifact.** Fetch again; assert remote main equals PR merge commit, merge parents equal `<reviewed-base> <reviewed-head>`, merge tree equals reviewed head tree, and first-parent changed paths equal the allowlist.
8. **Reproduce from immutable archive.** Run focused tests/build/lint/format/compile from `git archive <merge-commit>` in a disposable directory, not from the dev worktree. Report as `ad-hoc targeted post-merge archive`, not canonical full-suite green unless the canonical suite actually ran.
9. **Preserve branch unless authorized.** Merge authorization is not branch-deletion authorization.

## Proof markers to report

```text
REVIEWED_BASE=<sha>
REVIEWED_HEAD=<sha>
REVIEWED_TREE=<tree>
PR=<url/number>
MERGE_COMMIT=<sha>
REMOTE_MAIN=<sha>
MERGE_PARENT_1=<reviewed-base>
MERGE_PARENT_2=<reviewed-head>
MERGE_TREE=<tree>
TREE_MATCH=true
POST_MERGE_ARCHIVE_LOG=/tmp/hermes-verify-*.log
AD_HOC_OR_CANONICAL=ad-hoc targeted post-merge archive
NOT_CLAIMING=GitHub CI execution, canonical full-suite green, deployment, branch deletion
```
