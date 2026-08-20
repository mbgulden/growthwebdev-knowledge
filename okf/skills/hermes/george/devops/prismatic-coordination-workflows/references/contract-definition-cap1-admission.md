# Contract-definition-only cap-1 admission pattern

Use this when Michael authorizes a Prismatic task that must define a normative contract before any implementation work begins.

## Durable lesson

A contract-definition slice should be admitted like ordinary Prismatic work, but with a narrower write and authority boundary than implementation tasks. The handoff/prompt must prevent the producer from using the contract task as implicit authorization to mutate runtime, schemas, transports, Linear, deployment, or successor tasks.

## Required shape

1. Bind the task to the exact accepted base commit/tree and the upstream accepted artifact it extends.
2. State the authorization boundary up front: **contract definition only, no implementation**.
3. Name exactly one authorized repository path for the normative document.
4. Require repository investigation before selecting durable authority; do not let the producer invent authority that current code does not support.
5. Require RFC-style `MUST` / `MUST NOT` / `SHOULD` language and explicit sections for:
   - scope/non-goals;
   - terminology/versioning;
   - trigger envelope;
   - execution identity;
   - state machine;
   - fenced claim/lease semantics;
   - canonical durable authority;
   - admission/policy rejection;
   - catch-up/replay/idempotency;
   - migration/backup/restore;
   - security/evidence;
   - canary acceptance matrix;
   - implementation slices and unresolved decisions.
6. Require a disposable `/tmp/hermes-verify-*` verifier that fails unless the exact sections, key fields, outcomes, uniqueness tuple, authority/transaction language, canary cases, no TODO markers, one-path scope, and `git diff --check` all pass.
7. Commit the documentation candidate only; no push, PR, merge, deploy, restart, Linear mutation, runtime/config mutation, or successor admission without separate authorization.

## Admission proof checklist

```text
TASK=<Linear task id>
MODE=contract-definition only
BASE_COMMIT=<exact commit>
BASE_TREE=<exact tree>
BRANCH=<producer branch>
WORKTREE=<clean worktree>
ALLOWED_WRITE=<single doc path>
TASK_SHA256=<task prompt hash>
EVENT_ID=<dashboard admission event>
CLAIM_ID=<consumer claim id>
LAUNCH_ID=<producer launch id>
OUTBOX_STATUS=processed
CLAIM_STATE=completed
WRITER_LEASES=0
POLICY_RESTORED=true
TEMP_CONFIGS_REMOVED=true
NOT_CLAIMING=contract completion, implementation, source mutation beyond allowed path, push, PR, merge, deployment, Linear update, successor admission
```

## Pitfalls

- Consumer `completed` means the launch completed, not that the producer finished the work.
- Do not report contract acceptance until the committed artifact has been checked for the one-path scope and independently reviewed.
- Keep transport separate from semantic trigger kind in trigger/outcome contracts; delivery mechanism must not become uniqueness identity unless the contract explicitly says so.
- If the repository lacks a current durable authority satisfying the contract, document the gap and minimum future authority requirements rather than inventing one.
