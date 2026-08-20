# Runtime recovery merge/release closeout reference

Use this reference after a runtime recovery/reconciliation candidate reaches exact-head `CLEAN` review and refreshed CI. The goal is to close the cap-1 slice without confusing merge, immutable release proof, durable coordination state, and production deployment.

## Trigger

- A runtime recovery/convergence PR has gone through one or more repair commits.
- The latest exact head has independent `CLEAN` review and refreshed GitHub CI.
- Standing merge policy permits source merge, but production repoint/restart/Linear closeout remain separately authorized.

## Closeout sequence

1. **Invalidate stale evidence explicitly.** If any repair commit landed after a `CLEAN`, mark the older review/CI obsolete and dispatch/read the exact-head review again.
2. **Pre-merge readback.** Read live PR state, head SHA, mergeability, review decision, required checks, changed paths, and expected branch. Do not merge from a propagated-stale PR response.
3. **Merge under policy only after exact-head gates.** Retain the source branch unless explicitly authorized to delete it.
4. **Create a standalone immutable release from the GitHub merge SHA.** Prefer a fresh clone/worktree under `.prismatic/releases/<repo>-<merge-prefix>` pinned detached to the merge commit. Verify `git rev-parse HEAD`, detached state, `git fsck`, no object alternates, and clean worktree.
5. **Run merge-SHA verification from the release checkout.** Include focused/adversarial recovery proofs, canonical suite, manifest/release/build/precommit checks, and lint delta against the original base when legacy debt exists.
6. **Publish receipts back to the PR.** Include candidate head, merge SHA, release path, log root, log digests, proof classes, and non-claims.
7. **Update durable state and handoff only after release proof.** Mark task as merged/release-verified, producer inactive, cap available but held, generic dispatch paused, no successor active unless explicitly launched.
8. **Run a final state/readback verifier after the last handoff/control/PR-body edit.** Bind GitHub PR merged state, head SHA, merge commit, release checkout HEAD/clean state, control JSON fields, handoff marker, PR body receipt, and non-claim language. Create the verifier under `/tmp` with a `hermes-verify-` prefix, capture a log+SHA256, and remove the verifier.

## Proof packet shape

```text
COMMAND=<grouped merge-SHA release verifier + final state verifier>
RESULT=<PASS|FAIL|BLOCKED>
LOG_ROOT=<log directory>
RELEASE=<immutable release path>
PR=<url>
CANDIDATE_HEAD=<sha>
MERGE_SHA=<sha>
FOCUSED=<count>
CANONICAL=<count>
LINT_DELTA=<base/candidate/new findings>
AD_HOC_OR_CANONICAL=<merge-SHA release suite + ad-hoc targeted state closeout>
NOT_CLAIMING=<no production repoint/restart/live-row replay/Linear closeout/cap increase/generic dispatch resume>
MARKER=<slice-specific merged-release marker>
```

## Pitfalls

- Do not treat a `CLEAN` review from a prior repair head as valid after any new commit, even if the new commit only looks like a small semantic hardening patch.
- Do not call a standalone release verified until it is pinned to the GitHub merge SHA, not the PR head or a mutable local branch.
- Do not use source merge authorization as production deploy/restart authorization.
- Do not update handoff/control JSON after proof without a final verifier that covers those changed artifacts.
- If Hermes reports edited-path verification warnings after a final state verifier, report the detector boundary only after a current-turn verifier was actually run and logged.
