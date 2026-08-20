# Provider-neutral ordered execution controller

Use this reference when Michael asks George to execute a Beyond-North-Star / provider-neutral runway rather than only plan it.

## Trigger

- GitHub Actions is optional/unavailable under explicit continuation policy.
- One provider-neutral PR has clean exact-head review and local proof.
- Michael asks to execute the recommended order across several dependent slices.

## Pattern

1. **Close the current reviewed PR first.**
   - Refresh exact-head proof on the reviewed candidate.
   - Preserve/hash the candidate before mutating the remote branch.
   - If the PR branch must be force-updated, use an exact old-head lease and update only that existing branch.
   - Read back PR head/mergeability before merge.
2. **Verify the merge SHA, not just the PR head.**
   - After merge, bind the GitHub merge SHA and prove its tree equals the reviewed candidate tree when that is the intended invariant.
   - Build a standalone immutable release from the merge SHA.
   - Run canonical/source/package/build proof from that release.
   - Keep deployment/restart/Linear closeout as separate explicit authorization gates.
3. **Reconcile state before starting successors.**
   - Pause/retire completed-slice watchers.
   - Update queue, control JSON, and `PRISMATIC_CURRENT_HANDOFF.md` from completed-slice active/pending to merged-release-verified.
   - Run a focused state verifier that binds PR merged state, release SHA, queue digest, control state, handoff markers, and non-claims.
4. **Admit only one next producer.**
   - Do read-only current-main/API/path architecture analysis first.
   - Freeze a bounded contract on exact merged `main`, then dispatch one cap-1 producer.
   - Keep successors `QUEUED_DISPATCH_PAUSED`.
5. **Filesystem-bus dispatch compatibility.**
   - Do not assume the newest CLI interface is installed. If the bus rejects rich flags, read the live dispatch interface and fall back to the older `repo=<worktree>` / `branch_base=<exact SHA>` style while keeping the full FINAL contract inside the task packet.
   - After dispatch, bind the actual task ID from the worker command line/status file; do not infer from a failed or retried timestamp.
   - Some bus versions use `status`, not `state`, in `STATUS.json`; check both when writing verifiers/watchers.
6. **Attach a finite controller for long runways.**
   - Use an attached cron/controller with a finite repeat cap, one material transition per tick, and material-change-only reports.
   - Every tick should re-read process/Git/GitHub/queue/control state before acting so it does not duplicate a producer or overwrite a newer candidate.
   - The controller may advance the runway only when cap 1 is free and the predecessor is closed by exact proof/review/merge/release rules.

## Proof packet fields

```text
COMMAND=<merge/release/dispatch/controller/state-verifier summary>
RESULT=<PASS|PARTIAL|BLOCKED>
LOG=<state verifier or canonical release log path>
SCOPE=<PR closeout plus next-slice admission>
AD_HOC_OR_CANONICAL=<canonical release proof + ad-hoc state proof>
NOT_CLAIMING=<successor complete; deployment authorized; cap increase authorized>
MARKER=PROVIDER_NEUTRAL_ORDERED_EXECUTION_ACTIVE
```

## Pitfalls

- `CLEAN` review on an old head is invalidated by rebase or any new commit.
- Local PR-head proof is not enough after merge; prove the immutable merge-SHA release.
- A scheduler/controller is not authorization to raise cap, deploy, restart, close/delete PRs, or write Linear.
- Queue/control/handoff can be stale immediately after a producer exits; trust direct process/Git/GitHub truth, then reconcile durable state.
- A bus startup assertion can fail because the verifier used the wrong timestamp or field name even though the worker actually claimed the task; inspect the live worker command line before declaring dispatch failed.
