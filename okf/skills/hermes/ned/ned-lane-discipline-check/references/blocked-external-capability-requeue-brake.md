# Blocked external-capability task: stop autonomous requeue without fake-finalizing

Use this when a Ned-lane task has already produced a valid PR/branch/test evidence, but execution is blocked by an external product/API capability that is not exposed to the local toolchain (example: Jules v0.1.42 has no `remote delete`/`cancel` command for legacy sessions).

## Trigger

- Linear issue keeps resurfacing as `TASK:GRO-XXXX` after a prior blocker report.
- The issue is genuinely Ned/infrastructure lane, not a misroute.
- Existing branch/PR/artifact is intact and targeted tests still pass.
- Live execution still fails closed because the external capability is unavailable.
- Finalizing would be dishonest because the acceptance criterion requiring the external side effect is not satisfied.

## Required sequence

1. Re-read the issue comments and confirm a prior blocker report or result artifact exists.
2. Reverify the branch/PR in an isolated worktree, not the dirty shared checkout:
   - `git worktree add /tmp/prismatic-<issue>-verify origin/ned/<issue>`
   - confirm `HEAD == origin/ned/<issue>` and worktree clean
   - run the focused tests/lint/format and a live dry-run/execute probe if safe
   - remove the temporary worktree afterward
3. Before preserving the blocker, satisfy the hard blocker due-diligence rule:
   - inspect OKF integration docs for the tool/API capability
   - use `session_search` for prior working recipes or known blockers
   - grep relevant `.env` files for alternate endpoints/credentials
4. If still blocked, do **not** run `finalize_task.sh` and do **not** transition the issue to In Review.
5. Add `agent:needs-human-review` while preserving the existing owner/lane labels and current state (`Todo` is fine). This is the queue brake: it tells the scanner/curator this is not autonomous-executable until a human supplies the missing external capability or decision.
6. Verify Linear state+labels after mutation.
7. Re-run the Ned scanner from the cron script location when possible (`~/.hermes/profiles/ned/scripts/prismatic/lanes/ned/scan_tasks.py`) and confirm the blocked issue no longer emits as the active `TASK:`. It may still be listed as open; the key check is that the emitted task pointer advances or disappears.
8. Final response should be a concise blocker/update report, not `[SILENT]`, when the cron prompt is delivering a queue-piling alert and you changed Linear labels.

## Notes

- This is different from misroute handling: keep the correct Ned infra label if the task is in-lane; add the human-review blocker label rather than relabeling to another owner.
- This is different from already-finalized PR resurfacing: there is no successful finalization because the external side effect remains impossible.
- The useful action is reducing repeat autonomous churn while leaving clear evidence for Michael/human review.
