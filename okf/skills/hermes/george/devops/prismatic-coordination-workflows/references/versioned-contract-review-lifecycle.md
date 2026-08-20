# Versioned contract review lifecycle

Use this when a Prismatic slice is still pre-implementation and the active artifact is a prompt/contract under independent review.

## Durable pattern

1. Preserve every blocked version byte-for-byte. Do not overwrite V1/V2/etc. when a reviewer finds a blocker.
2. Create the next version as a new immutable artifact with the minimum correction only.
3. In the new version, record the prior version SHA and the independent review verdict/blocker that caused supersession.
4. Freeze the new artifact before review: SHA-256, line count, byte count, marker, and explicit zero-authority assertions.
5. Dispatch a fresh full review of the whole new version, not a delta-only review. Prior versions are evidence, not accepted text.
6. Update the handoff so exactly one contract is active, and all prior versions are listed as preserved/BLOCKED with reviewer IDs and blocker summaries.
7. Do not create tasks/events, launch producers, mutate source, open PRs, merge, deploy, or write to Linear while the contract gate is still pending.

## Minimum-correction examples from GRO-4318

- If a contract says both “no production access” and “hash/stat/count production DB,” split the phases: disposable-DB implementation verification now; production invariance/live proof only in a separately reviewed post-acceptance release gate.
- If SQLite `BEGIN IMMEDIATE` raises, do not assume no transaction. Split by observed state:
  - `conn.in_transaction is False`: no rollback; restore FK mode; preserve BEGIN error; connection can remain usable.
  - `conn.in_transaction is True`: ownership is uncertain; no rollback; no FK restoration while open; close/invalidate; preserve BEGIN error.
- Require real-path adversarial wrappers that exercise the production decision path. Helper-only exception tests are insufficient.

## Proof packet shape

```text
CONTRACT=<path>
SHA256=<sha>
LINES=<n>
BYTES=<n>
REVIEW=<delegation_id>:<pending|CLEAN/PASS|BLOCKED>
PREVIOUS=<version>:<sha>:<verdict>:<blocker>
SOURCE_MUTATION=false
TASK_FILE_CREATED=false
EVENT_CREATED=false
PRODUCER_LAUNCHED=false
LINEAR_WRITE=false
PRODUCTION_DB_ACCESSED=false
NOT_CLAIMING=implementation accepted, PR opened, merge, deployment, live proof
```
