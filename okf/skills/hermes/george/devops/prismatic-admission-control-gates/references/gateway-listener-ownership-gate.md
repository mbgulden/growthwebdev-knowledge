# Gateway listener ownership gate

Use this reference when a Prismatic admission launcher posts to a local gateway/service and prior proof only established expected files, imports, systemd state, or health. Those checks are necessary but not sufficient: the POST target might be served by a different/stale process or an ambiguous/reuse-port listener.

## Failure signal

A review should block a launcher if it proves any of these separately but never binds them together:

- deployed source hash/import path;
- `systemctl MainPID` process identity;
- HTTP health response;
- local POST port availability.

The minimum safe gate is: the exact `MainPID` process must own the exact socket inode that is listening on the POST port, and that binding must remain stable after the health check.

## Required read-only checks before credentials/policy open

1. Read `ActiveState` and `MainPID` with `systemctl show ... --value --no-pager`; require active and positive PID.
2. Resolve `/proc/<pid>/exe`, `/proc/<pid>/cwd`, and `/proc/<pid>/cmdline`; compare to the exact expected venv, release directory, module, host, port, and log-level command line.
3. Parse both `/proc/net/tcp` and `/proc/net/tcp6`:
   - inspect only rows with state `0A` (`LISTEN`);
   - decode the local-address port from hex;
   - collect matching rows for the POST port;
   - require exactly one matching listener;
   - require a positive decimal socket inode.
4. Inspect `/proc/<pid>/fd` symlinks and collect `socket:[<inode>]`; require the listener inode from step 3 to be present.
5. Perform the bounded health request.
6. Repeat steps 1-4 after health and require:
   - same `MainPID`;
   - same executable/cwd/cmdline;
   - same sole listener inode;
   - same inode still owned by that PID.

Only after all checks pass should the launcher open temporary credentials/policy or POST an event.

## Pitfalls

- A healthy response alone does not prove the event POST will hit the intended process.
- `systemctl MainPID` alone does not prove that process owns the port, especially after restarts or socket/reuse-port ambiguity.
- Checking only `/proc/net/tcp` misses IPv6 listeners; check both tcp and tcp6.
- Multiple matching listeners are ambiguous; fail closed instead of choosing one.
- Read races are possible; after health, repeat identity/listener/ownership and require stability.
- Preserve blocked launcher bytes and supersede with a new versioned launcher/envelope rather than mutating the reviewed artifact in place.

## Compact proof marker

```text
LIVE_GATEWAY_GATE=exact_MainPID_process_plus_sole_port_listener_inode_fd_owner_plus_post_health_recheck
LISTENER_COUNT=1
LISTENER_OWNED_BY_MAINPID=true
POST_HEALTH_IDENTITY_STABLE=true
NOT_CLAIMING=event,consumer,producer,merge,deploy,or canonical full-suite green
```
