# Pre-implementation contract freeze gate

## Trigger
Use this when a Prismatic dispatch issue has been created/reconciled and mirrored, but before creating the implementation worktree or editing source.

## Lesson
The safe bridge from dispatch to implementation is a frozen, byte-bound contract. Do not let a mutable draft, stale placeholders, or a semantically correct but unreviewed Linear/registry state authorize source edits.

## Required pattern
1. Preserve the mutable draft; copy it to a versioned contract path (`..._CONTRACT_V1_YYYY-MM-DD.md`) before editing the frozen artifact.
2. Replace all placeholders with live identities: Linear identifier/server ID/URL, labels and label IDs, registry receipt hash, post-mirror registry hash, exact base commit/tree, branch/worktree names, and bounded baseline logs.
3. Bind exact source/config/test/log hashes for every file the contract assumes, including containment config and baseline verification logs.
4. Add machine-readable authorization flags near the top, for example:

   ```text
   LOCAL_IMPLEMENTATION_AUTHORIZED_AFTER_CLEAN_REVIEW=true
   COMMIT_AUTHORIZED=false
   DEPLOYMENT_AUTHORIZED=false
   PUBLIC_UNBLOCK_AUTHORIZED=false
   EVENT_OR_PRODUCER_AUTHORIZED=false
   ```

5. Run a contract self-check that:
   - recomputes every declared hash from disk;
   - confirms the repo is still at the expected clean base;
   - rejects stale placeholders/version lineage such as `<GRO-ID>`, draft markers, old packet hashes, or obsolete env var names;
   - checks the expected hard-boundary markers are present.
6. If the self-check fails because the verifier script/transcription is wrong, repair the verifier and rerun; do not mutate the artifact unless the artifact is actually wrong.
7. Dispatch the exact contract SHA for independent read-only review. Do not create branch/worktree or modify source until review returns `CLEAN/PASS`.
8. Once dispatched, the reviewed artifact's bytes are immutable. If a verifier or reviewer finds an omission after dispatch, do **not** patch the reviewed version in place. Preserve/re-hash it, restore exact bytes if necessary, copy forward to `V(N+1)`, apply the minimum correction there, and launch fresh exact-byte review. For the compact old/new hash proof packet and quarantine pitfall, see `references/immutable-contract-artifact-versioning.md`.
9. When a downstream Linear/external projection lacks immutable provider-native target identity in exact-base receipts/snapshots, use `references/linked-issue-authority-precontract-gate.md`: freeze `RESULT=BLOCKED`, state the finite authority-schema prerequisite, and keep task/worktree/event/producer/source/DB/Linear mutation counts at zero.

## Non-claims
- A frozen contract does not authorize deployment, public unblocking, event POST, producer launch, commit, push, merge, or cleanup.
- Linear creation and registry mirror completion are dispatch proof only; implementation remains gated by the independent contract review.
- Baseline tests prove the starting point, not the future implementation.

## Compact proof fields
```text
CONTRACT_PATH=<absolute path>
CONTRACT_SHA256=<sha256>
LINEAR=<identifier/server id>
REGISTRY_RECEIPT_SHA256=<sha256>
BASE=<commit/tree/status>
SOURCE_CONFIG_HASHES=<PASS|FAIL>
STALE_PLACEHOLDERS_ABSENT=<true|false>
AUTHORIZATION_FLAGS_PRESENT=<true|false>
REVIEW=<delegation id/status>
NOT_CLAIMING=<deploy/public unblock/event/producer/git cleanup>
```
