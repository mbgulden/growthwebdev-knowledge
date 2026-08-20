# Self-Build Candidate Manifest Gate

Session-derived pattern for the first supervised Prismatic self-build optimization slice: make merge/review eligibility a canonical exact-artifact manifest instead of relying on PR text, labels, or GitHub defaults.

## Trigger

Use when moving Prismatic from supervised cap-1 self-build toward faster, safer merge/review throughput, especially when Michael asks to continue the self-build plan or optimize merge/review.

## Pattern

1. **Keep cap 1 for writers.** Admit exactly one producer and one exact issue/slice. Additional helpers may be read-only reviewers only; they must not edit, push, mutate Linear, dispatch agents, merge, deploy, or inspect partial producer files unless explicitly asked.
2. **Start from current `origin/main`.** Create a fresh worktree from the current merge SHA; treat stale PRs/branches only as path-level source material.
3. **Baseline before changes.** Run the existing adjacent gate first (for this class, `tests/test_merge_factory.py`) so later failures can be attributed to the candidate rather than inherited debt.
4. **Bind to live branch protection.** Read branch protection and recent PR check names. If GitHub requires fewer reviews than Prismatic policy, the Prismatic manifest must enforce independent review above GitHub defaults.
5. **Use a pure contract slice first.** Prefer one immutable manifest module, focused tests, and contract docs; avoid adding a new DB/ledger, background worker, GitHub/Linear mutation, or auto-merge behavior in the first slice.
6. **Require exact-artifact promotion.** Candidate states should invalidate/rebind stale review, CI, merge, and release evidence when candidate head changes.
7. **Do not trust historical tracker labels.** If issue description and labels/state contradict each other (for example `dispatch:ready` despite text saying not to dispatch), treat the label as untrusted until reconciled; do not launch from label alone.
8. **Mirror real CI locally.** If GitHub CI runs full tests but scoped lint excludes new paths, add local scoped Ruff/format for every changed file before claiming readiness.

## Acceptance checklist for a merge-candidate manifest

- canonical JSON/digest is stable and deterministic;
- duplicate JSON object keys reject at every nesting level;
- exact built-in scalar/container types where trust matters; reject bool-as-int and subclass tricks;
- commit/digest formats, changed paths, proof classes, and check names validate strictly;
- path values reject absolute, traversal, controls, backslashes, duplicates, and non-normalized forms;
- review verdict and reviewed SHA bind to exact candidate head;
- CI head and all-success check set bind to exact candidate head;
- state construction cannot create inconsistent state/evidence combinations;
- rebind to a new head resets to candidate and clears stale review/CI/merge/release evidence;
- merged state binds candidate head; release-verified state binds exact merge SHA;
- optional file writes are explicit and atomic; no automatic GitHub, Linear, DB, dispatch, merge, deploy, or runtime side effects;
- manifest digest can feed existing `MergeFactoryStore.manifest_digest` instead of creating a parallel ledger.

## Proof packet

```text
COMMAND=<baseline + focused + full tests + scoped lint/format + build + installed-wheel probe>
RESULT=<PASS|FAIL|BLOCKED>
BASE=<origin/main sha>
CANDIDATE_HEAD=<candidate sha>
PRODUCERS=1
READ_ONLY_REVIEWERS=<count>
AD_HOC_OR_CANONICAL=<separate classes>
NOT_CLAIMING=<no deploy/restart/Linear/bulk dispatch/cap increase unless separately authorized>
```
