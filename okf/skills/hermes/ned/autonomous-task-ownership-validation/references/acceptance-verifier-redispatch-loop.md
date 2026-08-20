# Acceptance-verifier redispatch loop pattern

When a Ned issue is an acceptance verifier (example class: “run this live query and close only if result > 0”) and the acceptance check keeps failing, do not keep treating every scanner pickup as new implementation work.

## Durable pattern

1. Re-run the acceptance check honestly against the live source of truth.
2. Confirm real upstream activity exists when the verifier requires it (e.g. recent AGY/GRO activity markers) so the failure is not just “nothing ran.”
3. Check whether the child/fix task already exists and whether its PR/branch is still pending review or deployment.
4. If acceptance is still `0`/false and the fix is already pending elsewhere:
   - Do **not** run `finalize_task.sh`; that would mark an unmet verifier as progress.
   - Do **not** synthesize/backfill passing evidence.
   - Post one concise Linear evidence comment if the latest comment does not already reflect the current state.
   - Move the verifier back to `Todo`.
   - Remove active redispatch labels such as `dispatch:ready`, `agent:agy`, and `agent:ned`.
   - Add `agent:needs-human-review` to stop the cron redispatch loop until the pending fix is merged/deployed.
   - Write/update the local `RESULT.md` with the failing query, state, child task/PR, and close condition.
5. Unlock any files manually if you acquired locks for read/verification only.

## Why

A verifier issue is not complete until its acceptance predicate is true. Re-running `finalize_task.sh` on a failing verifier is the same theater failure as finalizing an out-of-lane task: it creates Linear state churn without a working artifact.

## Example close-condition wording

“Merge/deploy the child fix PR, run one real Popen-backed GRO cycle, then require the acceptance query to return `> 0`.”
