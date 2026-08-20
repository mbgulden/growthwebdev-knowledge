# Parent/Child Objective Sequencing for Prismatic Linear Families

Use this reference when Michael authorizes completion of a broad parent issue such as a foundational Linear family. Treat the authorization as permission to drive the verified child/dependency sequence, not as permission to bulk-launch or bulk-close.

## Pattern learned

When a parent objective has multiple children, do this before any producer/event/worktree:

1. Take a fresh bounded read-only parent/child export through the reviewed Linear path.
2. Freeze the export path, file mode, SHA256, exporter SHA256, test SHA256, and independent exporter review.
3. Split restricted per-child derivatives when descriptions are needed for review, so chat/proofs do not expose unrelated issue content.
4. Classify every child into a small finite state, for example:
   - `DONE`
   - `SUPERSEDED_CANCEL_PENDING_REVIEWED_STATE_PACKET`
   - `BLOCKED_IMPLEMENT`
   - `PARTIAL_FOUNDATION_IMPLEMENT_LATER`
   - `HARD_BLOCKED_LINKED_ISSUE_AUTHORITY`
   - `READY_READ_ONLY_DISCOVERY_DEFER_FINAL_PROOF`
5. Run independent exact-base audits before accepting the sequence. Use audits to answer whether each Todo child is genuinely unimplemented, superseded, or already satisfied by merged work.
6. Freeze a parent classification artifact under `private/` with mode `0600`, exact hashes, sequence, controls, and nonclaims.
7. Update durable and hot handoffs with the classification artifact and the single next admissible child.

## Gate rule

A broad parent authorization may support state-only reconciliation only after each child’s acceptance/replacement is proven and reviewed. It is not authority to:

- bulk-mark the parent or siblings Done;
- launch multiple child producers in parallel;
- bypass child-specific contract/admission/envelope review;
- convert superseded children to Done by shortcut;
- treat a stale or quarantined export as live source evidence.

## Choosing the first implementation slice

Pick the first child by production-safety dependency, not by issue order. If a lower-level invariant can invalidate later projection/retention claims, it goes first.

Example class of precedence: fix receipt/lease/fence authority before projection/read-model work. Projection proof is not meaningful if terminalization can be stale-owner or false-`reconciled`.

## Contract freeze discipline

For the first child contract:

- bind exact production commit/tree and safe Linear export hashes;
- state the exact defects and the finite repair;
- include a four-path or otherwise finite allowlist;
- require deterministic temporal authority where relevant;
- include zero-action markers (`TASK_MATERIALIZED=false`, `WORKTREE_CREATED=false`, `EVENT_COUNT=0`, `PRODUCER_STARTED=false`, `LINEAR_WRITE_COUNT=0`);
- dispatch full and focused adversarial reviews before any task/event/worktree.

If a local verifier finds a contract omission after a version is frozen or dispatched, preserve that version and create V+1; do not edit the frozen artifact in place.

## Proof packet

Use a compact marker like:

```text
PARENT_CLASSIFICATION=/path/private/PARENT_CHILD_CLASSIFICATION_V1.json
PARENT_CLASSIFICATION_SHA256=<sha256>
SAFE_EXPORT=/path/private/linear-parent-safe.json
SAFE_EXPORT_SHA256=<sha256>
FIRST_SLICE=<child-id>
FIRST_SLICE_REASON=<production-safety dependency>
SEQUENCE=<child-a>,<child-b>,...
SUPERVISED_CAP=1
PARALLEL_PRODUCERS=false
TASK_MATERIALIZED=false
WORKTREE_CREATED=false
EVENT_COUNT=0
PRODUCER_STARTED=false
SOURCE_EDIT_COUNT=0
LINEAR_WRITE_COUNT=0
NEXT_ACTION=<consume reviews or freeze admission artifacts>
MARKER=<PARENT>_<FIRST_SLICE>_REVIEW_PENDING_ZERO_AUTHORITY
```
