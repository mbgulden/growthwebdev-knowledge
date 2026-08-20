# Frozen contract before admission

Use this pattern when Michael asks for the next Prismatic slice but explicitly says **do not deploy**, **do not admit another producer**, or asks to freeze a bounded implementation contract first.

## Trigger
- A prior reviewed/merged candidate exposed a wider production trust gap.
- The next move is to define the implementation contract, not to launch AGY/Fred/Ned or create a PR.
- User wording includes boundaries like “Do not deploy or admit another producer yet” or requires a finite contract for production-owned code, workflow integration, adversarial tests, clean archive proof, and independent review.

## Procedure
1. **Bind to the exact current base first**
   - Confirm the intended merged base commit/tree from the repository before writing the contract.
   - Include both in the contract and handoff.

2. **Map existing production surfaces before drafting**
   - Identify the real production-owned modules/scripts and existing workflow entry points.
   - Require reconnection to those surfaces instead of a parallel/fallback path.
   - Distinguish production authority/runtime modules from mutable state files or test helpers.

3. **Freeze a finite contract, not a task launch**
   - Write a contract prompt that explicitly says it authorizes no task envelope, branch/worktree, event admission, producer launch, PR, merge, deploy/restart, cron/timer mutation, or Linear write.
   - If a future task id is named, validate it against the deployed admission schema, but do not create the event-consumable envelope unless separately authorized.

4. **Contract must close the trust gap in production code**
   - Require production-owned classifier/validator code, with tests calling that production code rather than duplicating the decision logic.
   - Require intended workflow integration, e.g. installer/export path wiring, not only standalone tests.
   - Require fail-closed behavior for missing/empty/malformed/partial/stale/mismatched evidence.
   - Require provenance, freshness, canonical bytes, descriptor/symlink/race/mode/owner checks, and strict boolean provenance when evidence is security-sensitive.
   - For security provenance contracts, draw the digest/dependency graph explicitly and reject cycles before admission. A common safe pattern is: exact binding bytes -> manifest binding hash -> manifest digest -> downstream rendered command. Do not put the downstream rendered command, release digest, or manifest hash back into any manifest-hashed input.
   - Separate runtime-recomputable facts from recorded release identities. Recompute only from descriptor-bound bytes actually available to the runtime validator (config, executable, lock, binding, etc.). If runtime evidence lacks a Git object database, do not require or claim independent recomputation of Git tree OIDs; instead require exact recorded equality between manifest/binding and bind merge commit through path/manifest/binding/rendered-hook identities.

5. **Make verification gates explicit**
   - Focused production/integration tests.
   - Canonical project suite from a clean exact-head archive.
   - Installed-state invariance around the entire verification sequence.
   - Independent exact-head review must return `CLEAN/PASS` before PR creation.

6. **Run a detector-shaped freeze proof**
   - Hash and line-count the contract.
   - Prove base/tree binding.
   - Prove future task id schema validity if present.
   - Prove zero event count, no task envelope, no worktree, no branch, no producer, no PR.
   - Update handoff with the frozen contract path/hash and review status.

7. **Optional but preferred: read-only contract review**
   - Dispatch a read-only independent review of the contract only.
   - The reviewer must be forbidden to edit files, admit events, create branches/PRs, launch producers, deploy, mutate cron/timers, or write Linear.

## Proof packet shape

```text
COMMAND=<contract hash/readback + zero-admission detector>
RESULT=PASS
LOG=<path>
SCOPE=frozen contract only
AD_HOC_OR_CANONICAL=ad-hoc targeted contract-freeze readback
CONTRACT_SHA256=<sha256>
BASE=<commit>
TREE=<tree>
FUTURE_TASK_ID=<id or none>
SCHEMA_VALID=<true|n/a>
EVENT_COUNT=0
TASK_ENVELOPE_CREATED=false
WORKTREE_CREATED=false
BRANCH_CREATED=false
PRODUCER_LAUNCHED=false
NOT_CLAIMING=implementation, admission, producer, tests executed, candidate, review acceptance, PR, merge, deployment/restart, cron/timer mutation, or Linear write
MARKER=<slice>_CONTRACT_FROZEN_OK
```

## Pitfalls
- Do not treat a contract hash as implementation acceptance.
- Do not create the event-consumable task envelope while “do not admit” is in force.
- Do not launch a producer merely because the future task id is schema-valid.
- Do not let tests own the security classifier; tests should prove production-owned code.
- Do not claim canonical suite green from a contract-freeze proof; no implementation was tested.
- If a schema probe fails, inspect required fields and validate the probe shape; do not infer the future task id is invalid without reading the schema.
- Do not encode mutual digest dependencies. If manifest hashes binding and binding contains the manifest/release digest, the contract is infeasible even if each individual field sounds useful.
- Do not overclaim Git identity at runtime. Without Git object evidence, a validator can compare recorded source-tree fields but cannot independently recompute the tree object ID from ordinary release files.
- When a contract review blocks, preserve the blocked version/hash and freeze a new versioned artifact; do not silently edit the same contract and continue as if the prior review had passed.
