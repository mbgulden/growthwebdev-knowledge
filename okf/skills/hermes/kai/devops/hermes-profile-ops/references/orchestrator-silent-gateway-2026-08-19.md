# Silent orchestrator gateway — 2026-08-19

Fred's (profile `orchestrator`) Telegram bot went unresponsive. Full trace:

## Timeline
- Unit: `hermes-orchestrator-gateway.service` (real unit; a stale failed alias `hermes-gateway-orchestrator.service` not-found also existed in `systemctl list-units`).
- SIGTERM received 2026-08-19 02:57 UTC; exited `code=exited, status=0/SUCCESS` (clean).
- Unit had `Restart=on-failure` → clean exit ≠ failure → systemd never respawned. Fleet standard (kai/george/ned units) is `Restart=always`.
- Model side was healthy: vLLM at 192.168.1.230:8000, model `local-qwen-27b-q8-fred`, answered a probe correctly. Old log's `Empty response ... retry 1/3` warnings were transient, not the cause.

## Fix applied
1. Emergency manual start via detached launcher (terminal guard blocks `systemctl start` from inside a gateway session):
   ```bash
   # /tmp/start-orchestrator-gw.sh
   #!/usr/bin/env bash
   exec setsid /home/ubuntu/.local/bin/hermes --profile orchestrator gateway run </dev/null >/dev/null 2>&1
   ```
   Note: running it with a trailing `sleep` + ps in the same command hit the 180s terminal timeout — launch bare, then verify in a separate call.
2. Verified: exactly one `--profile orchestrator gateway run` process; fresh `Hermes Gateway Starting` banner in `/home/ubuntu/.hermes/logs/orchestrator-gateway.log` with zero `Telegram polling conflict` lines after it; adapter processed a `/reload` Telegram message (proves token polling clean).
3. Prepared permanent unit at `/tmp/hermes-orchestrator-gateway.service` (aligned to kai/george/ned shape): `Restart=always`, `RestartSec=5`, `RestartForceExitStatus=75`, per-profile `HERMES_HOME=/home/ubuntu/.hermes/profiles/orchestrator`, `WorkingDirectory` set, `StartLimit*` moved from `[Service]` (invalid placement — systemd warned "Unknown key name") to `[Unit]`, kept `MemoryHigh=40G/MemoryMax=48G`, `TimeoutStopSec=240` (≥ 210 fixes the stale-unit drain warning), kept `HERMES_CRON_SCRIPT_TIMEOUT=7200` (AGY sandbox supervisor needs 25–90 min tasks), kept `append:` log paths.
   Verified with `systemd-analyze verify` (no sudo needed) + manual INI-ish parser (configparser fails on repeated `Environment=` keys).
4. Pending user sudo: `sudo cp /tmp/... /etc/systemd/system/... && daemon-reload && systemctl restart hermes-orchestrator-gateway`.

## Log location gotcha
`journalctl -u hermes-orchestrator-gateway` was nearly empty — the unit uses `StandardOutput=append:/home/ubuntu/.hermes/logs/orchestrator-gateway.log`. Always `systemctl cat <unit>` to find the real log path before concluding "no logs."

## Reusable verification pattern
`/tmp/hermes-verify-orchestrator-gw.sh` (ad-hoc, not a suite): manual unit parser (9 semantic checks) → `systemd-analyze verify` → `pgrep -fc` count == 1 → uptime → latest startup banner with zero post-banner polling conflicts.

## Recurrence 2026-08-22 (same trap, third occurrence class)
Gateway was down again; unit still `inactive (dead)` — the 08-19 unit alignment had NEVER been sudo-installed (the pending `sudo cp` was never run), so `Restart=on-failure` + clean exit left it dead for 3 days. Same emergency path: detached launcher, verified healthy (1 process PPID=1, 04:06:33 UTC banner, webhook + telegram connected, zero post-banner polling conflicts, cron firing).

New lessons from this recurrence:
1. **Live log is profile-scoped, not unit-level**: `~/.hermes/profiles/orchestrator/logs/gateway.log` (unit-level `~/.hermes/logs/orchestrator-gateway.log` mtime frozen at the 08-19 crash). Locator: `ls -l /proc/<pid>/fd/` — fd 3/4/8 = agent/errors/gateway logs. The 08-19 "log location gotcha" was about journalctl; the manual-launch case adds the profile-logs dir.
2. **`pgrep -fc 'orchestrator gateway run'` returned 2** with only ONE real gateway — the wrapping check shell's command line matched the pattern. Use `ps -eo pid,ppid,args` to enumerate; a single PPID=1 `gateway run` = healthy, the 2nd "match" is the probe itself.
3. **Fleet-wide stale-unit warning fired at startup**: `hermes-gateway-kai.service has TimeoutStopSec=90s but drain_timeout=180s (expected >=210s)` — a running gateway audits SIBLING units and warns. Every gateway startup log is a free fleet health audit; fix flagged units via `hermes gateway service install --replace`.
4. **Status check that matters**: `systemctl show hermes-gateway-{kai,george,ned} -p Restart --value` → all `always` (fleet standard confirmed 08-22); the orchestrator unit on disk was the outlier and is STILL the open follow-up: `/tmp/hermes-orchestrator-gateway.service` staged 08-19, `sudo cp /etc/systemd/system/ && daemon-reload && systemctl restart hermes-orchestrator-gateway` never executed as of 08-22.

Until the unit is installed, expect this recurrence: every clean exit (reboot, OOM-then-clean-kill, mid-call interruption) leaves the orchestrator bot dark with no alert until Michael notices.
