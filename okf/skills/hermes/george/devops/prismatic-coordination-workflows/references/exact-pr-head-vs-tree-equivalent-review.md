# Exact PR-head vs tree-equivalent review

## When to use

Use this pattern when a Prismatic repair has already received independent clean-room proof on an equivalent tree, but the open PR head or merge candidate is not the same commit object.

## Lesson

A tree-equivalent integration branch is strong evidence that content can be reconstructed cleanly on current `main`, but it is **not** by itself merge authorization for the open PR. Michael's standing merge authorization is exact-head based: the PR head itself must receive an independent `CLEAN` verdict, even when another commit has the identical tree.

## Workflow

1. Capture current source-of-truth values:
   - `origin/main` commit and tree
   - PR number, head ref, head SHA, base ref, mergeability, hosted check status
   - PR head tree
   - reconstructed integration head/tree, if used
2. Verify tree equality explicitly:
   - `git rev-parse <pr-head>^{tree} <integration-head>^{tree}`
   - record whether the two tree SHAs match
3. Run local proof on the integration or PR head as appropriate:
   - focused tests for the changed behavior
   - canonical suite when practical
   - lint/format/diff checks
   - wheel/package import if packaging/runtime behavior matters
   - save noisy output to logs and hash logs/artifacts
4. Dispatch independent review(s) with narrow, read-only contracts:
   - tree-equivalent integration review may validate reconstruction quality
   - exact PR-head review must validate the open PR head SHA before merge
5. Keep successors paused until exact PR-head review is `CLEAN`.
6. If exact PR-head is `CLEAN`, merge only under current authorization policy; then read back merge commit/tree and run post-merge immutable checkout/package proof.
7. If exact PR-head is `REPAIR`, stop the line and perform same-task repair.

## Reporting boundary

Use language like:

```text
TREE_EQUIVALENT_REVIEW=<clean|pending|repair> — useful evidence only
EXACT_PR_HEAD_REVIEW=<clean|pending|repair> — required before merge
MERGE_AUTHORIZATION=<blocked until exact PR-head clean|authorized by exact-head clean>
NOT_CLAIMING=hosted CI green, deployment, runtime release, successor dispatch
```

## Pitfalls

- Do not merge from a tree-equivalent commit review alone when the open PR head commit has not been independently reviewed.
- Do not treat hosted GitHub zero-step account/spending-policy failures as code-test evidence; report them separately from local/canonical proof.
- Do not let an integration branch replace the PR source of truth unless Michael explicitly changes the merge target.
- Do not resume GRO successors until the repair PR is exact-head clean and merged or explicitly abandoned.
