# Post-stage drift cleanup before the next controlled AGY stage

Use this reference after a recovery/canary/output-review chain has succeeded and the next request is to continue with another staged dispatch.

## Trigger

- Prior canary/stage outputs were merged and accepted.
- The next proposed move is another small controlled AGY batch.
- Live state shows completed issues, stale dispatch labels, abandoned-run comments, or local WIP branches from the previous stage.

## Pattern

1. **Clean drift before launching anything**
   - Query live Linear for the completed upstream/canary issues and the next candidate issues.
   - Remove `dispatch:ready` from completed issues so they cannot be redispatched.
   - Add a concise Linear comment explaining the cleanup.
   - Park any local WIP branch without deleting it: switch the active worktree back to a clean base branch (`main`/`origin/main`) and report the parked branch/diff.

2. **Preflight the exact next issues**
   - Read title, state, labels, and recent comments for each next issue.
   - Treat old abandoned-run / empty-log comments as historical context, not current blockers, if the issue is still intentionally selected for the new controlled stage.
   - Confirm `agent:agy` or the intended assigned-agent label is present.

3. **Prevent duplicate broad dispatch**
   - Before the manual controlled runner starts, remove `dispatch:ready` from the selected issues.
   - Add `output:requires-verification` so the stage result is clearly review-gated.
   - Add a launch comment stating the exact allowed issue set and that dispatch success is not Done.

4. **Hard-guard the runner**
   - Encode the allowed issue identifiers in the runner and assert the set exactly.
   - Run `agy --print` sequentially per issue with per-issue `prompt.txt`, `task_payload.json`, `RESULT.md`, `proof.json`, and `stage_summary.json` under `/tmp/agy-controlled-stage-proofs/<timestamp>/`.
   - Do not launch or inspect unrelated issues.

5. **Normalize output state after AGY returns**
   - Move each issue to `In Review`, never Done.
   - Post a Linear result comment with return code, DONE marker, artifact paths, bytes/hash, model, and duration.
   - If opening a PR was part of the output but AGY only pushed a branch, open the PR manually and post the PR link back to Linear.
   - If Linear or automation drifts a launched issue back to `In Progress`, correct it to `In Review` and comment the correction.

6. **Final verification packet**
   - Verify exact allowed set, no active AGY process, PRs open, CI status if available, Linear states/labels/comments, and stale completed upstream labels cleaned.
   - Explicitly say: `Recovery proof is ad-hoc targeted, not canonical full suite green.`
   - Final marker should be a stage-complete-for-review marker, not an output-accepted marker.

## Pitfalls

- Do not leave `dispatch:ready` on completed canary/output issues.
- Do not leave `dispatch:ready` on controlled-stage issues while a manual runner is active; that permits duplicate dispatcher grabs.
- Do not mark the selected issues Done after a successful `DONE:` marker; the PR/artifact still needs normal review.
- Do not assume AGY opened a PR just because it pushed a branch. Check GitHub; open the PR yourself if needed and mark it as review-gated.
- Do not merge a downstream PR that includes upstream files by accident. Note the dependency/scope and review or rebase after the upstream PR lands.
