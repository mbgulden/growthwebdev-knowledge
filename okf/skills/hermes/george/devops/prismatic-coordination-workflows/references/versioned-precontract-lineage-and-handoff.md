# Versioned precontract lineage and handoff bookkeeping

Use this when an async/independent review blocks a frozen Prismatic contract/precontract and the safe next move is a new immutable artifact version rather than editing the blocked file.

## Durable pattern

1. Treat every async review as bound to its exact artifact SHA, not to the current task name.
   - If the hash is stale, preserve it as a valid stale-hash review and do not let it approve or block a newer artifact unless the finding still applies.
   - If the finding is valid for the current artifact, create the next version only; do not mutate the reviewed bytes.
2. Keep the version lineage machine-readable in the handoff:
   - `*_V1_SHA256`, `*_V1_REVIEW`, `*_V2_SHA256`, `*_V2_REVIEW`, etc.
   - Record `BLOCKED` findings with the exact line/field and the minimum correction needed.
   - Keep the active gate as `await exact Vn review`, not a vague task-level pending state.
3. When the only repair is machine-readable identity, keep the diff minimal and prove it:
   - title/version header,
   - `CONTRACT_VERSION`,
   - marker/state token,
   - no substantive contract/topology changes.
4. After handoff edits, verify the bookkeeping itself:
   - each state/review/next-gate/marker key occurs exactly once;
   - all preserved artifact hashes still match;
   - zero-event/admission boundary remains true;
   - write a compact `/tmp/hermes-verify-*` proof.

## Admission-ready envelope gate

A contract/precontract `CLEAN/PASS` is only a contract-review result. Do not report admission readiness until all of these are separately proven:

1. exact reviewed bytes copied verbatim into the declared task/envelope paths;
2. branch/worktree identity matches the contract-declared base/tree and is tracked-clean;
3. admission/lifecycle/outbox/claim tables for the task remain zero before authorization;
4. preserved blocked or recovery workspaces were not mutated;
5. an independent envelope review returns `CLEAN/PASS` for the exact task-copy hash; and
6. the handoff records `ADMISSION_READY_AWAITING_EXPLICIT_AUTHORIZATION`, not an implied POST/producer launch.

If a clean contract review is followed by envelope creation, dispatch a fresh exact-hash envelope review and stop at that gate.

See also `references/versioned-precontract-stale-review-lineage.md` for the stale async review + admission-ready lineage addendum from the CRONRUNNER/GRO-4318 session.

## Pitfall: fuzzy handoff patches can damage lineage

When patching a dense handoff block with many similar keys, a fuzzy replace may accidentally remove historical V2/V3 detail lines or create duplicate keys. Do not stop after a successful patch result. Re-read the changed bounded block and run a key-count verification for the active keys. If a fuzzy patch damaged history, restore the entire version lineage block in one exact replacement and verify again.

## Example proof fields

```text
V3_SHA256=<blocked artifact sha>
V3_REVIEW=<delegation>:BLOCKED;<precise finding>
V4_SHA256=<new artifact sha>
V4_DIFF=title_V3_to_V4;CONTRACT_VERSION_3_to_4;marker_V2_to_V4
V4_REVIEW=<delegation>:pending
EVENT_COUNT=0
WORKTREE_CREATED=false
HANDOFF_VERSION_KEYS_UNIQUE=true
RESULT=PASS
SCOPE=<issue> Vn-to-Vn+1 artifact identity repair
AD_HOC_OR_CANONICAL=ad-hoc targeted artifact verification
NOT_CLAIMING=review acceptance, implementation, event, producer, PR, merge, deployment, Linear write
MARKER=<issue>_PRECONTRACT_Vn+1_REVIEW_PENDING
```

## Boundaries

- Do not convert contract-clean or envelope-clean into event authorization.
- Do not treat downstream status/projection implementation as safe until the upstream canonical read/query and shared schedule/bucket model exist, are reviewed, and are merged.
- Do not erase prior blocked versions from the handoff just because a newer version supersedes them; blocked history is part of the audit trail.
