# Terminal Producer Closeout and Existing-Event Retry

Use when a cap-1 event-admitted Prismatic producer is launched through the dashboard/event gate, the initial consumer invocation fails before producer launch, or a closeout verifier races with producer completion.

## Pattern

1. **Classify launch failure event-scoped, not globally.** Read the exact `task_id`/`event_id` rows in SQLite (`task_admissions`, `task_admission_outbox`, `task_admission_consumer_claims`, lifecycle rows). Do not count historical claims globally and do not repost just because a wrapper assertion or local script failed.
2. **Preserve attempt history.** If attempt 1 failed before launch, report it as a blocked checkpoint (`retryable_failed`, `producer_launched=false`) rather than hiding it after repair.
3. **Repair dependencies outside the event.** Restore policy/control-auth/temp configs first; then fix the invocation/config/wrapper defect. The common durable shape for AGY consumers is one canonical regular executable wrapper, not a symlink plus `-m` argv bundle.
4. **Retry the existing event once.** Invoke the consumer against the persisted retryable event; do not POST a duplicate admission unless event-scoped proof shows no durable side effects.
5. **Bind launch proof to receipts.** Use `launch-receipt.json`, `harness-run.json`, `activity.json`, active slot path, and receipt-bound tmux/session identity. Do not guess status import paths or tmux names.
6. **If producer completes during closeout, switch states.** A verifier expecting `RUN_STATUS=running` can become stale while running. Read `harness-run.json`, `process-result.json`, and `RESULT.md`; if `exit_code=0` and process-tree cleanup is verified, update the handoff to `completed` / `review_pending` and dispatch exact-head review.
7. **Validate live request/response and launcher shapes before recovery.** When a one-shot admission or recovery utility is rebuilt, read the deployed route/config contract directly. Durable R2-specific pitfalls: admission may require an idempotency/admission-context header; successful admission coordinates may be nested under `record`; source configs may use legacy `producer` keys and a single regular-executable `command` array rather than `executable`/`argv`; consumer CLI flags may be `--policy`/`--identity`, not older local assumptions.
8. **Final closeout is no-mutation.** Verify policy restored, control auth restored, temp configs removed, gateway health/provenance, outbox processed, writer leases zero, and no live cron/schema mutation. Label this as targeted/ad-hoc unless the canonical suite ran.

## Proof packet skeleton

```text
TASK_ID=<task>
EVENT_ID=<event id>
ATTEMPT1=<retryable_failed|blocked reason>
ATTEMPT2=<completed|state>
CLAIM_ID=<claim>
LAUNCH_ID=<run id>
PRODUCER_STATUS=<running|completed>
PRODUCER_EXIT=<0|nonzero|n/a>
PROCESS_TREE_CLEANUP_VERIFIED=<true|false|n/a>
POLICY_RESTORED=<true|false>
CONTROL_AUTH_RESTORED=<true|false>
TEMP_CONFIGS_REMOVED=<true|false>
SELECTABLE_OUTBOX_EVENTS=<count>
WRITER_LEASES=<count>
NOT_CLAIMING=review acceptance, PR, merge, Linear write, cron installation, or live schema migration
```

## Pitfalls

- Do not repost an admission because a response-shape assertion failed after the event persisted.
- Do not assume the live gateway/admission API uses the same helper-script schema as the last slice. Missing idempotency/admission-context headers can produce pre-persistence auth/context errors; nested response coordinates, launcher `command` arrays, and consumer CLI flags must be discovered from the deployed runtime before retrying an existing event.
- Do not claim producer completion from `CLAIM_STATE=completed`; claim completion only from the harness/process/result artifacts.
- Do not keep a stale `running` handoff after terminal artifacts show exit `0`; transition to `review_pending` and require independent exact-head review.
- Do not expose control-auth paths or credential material in chat; prove restoration structurally and with redacted/key-assembled checks when sanitizer masking interferes.
