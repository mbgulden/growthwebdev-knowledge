# Repair authorization with pre-admission task review

Use this pattern when Michael authorizes a bounded Prismatic repair after an exact-head review blocks a candidate, but the repair task itself has not yet been independently reviewed.

## Lesson

Authorization to proceed with a repair is not the same as permission to skip task-contract quality gates. Treat the authorization as conditional on a frozen, byte-bound repair task returning pre-admission `CLEAN/PASS`.

## Sequence

1. Re-read the blocked checkpoint and prove it is stable:
   - `HEAD` equals blocked commit.
   - tree equals blocked tree.
   - tracked status is clean.
2. Prove no successor/repair event already exists:
   - task-specific event count is zero.
   - selectable outbox is zero.
   - writer leases are zero.
   - active cap slots are zero.
3. Freeze an event-consumable repair `TASK.md` with:
   - parent task and Linear issue;
   - base commit/tree and blocked checkpoint/tree;
   - normative contract artifact hash;
   - allowed write paths;
   - explicit forbidden mutations;
   - required verification and completion packet.
4. Copy the task into the worktree task envelope, then hash both copies and prove parity.
5. Validate the intended admission payload against the **deployed** task-admission parser/schema, not just the task prose. Include `task_id`, `task_file`, task SHA, base commit/tree, producer identity, worktree, writer cap, idempotency key, `created_at`, and `status=admitted`.
6. Run a local freeze verifier over task hash, base/tree, allowlist, boundaries, deployed-schema result, and marker.
7. Dispatch independent task-contract review bound to the exact task SHA and explicitly tell the reviewer to check deployed-schema admissibility.
8. Update handoff/control state as `REPAIR_TASK_PRE_ADMISSION_REVIEW_PENDING` with `EVENT_COUNT=0` and `REPAIR_LAUNCHED=false`.
9. Only if the task review returns exact `CLEAN/PASS` for the current bytes and deployed-schema-valid ID, admit the repair once through the authenticated event gate and launch one cap-1 producer.

## Required state packet before admission

```text
REPAIR_AUTHORIZED=true
TASK_FREEZE=PASS
DEPLOYED_SCHEMA_VALIDATION=PASS
TASK_REVIEW=<delegation-id>:pending|CLEAN/PASS|BLOCKED
STALE_TASK_REVIEW=<delegation-id>:CLEAN/PASS:<why-invalidated, if any>
REPAIR_TASK_SHA256=<sha256>
R1_EVENT_COUNT=0
ACTIVE_SLOT_COUNT=0
SELECTABLE_EVENTS=0
WRITER_LEASES=0
CHECKPOINT_STABLE=true
TRACKED_STATUS=clean
NOT_CLAIMING=task review acceptance, repair admission, producer launch, candidate acceptance, PR, merge, deployment, Linear write, or cron/timer mutation
```

## Pitfalls

- Do not post the event just because Michael said “I authorize the repair/cron export.” First freeze and independently review the exact task contract unless that review already exists.
- Do not mutate the blocked candidate while preparing the repair task. Use an out-of-repo task store and untracked worktree task envelope.
- Do not let a pending task review become an acceptance claim. Report `PARTIAL` until the review returns.
- Keep the old blocked checkpoint intact and name it explicitly in the repair task; repairs create a new commit, never amend/reset the blocked one.
- A semantically clear repair ID can still be inadmissible. The deployed schema may require a single-hyphen `<PREFIX>-<NUMBER>` shape; IDs like `CRONEXPORT-1-R1` must be caught before event POST. If a pre-admission reviewer returns `CLEAN/PASS` but missed deployed-schema admissibility, mark that review stale/invalidated, port the exact contract to a compliant internal ID, rehash, and rerun the review before admission.
