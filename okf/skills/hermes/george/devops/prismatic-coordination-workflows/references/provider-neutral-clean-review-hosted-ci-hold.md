# Provider-neutral verification closeout: clean review but hosted-CI hold

Use this pattern when a provider-neutral verification architecture/docs PR reaches independent exact-head `CLEAN`, but the repository's current enforced hosted CI gate is still red/skipped.

## Durable lesson

A proposed provider-neutral policy cannot authorize bypassing the governance gate that is still enforced before that policy is merged. If the PR is itself changing verification authority, keep the transition honest: exact-head review may be `CLEAN`, but merge remains held until current branch protection/hosted checks are satisfied or Michael explicitly authorizes a bounded exception.

## Required sequence

1. Bind the exact PR head/tree/path count and preserve the independent review verdict.
2. Re-read live GitHub PR/check state after the review, not from stale handoff fields.
3. If checks are failed/skipped/unstable, report a split verdict:
   - `REVIEW=CLEAN`
   - `MERGE_GATE=BLOCKED_HOSTED_CI`
   - `MERGE=HOLD`
4. Post the split verdict to PR/Linear when authorized for status writeback.
5. Keep downstream/schema/implementation slices paused or review-pending; do not use the clean docs review as production policy switch proof.
6. Update queue/control/handoff state with active producer count, watcher pause state, exact candidate/review IDs, and non-claims.
7. Run a final detector-visible `/tmp/hermes-verify-*` state verifier that binds:
   - PR head/tree/clean worktree;
   - live check/merge gate summary;
   - queue hash and active producer count;
   - handoff/control markers;
   - preserved candidate bundle digest when applicable;
   - non-claims for merge, deploy, production policy switch, downstream dispatch.

## Proof packet shape

```text
PR=<number>
HEAD=<exact sha>
TREE=<exact tree>
INDEPENDENT_REVIEW=<delegation id> CLEAN
LIVE_GITHUB_CHECKS=<failed/skipped/pending/green summary>
MERGE_STATE=<GitHub mergeStateStatus>
MERGE=HOLD
AD_HOC_OR_CANONICAL=ad-hoc targeted state/readback unless full suite/CI also green
NOT_CLAIMING=PR merge, production policy switch, deploy, downstream dispatch
MARKER=PNV_CLEAN_HOSTED_CI_HOLD_OK
```

## Schema-candidate companion boundary

If a schema/implementation candidate finishes during the same closeout:

- preserve it under a durable local ref/bundle before review;
- classify hung worker lifecycle separately from product quality;
- independently reproduce focused/adversarial proof on exact head;
- dispatch fresh exact-head read-only review;
- set active producers to zero and pause watchers once the candidate is no longer running;
- do not push/open PR/mark complete until the fresh review returns `CLEAN`.
