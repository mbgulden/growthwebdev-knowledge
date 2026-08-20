# BN-00 current-main repair: source-clean, canonical-hold pattern

Use this reference when a predecessor repair must be restarted on current `main` after successor drift, and George needs to drive one bounded producer through exact-head review without overclaiming canonical green.

## Trigger

- The intended helper task did not start from Telegram, or a prior branch was bypassed/stale.
- The same defect still reproduces on current `main`.
- Cap remains 1 and successors must stay `QUEUED_NOT_DISPATCHED`.
- A focused repair can be source-clean even if unrelated current-main canonical/package failures remain.

## Execution pattern

1. **Bind live truth first.** Read `origin/main`, retained repair branch, held successor PR heads, existing result packets, and worker/process state before dispatch.
2. **Use one bounded filesystem-bus task if chat did not start work.** Prepare an isolated current-main worktree and an exact task packet with allowed paths, base SHA, result contract, and explicit no-side-effect boundaries.
3. **Do not trust `RESULT.md` or inactivity completion.** If the producer writes a result but the task-owned chat/process remains alive, stop only the task-owned oneshot/process group before review and classify the packet as untrusted.
4. **Preserve every candidate before repair/review mutation.** Create a local preservation ref and verified bundle for the exact commit/tree before rejecting, repairing, pushing, or opening a PR.
5. **Reject excessive churn even when tests pass.** For narrow semantic repairs, compare public symbols/signatures and AST/function changes. If the candidate reformats large unrelated areas, issue a same-task repair that preserves the semantic commit but restores current-main formatting outside the target functions.
6. **Verify exact semantic scope.** For freshness/journal-tail repairs, adversarial probes should cover timezone offsets, single captured `now`, exact lower/upper cutoffs, just-outside rejection, complete-line suffixes, leading partial-line removal, trailing unterminated-line exclusion, multibyte safety, success-stderr suppression, and failed-Git behavior.
7. **Separate source-clean from canonical green.** Run focused tests, relevant regression suite, Ruff/format, `git diff --check`, build, and adversarial probes on the exact head. Then run canonical. If canonical failures reproduce on exact base under the same environment, classify them as inherited baseline debt and do **not** fold them silently into the narrow repair.
8. **Promotion split:**
   - `SOURCE_REVIEW=CLEAN_BN00_NO_REGRESSION` can justify preserving/pushing/opening a focused PR when the diff and independent proof are clean.
   - `MERGE_JUDGE=HOLD_CANONICAL_AND_HOSTED_CI_NOT_GREEN` must remain until exact PR-head hosted CI and canonical full-suite green pass.
9. **PR discipline.** Push only by fast-forward from the retained remote branch to the exact reviewed head, open one focused PR body with base/head/tree, proof logs/digests, inherited-failure boundary, and explicit non-claims. No auto-merge.
10. **Queue discipline.** Keep the predecessor task active/held and all successors queued until PR-head CI, inherited baseline repair, canonical green, and George merge verdict close the slice.

## Proof packet shape

```text
PROGRAM=PRISMATIC_BEYOND_NORTH_STAR
TASK=BN-00/GRO-4186 current-main repair
BASE=<origin/main sha>
HEAD=<candidate sha>
TREE=<tree sha>
PATHS=<allowed paths>
SOURCE_REVIEW=<CLEAN_BN00_NO_REGRESSION|REPAIR|BLOCKED>
CANONICAL=<pass/fail counts>
BASE_CONTROL=<same failures reproduce on base|not run|different>
MERGE_JUDGE=<HOLD_CANONICAL_AND_HOSTED_CI_NOT_GREEN|MERGE_ELIGIBLE>
PRESERVE_REF=<local ref>
BUNDLE=<path>
PR=<url or none>
NOT_CLAIMING=merge,deploy,restart,Linear writeback,generic dispatch,successor admission,cap increase
```

## Pitfalls

- A package/env failure in an incomplete worktree is not product proof. Hydrate the candidate environment or rerun using the verified project environment before judging.
- A full canonical failure can still be a useful blocker boundary if the same failures reproduce on exact base. Report it as inherited debt, not BN-00 regression and not canonical green.
- Do not let a clean focused suite plus inherited canonical failures unlock merge. It can at most justify a focused PR for CI/review while holding merge.
- Do not normalize process hangs after `RESULT.md`; containment and independent review are mandatory before accepting any candidate.
- Do not open successor work while the predecessor PR is source-clean but merge-held.
