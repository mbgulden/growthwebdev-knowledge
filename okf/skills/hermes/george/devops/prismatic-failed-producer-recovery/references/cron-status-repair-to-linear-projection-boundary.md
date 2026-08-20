# Cron status repair to Linear projection boundary

Use this reference when a failed/blocked cron-authority or cron-status foundation slice is being preserved/repaired and the next queued issue is a Linear projection/outcome writer.

## Lessons captured

- A clean exact-byte checkpoint can preserve useful bytes without accepting the implementation. Keep `producer_completed=false`, `implementation acceptance=false`, and `deploy=false` visible until separate gates pass.
- When blob identity is exact but a frozen patch hash mismatches, confirm the diff serialization. `git diff --binary --full-index` produces different text from an abbreviated-index diff even when resulting blobs are identical.
- After an explicit exact-byte checkpoint commit, reproduce from a `.git`-free archive. If dependencies changed, create a fresh disposable venv from that archive rather than relying on an older production venv.
- Canonical boundary comparisons must run candidate and base under the same interpreter/command and compare exact failed node IDs; do not compare historical pass counts from different environments.
- A migration repair contract is not a repair event. Freeze it as an artifact, hash/line/byte count it, prove no task file or event exists, and send it to independent review before source mutation.

## SQLite v2→v3 migration contract checks

A repair contract for rebuilding FK-bearing cron authority tables should require:

1. A hand-built populated true-v2 fixture, not only a current-schema DB with a downgraded version row.
2. Pre-rebuild validation against the real v2 shape; do not validate old tables against new/v3 DDL before rebuilding.
3. `PRAGMA foreign_keys = OFF` before `BEGIN`; toggling foreign keys inside an active SQLite transaction is ineffective.
4. Atomic rebuild after FK enforcement is disabled on that connection.
5. Explicit recreation/proof of triggers and indexes.
6. `PRAGMA foreign_key_check` and `PRAGMA integrity_check` before accepting the rebuild.
7. FK re-enable and verification on every exit path, including exceptions.
8. Rollback proof from an injected mid-rebuild mismatch/failure showing original v2 rows, FKs, triggers, and indexes survive unchanged.
9. Idempotence proof after migration.

## Downstream GRO-4336-style boundary

If the user authorizes the next Linear projection issue after the cron-status slice, bind the mutation boundary explicitly:

```text
BUILD_TEST_REVIEW_PR_MERGE_DEPLOY_AUTHORIZED=<as user granted>
LIVE_LINEAR_COMMENTS_AUTHORIZED=false
LIVE_LINEAR_LABELS_AUTHORIZED=false
LIVE_OUTCOME_PROJECTION_WRITES_AUTHORIZED=false
```

Implementation should build and prove idempotent accepted-outcome projection, durable quarantine/retry/DLQ, and linked issue identity with fake/disposable Linear adapters. Live comments, labels, or accepted-outcome projection writes need a separate exact mutation authorization unless the user explicitly grants them.

## Minimum handoff fields

```text
CHECKPOINT_HEAD=<sha>
CHECKPOINT_TREE=<tree>
CHECKPOINT_REVIEW=<delegation>:<status>
REPAIR_CONTRACT=<path>
REPAIR_CONTRACT_SHA256=<sha>
REPAIR_CONTRACT_LINES=<n>
REPAIR_CONTRACT_BYTES=<n>
REPAIR_CONTRACT_REVIEW=<delegation>:<status>
TASK_FILE_CREATED=false
EVENT_CREATED=false
PRODUCTION_DB_WRITE=false
LINEAR_WRITE=false
NOT_CLAIMING=producer success,implementation acceptance,canonical green,deployment,next-issue readiness
```