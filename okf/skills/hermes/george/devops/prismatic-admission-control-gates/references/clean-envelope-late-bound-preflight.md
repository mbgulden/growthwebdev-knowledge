# Clean admission envelope with late-bound freshness

Use this reference when a reviewed Prismatic task is tracked-clean and should pass ordinary deployed admission, but the envelope still needs a zero-mutation proof before any event POST or producer launch.

## Durable pattern

1. Bind immutable identity:
   - task id;
   - base commit and base tree;
   - task file path and SHA256;
   - producer identity;
   - exact worktree path;
   - writer cap.
2. Derive a stable idempotency key from frozen identity only. Do **not** include `created_at`; freshness must not change event identity.
3. Freeze an envelope JSON template with exactly one sentinel for `created_at` and no other late-bound fields.
4. Before any future POST, substitute a current UTC whole-second timestamp and immediately run deployed parser/policy/Git/task validation on that exact payload.
5. If the freshness window expires before POST, generate a new timestamp and rerun the whole zero-mutation preflight. Change no other field.

## Disposable preflight setup

Deployed policy loaders may reject unsafe policy files before task validation. Use owner-only temporary paths:

```text
TEMP_DIR_MODE=0700
TEMP_POLICY_MODE=0600
DISPOSABLE_DB=true
LIVE_POST=false
LIVE_DB_MUTATION=false
```

If preflight fails with a policy safety error before task validation, classify it as verifier setup only, correct the disposable setup, and rerun from the beginning. Do not call it task incompatibility unless deployed validation reaches the task and rejects the task shape.

## Envelope proof checklist

```text
ENVELOPE_SHA256=<sha>
ENVELOPE_LINES=<n>
ENVELOPE_BYTES=<n>
JSON_BLOCK_COUNT=1
LATE_BOUND_SENTINEL_COUNT=1
DEPLOYED_TEMPLATE_VALIDATION=PASS
TASK_ADMISSIONS_COUNT=0
TASK_ADMISSION_OUTBOX_COUNT=0
TASK_ADMISSION_CONSUMER_CLAIMS_COUNT=0
TASK_ADMISSION_LIFECYCLE_COUNT=0
WRITER_LEASE_COUNT=0
SELECTABLE_OUTBOX=0
NO_POST_VERIFIER_MUTATION=true
```

## Boundary language

The envelope is descriptive until independently reviewed and separately authorized. It must explicitly not claim or authorize event POST, consumer, producer, source edit, commit, candidate acceptance, canonical green, push, PR, merge, deploy/restart, cron/timer mutation, production database mutation, credential mutation, or Linear write.
