# Repair D authority/checkpoint contract pattern

Session-derived reference for failed producers that leave dirty checkpoint bytes with trust-boundary regressions.

## When to use

Use this reference after a failed cap-1 producer leaves:

- terminal producer truth (`producer_completed=false`, failed/review-pending, exit/signal recorded);
- no descendant commit from the blocked base;
- dirty checkpoint blobs on allowed paths;
- independent fresh-archive verification showing repair-specific regression(s);
- read-only triage identifying authority/trust-boundary defects.

## Contract requirements to preserve

A recovery contract should require a future separately authorized clean worktree from the exact blocked base and then materialize the preserved dirty patch there. It should not authorize that worktree/event/task by itself.

For authority/trust-boundary repairs, require all of these explicitly:

1. descriptor-relative, component-by-component traversal with no symlink following;
2. component containment by identity, not lexical prefix strings;
3. immediate pre-spawn authoritative name re-resolution;
4. `nlink`/unlink/replacement checks tied to the pinned evidence;
5. adapter invocation from the same pinned execution plan, not ambient `argv/cwd` strings;
6. claim-bound source id, storage object, schema id/version, canonical bytes, canonical digest, and digest domain;
7. durable fail-closed terminal/quarantine outcomes after claim instead of rollback ambiguity;
8. outer/finally file-descriptor lifecycle coverage;
9. adapter exception reconciliation so running attempts cannot remain ambiguous;
10. private disposable test roots and deterministic adversarial tests.

## Identity pitfall: schema ID vs digest domain

Keep these identities separate. The `.v1` suffix may belong to the digest domain while being wrong in `schema_id`.

Known-good shape from this session:

```text
SCHEMA_ID=prismatic.cron.registry-snapshot
SCHEMA_VERSION=1
DIGEST_DOMAIN=ASCII prismatic.cron.registry-snapshot.v1
```

Verify against both the accepted prior contract and source constants before freezing a new artifact.

## Outcome accounting pitfall: false zero counts

Durable fail-closed outcomes need phase-aware accounting. A contract is wrong if it requires `ADAPTER_CALL_COUNT=0` / `PROCESS_SPAWN_COUNT=0` for every post-claim trust/fence/finalization failure.

Correct split:

```text
PRE_INVOCATION_FAILURE => ADAPTER_CALL_COUNT=0 and PROCESS_SPAWN_COUNT=0
POST_INVOCATION_OR_FINALIZATION_FAILURE => persist actual adapter-call/process-spawn counts
```

The post-invocation/finalization receipt must also preserve exact claim identity, fence/owner identity, detection phase, reason code, and idempotent terminal/quarantine semantics. Do not let a rollback erase the aggregate/attempt/delivery identity, but also do not falsify counts to maintain a simpler invariant.

Tests should distinguish at least:

- stale owner/fence before spawn: zero adapter/spawn counts;
- stale owner/fence first detected during finalization: actual counts;
- adapter exception after running transition: actual adapter-call and process-spawn counts.

If an exact-artifact review flags false-zero accounting, preserve that version as blocked and create a new immutable `Vn+1` with only the phase-aware correction plus a fresh full review.

## Review iteration rule

When exact-artifact review blocks `Vn` on a first defect:

1. preserve `Vn` byte-for-byte with hash/line/byte proof;
2. create `Vn+1` with the minimum correction and updated version marker;
3. prove the bounded delta and all zero-authority nonclaims;
4. dispatch a fresh review that re-checks the full artifact, not only the changed line.

Early-stop review findings do not validate the unreviewed tail of the artifact.
