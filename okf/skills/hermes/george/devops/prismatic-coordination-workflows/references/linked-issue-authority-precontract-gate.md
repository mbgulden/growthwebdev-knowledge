# Linked issue authority precontract gate

## Trigger
Use this when a Prismatic task wants to project accepted cron/agent outcomes into Linear or another external issue system, but the exact production/main base has receipts/outcomes without an immutable provider-native target identity.

## Session lesson

A completed upstream dependency and canonical terminal receipts are not enough to authorize downstream Linear projection. If the registry snapshot, runner receipt, aggregate table, or receipt table lacks immutable target identity (for example `linked_issue_id` / provider / server ID), any projection would have to infer the target from display identifiers, labels, titles, descriptions, current Linear lookup, or chat context. That is not acceptable authority.

The safe move is a frozen **preimplementation blocker contract**, not a worktree/event/producer launch.

## Required audit before launch

1. Live-read the issue topology through the bounded, reviewed Linear read-only path.
2. Bind the exact production/main base commit and tree.
3. Search the exact immutable source/release for target-authority fields across:
   - registry snapshots;
   - runner receipts;
   - execution aggregates;
   - terminal receipts;
   - any existing schema versions.
4. If target authority is absent, freeze a blocker contract with `RESULT=BLOCKED`.
5. State the finite prerequisite separately from the original task. Typical shape:
   - additive registry snapshot schema version with immutable provider-native target identity;
   - additive authority schema/table if needed;
   - all-null/no-backfill behavior for old snapshots;
   - deterministic decoder from attempt-bound canonical snapshot bytes;
   - zero-network tests with `LINEAR_WRITES_ENABLED=false`, credentials absent, transport fake/local-only, event/producer counts zero.
6. Do not materialize a task, worktree, event, producer, source edit, DB migration, or Linear write while the contract result is blocked.
7. Even after `CLEAN/PASS` review of the blocker contract, separately reconcile dispatch/owner truth and review the exact task/envelope/launcher before launching the prerequisite.

## Frozen-version discipline

Once a contract artifact is frozen and/or dispatched for review, treat its bytes as immutable. If a local verifier or reviewer finds an omission after dispatch:

1. preserve and re-hash the dispatched version;
2. restore it byte-for-byte if it was accidentally edited in place;
3. copy forward to `V(N+1)`;
4. make the minimum correction there;
5. re-run local proof and dispatch fresh exact-byte reviews bound to the new SHA, line count, and byte count.

Never silently mutate V6/V7/etc. in place after a review has been launched.

## Compact proof fields

```text
ISSUE=<GRO-id>
STATE=<live Linear state>
LABELS=<live labels>
RELATION=<live dependency edge + peer state>
BASE=<commit>
TREE=<tree>
AUTHORITY_FIELDS_PRESENT=<true|false>
BLOCKER=<missing immutable target authority; dispatch label not ready; etc.>
CONTRACT_VERSION=<n>
CONTRACT_PATH=<absolute path>
CONTRACT_SHA256=<sha>
PREVIOUS_VERSION_PRESERVED_SHA256=<sha or n/a>
LINEAR_WRITES_ENABLED=false
CREDENTIALS=absent
TRANSPORT=none/fake-local-only
TASK_MATERIALIZED=false
WORKTREE_CREATED=false
EVENT_COUNT=0
PRODUCER_STARTED=false
SOURCE_EDIT_COUNT=0
LINEAR_WRITE_COUNT=0
NOT_CLAIMING=<implementation, event, producer, source, DB, Linear mutation>
```
