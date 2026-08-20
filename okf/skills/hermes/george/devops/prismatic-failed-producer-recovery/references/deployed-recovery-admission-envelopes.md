# Deployed Recovery Admission Envelopes

Session-derived pattern for preparing a second/recovery Prismatic admission after a failed producer, without admitting it prematurely.

## When to use

Use after a failed producer candidate is independently blocked, a same-worktree recovery contract has been iteratively reviewed, and the latest repair contract returns exact-artifact `CLEAN/PASS`.

## Sequence

1. **Preserve failed-producer truth first**
   - Keep original event count, failed run status, `producer_completed=false`, blocked candidate HEAD/tree, and candidate review blockers visible.
   - Never replay the original task/event identity.

2. **Create copied task files only after contract CLEAN/PASS**
   - Copy the accepted repair contract into both the bus task path and bound worktree `.prismatic-task/<TASK_ID>.md`.
   - Prove byte-identical SHA-256 against the reviewed contract.
   - Preserve the same blocked base HEAD/tree and tracked-clean state.

3. **Freeze an admission envelope as an artifact**
   - Freeze all authority-bearing fields: task id, base commit/tree, task file path/hash, producer identity, worktree, writer cap, status, and idempotency key.
   - If the deployed admission policy has a freshness window, make `created_at` the only late-bound field. State the sentinel and the substitution rule explicitly.
   - The stable idempotency key must not depend on late-bound `created_at`.

4. **Validate with deployed code and zero live mutation**
   - Use the actual deployed parser/validator release, not a reimplemented schema.
   - Use a disposable DB for `TaskAdmissionStore` or equivalent validation.
   - Narrow a temporary policy to the exact deployed policy shape. Do not invent policy keys that the deployed release does not load.
   - Prove schema parse, policy validation, Git HEAD/tree validation, task digest validation, and live repair event count zero.

5. **Separate policy truth from schema/task-binding truth**
   - If deployed policy only narrows producer/worktree, say exactly that.
   - Put task ID, writer cap, status, and task hash enforcement under deployed schema/task-binding validation, not under policy, unless the deployed policy actually enforces them.

6. **Review envelope before authorization**
   - Dispatch independent read-only review over copied task hashes, envelope hash/lines/bytes, deployed preflight log, late-bound field boundary, one-event/cap-1 rules, cleanup/finally restoration, and non-claims.
   - Stop for explicit authorization after review returns `CLEAN/PASS`.

## Freshness-window rule

If `created_at` expires before POST:

1. regenerate only `created_at`;
2. rerun the entire zero-mutation deployed preflight on the exact substituted bytes;
3. keep the idempotency key and every non-time field unchanged;
4. only then POST within the freshness window.

## Proof fields

```text
TASK_COPIES_SHA256=<sha>;byte_identical=true
ENVELOPE_SHA256=<sha>
LATE_BOUND_FIELD=created_at_only
IDEMPOTENCY_KEY=<stable key>
DEPLOYED_PREFLIGHT=PASS
DEPLOYED_RELEASE=<release>
DEPLOYED_PREFLIGHT_LOG=<path>
ORIGINAL_EVENT_COUNT=<n>
REPAIR_EVENT_COUNT=0
REPAIR_PRODUCER=false
ENVELOPE_REVIEW=<delegation>:pending|CLEAN/PASS|BLOCKED
NOT_CLAIMING=envelope acceptance, event, producer, implementation correctness, canonical suite, PR, merge, deploy, cron/timer, DB, credentials, Linear
```

## Pitfalls

- **Static timestamp in a freshness-gated envelope**: a permanently frozen `created_at` will age out. Freeze a template and make time the only late-bound field.
- **Policy overclaim**: do not state `POLICY_EXACT_MATCH=task_id+writer_cap` unless the deployed policy actually has those keys. Attribute those checks to schema/task validation when appropriate.
- **Preflight mutation leak**: deployed validation should use disposable storage. The live ledger must remain at repair event count zero until explicit authorization.
- **Reviewed-contract shortcut**: contract `CLEAN/PASS` authorizes copied-task/envelope preparation only, not event admission.
