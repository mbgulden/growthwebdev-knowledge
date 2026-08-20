# Immutable-schema contract review and repair pattern

Use this when a Prismatic implementation contract proposes adding required fields or read-model authority to an existing immutable persisted artifact, especially SQLite tables with schema-version constraints and digest-bound canonical bytes.

## Session signal

A contract for the GRO-4318 prerequisite repair originally required adding `schedule` and `schedule_timezone` to existing cron registry snapshots. Independent review blocked it because the base persisted registry snapshots as schema version 1 with:

- exact source/table identity;
- schema-version constraint fixed at `1`;
- strict top-level canonical key validation;
- digest coverage over exact canonical bytes.

Adding required fields under the same schema version would force one unsafe choice:

- silently reinterpret old v1 bytes;
- fabricate schedule authority for legacy rows;
- reject existing durable rows; or
- leave implementers to invent a migration path.

## Required coordination response

When this happens, do **not** launch implementation and do **not** paper over the gap with ad-hoc defaults. Repair the same contract into a versioned transition and preserve the blocked version as evidence.

Minimum safe shape:

1. Mark the prior contract version/review as `BLOCKED` with the precise defect.
2. Revise the same contract or a clearly superseding versioned artifact; do not create a parallel ambiguous precontract.
3. Add an explicit schema transition:
   - preserve legacy table/source/rows/canonical bytes/digests/triggers byte-for-byte;
   - introduce a distinct new schema/table/source/version for the added required authority;
   - make legacy rows readable but authority-unavailable with a stable reason;
   - prohibit downstream status/next-run projection from legacy unavailable rows;
   - require new writes to use the new schema only;
   - specify transactional migration/rebuild rules, FK/trigger/index preservation, integrity checks, rollback, and idempotence;
   - keep unrelated schema families distinct, e.g. receipt schema version stays independent.
4. Add adversarial tests for both legacy and new rows:
   - legacy bytes/digests survive exactly;
   - legacy rows are not projected as live authority;
   - new rows require/validate the new fields;
   - migration preserves row counts/FKs/triggers and rolls back on mismatch;
   - unknown/partial schema fails closed.
5. Hash the repaired artifact and obtain a fresh independent exact-bytes review before any event/producer/worktree launch.

## Proof-packet fields to report

```text
OLD_CONTRACT_SHA256=<sha>
OLD_REVIEW=<delegation_id>:BLOCKED
OLD_FINDING=<first precise defect>
NEW_CONTRACT_VERSION=<n>
NEW_CONTRACT_SHA256=<sha>
NEW_REVIEW=<delegation_id>:running|CLEAN/PASS|BLOCKED
EVENTS_POSTED=0
PRODUCERS_LAUNCHED=0
NOT_CLAIMING=<implementation/event/candidate/merge/deploy not yet claimed>
```

## Pitfalls

- Do not call missing persisted fields “defaults” if they would create operational authority. Defaults are fabrication when the original bytes never carried the fact.
- Do not conflate independent schema families. Snapshot schema, attempt schema, and receipt schema may have different version lifecycles.
- Do not let “backward compatible constructor call sites” override canonical byte compatibility; constructor convenience must not mutate durable semantics.
- A blocked contract version is useful evidence. Preserve its hash/finding in the handoff instead of overwriting the record.
