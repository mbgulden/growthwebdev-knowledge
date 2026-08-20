# Linear Recovery-Execution Retry Pattern

Use this when an approved Prismatic Linear packet partially executed, failed safely/rolled back, and a bounded retry is needed. The goal is not to make a generic second executor; it is to create a separately reviewed recovery-only execution path with exact provenance and rollback containment.

## Durable lessons

1. **Treat a retry executor as a new authority artifact.**
   - Bind it to its own exact script SHA.
   - Require `mode=recovery`; reject normal execution through the recovery revision.
   - Keep the original frozen bundle approval SHA and frozen payload unchanged.
   - Require the exact retry baseline SHA and exact source recovery receipt/provenance.

2. **Do not rely on private baseline files without hash-binding them.**
   - If a recovery script reads a private before-snapshot or source receipt, the script must verify its expected SHA before using it.
   - The receipt path alone is not enough proof; hash drift must fail closed.

3. **Model service canonicalization before writing.**
   - Linear may store submitted Markdown differently, e.g. `- list item` can normalize to `* list item` and Linear may insert a blank line before the first contiguous list after a paragraph/header.
   - Expected stored content should account for known canonicalization without weakening unrelated drift checks.
   - Capture the submitted form and expected stored form explicitly in dry-run/proof logs.
   - Use `references/linear-markdown-canonicalization.md` when writing exact postcondition/recovery guards for Linear Markdown descriptions and projections.

4. **Keep dispatch restoration disabled for recovery retries unless separately authorized.**
   - A content/relation retry should not re-enable queues, dispatch, or runtime orchestration as an incidental side effect.
   - If dispatch restoration is needed, make it a distinct reviewed slice.

5. **Failure injection must include applied-then-timeout cases.**
   - Simulate success plus failures after each mutation class: content update, mid-update, reparenting, cancel/delete, create, and relation creation.
   - If exact ownership and the complete affected postcondition converge, record `PASS_RECONCILED` and continue. If the write is proven not applied, retry the same idempotent stage within a bounded budget. Roll back only an unresolved or incorrect mutation—not a single slow response/read.

6. **Review stale async results by exact hash.**
   - If a delegated review returns `BLOCKED` against an obsolete SHA, do not dismiss the finding outright.
   - Port valid defects into a new frozen/versioned artifact, re-run local proof, and request fresh exact-SHA review.

7. **Parse only the bytes that were verified.**
   - Open each frozen artifact once, use `fstat()` on that descriptor, read and hash those exact bytes, and parse only the verified in-memory bytes.
   - Apply the same rule to retry baselines and source receipts. Hashing a path and reopening it for parsing leaves a same-UID TOCTOU gap.

8. **Treat immediate post-write reads as potentially stale.**
   - A Linear update response may be followed by a temporarily stale read even though the canonical write was applied. Do not trigger rollback from one immediate mismatch.
   - Re-read toward the exact evolving full-snapshot postcondition within a bounded monotonic convergence window. Preserve exact ownership/drift checks during every retry.
   - Make the bound real: each network request must have a hard wall-clock interruption covering connection and full response reading, capped at the remaining convergence time; override direct lookup methods that bypass the normal GraphQL request path.
   - If convergence is not proven before the deadline, fail closed and name the residual.

9. **Preserve verified stages; resume instead of replaying the whole packet.**
   - Use one canonical stage state machine: `content -> create -> topology/state -> relations -> final proof`. Persist the exact stage checkpoint and verified evolving snapshot after each stage.
   - On transport pressure or a stale projection, pause and resume the current stage after paced convergence. Do not erase already verified stages merely to regain a pristine baseline.
   - Keep the whip ready: roll back only for wrong-object mutation, wrong exact value, lost deterministic ownership, external drift, or an unresolved mutation after the bounded reconciliation budget.
   - Pace Linear requests and honor service terrain. Client-supplied Linear issue/relation IDs must be frozen valid UUIDv4 values; UUIDv5 strings can be rejected by Linear's validator even though they are syntactically UUIDs. Treat IDs of soft-deleted Linear issues/relations as permanently reserved: an exact-ID absence lookup does not prove the ID can be reused. Roll the checkpoint forward to a fresh frozen UUIDv4 ledger without replaying already verified stages.
   - A reviewer finding is blocking only when it demonstrates unintended mutation, acceptance of an incorrect final state, ownership loss, unrecoverable mutation, or authorization/baseline bypass. Record theoretical hardening ideas as follow-up work rather than recursively expanding the execution gate.

## Minimum proof block

```text
SCRIPT_SHA256=<exact recovery executor sha>
FROZEN_BUNDLE_SHA256=<approved original packet sha>
RETRY_BASELINE_SHA256=<hash of before/baseline snapshot used for retry>
SOURCE_RECEIPT=<path>
SOURCE_RECEIPT_SHA256=<sha if consumed by recovery script>
MODE=recovery
DISPATCH_RESTORATION=false
DRY_RUN=<PASS|FAIL> RECEIPT=<path> LINEAR_MUTATED=false
FAILURE_INJECTION=<N/N PASS> LOG=<path>
REVIEW=<delegation id or reviewer receipt>
NOT_CLAIMING=production write/live mutation until explicit post-CLEAN authorization
```

## Execution gate

Only proceed to live mutation when all are true:

- Exact-SHA independent review is `CLEAN` for the current recovery executor.
- Michael explicitly authorizes the exact recovery-mode retry after that review.
- Dry-run receipt says `LINEAR_MUTATED=false`.
- Failure-injection log includes both full success and applied-then-timeout rollback/quarantine cases.
- The command line includes `--mode recovery`, exact retry baseline SHA, all required rollback flags, and dispatch restoration disabled.
