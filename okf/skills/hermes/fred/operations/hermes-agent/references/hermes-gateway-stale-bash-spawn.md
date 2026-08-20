# Hermes gateway stale-bash-spawn lockout — session evidence

**Captured:** 2026-07-28, Ned profile.
**Trigger:** Michael pivoted to the KPI dashboard PWP plugin workstream and needed Ned's Telegram working again.
**Resolution time:** ~3 minutes from symptom to recovered gateway.

## Symptom

`hermes --profile ned gateway status` showed:

```
⚠ Installed gateway service definition is outdated
● hermes-gateway-ned.service
     Active: activating (auto-restart) (Result: exit-code) since Tue 2026-07-28 20:31:20 UTC
    Process: 499900 ExecStart=... (code=exited, status=1/FAILURE)
✗ System gateway service is stopped
```

Other profiles (`autobot`, `fred`, `george`, `kai`, `next-step`) were all healthy. Ned had been restarting for ~36,000 cycles (`restart counter is at 36110` and counting).

## Root cause

`journalctl -u hermes-gateway-ned.service -n 20`:

```
python[499866]: ❌ Gateway already running (PID 1707198).
python[499866]:    Use 'hermes gateway restart' to replace it,
python[499866]:    or 'hermes gateway stop' to kill it first.
```

`ps -p 1707198 -o pid,user,etime,cmd`:

```
  PID USER         ELAPSED CMD
1707198 ubuntu    2-18:15:10 /.../python .../hermes --profile ned gateway run --replace
```

The stale process had been alive for **2 days 18 hours 15 minutes**. Tracing its parent chain:

```
1707198 → bash 1707191 → bash 1650654 (kai gateway, systemd-managed)
```

The kai gateway had been the bash session's parent. A kai session on 2026-07-26 had run:

```bash
hermes --profile ned gateway run --replace > /tmp/ned-gateway.log 2>&1
```

as a backgrounded job. The kai session ended, but bash + python kept running. The systemd unit for `hermes-gateway-ned.service` could not start because the duplicate-check correctly saw another instance.

## Evidence chain

```bash
# 1. Confirm the stale process is non-systemd (PPID != 1)
$ ps -o pid,ppid,etime,cmd -p 1707198
    PID    PPID     ELAPSED CMD
1707198 1707191 2-18:15:10 /.../hermes --profile ned gateway run --replace

# 2. Kill ONLY the stale instance (NOT the systemd-managed one)
$ kill -TERM 1707198

# 3. Wait for systemd's next restart attempt (~5s by RestartSec=5)
$ systemctl show hermes-gateway-ned.service -p ActiveState -p SubState -p MainPID
ActiveState=active
SubState=running
MainPID=500625    # new PID, distinct from 1707198

# 4. Live capability probe (bypasses gateway and Telegram)
$ hermes --profile ned -z "Reply with exactly: NED_GATEWAY_OK"
NED_GATEWAY_OK
```

## Two follow-on warnings (non-fatal but worth fixing)

1. **Stale systemd unit:** `TimeoutStopSec=90s` vs `drain_timeout=180s` (expected ≥210s).
   ```
   WARNING gateway.run: Stale systemd unit detected: hermes-gateway-ned.service has
     TimeoutStopSec=90s but drain_timeout=180s (expected >=210s). systemd may SIGKILL
     the gateway mid-drain. Run `hermes gateway service install --replace` to regenerate the unit.
   ```
   **Fix (not run this session):** `sudo hermes gateway service install --replace --profile ned && sudo systemctl daemon-reload && sudo systemctl restart hermes-gateway-ned.service`.

2. **state.db has hundreds of Telegram sessions with `ended_at IS NULL`** dating back to 2026-06-09. Session-end hook isn't firing. Future cleanup; non-blocking.

## Prevention recipe (proposed, not yet deployed)

A daily no-agent watchdog that scans for non-systemd gateways:

```bash
#!/usr/bin/env bash
# ~/.hermes/profiles/orchestrator/scripts/watchdog-stale-gateways.sh
set -euo pipefail
LEAKS=$(ps -eo pid,ppid,etime,cmd | awk '
  /hermes.*gateway run/ && !/hermes_cli\.main/ {
    # systemd-managed gateways have ppid=1 or are launched by `hermes_cli.main -m ...`
    # bash-spawned ones have ppid != 1 and were invoked directly via the binary
    if ($2 != "1") print
  }')
if [[ -n "$LEAKS" ]]; then
  printf "STALE_GATEWAY_DETECTED\n%s\n" "$LEAKS"
  exit 1
fi
exit 0
```

Wire as a no-agent cron with empty healthy stdout (script's exit 0 silences; exit 1 emits the leaks list as the alert). Add to the `cron-failure-remediation` skill's watchdog catalogue.

## Cross-references

- `hermes-agent` SKILL.md → "Stale-bash-spawn gateway lockout (most common Telegram outage pattern)" — the troubleshooting flow this evidence supported.
- `session-state-handoff` SKILL.md → pattern for the handoff rewrite that captured this incident (`/home/ubuntu/.hermes/profiles/ned/state/current.json` 2026-07-28 entry).
- `cron-failure-remediation` SKILL.md → add the watchdog above to its watchdog recipe list.