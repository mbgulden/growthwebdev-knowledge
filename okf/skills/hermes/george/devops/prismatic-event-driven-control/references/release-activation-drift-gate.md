# Release activation drift gate

Use when a Prismatic slice is merged and a durable release checkout exists, but the next event-driven admission depends on the runtime actually serving that merged code.

## Trigger

- A merge/release proof exists, but `DEPLOYED=false` or the live gateway may still point at an older release.
- Dashboard/admission routes are reachable, but successor admission would depend on behavior from the newly merged slice.
- Systemd state appears inconsistent across the base unit, loaded unit, and handoff/deployment receipts.

## Read-only provenance checks before any successor admission

```bash
systemctl show prismatic-gateway.service \
  -p MainPID -p ExecMainStartTimestamp -p ExecStart -p WorkingDirectory -p FragmentPath -p DropInPaths -p NeedDaemonReload \
  --no-pager
systemctl cat prismatic-gateway.service --no-pager
systemctl is-active prismatic-gateway.service
systemctl is-enabled prismatic-consumer.service; systemctl is-active prismatic-consumer.service
systemctl is-enabled prismatic-watchdog.timer; systemctl is-active prismatic-watchdog.timer
git -C /home/ubuntu/.prismatic/releases/<expected-short-sha> rev-parse HEAD 'HEAD^{tree}'
```

Interpretation:

- The loaded `ExecStart`/`WorkingDirectory` from `systemctl show` is authoritative for the currently running gateway.
- `/etc/systemd/system/prismatic-gateway.service` alone is not authoritative when drop-ins exist.
- With stacked drop-ins, the final applicable override wins; `systemctl cat` is the fastest way to explain why a loaded release differs from the base unit file.
- `NeedDaemonReload=no` means systemd has consumed the unit/drop-in files; it does not mean the latest merged source has been activated.

## Gate decision

If live `WorkingDirectory`/venv do not match the newly merged release:

```text
STATUS=AUTHORIZATION_POINT
REASON=merged_release_staged_but_not_activated
NEW_TASK_ADMITTED=false
PRODUCER_LAUNCHED=false
DEPLOYMENT_REQUIRED=true
```

Do not admit the successor task yet. Ask for explicit immutable deployment authorization limited to:

1. Build/version the gateway venv for the exact release.
2. Add the next systemd release drop-in.
3. `daemon-reload` and restart gateway.
4. Prove exact `ExecStart`, `WorkingDirectory`, health, dashboard/admission route, rollback readiness.
5. Preserve legacy consumer masked/inactive, watchdog disabled/inactive, and producer cap unchanged.

## Reporting shape when user asks for only exceptions/authorization points

Keep the report terse and omit routine proof narrative. Emit only:

- `Exception` if a dependency prevents admission.
- `Authorization point` if the next safe step has side effects.
- A compact proof block with exact release, live release, queue/producer state, and non-claims.
