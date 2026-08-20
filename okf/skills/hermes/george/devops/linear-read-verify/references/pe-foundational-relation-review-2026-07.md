# PE foundational relation review — July 2026 example

Session-specific example for `linear-read-verify` relation/reuse manifests. Keep this as a review pattern, not a hardcoded issue list for future unrelated Linear work.

## What changed after exact-description review

A first manifest was locally verified against a bounded read-only export, but independent exact-description reviewers found that the proposed graph still overfit stale titles and prose dependency text. The repair pattern was:

- **Preserve useful adjacent work.** `GRO-4268` was not canceled/reused because exact text showed a distinct George executable-review lane. `GRO-4269` stayed narrow and was not broadened into Codex.
- **Patch parent umbrella wording before children.** `GRO-4262` needed provider-lane parent text while retaining existing children; Codex candidates remained blocked on exact read of the existing `GRO-4304`/`GRO-4314`–`GRO-4316` family.
- **Create only genuinely missing candidates.** `PE-CRON-RECEIPTS-EXT` was genuinely missing under `GRO-4263`; it should be blocked by exact-head receipt schema acceptance and should not duplicate the base schema task.
- **Reuse/reparent instead of duplicating.** `GRO-4319` should be reparented from HTTP to receipts/runtime and fully rewritten as `PE-CRON-RUNTIME-01`, with operational hold for actual cron mutation.
- **Split runtime/runner/status.** Runner acceptance follows immutable trigger/runtime plus receipt identity; status derives from runner receipts; hook validation follows exact runtime migration.
- **Consolidate ambiguous nodes.** Direct label mutation (`GRO-4274`) consolidated into an idempotent Linear projection task. Ambiguous API receipt/state work (`GRO-4280`) consolidated into typed receipt/state-event work rather than remaining a chain node.
- **Retention stays plan-only.** Retention/dry-run can be rewritten, but cleanup remains uncreated until restore/reference proof and separate authorization.

## Relation graph lesson

Do not materialize cumulative or malformed dependency prose from descriptions. Separate:

1. live Linear relation arrays;
2. stale textual dependency fields that need description repair;
3. corrected minimal direct `blockedBy` edges;
4. symbolic/future edges for not-yet-created candidates.

A good proof packet reports current relation count, proposed current-identifier edges, proposed symbolic/future edges, and `LINEAR_MUTATED=false` separately.

## Executable-packet lessons

A planning graph is not yet an executable mutation packet. Before asking for write approval:

- freeze immutable/versioned payload components and review exact path+hash bytes; never modify a file while an exact-hash review is in flight;
- make the source exports integral frozen components or generate one canonical before-guard row per existing issue with immutable issue/team IDs, `updatedAt`, exact title/description hashes, complete sorted labels, state, parent, and complete incoming/outgoing relations;
- keep one master relation ledger as the sole writer; component relation lists are declarative only so a cross-component edge cannot be created twice;
- model create operations with exact team/parent/title plus a durable packet idempotency marker, zero-match checks before any write and immediately before create, and receipt-bound recovery semantics;
- record the expected evolving state after every write and re-read before every later mutation; use conditional version writes when supported and fail closed on unexplained drift;
- materialize relations in prerequisite-first order and compare both endpoints' complete evolving relation sets;
- require terminal-state resolution by exact name, semantic type, and team, then revalidate immediately before the transition;
- keep dispatch quarantine after partial failure. A later approval must separately authorize relation rollback, existing-field restoration, new-issue deletion, and dispatch restoration; omitted rollback permissions default to denied;
- for Codex, use the installed Codex CLI behind PE's canonical `AgentHarness`, never a Hermes `codex` profile, `SOUL.md`, copied Hermes credentials, or a second launcher/queue/state authority.

## Approval boundary reminder

Even after local manifest checks pass, request exact-hash independent review before asking Michael to approve writes. If the review is pending, report `PARTIAL` and do not ask for execution approval unless Michael explicitly requests a provisional packet.
