# Deployed admission contract drift and running repair proof

Use this reference when an already-reviewed Prismatic repair/successor task must be admitted through the live authenticated event gate, but deployed runtime behavior differs from older scripts, assumptions, or review packets.

## Durable lessons

1. **Validate against the deployed parser before review/admission.**
   - A task can be semantically good but invalid for the live admission schema.
   - Run a deployed-schema payload validation before considering any task-contract review fresh.
   - If a reviewer misses a deployed schema constraint, mark that review stale and re-freeze/re-review the schema-valid envelope.

2. **Discover runtime coordinates from the live service, not old one-shot scripts.**
   - Use systemd-loaded provenance (`ExecStart`, `WorkingDirectory`, env/drop-ins) to identify the real gateway port and immutable release.
   - Wrong HTTP surfaces can return plausible health/405 responses; do not treat those as admission route proof.

3. **Control-auth and payload freshness are part of the contract.**
   - Validate temporary credential documents through the deployed credential loader before POST.
   - Include all deployed-required credential fields such as roles.
   - Format `created_at` exactly as the deployed parser requires; in this session it required whole-second UTC `YYYY-MM-DDTHH:MM:SSZ`, not fractional seconds.

4. **Admission context, response shape, and launcher schema can drift too.**
   - Route-level context may require an idempotency/admission header even after control authentication passes.
   - Successful response coordinates may be nested under `record`; parse the deployed response model instead of expecting top-level fields.
   - Producer source config may use legacy `producer` keys plus a single-executable `command` array, not `executable`/`argv`.
   - Consumer invocation flags can change (`--policy`/`--identity` in the R2 recovery); inspect the deployed CLI before recovering an already-persisted event.

5. **Reconcile before retrying.**
   - After any nonzero local wrapper, read event-scoped SQLite state before another POST.
   - If the event persisted and consumer ran, do not repost. Treat wrapper response-shape mismatches as local closeout defects.
   - Canonical consumer completion may be `status=processed`, not older assumed `state=completed` / `status=completed` shapes.

6. **Running producers can legitimately advance HEAD.**
   - For an active repair producer, final running-state proof should not assert the worktree HEAD is still the blocked base.
   - Assert the blocked checkpoint is an ancestor, the task hash/event are bound, tracked status is clean, and the producer/passive wait are alive.
   - Treat any new HEAD as provisional until terminal result, reproduction, and independent exact-head review pass.

7. **Receipt-bound passive wait.**
   - Attach one PID-based passive wait (`tail --pid=<pane_pid> -f /dev/null`) with notify-on-complete.
   - Do not poll, set inactivity deadlines, or kill the producer.
   - Resolve `RESULT.md` via the canonical `harness-run.json` / receipt `result_path`, not by guessing the launch directory.

## Proof skeleton

```text
TASK_ID=<schema-valid task id>
TASK_SHA256=<sha256 of frozen TASK.md>
TASK_REVIEW=<deleg id>:CLEAN/PASS
EVENT_COUNT=1
REPOSTED=false
OUTBOX=processed
CLAIM=completed
ATTEMPT=1
CONSUMER_STATUS=processed
LAUNCH_ID=<receipt-bound launch id>
PRODUCER_RUNNING=true
PROVISIONAL_HEAD=<current head while running>
BLOCKED_CHECKPOINT_IS_ANCESTOR=true
TRACKED_STATUS_CLEAN=true
POLICY_CONTROL_RESTORED=true
TEMP_CONFIGS_REMOVED=true
PASSIVE_WAIT=<process session id>
NOT_CLAIMING=producer completion, candidate correctness, review acceptance, PR, merge, deployment, Linear write, cron/timer mutation, or canonical full-suite green
```

## Boundary language

Say explicitly:

- setup failures before persistence are not durable event attempts;
- the only persisted event is the event-scoped SQLite row proven by readback;
- a running/provisional commit is not an accepted candidate;
- no PR/merge/deploy/Linear write follows until terminal result, local reproduction, and fresh independent exact-head review pass.
