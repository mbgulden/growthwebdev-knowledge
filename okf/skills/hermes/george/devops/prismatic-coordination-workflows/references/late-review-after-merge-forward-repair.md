# Late review returns REPAIR after merge — forward-repair gate pattern

Use when an async or delegated exact-head review returns a valid `REPAIR` verdict after the candidate PR has already merged.

## Durable sequence

1. Treat this as a verification race / merge incident, not as a completed task.
2. Immediately pause successor slices and producer admission for the affected line. Do not dispatch the next governance issue until the merged fail-open state is repaired and reviewed.
3. Verify the merged PR state directly (`gh pr view <n> --json state,mergedAt,mergeCommit,headRefOid,url`) and record:
   - PR head SHA
   - merge commit SHA
   - merged timestamp
   - late review identifier/verdict
4. Do **not** reset history or attempt to erase the merge. Create a clean forward-repair branch/worktree from current merged `main` and carry the minimal fix forward.
5. Preserve the valid late-review findings as blockers. Apply the repair in the same task lane, with explicit boundaries for what remains out of scope.
6. Produce exact-head proof on the forward-repair commit:
   - focused regression tests for the blocker
   - canonical suite where feasible
   - lint/format/diff checks
   - package/import smoke when the module is distributed
   - bundle or other immutable artifact with SHA256
7. Dispatch a fresh independent exact-head adversarial review against the forward-repair commit. Any valid `REPAIR` stops the line again.
8. Only after exact-head `CLEAN`, open a focused forward-repair PR. Require exact PR-head review before merge.

## Proof packet fields

```text
INCIDENT=MERGED_BEFORE_LATE_VALID_REPAIR_VERDICT
PR_HEAD=<sha>
MERGE_SHA=<sha>
MERGED_AT=<timestamp>
FORWARD_REPAIR_BRANCH=<branch>
FORWARD_REPAIR_HEAD=<sha>
FORWARD_REPAIR_TREE=<tree>
BUNDLE=<path>
BUNDLE_SHA256=<sha256>
FOCUSED=<result>
CANONICAL=<result or not-run reason>
REVIEW=<delegation/job id + status>
NOT_CLAIMING=deployment, restart, successor admission, generic dispatch resume, Linear write unless explicitly performed
```

## Pitfalls

- Do not describe the merged PR as accepted proof once a late valid `REPAIR` exists. The accepted state becomes `post-merge forward repair pending`.
- Do not launch successor tasks while the repair review is pending; this violates fail-closed sequencing.
- Do not overclaim public safety: local/canonical proof on the repair commit is not production proof, and a repair branch is not a deployed service.
- Do not rewrite or revert by default. Prefer forward repair from merged main unless Michael explicitly authorizes a revert/rollback path.
