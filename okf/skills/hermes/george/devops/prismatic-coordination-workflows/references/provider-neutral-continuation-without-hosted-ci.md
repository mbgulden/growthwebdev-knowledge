# Provider-neutral continuation without hosted CI

Use this when Michael explicitly authorizes Prismatic to continue without GitHub Actions after a zero-step GitHub account/billing/spending-limit blocker has been bound.

## Durable lesson

GitHub Actions is an optional hosted verifier backend, not Prismatic's canonical acceptance authority. Once Michael authorizes provider-neutral continuation, do not keep treating hosted-CI billing/spending-limit failures as the controlling blocker. Do not relabel them green; record them as optional/unavailable and continue only through exact-artifact provider-neutral proof.

## Closeout sequence

1. **Bind exact current truth first.** Read PR state/head/tree, branch protection/check requirements, direct `origin/main`, and current handoff/control-state fields. Treat stale handoff/JSON as coordination debt if it contradicts direct GitHub/Git truth.
2. **For a PR already clean-reviewed before the policy change:** refresh local exact-head proof, verify independent review still binds the same head/tree/path scope, then merge only if Michael's continuation policy covers the exception. Keep GitHub Actions as `OPTIONAL_UNAVAILABLE`, not green.
3. **After merge:** verify GitHub merge SHA, remote `main` SHA, and merge-tree parity to the reviewed PR tree. Create a standalone immutable release pinned to the merge SHA and run release-local canonical/build/validator/compile proof with no object alternates or mutable-checkout dependency.
4. **For dependent PRs:** rebase onto the exact merged `main`; invalidate the old review; preserve the new candidate under a durable ref and bundle before review; rerun focused/canonical/package proof; dispatch fresh independent exact-head review before any remote push or merge.
5. **If `git bundle verify` fails with `need a repository to verify a bundle`:** the bundle may still be valid; rerun `git -C <worktree> bundle verify <bundle>` from a repository and hash the bundle plus verification log.
6. **Add installed-wheel/package-resource proof for schema/resource PRs:** install the built wheel into a temporary venv, run from outside the source checkout with isolated Python when possible, verify installed resources are byte-identical to reviewed source files, and validate schemas from the installed package.
7. **Retire stale operational blockers.** Pause/change watchers whose only job is to report hosted-CI billing as a controlling gate. Replace durable handoff language with `GITHUB_ACTIONS_OPTIONAL_UNAVAILABLE_NOT_BLOCKING` and record queue/control JSON reconciliation as pending if an independent review is still open.
8. **Write public receipts compactly.** PR comments should split: merged provider-neutral proof, optional-unavailable GitHub Actions status, exact non-claims, and for dependent PRs `REMOTE_PUSH=false` while review is pending.
9. **Final state verifier:** bind PR merged/open states, exact heads/trees, release path/no-alternates, log existence, handoff markers, paused watcher state if changed, and non-claims. Label it `AD_HOC_OR_CANONICAL=ad-hoc targeted state closeout` unless it is a canonical suite.

## Proof packet fields

```text
STATUS=<MERGED|REBASED_REVIEW_PENDING|BLOCKED>
PR_HEAD=<sha>
MERGE_SHA=<sha if merged>
MERGE_TREE=<tree if merged>
LOCAL_REBASED_HEAD=<sha if dependent PR>
REMOTE_HEAD=<sha if unchanged>
CANONICAL=<summary>
PACKAGE_RESOURCE_PROOF=<PASS|N/A>
INDEPENDENT_REVIEW=<id CLEAN|PENDING|REPAIR>
GITHUB_ACTIONS=OPTIONAL_UNAVAILABLE_ACCOUNT_OR_SPENDING_LIMIT_NOT_GREEN
PRESERVE_REF=<ref if review pending>
BUNDLE_SHA256=<sha if preserved>
WATCHER=<paused/retargeted job id>
NOT_CLAIMING=<deploy/restart/Linear/cap/remote-push/etc.>
```

## Pitfalls

- Do not carry forward the superseded `CLEAN_BLOCKED_HOSTED_CI` status after Michael has authorized provider-neutral continuation.
- Do not say GitHub Actions passed or is green when it failed before executing steps.
- Do not reuse pre-rebase independent review on a rebased dependent PR.
- Do not push a rebased dependent PR head before fresh exact-head review closes clean.
- Do not reconcile every queue/control file mid-review without marking boundaries; update the live handoff to prevent paralysis, then perform full JSON reconciliation after the review verdict if that is safer.