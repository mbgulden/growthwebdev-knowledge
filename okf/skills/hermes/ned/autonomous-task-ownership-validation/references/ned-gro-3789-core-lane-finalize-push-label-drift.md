# GRO-3789 — core-lane handoff after finalize: lane push + Linear drift recovery

When a core-lane handoff is implemented under Ned's branch, `finalize_task.sh` can run before the final push/PR is clean. If the post-finalize push then fails, treat the finalize transcript as provisional and correct the branch/Linear state before suppressing delivery.

## Durable pattern

1. **Commit early, run verification, then finalize** per the skeleton.
2. **If pre-push rejects out-of-lane verification files**, do not bypass the guard for routine work. Remove or relocate the offending files, amend the branch, and rerun a fresh targeted verifier. For Ned, top-level `tests/` is outside lane; use a `/tmp/hermes-verify-*` ad-hoc verifier when a durable top-level test file would violate lane ownership.
3. **Push only the in-lane branch** and open the PR. Record the pre-push guard output (`Files: N changed, N in-lane, 0 violations`) as evidence.
4. **Re-query Linear after PR creation/finalize.** Automation may drift the issue back to `In Progress` or add stale labels such as `dispatch:ready`, `agent:agy`, or `agent:done` even after `finalize_task.sh` printed `In Review`.
5. **Manually restore review state/labels if needed:** set state to `In Review`, keep `agent:peer-review`, remove active dispatch/done labels, and post a Linear evidence-refresh comment with commit, PR, verifier output, and cron rerun evidence.
6. **Refresh `/tmp/issue-batches/<ISSUE>_RESULT.md`** with final remote branch, PR, verifier, cron rerun, and cleanup evidence.

## Verification shape used

- `python3 -m py_compile prismatic/journal.py`
- `/tmp/hermes-verify-<ISSUE>-*.py` with explicit booleans for changed behavior, then `rm -f` in the same shell and print `AD_HOC_VERIFIER_CLEANED`.
- For cron-specific exit criteria, rerun the relevant Hermes cron under the owning profile by setting both `HERMES_HOME` and `HERMES_PROFILE` to that profile before `hermes cron run <job_id>`.

## Pitfall

Do not assume a successful `finalize_task.sh` run means the task is actually ready for review when later push/PR/label operations occurred. The authoritative end state is: remote branch pushed, PR open, Linear re-queried in `In Review`, labels cleaned, and local RESULT updated.