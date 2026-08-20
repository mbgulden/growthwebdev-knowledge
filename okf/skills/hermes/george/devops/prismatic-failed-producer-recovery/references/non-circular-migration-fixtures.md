# Non-circular migration fixtures for failed-producer recovery

Use this reference when an independent review blocks a migration candidate because the test fixture for an old schema imports runtime-private DDL constants or helper functions.

## Problem signal

A migration repair can look covered while the test oracle is circular:

- `_create_true_v2_db()` or equivalent imports `_CREATE_*`, `_TRIGGERS_DDL`, `_V2_TRIGGERS_DDL`, or `_main_ddl` from the runtime module under test.
- The old-schema fixture is generated from the current repaired implementation at test runtime.
- The fixture silently widens when runtime DDL changes, so the test no longer proves migration from the intended prior schema.

Treat this as a real blocker even if focused tests pass.

## Durable fix pattern

1. Preserve the blocked candidate/version as evidence.
2. Create the next candidate version with the minimum fixture repair only.
3. Generate the prior-schema SQL tuple once from an exact accepted source, but do not import that source at test runtime.
4. Embed the complete old-schema object set as test-local SQL literals:
   - all tables required to make a realistic populated DB;
   - all old-version triggers/indexes needed for integrity behavior;
   - schema version row/identity matching the migration’s accepted prior-version contract.
5. Bind the literal tuple with a fixed SHA-256 over a stable separator such as `"\0".join(frozen_ddl)`.
6. Add static assertions that the fixture body contains no runtime-private DDL names or helper names.
7. Rerun focused migration tests and then compare canonical candidate vs exact base under the same interpreter/command.
8. Send the revised candidate for fresh full review; do not treat the previous review as accepting the uninspected remainder.

## Important distinction

Patch-generation can inspect exact source constants to avoid hand transcription errors, but the committed test must contain frozen literal SQL and a digest. Future runtime changes must not alter the oracle.

## Proof packet fields

```text
PRIOR_SCHEMA_OBJECT_COUNT=<n>
PRIOR_SCHEMA_LITERAL_SHA256=<sha256>
RUNTIME_PRIVATE_DDL_IMPORTS=false
FOCUSED_MIGRATION_TESTS=<pass/fail summary>
CANONICAL_BASE_COMPARISON=<same nodes|candidate-only nodes>
NOT_CLAIMING=canonical green, producer success, merge, deploy
```

## Pitfalls

- Do not assume the immediately previous checkpoint is the intended legacy schema; it may already contain partial repair DDL. Verify table columns and schema identity against the migration contract.
- Do not fix a circular fixture by importing a differently named runtime constant. That preserves the same defect.
- Do not patch only the failing table if the old DB identity includes triggers or companion tables; freeze the complete object set.
- Do not let focused green promote a failed producer. The producer remains failed; only the candidate/recovery review can advance.
