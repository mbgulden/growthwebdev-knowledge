# Linear server-generated issue create fallback — Prismatic Phase 2 learning (2026-07)

## Trigger

Use this note when an exact reviewed Linear writer intends to create an issue and the planned deterministic `IssueCreateInput.id` path fails, but exact reconciliation proves the issue was not created.

## Durable lesson

Do not assume Linear will accept client-supplied issue IDs just because schema introspection exposes an `id: String` field. In this workspace, a reviewed attempt with a syntactically valid UUIDv5 returned a GraphQL error before success receipt, and exact UUID/title reconciliation showed no issue existed. Existing successful local Linear writers omitted client-supplied issue IDs and used the server-generated ID returned by `issueCreate`.

## Safe corrected pattern

1. Preserve the failed writer version and reconciliation receipt; do not retry the same writer.
2. Create a new versioned writer/packet and bind exact SHA256s.
3. Omit `id` from `IssueCreateInput`.
4. Keep the packet UUID as `correlation_uuid` in durable intent/receipt rows only; do not compare it to the server issue ID.
5. Use an approved immutable packet key for idempotency/reconciliation, typically exact full title plus exact expected fields.
6. Query candidates with an explicit bound and `pageInfo.hasNextPage`; fail closed on pagination.
7. If exactly one candidate is returned, read it back by its server `id` with all nested connections explicitly bounded.
8. Fail closed on:
   - multiple exact-title/equivalent candidates;
   - candidate readback missing by server ID;
   - title/description/team/state/label mismatch;
   - nested label pagination;
   - transport/HTTP ambiguity after create when reconciliation cannot prove one exact candidate.
9. Prove at most one `issueCreate` call in tests.
10. Prove `--dry-run` leaves both remote state and local receipt/lock paths unchanged.
11. Require fresh independent `CLEAN` review for the corrected writer SHA before any second mutation attempt.

## Minimum test cases

- clean dry-run returns no mutation and no receipt filesystem changes;
- create omits `input.id` and uses returned server ID for readback/mirror;
- transport ambiguity does not retry create;
- exact-title duplicate blocks;
- exact-title field mismatch blocks;
- candidate server-ID readback missing blocks;
- nested issue label pagination blocks;
- intent publication fsyncs file and containing directory, including first-run directory creation.

## Reporting boundary

Report the failed deterministic-ID attempt separately from the corrected server-ID writer. Do not call the failed attempt a partial create if exact reconciliation proves no issue exists, and do not call the corrected writer executable until its current SHA has local proof plus independent review.
