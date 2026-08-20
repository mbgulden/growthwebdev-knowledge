# Checkpoint-first recovery while preserving clean admission

Use this note when a reviewed recovery producer must repair from a preserved dirty checkpoint, but deployed admission only accepts a tracked-clean worktree.

## Pattern

1. Create the dedicated recovery worktree clean at the exact reviewed base.
2. Materialize the preserved dirty checkpoint only in a disposable archive/workdir that cannot mutate the admitted worktree.
3. Prove the checkpoint patch identity and endpoint blob identities after application.
4. Keep the admitted worktree tracked-clean through task-copy creation, deployed preflight, envelope freeze, review, POST, and consumer invocation.
5. In the producer task/contract, require the producer to apply and prove the checkpoint patch as its first tracked mutation after launch, before attempting repair.
6. Preserve a one-descendant boundary: the final candidate must descend from the clean base and incorporate the exact checkpoint bytes before repair.

## Deployed-preflight lessons

- Do not infer `TaskAdmissionStore` constructor arguments, schema fields, status/version values, policy key names, or validation call shape. Inspect the deployed release source and a proven launcher/preflight before retrying.
- Setup-only failures are useful evidence. Record them in the proof log as verifier setup failures, then rerun from the beginning with the corrected binding.
- Do not add live-table assertions to a disposable `_validated_payload()` preflight unless those tables are actually initialized by that path. Check live zero-state separately using the real event DB in read-only mode.

## Proof anchors to capture

```text
BASE_HEAD=<sha>
BASE_TREE=<sha>
RECOVERY_WORKTREE=<path>
TRACKED_STATUS=clean
CHECKPOINT_PATCH_SHA256=<sha>
DISPOSABLE_PATCH_APPLY=PASS
ENDPOINT_BLOBS=<path=blobsha,...>
TASK_SHA256=<sha>
TASK_COPIES_BYTE_IDENTICAL=true
DEPLOYED_SOURCE_SHA256=<sha>
PREFLIGHT_RESULT=PASS_AFTER_RECORDED_VERIFIER_SETUP_FAILURES
LIVE_ZERO_STATE=true
NOT_CLAIMING=event,consumer,producer,source repair,commit,candidate,merge,deploy
```
