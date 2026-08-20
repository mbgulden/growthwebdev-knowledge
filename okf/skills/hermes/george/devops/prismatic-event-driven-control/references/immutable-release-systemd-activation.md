# Immutable release systemd activation gate

Use this reference after a reviewed/merged Prismatic release is staged but not yet the live gateway runtime, and Michael explicitly authorizes the bounded deployment/restart.

## Activation sequence

1. **Restate the exact authorization boundary** before mutation: release SHA/tree, service name, no successor admission, no cap increase, no Linear writes, no legacy consumer/watchdog unmasking.
2. **Build/prove the versioned runtime first**:
   - release checkout is detached/immutable and has no `.git/objects/info/alternates`;
   - `git fsck --full` passes;
   - versioned venv exists for the release;
   - install declared runtime extras needed by the gateway, not only the base package;
   - run import/package/doctor probes from a neutral directory with `VIRTUAL_ENV`/`PYTHONPATH` unset.
3. **Write rollback before cutover**:
   - record current `systemctl show` provenance including `ExecStart`, `WorkingDirectory`, `MainPID`, `DropInPaths`;
   - capture health/dashboard/receipt response hashes;
   - capture read-only SQLite counts for admission/outbox/claim/lease/lifecycle tables;
   - write a rollback file that removes only the new drop-in, daemon-reloads, restarts gateway, and proves health.
4. **Apply a release-specific drop-in**:
   - set `WorkingDirectory` to the immutable release;
   - clear and replace `ExecStart` with the versioned venv python and gateway module;
   - set `PRISMATIC_RUNTIME_SERVICES_CONFIG` to the release's public runtime inventory;
   - quote any `Environment=` assignment whose value contains spaces so systemd receives one complete assignment;
   - keep generic consumer/watchdog services masked/disabled.
5. **Restart only the gateway with auto-rollback trap**. If health/provenance checks fail, remove the new drop-in, reload systemd, restart the prior gateway, and record rollback output.
6. **Run post-cutover proof**:
   - `systemctl show` loaded state, not just unit files on disk;
   - health/dashboard/receipts HTTP 200;
   - unauthenticated admission route fails closed (401 is acceptable/protective for unauthenticated probes);
   - DB counts are unchanged from pre-state;
   - exact merge SHA/tree match the immutable release;
   - legacy continuous consumer remains `masked,inactive` and watchdog timer remains `disabled,inactive`;
   - no producer/AGY process is active unless explicitly authorized.
7. **Write a deployment receipt and handoff update**, then run a final `/tmp/hermes-verify-*` no-mutation verifier over runtime provenance, receipt, rollback, DB preservation, containment, and cleanup.

## Proof packet shape

```text
RESULT=PASS
RELEASE=<immutable release path>
MERGE_SHA=<merge sha>
MERGE_TREE=<tree sha>
VENV=<versioned venv>
DROPIN=<systemd drop-in>
WORKING_DIRECTORY=<loaded systemd working directory>
HEALTH_HTTP=200
DASHBOARD_HTTP=200
RECEIPTS_HTTP=200
ADMISSION_ROUTE_UNAUTHENTICATED=fail-closed
DB_COUNTS_PRESERVED=true
PRISMATIC_CONSUMER=masked,inactive
PRISMATIC_WATCHDOG_TIMER=disabled,inactive
ROLLBACK=<path>
DEPLOYMENT_RECEIPT=<path>
NOT_CLAIMING=successor admission, producer launch, Linear write, cap increase
MARKER=<production closeout marker>
```

## Pitfalls

- A staged release is not active until loaded `systemctl show` proves the gateway is running from that release and venv.
- Base package install success is not enough for gateway activation; install and prove declared runtime extras before touching systemd.
- Do not trust base unit-file contents when drop-ins exist. `systemctl show`/`systemctl cat` and `DropInPaths` are authoritative.
- Treat unauthenticated `401` on protected admission routes as a valid fail-closed presence proof; do not send real admission credentials unless the task admission itself is authorized.
- Clean temporary drop-in/body files before the final verifier; keep durable pre/post/rollback/receipt artifacts under the deployment directory.
- If the deployment also closes a failed-producer recovery, record canonical acceptance through the harness/API path after live proof and verify the canonical readback. Do not directly edit run JSON/SQLite as the acceptance mechanism.
