# Bounded repair prompt admission after a blocked exact-head review

Use this when a Prismatic candidate is preserved as BLOCKED and Michael authorizes the same-task repair.

## Coordination rule

Do not jump directly from authorization to producer launch. First create a frozen repair prompt/task that converts the review finding into a finite contract, then independently review that exact task before event admission.

## Prompt/task requirements

- Name the blocked checkpoint commit/tree and require it remain immutable.
- Require a new commit, no amend/reset/rewrite of the blocked checkpoint.
- Bind to normative artifacts and their SHA-256 when the repair depends on contract language.
- Keep allowed writes narrow and path-explicit.
- State forbidden side effects: deployment, live cron/timer mutation, Linear writes, DB/network mutation, production source changes when out of scope.
- Include verification commands, archive reproduction, invariance proof, log paths/digests, and explicit non-claims.
- Require fresh exact-head independent `CLEAN/PASS` before PR/merge.

## Pre-admission proof packet

```text
TASK_SHA256=<sha256>
TASK_COPY_MATCH=true
BASE_CHECKPOINT_PRESERVATION=true
ALLOWLIST_BOUNDED=true
MUTATION_BOUNDARIES_PRESENT=true
TASK_REVIEW=<delegation-id>:pending|CLEAN/PASS|BLOCKED
REPAIR_EVENT_COUNT=0
ACTIVE_SLOT_COUNT=0
NOT_CLAIMING=task review acceptance, repair admission, producer launch, candidate acceptance, PR, merge, deployment, Linear write, or cron/timer mutation
```

## When review is pending

Report `PARTIAL`, not `PASS`. The next action is conditional: **if** exact task review returns `CLEAN/PASS`, admit exactly once and launch one cap-1 producer under the existing authorization.
