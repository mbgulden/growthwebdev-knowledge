# Already-finalized redispatch: clean verification refresh

When cron redispatches an issue that is already completed enough to be in `In Review` with a pushed `ned/<issue>` branch and PR/evidence present, treat the run as a verification refresh, not a new implementation pass.

## Pattern

1. Verify completion signals first:
   - Linear state is `In Review` (or otherwise already past build execution).
   - Remote branch exists at the expected commit.
   - PR/attachment/finalization evidence exists.
   - Local `/tmp/issue-batches/<ISSUE>_RESULT.md` may already describe prior finalization.
2. If the shared checkout is dirty or on another task branch, do **not** run `finalize_task.sh` against it and do not stage unrelated files.
3. Create a detached clean worktree from `origin/ned/<issue>` under `/tmp/prismatic-<issue>-croncheck-<timestamp>`.
4. Run focused verification there, plus a fresh `/tmp/hermes-verify-*` ad-hoc verifier when the detector expects fresh evidence.
5. Update only `/tmp/issue-batches/<ISSUE>_RESULT.md` with current evidence, Linear state, PR attachment, commit hash, and cleanup status.
6. Remove the temporary worktree and verify:
   - `WORKTREE_EXISTS=no`
   - `VERIFIER_EXISTS=no`
7. Do not post duplicate Linear finalization comments and do not rerun `finalize_task.sh` unless state/evidence is actually missing.
8. If nothing changed and there is no blocker, final cron response should be `[SILENT]`.

## Small but important cleanup pitfall

Write the result file after verification, but either perform cleanup before writing final cleanup status or patch the result after cleanup. Avoid leaving `WORKTREE_EXISTS=pending cleanup` in the final result when the worktree was actually removed later.

## Example evidence shape

```text
Focused pytest: plugins/pwp/tests/test_compiler_determinism.py PASSED
VERIFIER_SCRIPT=/tmp/hermes-verify-<issue>-cron.py
ASSERTION_SUMMARY=deterministic sorted --pwp-* CSS output confirmed
PYTEST_EXIT=0
VERIFICATION_EXIT=0
CLEANUP_EXISTS=no
WORKTREE_EXISTS=no
VERIFIER_EXISTS=no
```
