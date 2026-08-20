# Failed-producer same-task recovery for Prismatic agents

Session lesson from GRO-4270 AGY admission: the producer timed out after leaving useful uncommitted diffs but no completion/result receipt.

## Durable rule

A timed-out producer with useful diffs is **not** a producer pass. It may become a recovered candidate only through bounded operator recovery and exact-head independent review.

## Recovery sequence

1. Bind to the admitted task/event and read the task contract.
2. Inspect the uncommitted diff and preserve only in-scope source/test/package-data edits.
3. Remove undeclared scratch/progress artifacts such as `STARTED.md` before candidate commit.
4. Repair concrete contract defects discovered by operator inspection; do not launch a second producer unless Michael authorizes it.
5. Run focused behavior checks plus packaging/resource proof; run the project-defined canonical local target when feasible and label it separately from ad-hoc proof.
6. Commit once, then record exact `HEAD`, tree, changed paths, worktree cleanliness, log paths, and log hashes.
7. Dispatch independent exact-head review before accepting, pushing, merging, deploying, mutating Linear, or admitting dependent work.

## Reporting shape

```text
PRODUCER_STATUS=failed_or_timeout
PRODUCER_COMPLETED=false
RECOVERY_STATUS=candidate_ready_pending_independent_review
CANDIDATE_COMMIT=<sha>
CANDIDATE_TREE=<tree>
EXACT_CHANGED_PATHS=<n>
WORKTREE_CLEAN=<true|false>
AD_HOC_OR_CANONICAL=<proof class>
NOT_CLAIMING=producer PASS, independent acceptance, push, PR, merge, deploy, Linear mutation, dependent-task admission
```

## Pitfall

Do not let successful recovery proof erase the producer boundary. The accepted object is the exact recovered candidate after independent review, not the failed producer run.
