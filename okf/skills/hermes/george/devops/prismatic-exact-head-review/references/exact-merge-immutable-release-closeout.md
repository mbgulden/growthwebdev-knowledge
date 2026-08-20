# Exact merge immutable release closeout

Use this as the release-side continuation of exact-head acceptance when a Prismatic candidate is already independently `CLEAN/PASS`, but still needs push/PR/merge/deploy/closeout.

## Why this matters

Exact-head acceptance is not deployment. A release contract must prevent identity drift between reviewed candidate, current GitHub base, merge commit, immutable runtime checkout, production proof, and bounded Linear state transition.

## Minimum release contract bindings

```text
HEAD=<accepted_commit>
HEAD_TREE=<accepted_tree>
BASE_REF=main
BASE_SHA=<current_origin_main>
BASE_TREE=<current_origin_main_tree>
EXPECTED_MERGE_TREE=<git merge-tree --write-tree BASE_SHA HEAD>
MERGE_TREE_CONFLICTS=none
EXACT_HEAD_REVIEW=<delegation>:CLEAN/PASS
```

Before push and again before merge:

1. fetch origin;
2. require `origin/main == BASE_SHA`;
3. require local branch HEAD/tree/blob hashes still match accepted bytes;
4. require only preserved operational metadata outside the commit;
5. require deterministic merge tree still equals `EXPECTED_MERGE_TREE`;
6. stop and version a new release contract if base/tree drifts.

## Publication and merge

- Push exact reviewed HEAD; do not bypass hooks.
- Open PR to `main` with exact head OID and expected base.
- Verify PR head/base OIDs, changed paths, mergeability, and no unexpected files.
- Normal merge commit if ordered parent/tree identity is required; do not squash/rebase unless a new reviewed contract authorizes it.
- After merge, require parents exactly `[BASE_SHA, HEAD]` and tree exactly `EXPECTED_MERGE_TREE`.
- Do not delete branches unless explicitly authorized.
- Classify GitHub no-run CI separately from product failures; do not claim GitHub tests ran when runner/steps are absent.

## Immutable deployment

After exact merge proof only:

1. create standalone `/home/ubuntu/.prismatic/releases/<merge-sha>` from the merge commit;
2. require no hardlinks/alternates, clean status, detached exact HEAD/tree, and `git fsck --full` PASS;
3. create commit-specific venv and install non-editably with required extras;
4. prove neutral imports from the venv and installed module hashes match release source;
5. run focused/package/gateway smoke verification without relying on a mutable checkout;
6. stage rollback before touching production;
7. inspect production read-only only after staging proof passes;
8. bind a release-specific systemd drop-in to immutable release/venv while preserving the current effective gateway argument shape;
9. restart only the target gateway under an automatic rollback trap;
10. do not restart generic consumers, producers, admission workers, or watchdogs.

## Production proof

Use bounded non-secret proof:

- systemd active state, working directory, exec start, drop-ins;
- health/dashboard/receipts HTTP status;
- SQLite read-only/query-only schema version, authority table names, row counts, `foreign_key_check`, `integrity_check`;
- no raw canonical bytes, receipt payloads, process environment, or secrets.

For a read-only Python projection API, prove from a neutral directory using the installed package, not a checkout:

```python
read_cron_projection_source('/home/ubuntu/.prismatic/bus/event_log.sqlite')
```

Require two equal reads, tuple row-family counts matching direct read-only SQL, write rejection, and no count/schema/integrity drift. Do not invent or claim a public HTTP endpoint when the accepted surface is a Python API.

## Closeout

Only after production proof PASS:

- perform the specifically authorized Linear state transition;
- read back state/completedAt and write a receipt;
- do not add comments or mutate labels unless the contract authorizes it;
- preserve failed-producer truth separately from accepted/deployed artifact truth;
- stop before successor implementation; freeze and review a new deployed-base contract first.
