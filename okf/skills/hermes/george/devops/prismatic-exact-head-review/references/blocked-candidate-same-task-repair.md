# Blocked exact-head candidate → same-task repair contract

Use when independent exact-head reviews agree that a producer candidate is semantically blocked, but the defect is narrow enough to repair without widening the original task.

## Pattern

1. **Preserve the blocked candidate first.** Record the candidate commit/tree, result packet, review IDs/verdicts, failing invariant, changed files, proof logs, and non-claims. Do not overwrite the blocked state with a repair narrative.
2. **Classify the defect as candidate-blocking, not producer-transport failure.** A producer can exit `0`, run targeted tests, and still be blocked if independent review finds an untested semantic invariant violation.
3. **Repair inside the same bounded task/worktree only when scope is narrow.** The repair contract must state the original Linear issue, blocked candidate lineage, allowlisted files, exact invariant to fix, required tests, and explicit non-authority for merge/deploy/successor admission.
4. **Use a separate internal repair event identity when the runtime schema needs it.** Bind that internal ID to the real Linear issue and prove it is schema-valid, but do not replay or relabel the original admission as if it had succeeded.
5. **Prove zero durable state before review.** Check no repair task admissions, outbox rows, lifecycle rows, active slots, leases, or producer processes exist before saying the repair is only a frozen contract.
6. **Validate future admission shape against deployed schemas/policy without posting.** Use disposable DB/policy copies where necessary; production policy must hash-restore before/after. Treat policy rejection of the temporary repair worktree as expected unless one-shot policy is explicitly frozen and restored.
7. **Require independent review of the repair task before any launcher/envelope.** Prior `CLEAN/PASS` on the original candidate does not carry forward to the repair contract.
8. **After repair producer completion, re-run exact-head reproduction from a fresh immutable archive.** Failed setup/verifier attempts stay non-evidence; acceptance starts only at the clean, complete rerun.

## Proof packet fields

```text
BLOCKED_CANDIDATE_HEAD=<sha>
BLOCKED_CANDIDATE_TREE=<sha>
BLOCKING_REVIEWS=<ids/verdicts>
FIRST_DEFECT=<semantic invariant>
REPAIR_LINEAR_ISSUE=<real issue id>
REPAIR_INTERNAL_EVENT_ID=<schema-valid repair id or none>
REPAIR_ALLOWLIST=<files>
ZERO_EVENT_STATE=PASS
SCHEMA_PREFLIGHT=<PASS|BLOCKED_expected_policy|FAIL>
REPAIR_TASK_REVIEW=<pending|clean|blocked>
NOT_CLAIMING=original_candidate_acceptance,repair_event,producer,merge,deployment,succcessor_admission
```

## Pitfalls

- Do not let a green producer packet or targeted tests override a shared independent-review blocker.
- Do not mutate production policy to make a repair preflight pass; use disposable policy/DB copies and prove production hashes unchanged.
- Do not call a repair task reviewed just because the original task package was reviewed. Rehash and re-review the current bytes.
- Do not collapse `blocked candidate`, `repair task frozen`, `repair event admitted`, `repair producer running`, and `repair candidate accepted` into one state.