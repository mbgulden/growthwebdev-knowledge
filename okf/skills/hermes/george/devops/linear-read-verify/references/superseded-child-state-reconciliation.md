# Superseded child state reconciliation under parent completion

Use this when Michael authorizes completion of a parent Linear objective and one or more child issues are already explicitly superseded by their current Linear descriptions.

This is **not** implementation work and not the one-issue `Done` shortcut. It is a state-only reconciliation packet for children whose accepted prose says not to implement from that issue.

## Admission conditions

All must be true before drafting a packet:

1. Michael has explicitly authorized the parent completion or the exact superseded child reconciliation.
2. Fresh read-only Linear evidence for the parent and children is available from a reviewed bounded exporter or broker.
3. The child description contains an explicit supersession notice / do-not-implement boundary and names the replacement issue/authority or consolidation target.
4. The replacement/transferred authority is already accepted or terminal in Linear. A replacement contract that is merely designed, frozen, or under review is not enough; hold the superseded child open until the replacement exists and is accepted.
5. The intended mutation is only the child workflow state to the canonical canceled/superseded terminal state, with no labels, comments, description edits, parent/child topology, assignees, projects, or relations.
6. The mutation is not being used to hide unfinished acceptance.

If any condition fails, do not mutate; freeze the blocker and sequence the real implementation/review first. It is acceptable to freeze a **non-executable** packet for later review while the writer/replacement gate is still pending, but the packet must say `executable=false` and `specific_post_packet_mutation_approval=pending`.

## Required packet fields

For each child, bind:

- child ID, identifier, title hash, description hash, current state id/name/type, `updatedAt`, `completedAt`/`canceledAt` if exposed;
- exact team binding from direct metadata or exporter (`team.id`, `team.key`, `team.name`) so the target terminal state lookup is scoped to the correct team;
- non-state baseline surfaces that must remain unchanged: labels, parent, priority, assignee, project, relations, URL when available;
- parent ID/identifier and child count from the same fresh export;
- exact supersession marker quoted only as a compact phrase, not full sensitive descriptions in chat;
- replacement issue/authority identifier and its current state/type plus hash-bound title/description where available;
- canonical target state id/name/type selected by exact live lookup (for example `Canceled`/`canceled`), never guessed from display order;
- mutation scope: `stateId-only`; explicitly `no labels/comments/prose/topology/relations/assignee/project/priority`;
- allowed server-derived state fields after mutation: usually only `updatedAt` and `canceledAt`; do not accept changes to `completedAt` for a canceled transition;
- rollback/reconciliation policy for ambiguous transport: read back first, never blindly repeat the mutation.

## Writer selection

Do not repurpose a hardcoded historical multi-issue writer for one-issue superseded reconciliation. If the existing durable executor is bound to an old packet, relation ledger, create/update phases, or default redirect-following HTTP client, treat it as design reference only.

A dedicated one-issue writer must have:

- default dry-run and a separate execution mode gated by exact packet SHA, exact writer SHA, Michael's post-packet approval, and `executable=true`;
- rejecting redirect handler / no-follow opener for all Linear HTTP requests;
- exact credential stripped from raw bounded responses before normalization/truncation, with generic secret-pattern redaction as defense in depth;
- bounded response size and hard per-request/convergence deadlines;
- unique live target state resolution by team + state name + state type;
- durable mode-`0600` intent receipt fsynced before the single `issueUpdate(stateId)` mutation;
- one mutation call maximum, enforced in code and receipt;
- ambiguous timeout/transport policy: reread current issue, accept only exact before-or-target convergence, never blindly repeat;
- exact post-readback guard that all non-state fields remain baseline-bound.

## Review and execution requirements

Because this is not the accepted-head `Done` shortcut, use the normal fail-closed writer pattern:

1. Keep writer code separate from read-only brokers.
2. Require local dry-run and failure-injection proof for the exact packet/writer bytes.
3. Require independent `CLEAN` review on the exact packet and writer hash before live mutation.
4. Before each live mutation, record and fsync a durable intent with expected `updatedAt` and expected before-state.
5. Execute one issue `stateId` mutation at a time.
6. Immediately read back the same issue through a read-only path; accept only exact target state and non-null terminal timestamp where Linear exposes one.
7. Append a result receipt and hash it.

## Reporting packet

```text
RESULT=<PASS|BLOCKED>
PARENT=<GRO-N>
CHILDREN=<GRO-A,GRO-B>
MUTATION_SCOPE=stateId-only superseded/canceled reconciliation
SOURCE_EXPORT=<path>
SOURCE_EXPORT_SHA256=<sha256>
WRITER_SHA256=<sha256>
PACKET_SHA256=<sha256>
DRY_RUN=<PASS|FAIL>
FAILURE_INJECTION=<PASS|FAIL>
REVIEW=<handle:CLEAN|BLOCKED>
LINEAR_MUTATED=<true|false>
RECEIPT=<path>
RECEIPT_SHA256=<sha256>
NOT_CLAIMING=implementation, transferred acceptance completion unless separately proven, labels/comments/prose/topology mutation, parent completion
```

## Pitfalls

- A broad parent-completion authorization does not justify bulk-marking every child terminal. Classify child-by-child: done, superseded, substantive-Todo, blocked, or held.
- Do not mark a superseded child `Done` when its prose says “do not implement from this issue.” Use the canonical canceled/superseded terminal state if reconciliation is approved and reviewed.
- Do not use session history as current proof of supersession. Use a fresh read-only export/broker and bind hashes.
- Do not mutate superseded children before the replacement issue’s transferred acceptance is proven or explicitly held as a separate prerequisite.
- Do not mix superseded reconciliation with starting the replacement issue, adding relations, or closing the parent in the same packet unless Michael explicitly authorizes that exact multi-mutation packet and it receives fresh review.
