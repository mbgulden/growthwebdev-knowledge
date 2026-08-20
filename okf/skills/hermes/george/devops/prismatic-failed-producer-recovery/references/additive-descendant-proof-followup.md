# Additive descendant proof follow-up after an exact-head block

Use this when a Prismatic recovery contract allowed a tightly bounded commit, the operator made that commit, and a fresh exact-head review correctly blocks the commit for **insufficient proof**, not for runtime-source defects.

## Durable lesson

A one-commit/normal-descendant exception can produce an immutable blocked checkpoint. If review then finds missing tests or under-proved invariants, do **not** amend/reset/rebase the commit to make the history look clean. Preserve the blocked commit as terminal evidence and freeze a new versioned contract that authorizes exactly one additive descendant commit for the minimum proof correction.

## Required shape

1. Bind the blocked checkpoint:
   - blocked commit SHA, tree SHA, parent/base SHA;
   - independent review id/verdict and first blocker;
   - explicit `AMEND=false`, `RESET=false`, `REBASE=false`, `SQUASH=false`, `FORCE=false`.
2. Freeze a new contract version (`Vn+1`), not an in-place edit of the old contract.
3. Allow only the minimum path set. If the implementation is already reviewed and the block is proof-only, the allowlist should usually be test-only.
4. Bind unchanged runtime source by SHA-256 so the follow-up cannot smuggle runtime changes.
5. Bind the exact follow-up patch, changed test hash, line/byte counts, and evidence directory.
6. Require reproduction from the committed objects after the additive commit, then fresh exact-head review. The earlier implementation review is supporting evidence, not acceptance of the new head.
7. Keep operational non-claims: no push, PR, merge, deploy, production state access, Linear write, second event, or second producer until exact-head review passes.

## Verification pattern

```text
BLOCKED_HEAD=<sha>
BLOCKED_TREE=<tree>
BLOCKED_REVIEW=<delegation>:BLOCKED
FOLLOWUP_CONTRACT=<path>
FOLLOWUP_CONTRACT_SHA256=<sha256>
MUTABLE_PATHS=<usually tests only>
RUNTIME_SOURCE_SHA256=<unchanged sha>
PATCH_SHA256=<sha256>
FOCUSED_TESTS=<pass count>
BASE_COMPARISON=<candidate-only failures none, if broader tests fail>
AD_HOC_OR_CANONICAL=<ad-hoc targeted|canonical suite>
NOT_CLAIMING=exact-head acceptance, push, PR, merge, deploy, production proof
```

## Complete migration-oracle escalation

If the exact-head blocker is “the tests prove stability but not conformance,” a small idempotence or row-count test is not enough. Freeze expected post-migration state independently from a disposable successful migration and embed literal expected projections in the test file. Do **not** import runtime DDL/constants/helper functions to construct expected values.

For SQLite authority migrations, the oracle should assert, for every authority-owned table:

- exact canonical ordered rows;
- exact `PRAGMA table_info` rows;
- exact `PRAGMA index_list` rows;
- exact `PRAGMA foreign_key_list` rows;
- complete `sqlite_master` SQL projection for tables/triggers plus associated SQLite autoindexes (`sql=NULL`).

Also assert deterministic legacy→new transformations, empty new tables, unrelated caller-table preservation, required joins/aggregates/evidence projections, absence of removed/TEMP authority objects, `foreign_key_check=[]`, `integrity_check='ok'`, `foreign_keys=1`, and full second-run canonical equality. Retain all earlier exact rollback/adversarial cases rather than replacing them with the oracle.

## Pitfalls

- **Governance shortcut:** “The commit already exists” is not permission to amend it. A blocked exact-head commit is evidence to preserve.
- **Proof-only drift:** If review blocks on test undercoverage, bind runtime source unchanged by SHA; otherwise a test-only follow-up can silently become a new implementation candidate.
- **Base-comparison overclaim:** If a broad suite has existing failures, compare the same command against the immutable base and report candidate-only failures. Do not convert “no candidate-only failures” into canonical green.
- **Old review overuse:** A precommit implementation review can support the governance exception, but the additive descendant still needs fresh exact-head review before public or operational side effects.
