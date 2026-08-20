# Dirty checkpoint with RESULT overclaim and repair-specific regression

Use this reference when a Prismatic cap-1 producer exits unsuccessfully but leaves both a `RESULT.md` and dirty tracked bytes.

## Classification rule

A producer `RESULT.md` is not authoritative. If terminal/harness truth says failed or `producer_completed=false`, treat the result as an artifact to audit. Reject success claims when any of these hold:

- no descendant commit exists from the admitted base;
- HEAD remains the original base;
- tracked files are dirty;
- the result's reported diff/test commands did not cover uncommitted changes;
- independent fresh-archive reproduction finds a repair-surface failure or adds canonical failures beyond the accepted baseline.

Classify as `BLOCKED_DIRTY_CHECKPOINT_REPAIR_SPECIFIC_REGRESSION` when the dirty bytes introduce a failure in the repair's own acceptance surface, even if compile/lint/format pass.

## Required reconciliation fields

Capture terminal and worktree truth before any triage:

```text
HARNESS_STATUS=<failed/review_pending/etc>
PRODUCER_COMPLETED=false
PROCESS_EXIT=<code/signal>
CANCEL_REQUESTED=<true|false>
AUTOMATIC_KILL=<true|false>
RUNTIME_DEADLINE=<value|null>
PROCESS_TREE_CLEANUP_VERIFIED=<true|false>
ACTIVE_SLOT_COUNT=<n>
HEAD=<base sha>
TREE=<base tree>
DESCENDANT_COMMIT_COUNT=0
DIRTY_PATHS=<bounded tracked paths>
DIRTY_BLOB_<n>=<git hash-object path>
PATCH_SHA256=<external preserved patch>
RESULT_SHA256=<result artifact hash>
RESULT_CLAIM_ACCEPTED=false
```

Do not claim the signal source unless the terminal artifacts actually prove it.

## Fresh-archive reproduction pattern

1. Preserve an external patch/checkpoint before touching anything.
2. Materialize a `.git`-free archive from the exact base and apply/copy only the dirty bytes under review.
3. Prove archive byte equality to the worktree blobs before running product checks.
4. Run the exact acceptance gates against the archive, not the shared worktree.
5. If a verifier setup attempt uses missing executables or invalid command shape, classify that attempt as setup-only and rerun the entire sequence from the beginning with established product bindings.

Minimum gates:

```text
git -C <shared_worktree> diff --check   # read-only against exact dirty bytes
python -m compileall -q prismatic tests
ruff check <allowed implementation/test paths>
ruff format --check <allowed implementation/test paths>
python -m pytest -q <focused repair/authority tests>
python -m pytest -q tests/              # canonical comparison, if feasible
```

Compare canonical failures to the immutable base under the same parser. A dirty-only failure inside the repair surface blocks promotion even if other canonical failures are known baseline noise.

## Reporting boundary

Use a no-authority checkpoint manifest and dispatch fresh read-only triage. The next gate is diagnosis/minimum repair scope only.

Hard non-claims:

```text
NOT_CLAIMING=producer success,candidate,focused green,canonical green,implementation correctness,commit,push,PR,merge,deployment,cron/timer mutation,production DB mutation,or Linear write
```

Do not reset, clean, restore, stash, commit, replay admission, run a second consumer, launch a second producer, push, open/merge PRs, deploy, mutate timers/DBs, or write Linear without a new explicit authorization.