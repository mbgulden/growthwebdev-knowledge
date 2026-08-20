# SQLite FK readback fail-closed migration repair

Use when a Prismatic recovery candidate toggles SQLite `PRAGMA foreign_keys` during a migration or rebuild path and an independent review raises uncertainty about whether callers can receive a connection with FK enforcement off.

## Durable rule

A real `PRAGMA foreign_keys = OFF` creates an unsafe interval. Code must mark that unsafe state immediately after issuing `OFF`, not only after readback succeeds. Until a successful readback confirms the intended state and later restoration confirms `ON`, do not return the connection to callers.

## Required behavior

- Before migration, establish baseline FK state intentionally.
- After the real `OFF`, set an internal unsafe flag immediately.
- If the disable readback raises or reports the wrong value, close/invalidate the caller connection before raising a stable bounded error such as `foreign_keys_disable_failed`.
- If the migration body fails after FK was disabled, rollback once, attempt exactly one restoration `ON`, and read back exactly once.
- If restoration readback raises or reports the wrong value, close/invalidate the caller connection and preserve the primary migration failure as `__cause__` or bounded context; do not leak rollback/restoration text as the primary error.
- Do not retry `OFF`/`ON` behind the test's back; retries blur ownership and can hide unsafe state transitions.

## Adversarial test shape

Create wrappers around a real SQLite connection rather than pure mocks when possible. Tests should prove:

1. The wrapper observed one real post-baseline `OFF`.
2. Disable readback failure occurs after the real `OFF` and closes/invalidate the connection.
3. Restore readback failure occurs after real rollback and real post-`OFF` `ON`.
4. Total `ON` calls may include a baseline enable plus one restoration; separately count post-`OFF` `ON` calls and assert exactly one.
5. Readback count distinguishes baseline/readback sequencing from post-`OFF` disable and restore readbacks.
6. Subsequent use of the returned/held connection fails after invalidation.
7. Error code/message is stable and bounded; primary migration cause is preserved where relevant.

## Reporting boundary

Focused migration tests and matched baseline canonical failures are not canonical green. Report them as ad-hoc/focused proof and require fresh exact-byte review before commit/merge/deploy.
