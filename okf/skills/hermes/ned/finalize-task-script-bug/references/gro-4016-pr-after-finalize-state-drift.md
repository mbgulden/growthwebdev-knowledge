# GRO-4016 — PR-after-finalize Linear state drift

## Pattern

When a Ned task requires both `finalize_task.sh` and a GitHub PR, opening the PR after finalize can trigger repository/issue automation that changes Linear state after finalize's successful transition.

## Observed example

Task: GRO-4016 SIAL closeout.

Sequence:

1. Committed docs delta on `ned/GRO-4016-sial-closeout`.
2. Ran `finalize_task.sh` with:
   - `PRISMATIC_REPO_ROOT=/home/ubuntu/work/sentinel-it-asset-logistics`
   - `FINALIZE_LOCK_FILES='README.md docs/separation-from-sovereign-sentinel.md docs/workspace-index.md okf/audits/index.md'`
3. Finalize output reported:
   - working tree clean
   - locks unlocked
   - Linear transitioned to `In Review`
   - Linear finalization comment posted
4. Pushed branch and opened PR #2.
5. Posted richer RESULT evidence with PR URL.
6. Re-query showed Linear state had drifted to `In Progress`.
7. Explicit `issueUpdate` restored GRO-4016 to `In Review`.

## Durable workflow rule

For PR-backed finalize tasks:

- Run finalize before push/PR when following the autonomous skeleton.
- After opening the PR and posting any PR-specific evidence, re-query Linear state.
- If automation changed state away from the intended review state, explicitly restore `In Review` and report that correction.

This is not a blocker; it is a post-finalize verification step.
