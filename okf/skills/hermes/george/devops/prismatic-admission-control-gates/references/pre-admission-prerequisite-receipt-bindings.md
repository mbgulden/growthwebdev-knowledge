# Pre-admission prerequisite receipt bindings

Use when a Prismatic repair/admission envelope has passed semantic review but depends on earlier checkpoint, exact-head, dirty-byte, or contract-integrity reviews.

## Lesson

An envelope can be structurally safe and still be blocked if it references an upstream checkpoint/contract review only by implication. Bind every prerequisite review as a first-class receipt before execution.

## Required bindings

For each prerequisite, include in the frozen envelope or adjacent receipt:

```text
PREREQUISITE_REVIEW=<delegation-or-review-id>:<verdict>
PREREQUISITE_SCOPE=<exact scope; e.g. integrity_only, not implementation acceptance>
PREREQUISITE_RECEIPT_PATH=<absolute path>
PREREQUISITE_RECEIPT_SHA256=<sha256>
PREREQUISITE_HEAD=<commit if relevant>
PREREQUISITE_TREE=<tree if relevant>
PREREQUISITE_PARENT=<parent if relevant>
PREREQUISITE_NON_CLAIMS=<what the review did not accept>
```

## Review rule

A clean upstream review result quoted in chat is not enough. The envelope reviewer must be able to re-read the durable receipt and verify:

1. the receipt hash matches the envelope;
2. the receipt verdict is `CLEAN/PASS` or equivalent for the claimed prerequisite;
3. the scope is narrow enough to avoid laundering blocked implementation work into acceptance;
4. the envelope's action boundary still says no replay/retry/PR/merge/deploy/Linear unless separately authorized.

## Versioning pattern

If the only blocker is a missing prerequisite binding:

1. preserve the blocked envelope unchanged;
2. create a successor envelope whose delta is limited to version/status history, prerequisite receipt bindings, and marker;
3. prove launcher/payload/preflight identities are unchanged;
4. dispatch a fresh full envelope review before execution.

## Pitfall

Do not treat `checkpoint integrity CLEAN/PASS` as implementation acceptance. It proves exact frozen bytes/checkpoint lineage only. Any producer candidate still needs exact-head reproduction, independent review, merge/deploy proof, and live acceptance before a successor task may start.
