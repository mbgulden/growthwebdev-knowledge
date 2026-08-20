# SQLite authority adversarial review pattern

Use this reference when a Prismatic acceptance candidate hardens SQLite-backed authority/receipt/registry state. It captures durable review techniques from CRONAUTH-style repair chains; adapt names and tables to the current task.

## Invariant classes to probe

- **Normative identity vs stored evidence:** distinguish the contract key from storage-only fields. If a digest or evidence column is informational, do not let it widen uniqueness unless the task contract explicitly says so.
- **Replacement bypass:** test both `INSERT` and `INSERT OR REPLACE`; SQLite replacement can delete/reinsert and bypass assumptions about monotonicity, foreign keys, or triggers.
- **Immutable mappings:** if a row binds an external identity to a semantic key, attack `UPDATE`, `DELETE`, same-PK replacement, same-tuple replacement, and duplicate tuple with different evidence.
- **Trigger abort semantics:** prefer fail-closed statement behavior for guards and verify that a failed statement does not leave a partial receipt/attempt/cursor mutation.
- **Supplied-connection namespace squatting:** on connection-based migration APIs, create TEMP tables/triggers using authority object names before migration. Verify migration fails closed before durable `main` mutation and preserves caller TEMP objects/transaction boundaries.
- **Main-schema qualification:** when using SQLite metadata or version watermarks, qualify authority reads/writes/DDL execution against `main` where possible. Remember SQLite stores DDL text without `main.` qualification, so canonical DDL string comparisons may need unqualified expected text plus qualified execution paths.

## Exact-head verifier recipe

1. Create an immutable archive of the candidate commit, not a mutable checkout.
2. Assert `HEAD`, `TREE`, base ancestry, allowed changed paths, and tracked-clean source state.
3. Run focused tests and the bounded regression set protecting receipt/admission consumers.
4. Run static gates: `ruff check`, `ruff format --check`, `compileall`, and `git diff --check <base>..HEAD`.
5. Add a disposable `/tmp/hermes-verify-*.py` adversarial script that directly reproduces prior blockers and prints explicit pass markers such as:
   - `NORMATIVE_KEY_DUPLICATE=REJECTED`
   - `REPLACE_UPDATE_DELETE=REJECTED_UNCHANGED`
   - `TEMP_SCHEMA_SQUAT=REJECTED_MAIN_UNCHANGED`
6. Clean up reviewer-created scripts, archives, and temp DBs; do not reset/clean/restore the source worktree.

## Reporting boundary

Classify this as `ad-hoc targeted exact-commit verification` unless the repository's canonical full suite actually ran. Keep independent review, PR, merge, deployment, and live migration as explicit nonclaims until separately proven/authorized.
