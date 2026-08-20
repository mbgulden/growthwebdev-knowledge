# Exact merge → immutable deployment → closeout contract pattern

Use this when a Prismatic task has passed exact-head review and needs release, deployment proof, and bounded issue closeout without reopening implementation.

## Trigger

- Exact candidate HEAD/tree already has independent `CLEAN/PASS` acceptance.
- Current base may have advanced, so release must bind a deterministic merge result before any push/PR/merge.
- Production proof is required before Linear Done closeout.

## Contract shape

A release contract should bind, at minimum:

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

Require drift checks **before push and again before merge**:

1. fetch origin;
2. require `origin/main == BASE_SHA`;
3. require local HEAD/tree/blob hashes still match accepted bytes;
4. require `git merge-tree --write-tree BASE_SHA HEAD == EXPECTED_MERGE_TREE`;
5. stop and version a new release contract if anything drifts.

## Publication guardrails

- Push exact reviewed HEAD only; do not bypass hooks.
- Open PR to `main` with exact head OID.
- Normal merge commit only when allowed; no squash/rebase if exact parent/tree identity matters.
- Require merge parents exactly `[BASE_SHA, HEAD]` and tree exactly `EXPECTED_MERGE_TREE`.
- Do not delete branches unless explicitly authorized.
- Hosted CI product failures block. Infrastructure-only runner/billing failures with no executed steps may be bounded only if the contract already permits local/Git-free/exact-head evidence.

## Immutable deployment guardrails

After merge identity is proven:

1. create standalone release checkout under `/home/ubuntu/.prismatic/releases/<merge-sha>`;
2. require no hardlinks/alternates, clean status, detached exact HEAD/tree, and `git fsck --full` PASS;
3. create commit-specific venv, install non-editably with required extras;
4. prove neutral imports from the venv/source bytes, not from a mutable checkout;
5. stage and verify rollback **before** restart;
6. inspect production only read-only after staging proof;
7. bind systemd drop-in to immutable release/venv and preserve current effective argument shape;
8. restart only the target service under auto-rollback; do not restart generic consumers/producers/watchdogs.

## Production proof discipline

Use bounded, non-secret evidence:

- systemd provenance: active state, working directory, exec start, drop-ins;
- health/dashboard/receipt HTTP status;
- SQLite read-only/query-only schema version, authority table names, row counts, `foreign_key_check`, `integrity_check`;
- no raw canonical bytes, receipts, payloads, process environment, or secrets.

For accepted read-only Python projection APIs, prove from a neutral directory using the installed package:

```python
read_cron_projection_source('/home/ubuntu/.prismatic/bus/event_log.sqlite')
```

Prove idempotence, tuple row-family counts matching direct read-only SQL, write rejection, and no count/schema/integrity drift across the proof. Do not claim a public HTTP endpoint when the accepted interface is a Python API.

## Closeout boundary

Only after production proof PASS:

- perform the bounded Linear state transition authorized by the contract;
- read back state/completedAt and write a receipt;
- do not add comments or mutate labels unless explicitly authorized;
- preserve failed-producer truth separately from accepted/deployed artifact truth;
- stop before successor implementation and freeze a new deployed-base contract first.
