# Terminal timeout dirty-checkpoint baseline comparison

Use this reference when an admitted Prismatic producer is killed by the producer/CLI print timeout rather than by the admission runtime deadline, leaves no `RESULT.md` or commit, but leaves substantial dirty bytes in the allowed paths.

## Durable pattern

1. **Separate timeout sources first**
   - Record the producer's terminal truth exactly: `exit`, `cancel_requested`, `elapsed_seconds`, `runtime_deadline`, `stderr`, `result_exists`, `producer_completed`, cleanup/survivors, and active slot count.
   - If `runtime_deadline=null` but stderr says `timeout waiting for response`, classify it as the producer/CLI interaction timeout, not an admission-runtime deadline.
   - Do not rerun or retry automatically. This is still a failed producer.

2. **Freeze the dirty checkpoint before any review**
   - Preserve `HEAD`, `HEAD^{tree}`, `commits_from_base`, changed tracked paths, and `git diff --binary --full-index` as an immutable patch.
   - Hash the patch and each changed tracked file blob.
   - Write a no-authority manifest that explicitly says: not a candidate, not producer success, not recovery authorization, not second event/producer, not commit/PR/merge/deploy.
   - Leave untracked operational files out of the tracked patch unless a reviewed contract explicitly includes them.

3. **Reproduce from exact base, not the mutable worktree**
   - Materialize exact base with `git archive` into a disposable directory with no `.git`.
   - Apply only the frozen tracked patch.
   - Prove byte equality for every changed tracked file before running tests.
   - Run compile, lint, format-check, focused tests, and task-specific invariants in the disposable copy.

4. **Canonical failure attribution requires a baseline run**
   - If the checkpoint canonical suite fails, reproduce the exact base under the same interpreter and command.
   - Compare failed node IDs, not only pass/fail counts.
   - If the failed-node set/order is identical and the checkpoint only adds passing tests, classify as baseline-only canonical failures: viable evidence for review, but still not a candidate and not canonical green.
   - If checkpoint-only failures exist, classify fail-closed as a checkpoint-specific regression.

5. **Review gates**
   - Dispatch at least two read-only reviews when the dirty bytes look viable: terminal/reproduction truth and deep implementation safety against the accepted contract.
   - Handoff should point to the frozen manifest/patch hashes, exact run truth, baseline comparison, and pending review IDs.
   - The next allowed action after CLEAN/PASS reviews is only a separately frozen recovery/operator-exception contract, followed by explicit authorization. It is not a second event or producer.

## Minimum evidence fields

```text
PRODUCER_COMPLETED=false
EXIT_CODE=<code-or-signal>
CANCEL_REQUESTED=<true|false>
RUNTIME_DEADLINE=<value|null>
STDERR=<exact timeout/error line>
RESULT_EXISTS=false
PROCESS_TREE_CLEANUP_VERIFIED=true
ACTIVE_SLOT_COUNT=0
BASE_COMMIT=<sha>
BASE_TREE=<tree>
COMMITS_FROM_BASE=0
TRACKED_PATHS=<allowlist>
PATCH_SHA256=<sha256>
MANIFEST_SHA256=<sha256>
BYTE_EQUALITY=PASS
FOCUSED=<compile/lint/format/tests result>
CHECKPOINT_CANONICAL=<summary>
BASE_CANONICAL=<summary>
FAILED_NODE_IDS_EQUAL=<true|false>
CANONICAL_SUITE_GREEN=false
ORIGINAL_EVENT_COUNT=1
FUTURE_RECOVERY_EVENT_COUNT=0
SECOND_EVENT=false
SECOND_PRODUCER=false
NOT_CLAIMING=producer success,candidate,implementation correctness,canonical green,recovery authorization,commit,push,PR,merge,deploy
```
