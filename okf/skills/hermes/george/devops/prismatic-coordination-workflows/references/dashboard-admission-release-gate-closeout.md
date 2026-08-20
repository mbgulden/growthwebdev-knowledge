# Dashboard admission release-gate closeout pattern

Use this after a Prismatic dashboard/control-plane prerequisite has passed exact-head repair review and is ready to merge, but before any deployment/restart or live task admission.

## Closeout sequence

1. **Bind the independent review to the exact candidate** before merge: record reviewed head/tree and reviewer verdict. If the review returns `REPAIR`, pause successors, repair from the current reviewed base, and re-review the new exact head.
2. **Merge only under explicit merge policy** and then prove the merge contains the reviewed tree:
   - `MERGE_PARENT2=<reviewed_head>` for a normal GitHub merge commit, or otherwise document the exact reviewed-tree binding.
   - `MERGE_TREE=<reviewed_tree>`.
   - `origin/main=<merge_sha>`.
3. **Create a standalone detached release checkout** for production prep. Avoid mutable branch/worktree dependence and avoid local alternates/object borrowing when the checkout will be treated as durable runtime input.
4. **Re-run merged-release proof from the detached checkout**, not just the feature worktree. At minimum for dashboard admission/control-plane work:
   - focused API/UI/auth tests;
   - Ruff or equivalent scoped lint/format checks;
   - deterministic dashboard build check;
   - public/security readiness audit;
   - clean-tree/diff check;
   - handoff/checkpoint marker verification.
5. **Update durable reports and handoff** after merge with current reality: reviewed head/tree, merge sha/tree, release path, proof logs/hashes, and explicit non-claims.
6. **Hold deployment gate** unless Michael explicitly authorizes deployment/restart. Merge approval does not imply service restart, policy installation, runtime smoke, live task admission, Linear writes, cap increase, or producer launch.

## GitHub Actions boundary

If GitHub Actions is blocked before code execution by account/billing/spending infrastructure, state it as infrastructure-blocked and do **not** claim CI green. Acceptance can proceed only when local/independent/remote-clone/release proofs are exact-artifact, fresh, and sufficient under Michael's policy.

## Runtime smoke after deployment authorization

Initial runtime proof must use a fixture-only task/worktree, not the real next task such as GRO-4210. Prove fail-closed auth, role-scoped readback, `launch_performed=false`, exact replay, one admission/outbox/audit row, pending outbox, token absence from browser storage/responses/logs/SQLite, rendered dashboard usability, and `/health` plus existing tabs. Only then admit the real task.

## Report shape

Lead Michael-facing closeout reports with behavior and impact before IDs:

1. Problem found / review verdict.
2. What changed.
3. Why it matters.
4. Current state.
5. Exact next move.
6. IDs, hashes, and logs for traceability.

Use explicit proof/non-claim blocks:

```text
COMMAND=<merge binding + detached release proof summary>
RESULT=PASS|PARTIAL|BLOCKED
LOG=<path>
SCOPE=<exact release/control-plane scope>
AD_HOC_OR_CANONICAL=<canonical candidate|ad-hoc merged-release closeout>
NOT_CLAIMING=deployment, restart, runtime smoke, live task admission, producer execution
MARKER=<stable closeout marker>
```
