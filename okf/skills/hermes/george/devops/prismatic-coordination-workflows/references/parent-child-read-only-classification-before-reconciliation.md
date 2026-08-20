# Parent-child read-only classification before reconciliation

Use this pattern when a Prismatic parent issue has many children and some child state/title/description signals disagree.

## Trigger

A parent cannot be closed because children are mixed across accepted, active, superseded, and unreconciled states. Titles or descriptions may say `[SUPERSEDED]`, while live Linear state remains `Todo`.

## Pattern

1. **Fresh Linear export first.** Capture current child identifiers, titles, descriptions, labels, relations, and states. Treat live state as authoritative over title text.
2. **Classify read-only.** Split children into:
   - accepted/done within scope;
   - superseded-but-live state-reconciliation candidates;
   - active incomplete children;
   - blocked/review-pending children.
3. **Bind implementation evidence separately.** For accepted children, cite exact immutable release paths, source symbols, tests, contracts, or review receipts. Do not treat a `Done` state alone as implementation proof.
4. **Make sequencing explicit.** Record `ACTIVE_SEQUENCE=<id->id->id>` as a machine-readable field in the classification packet.
5. **Do not mutate during classification.** Keep `LINEAR_WRITE_COUNT=0`; classification is evidence, not a state writer.
6. **Gate superseded-state reconciliation.** A superseded child that is still `Todo` remains live until a reviewed state-only writer runs with explicit Linear mutation authority. If its replacement is not accepted yet, record that dependency before allowing reconciliation.
7. **Do not close the parent.** Parent close requires all active/replacement children accepted plus explicit close authority.

## Packet boundary fields

```text
CHILD_COUNT=<n>
DONE_ACCEPTED_SCOPE=<ids>
SUPERSEDED_TODO_PENDING_STATE_RECONCILIATION=<ids>
ACTIVE_INCOMPLETE=<ids>
ACTIVE_SEQUENCE=<ids joined by ->>
LINEAR_WRITE_COUNT=0
PARENT_CLOSE_AUTHORIZED=false
NOT_CLAIMING=superseded_state_reconciliation,all_children_complete,parent_close,merge,deployment,Linear_mutation
MARKER=<stable_marker>
```

## Verification

- Assert the fresh Linear export child count and states exactly.
- Assert every classified issue id appears in the packet.
- Assert cited immutable-release files/symbols exist.
- Parse the boundary block semantically; do not depend on prose wording.
- Hash the final packet and proof log after any boundary-field patch.
