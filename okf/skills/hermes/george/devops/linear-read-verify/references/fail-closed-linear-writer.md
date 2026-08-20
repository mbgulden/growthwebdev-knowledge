# Fail-closed Linear writer review and execution pattern

Use this reference only after Michael explicitly authorizes a specific Linear mutation packet. It extends the read/verify and executable-packet drafting workflow into a guarded writer without weakening the read-only brokers.

## Core boundary

- Keep metadata/export brokers read-only. Put write logic in a separate reviewed writer script.
- Bind every review, dry-run, and execution request to exact writer SHA256 plus packet/export/receipt hashes.
- Do not execute live writes after code edits until the new exact SHA has passed local verification and independent review.
- Treat stale async reviews by exact hash: valid findings must be ported into the current artifact, then the current artifact must be independently re-reviewed `CLEAN`.

## Writer design requirements

A Linear writer for multi-issue packet execution should be fail-closed and deterministic:

1. **Expected baseline first** — read every touched issue and relation target; fail on missing, pagination, wrong team, wrong project/parent/state/labels/relations, or `updatedAt` drift. This includes nested readback connections: if an exact-ID issue lookup reads `labels`, `relations`, `children`, etc., every connection must request an explicit bound (for example `first:100`) and reject `pageInfo.hasNextPage` before exact comparison.
2. **Created artifact IDs must be proven, not assumed** — prefer deterministic packet-owned UUIDs for newly created issues and relations only after a live read-only/schema canary proves Linear accepts that specific client-ID path in the workspace. If the reviewed create path rejects client-supplied IDs, preserve the failed attempt/reconciliation evidence, then switch to a server-generated-ID writer: keep a packet-bound correlation UUID in durable intents/receipts, omit `IssueCreateInput.id`, and use an exact-title or other approved immutable packet key for idempotency/reconciliation.
3. **Absence/idempotency/reconciliation key** — before create, verify the selected key is absent or already maps to exactly one exact packet match. If using deterministic IDs, verify absence by exact ID, not by identifier ambiguity. If using server-generated IDs, query an explicitly bounded exact-title/equivalent collection, fail on pagination, zero readback for a returned candidate ID, multiple candidates, or any field mismatch. Do not rely on Linear's singular `issue(id:)` as an absence guard if the schema/transport reports a missing ID as a GraphQL error; use an exact, bounded collection query or another reviewed schema-supported absence proof. After response loss, reconcile once by the reviewed key/server ID path before deciding whether the outcome is ambiguous. Never retry `issueCreate` after transport/HTTP ambiguity unless reconciliation proves no candidate exists and a fresh exact review authorizes the corrected writer.
4. **Dry-run purity is broader than remote no-op** — `--dry-run` must not mutate Linear, the project registry, receipt directories, locks, or other local state. Prove this with a before/after filesystem snapshot of writer-owned receipt paths when claiming zero mutation.
5. **Durable receipt publication before mutation** — before the first live mutation, durably publish the writer-owned receipt path itself: recursively create missing receipt directories one level at a time, fsync each newly created directory's parent, create/replace receipt files via temp-file + file fsync + atomic rename + parent-directory fsync, and fsync appended intent files plus their parent directory before the Linear mutation. File fsync alone is not enough on first run because the directory entry may not survive a crash.
6. **Durable intents before mutation** — append and fsync a receipt intent before every forward mutation and before every rollback mutation. Include operation, target, expected-before, intended-after, and deterministic IDs; then fsync the intent file's parent directory before the external mutation.
7. **Full snapshot rollback** — preserve complete before snapshots for content, state, parent, labels, relations, and child topology. Rollback only when the current state still matches the packet-owned intended state; otherwise mark `MANUAL_INTERVENTION_REQUIRED`.
6. **Parent/child projections** — maintain expected child topology locally after reparent/create/delete so later checks do not compare against stale projections.
7. **Quarantine before destructive cleanup** — when rolling back a newly created issue, first move it to a safe canceled/quarantine state and verify ownership before deletion.
8. **Final proof** — after success or rollback, perform a final read-only projection of the canonical parent/root issue family and record it in the receipt.

## Failure-injection suite

Before live execution, run a deterministic local simulation that covers at least:

- clean success path;
- timeout/response loss after first update;
- timeout after a mid-content update;
- timeout after reparent;
- timeout after cancel/state change;
- timeout after deterministic issue create;
- timeout after deterministic relation create.

Every failure scenario should verify one of these exact outcomes:

```text
STATUS=FAILED_ROLLED_BACK_QUARANTINED
STATUS=MANUAL_INTERVENTION_REQUIRED
```

Never allow a scenario with ambiguous residual Linear state to report clean rollback.

## Review prompts

Ask independent reviewers to look specifically for:

- mutation calls without prior durable intent and durable receipt-path publication;
- first-run receipt directories/files that are created without parent-directory fsync;
- intent append logic that fsyncs the file but not the containing directory before the external mutation;
- rollback calls without prior durable intent;
- non-exact or schema-invalid created artifact absence/reconciliation lookup;
- stale expected snapshots after partial rollback;
- relation ownership ambiguity;
- child/parent projection drift;
- deletion guards that only check identifier lookup;
- final receipt claims that are not backed by a fresh read-only proof.

## Reporting

Use compact proof packets and separate scopes:

```text
SCRIPT_SHA256=<sha256>
PACKET_SHA256=<sha256>
DRY_RUN=<PASS|FAIL>
LINEAR_MUTATED=false
REGISTRY_MUTATED=false
LOCAL_RECEIPT_FS_CHANGED=false
FAILURE_INJECTION=<PASS|FAIL>
RECEIPT=<path>
REVIEW=<delegation/session id>
STATE=<running|CLEAN|BLOCKED>
NOT_CLAIMING=live writes executed
```

Only say `ready for execution approval` when the exact current writer SHA has local dry-run proof, failure-injection proof, and independent `CLEAN` review.

## One-issue state-only transitions

For superseded/canceled issue reconciliation, use a separate generic writer rather than trimming a broad historical packet executor.

- One packet, one exact issue UUID/identifier, one separately reviewed hash, one execution.
- Guard exact `updatedAt`, team, current state, title/description hashes, parent/project/assignee, labels, children, comments, and both relation directions. Every connection must be bounded and expose `hasNextPage=false`; malformed/null connections fail rather than normalize to empty.
- Resolve exactly one team-bound `Canceled`/`canceled` workflow state immediately before mutation and reject pagination, duplicates, wrong team/type, or target-ID drift.
- Structurally expose only a fixed `issueUpdate(id, {stateId})` mutation. Keep exactly one mutation document/call site and a runtime attempt counter that rejects a second call. No rollback mutation.
- Default invocation is read-only dry-run and must not create receipt/lock/log directories. Live execution requires explicit `--execute`, exact writer/packet hashes, and a trusted **post-packet** Michael approval artifact; a caller-typed actor/name or public SHA is not authentication.
- Reject redirects before follow-up construction. Remove the exact loaded credential recursively before generic redaction or truncation. Bound declared/actual response bytes, per-request timeout, and one monotonic convergence deadline.
- Before the sole mutation, durably create mode-700 receipt directories with parent fsync at each new level, publish a regular non-symlink mode-600 receipt, append/fsync a durable intent plus parent directory, and record mutation attempt 1.
- On timeout/connection loss/invalid response, never resend. Perform bounded read-only convergence: exact target plus unchanged non-state baseline may become `APPLIED_RECONCILED`; unchanged baseline is still ambiguous and cannot authorize retry; any third state, non-state drift, malformed/paginated read, or unavailable proof requires manual intervention.
- Restart with unfinished intent performs read-only convergence only and never issues a second mutation.
- Final success requires a fresh full readback and exactly one recorded mutation attempt.

Historical broad writer pitfalls: `linear_execute_packet_v2.py` is hardcoded, follows redirects, writes local receipt state in dry-run, has broad update/create/relation/rollback surfaces, and uses caller-asserted approval; do not reuse it unchanged for one-issue cancellation.