# In Review scanner resurfacing (GRO-3476, 2026-07-06)

## Pattern

A Ned task can be genuinely complete and still reappear in the cron scanner feed when Linear state is `In Review`.

Observed on GRO-3476:

- Linear state: `In Review`.
- Branch existed and was pushed: `ned/GRO-3476`.
- PR existed and was open.
- Linear already had a `## Ned finalization report` comment from `finalize_task.sh`.
- Worktree was clean.
- Targeted test still passed.
- The scanner still emitted `TASK:GRO-3476` because the dispatcher query includes Linear states whose `type` is `started`; `In Review` is a `started` state.

## Disposition

Do **not** rerun `finalize_task.sh` just because the scanner resurfaces an already-finalized issue.

First verify:

1. Linear issue state and last comments.
2. Existing branch/remote/PR.
3. Git status.
4. Targeted verification if cheap.
5. Whether a prior `## Ned finalization report` comment exists.

If all completion evidence is present, report that the resurfacing is scanner/query noise, not lost work. No new commit, no new finalize, no duplicate Linear comment.

### Missing-PR sub-case (GRO-3477, 2026-07-06)

If the issue has a finalization report and a pushed `ned/GRO-XXXX` branch, but **no GitHub PR exists**, do not classify it as pure scanner noise yet. The branch is finalized locally but review handoff is incomplete.

Validated recipe:

1. Check the remote branch exists (`git ls-remote origin ned/GRO-XXXX`).
2. Check PR absence (`gh pr list --head ned/GRO-XXXX --json number,state,url`).
3. Switch to the branch and run the cheapest targeted verification that covers the changed artifact.
4. Create the PR against the correct base (`deploy-fresh` in Prismatic Engine) with summary + verification evidence.
5. Run `finalize_task.sh GRO-XXXX ned/GRO-XXXX ned` again so Linear lands in `In Review` with a fresh finalization comment after the review handoff exists.
6. Re-verify: PR open, Linear `In Review`, worktree clean.

This is distinct from duplicate-finalization noise: the missing PR is a recoverable handoff gap, not a reason to suppress silently.

## Implementation cure

The durable cure is in scanner/query hygiene: completed or already-finalized review states need a separate queue interpretation. Either exclude `In Review` from pickup, or classify it as review-followup instead of executable Ned work when a finalization report + PR already exists.
