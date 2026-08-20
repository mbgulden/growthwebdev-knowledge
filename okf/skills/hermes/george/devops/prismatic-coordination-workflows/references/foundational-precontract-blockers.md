# Foundational precontract blockers before Prismatic admission

Use this when a requested Prismatic continuation points to a foundational Linear slice, but current topology makes a safe implementation contract premature.

## Trigger

- User asks to continue a named Prismatic foundational steering packet or next Linear slice.
- The slice appears unblocked in Linear, but repository topology or preserved checkpoints introduce an implementation-contract hazard.
- Especially relevant when a new canonical authority is supposed to eliminate duplicate paths, but current merged code still has an older direct path.

## Pattern

1. Bind the exact Linear source and relations.
   - Export/read the bounded parent issue or description through the approved Linear read path.
   - Record issue state, blockers, children, updated timestamp, description hash, and upstream contract hashes.
2. Bind the exact merged base/tree.
   - Verify current `origin/main` commit and tree.
   - Inspect existing authority modules and old adapters before writing any task contract.
3. Search for duplicate-authority hazards.
   - Existing direct execution paths, old CLIs, legacy queues, extra DBs, old receipt identities, mutable `last_run_at`/status fields, direct hook execution, or process spawns outside the intended new authority.
4. Check preserved dirty/recovery checkpoints at the same base.
   - If the next slice needs paths modified by a preserved interrupted checkpoint, do not start a new implementation worktree/task that overlaps them.
5. Freeze a **precontract blocker** instead of an implementation contract when overlap or duplicate authority would violate acceptance.
   - Include exact current topology, why admission is unsafe, allowed resolution states, future finite boundary, adversarial acceptance matrix, rollback/non-claims, and zero-event proof.
6. Dispatch/read-only independent review of the blocker artifact.
   - Ask for `CLEAN/PASS` if the blocker classification is accurate and sufficient, otherwise the first precise artifact-only correction.

## Boundary language

A precontract blocker should say clearly:

```text
STATUS=FROZEN_PRECONTRACT_BLOCKED
AD_HOC_OR_CANONICAL=ad-hoc targeted read-only precontract inspection
NOT_CLAIMING=implementation contract freeze, admission readiness, event, producer, implementation, candidate, tests, review acceptance, PR, merge, deployment, cron/timer mutation, or Linear write
```

Do not call a precontract artifact admission-ready. Do not create a worktree, event, producer, PR, or Linear write from it.

## Prismatic cron-runner example

For `GRO-4317`, the safe blocker was: merged `native_crons.py` still directly executed commands via `run_native_cron`/`subprocess.run`, while preserved `CRONENFORCE` recovery also modified `native_crons.py`. Starting the runner would either retain a second process authority or overlap/launder the preserved dirty checkpoint. The safe next gate was to complete/merge the recovery or freeze a separately reviewed absorption contract before any runner implementation admission.
