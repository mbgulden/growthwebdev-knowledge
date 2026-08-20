# Internal repair event zero-state gate

Use this reference when an exact-head candidate is blocked after successful producer completion and the minimum repair needs a new same-worktree task/event identity without replaying the original event.

## Pattern

1. **Preserve the blocked checkpoint first**
   - Record both independent review verdicts and the first real blocker.
   - Bind blocked `HEAD`, tree, tracked cleanliness, original event count, active slot count, and writer lease count.
   - State that the original event is not being replayed.

2. **Reserve an internal repair identity, not a fake Linear issue**
   - Use a gateway-schema-compliant internal task id such as `GROREPAIR-4275` when the real Linear issue remains `GRO-4275`.
   - In the task header, explicitly separate:
     - `TASK_ID=<internal repair event identity>`
     - `LINEAR_ISSUE=<real Linear issue>`
     - `TASK_ID_KIND=internal_repair_event_identity`
   - Do not imply that the internal task id exists in Linear.

3. **Validate the future admission payload against deployed code**
   - Review the Markdown contract is not enough. Construct a disposable payload with the intended `task_id`, `task_file`, worktree, base commit/tree, idempotency key, and task hash.
   - Run the deployed parser/validator against disposable SQLite/policy storage.
   - If production policy has already been restored and rejects the repair worktree, that is expected. Validate schema/Git/task-hash under a disposable narrow policy and prove production policy hash is unchanged.
   - Keep `created_at` late-bound if the deployed freshness window is short.

4. **Prove zero live state before review and before any launch**
   - Future repair event count is zero in `task_admissions`, outbox, claims, and lifecycle.
   - Original event count remains exactly one.
   - Active slot count is zero.
   - Writer lease count is zero.
   - Task copies are byte-identical to the reviewed repair contract.

5. **Stop at task review, then envelope review, then explicit authorization**
   - A clean repair task review does not authorize a POST.
   - The one-shot admission envelope and launcher remain separate executable artifacts.
   - Before POST, require unambiguous authorization for exactly one cap-1 repair event and preserve non-claims.

## Pitfalls

- Do not mutate the blocked candidate in place before the repair task and envelope gates are reviewed.
- Do not replay the original task/event to repair a blocked candidate.
- Do not use production policy mutation as schema validation proof; disposable narrow policy is sufficient for schema/Git/task-hash checks, but live policy must remain unchanged.
- Do not hide the distinction between the internal repair id and the Linear issue id.
- If logs/chat masking affects literal boolean display such as `EVENT_POST_AUTHORIZED=false`, parse key/value fields in disposable verifiers rather than embedding sanitizer-sensitive literals.

## Proof fields

```text
EXACT_HEAD_REVIEW=<delegation>:BLOCKED
BLOCKER=<first real blocker>
BLOCKED_COMMIT=<sha>
BLOCKED_TREE=<tree>
ORIGINAL_EVENT_COUNT=1
ORIGINAL_EVENT_REPLAY=false
REPAIR_TASK_ID=<internal id>
TASK_ID_KIND=internal_repair_event_identity
LINEAR_ISSUE=<real issue>
REPAIR_TASK_SHA256=<sha256>
TASK_COPY_PARITY=true
DEPLOYED_SCHEMA_VALIDATION=PASS_disposable_narrow_policy
PRODUCTION_POLICY_UNCHANGED=true
REPAIR_EVENT_COUNT=0
ACTIVE_SLOT_COUNT=0
WRITER_LEASE_COUNT=0
EVENT_POST_AUTHORIZED=false
REPAIR_LAUNCHED=false
NOT_CLAIMING=repair task acceptance,event authorization,repair launch,candidate acceptance,canonical suite,PR,merge,deployment,Linear mutation
```
