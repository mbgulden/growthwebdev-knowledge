# Focused PR durable deployment pattern

Use when a focused Prismatic governance PR has been merged and must be made operational without risking unrelated dirty runtime work.

## Pattern

1. After merge, read back the PR state and merge commit SHA from GitHub.
2. Create a clean immutable release checkout under `/home/ubuntu/.prismatic/releases/prismatic-engine-<sha12>` pinned to the merge SHA.
3. Verify the release checkout before wiring it into operations:
   - `git rev-parse HEAD` equals the merge SHA;
   - `git status --porcelain` is empty;
   - compile changed Python entrypoints;
   - run scoped linters/tests for the touched files;
   - run the relevant live monitor from the release checkout.
4. Preserve the current runtime before changing wrappers:
   - `runtime-before.sha`;
   - `runtime-before.status`;
   - `runtime-dirty.patch`;
   - copies of untracked files;
   - copies/checksums of profile scripts being edited.
5. Repoint only the operational wrapper(s) needed for the merged slice to the clean release checkout.
6. Add a rollback note under `/home/ubuntu/.prismatic/deployments/<slice-timestamp>/ROLLBACK.md` that restores prior wrappers and states non-claims.
7. Verify after deployment with a readback script that checks:
   - wrapper paths reference the release checkout and no longer reference mutable dev worktrees;
   - release SHA still matches expected merge SHA;
   - live monitor reports expected state;
   - dirty runtime SHA/status/patch/untracked files are unchanged when intentionally preserving runtime;
   - services and health endpoints remain active if relevant.

## Pitfall

Do **not** reset or replace a dirty production/runtime checkout merely because a focused PR merged. If the PR does not require runtime service code changes, prefer immutable release checkouts plus wrapper repoints. Blindly switching Gateway/runtime to clean `main` can discard still-deployed dashboard/governance work that belongs to another slice.

## Proof packet fields

Include both deployment and boundary evidence:

```text
COMMAND=<merge/readback/release-create/wrapper-repoint/verification summary>
RESULT=PASS|FAIL|BLOCKED
LOG=<verification log path>
SCOPE=<merged slice only>
AD_HOC_OR_CANONICAL=<GitHub CI plus ad-hoc targeted production readback>
NOT_CLAIMING=<no Prompt5 unlock,no dirty runtime reconciliation,no canonical full-suite claim>
MARKER=<durable deployment marker>
```
