# Controlled two-task AGY dispatch output cleanup

Use this reference after a post-canary controlled AGY stage has run and produced outputs that need review, split, or cleanup before merge/Done.

## Session pattern captured

A staged AGY launch for exactly two issues produced:

- one issue with useful baseline evidence but a lane-blocked script change,
- one issue with a PR that was CI-green but mixed unrelated/generated artifacts and a script change from the other issue.

The correct recovery was not another dispatch. It was output review, PR cleanup/splitting, and Linear proof closeout.

## Workflow

1. **Keep dispatch and output acceptance separate**
   - A `DONE:` marker and AGY return code 0 prove the task ran.
   - They do not prove the artifact/PR is mergeable or that Linear can move to Done.

2. **If output is blocked, pause redispatch immediately**
   - Remove `dispatch:ready`.
   - Add `dispatch:paused`, `output:requires-attention`, and `output:requires-verification` when available.
   - Keep the issue `In Review`, not `Done`.
   - Post exact fixes to Linear and GitHub.

3. **For lane-blocked useful output**
   - Do not bypass lane hooks.
   - Create a clean owner-lane branch from the current base branch.
   - Reapply the minimal needed change under the correct agent/branch prefix.
   - Rerun the key verification commands yourself; do not rely only on the blocked agent's self-report.
   - Add a compact evidence ledger with command markers, byte counts/hashes, and the ad-hoc-vs-suite boundary.

4. **For mixed-scope PRs**
   - First try to clean the PR branch in place.
   - If the pre-push hook blocks because existing remote history contains out-of-lane files, treat that as valid governance, not something to bypass.
   - Create a new clean replacement PR from the base branch with only the intended files.
   - Comment on and close the mixed PR as superseded.

5. **Acceptance before Done**
   - Run a focused `/tmp/hermes-verify-*` verifier over PR scope, CI, content requirements, and live Linear state.
   - Merge only clean accepted PRs.
   - Move Linear to Done only after merge readback and acceptance comments are present.
   - Remove dispatch/pause/output-blocker labels after closeout so completed issues do not re-enter dispatch.

## Verification shape

A good final verifier checks:

```text
- replacement/clean PRs are MERGED
- superseded mixed PR is CLOSED
- origin/main contains the accepted files/content
- expected command/result markers are present in evidence reports
- no absolute file:///home/... links in durable docs
- scoring language matches the accepted rubric scale
- Linear issues are Done
- dispatch:ready / dispatch:paused / output:requires-* labels are absent from completed issues
- temp verifier is removed
```

Always report:

```text
Recovery proof is ad-hoc targeted, not canonical full suite green.
```

## Pitfalls

- Do not merge a CI-green PR if its scope is wrong.
- Do not let a mixed PR remain open after a clean replacement exists.
- Do not close Linear from AGY self-report alone.
- Do not bypass lane governance to force-clean a branch with out-of-lane remote history.
- Do not include generated ad-hoc demo artifacts in a durable PR unless the issue explicitly asks for them.
