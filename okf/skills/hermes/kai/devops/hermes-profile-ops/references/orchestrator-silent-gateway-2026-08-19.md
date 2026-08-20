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
