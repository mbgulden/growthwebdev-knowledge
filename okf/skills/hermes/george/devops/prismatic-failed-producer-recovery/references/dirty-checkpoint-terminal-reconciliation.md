# Dirty-checkpoint terminal reconciliation

Use this reference when a Prismatic producer terminates without a committed candidate or `RESULT.md`, but leaves useful dirty worktree edits.

## Trigger

- Harness/receipt says failed or review_pending.
- `producer_completed=false` and `result_exists=false`.
- Worktree has zero commits from base but non-empty tracked diff or new module bytes.
- A prior recovery contract/envelope exists, but the user asks for a fresh checkpoint or the live state diverges from the stale handoff.

## Required sequence

1. **Reconcile terminal truth from receipts and ledger first**
   - Event count, outbox status, claim attempt/state, lifecycle.
   - Harness status/state, exit code, cancel/automatic-kill/runtime-deadline flags, stderr, cleanup, survivors, slot count.
   - Treat `tail --pid` completion as proof the PID exited, not as product success.

2. **Preserve the dirty worktree without mutation**
   - Record HEAD/tree/base, commits-from-base, tracked diff hash, new module hashes, checkpoint patch hash, allowed paths.
   - Do not reset, clean, stash, format, lint-fix, commit, or rerun the producer.

3. **Reproduce in a disposable exact-base materialization**
   - Archive exact base into a `.git`-free temp directory.
   - Apply only the current tracked diff and copy any new/untracked implementation module bytes explicitly.
   - Prove byte equality for every implementation file before running tests.
   - Redirect full command output to `/tmp/hermes-verify-*` logs and hash those logs.

4. **Classify executable results without overclaiming**
   - Compile PASS means syntax only.
   - Focused pytest PASS does not cure lint/format/security blockers or canonical-suite gaps.
   - If one interpreter fails due to verifier setup but a deployed/project interpreter runs the same focused tests, record the setup failure as verifier-environment evidence and make the valid interpreter result authoritative.

5. **Freeze a checkpoint artifact, not a candidate, when coherence fails**
   - Include terminal truth, dirty hashes, fresh materialization proof, command results, first implementation blocker, and hard non-claims.
   - Dispatch fresh exact-hash review of that checkpoint artifact.
   - Do not rely on older recovery-ready reviews until the fresh checkpoint review passes and Michael explicitly authorizes the next event.

## Minimum proof fields

```text
ARTIFACT_SHA256=<sha>
EVENT_COUNT=<n>
OUTBOX_STATUS=<processed|...>
CLAIM_STATE=<state>
LIFECYCLE=<events>
HARNESS=<status/state>
PRODUCER_COMPLETED=false
PROCESS_EXIT=<code>
CANCEL_REQUESTED=<true|false>
AUTOMATIC_KILL=<true|false>
RUNTIME_DEADLINE=<value|null>
RESULT_EXISTS=false
PROCESS_TREE_CLEANUP=<true|false>
SURVIVORS=<n>
ACTIVE_SLOT_COUNT=0
HEAD=<base head>
TREE=<base tree>
COMMITS_FROM_BASE=0
TRACKED_DIFF_SHA256=<sha>
NEW_MODULE_SHA256=<sha-if-any>
MATERIALIZATION_MATCH=<n>/<n>
COMPILE=<PASS|FAIL>
RUFF_CHECK=<PASS|FAIL>
RUFF_FORMAT=<PASS|FAIL>
FOCUSED_TESTS=<PASS|FAIL>
FIRST_IMPLEMENTATION_BLOCKER=<path:line-range:summary>
CANDIDATE_COHERENT=false
COMMITTED_CANDIDATE_EXISTS=false
SECOND_EVENT=false
SECOND_PRODUCER=false
NOT_CLAIMING=<candidate, canonical green, event, producer, PR, merge, deploy, cron/timer, DB, Linear>
```

## Pitfall

A historical recovery contract can become stale after a fresh terminal checkpoint request. Update the handoff to the current blocked-checkpoint review gate rather than leaving `RECOVERY_ADMISSION_READY` as the active next gate.