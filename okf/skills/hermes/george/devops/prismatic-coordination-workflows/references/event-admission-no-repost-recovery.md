# Event admission no-repost recovery pattern

Use when a Prismatic task has been authorized for bounded event admission through the authenticated gateway, and any setup/launch error occurs mid-transaction.

## Durable rule

Never repost after an ambiguous admission/consumer failure until the durable outbox proves zero matching event rows. If exactly one event exists, recover/consume that existing event; do not create a successor event to make the workflow look clean.

## Pre-admission checks

- Validate the task ID against the deployed schema before writing bus/worktree copies. Avoid human-readable suffixes that violate the deployed regex.
- Bind to the actually deployed gateway surface. Prefer systemd/process configuration and a live route proof over a generic `/healthz` endpoint; `/healthz` may belong to a proxy/sidecar and can be stale or undefined for a gateway release.
- Read deployed private schemas before building temporary config:
  - policy key set may gain additional required keys;
  - launcher schema may use `producer`/`command` rather than guessed `executable`/`argv`;
  - credential records may require fields such as `roles`;
  - timestamp parsers may require whole-second `YYYY-MM-DDTHH:MM:SSZ` with no fractional seconds.
- Keep temporary config/credential creation inside the same `try/finally` restoration envelope as policy/control mutations so setup failures still restore private bytes.

## Admission request contract

- Use the deployed authenticated port/header names, not previously successful defaults.
- Include the idempotency/admission-context header required by the route; missing context can yield auth-passed/route-failed `401` before persistence.
- Parse the deployed response shape. Coordinates may be nested under `record`, not top-level.
- Treat consumer terminal status according to the live enum (`processed` may be canonical rather than `completed`). Verify against DB tables/columns rather than assuming names like `attempts` or `state`.

## Failure handling sequence

1. Stop immediately after any nonzero transaction.
2. Prove restoration of private policy/control/config bytes.
3. Query durable event/outbox rows for the exact task/event key.
4. If zero rows exist, repair setup and retry only the original authorized admission.
5. If one row exists and is pending/unclaimed, create a no-POST recovery consumer that:
   - has zero HTTP/POST sites;
   - opens only the required temporary producer/worktree policy/config;
   - uses deployed consumer CLI flags;
   - consumes the existing event exactly once;
   - restores all private bytes in `finally`.
6. If a producer launches, attach a receipt-bound passive wait; do not poll or kill just because it is long-running.
7. After completion, reconcile exact commit/tree, process cleanup, receipt, lifecycle rows, and single-event/no-repost proof before reproduction/review.

## Proof packet fields

```text
TASK_ID=<schema-valid id>
EVENT_COUNT=1
REPOSTED=false
CLAIM_ATTEMPT=<n>
CONSUMER_STATUS=<live enum>
PRODUCER_SLOT=<id>
POLICY_RESTORED=true
TEMP_CONFIGS_REMOVED=true
REMOTE_OR_LOCAL_SURFACE=<systemd-proven route/port>
AD_HOC_OR_CANONICAL=ad-hoc targeted admission proof
NOT_CLAIMING=merge, deploy, canonical full-suite green, or unrelated runtime mutation
```

## Pitfalls seen

- Wrong gateway port can return method errors before admission; do not infer task failure from the wrong surface.
- Credential-loader failures can fail closed before auth and leave no event; validate temporary credentials through the deployed loader before POST.
- Fractional timestamps can fail freshness validation even when logically fresh.
- A transaction can succeed in admission and fail only because the local assertion expected the wrong status enum; never repost until DB reconciliation decides.
- Consumer CLI flags drift; if an event exists, recover the same event with current flags instead of posting a duplicate.