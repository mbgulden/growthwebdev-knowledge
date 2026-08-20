# Stale bash-spawned gateway blocking systemd restart loop

Session pattern: a profile's gateway service is in `activating (auto-restart) (Result: exit-code)` loop. Every restart attempt fails with `code=exited, status=1/FAILURE`. The systemd unit looks healthy (`Restart=always`, `KillMode=mixed`). `systemctl is-active` reports `activating`. None of the obvious fixes (service install, daemon-reload, manual restart) work.

## Durable failure contract

A Hermes gateway can fail to start cleanly because **a different, non-systemd-managed instance of the same gateway already holds the duplicate-check lock**. The systemd unit starts → checks for an existing PID → finds the stale bash-spawned one → exits with `❌ Gateway already running (PID <stale>).` → restart loop continues forever.

Distinct from the Telegram reconnect wedge (`hermes-gateway-telegram-reconnect-wedge.md`) because:
- systemd is in restart loop, not just Telegram adapter wedged
- `hermes --profile <p> -z '...'` CLI chat path still works (gateway is reachable for one-off sessions; only the systemd-managed service fails)
- The error message is exact and visible in journal: `❌ Gateway already running (PID <stale>).`

## Diagnostic sequence

1. **Read journal for the exact error:**

```bash
journalctl -u hermes-gateway-<profile>.service -n 30 --no-pager | tail -40
```

Look for the line `❌ Gateway already running (PID <stale>).` — if present, the failure mode is confirmed.

2. **Find the stale process and its parent chain:**

```bash
ps -p <stale_pid> -o pid,user,etime,cmd
ps -ef | grep "<stale_pid>" | grep -v grep
```

The parent chain matters. If the parent is `bash` (not `systemd`), the stale process was started interactively and outlived its session. If the parent bash's parent is *another* running gateway (e.g. `kai` gateway spawning `ned` gateway as a backgrounded job), the leak path is identified.

3. **Check user-systemd scope** (sometimes the pollers run there rather than the system scope):

```bash
systemctl --user status hermes-gateway-<profile>.service 2>&1
ls /home/ubuntu/.config/systemd/user/hermes-gateway-*.service 2>&1
```

4. **Confirm via gateway status output:**

```bash
hermes --profile <profile> gateway status 2>&1 | head -25
```

The output should show the systemd unit in restart loop with the same `❌ Gateway already running` text in the active state block.

## Root cause pattern

The leak originates when an interactive bash session (often inside another running gateway's environment, e.g. a kai session) runs:

```bash
hermes --profile <other_profile> gateway run --replace > /tmp/<other>-gateway.log 2>&1
```

The bash backgrounds the python child. When the interactive session ends, the bash + python keep running indefinitely. The duplicate-check logic correctly rejects the systemd-managed instance because another instance is bound to the socket/state file.

## Repair pattern

**Signal only the stale bash-spawned instance, never the systemd-managed one.**

```bash
# Confirm the stale PID is bash-spawned, not the systemd-managed unit
ps -p <stale_pid> -o pid,ppid,cmd
# ppid should be a bash process, not systemd (PID 1)

# Send SIGTERM; if it persists >30s, escalate to SIGKILL
kill -TERM <stale_pid>
sleep 5
ps -p <stale_pid> 2>&1  # should now return "No such process"
```

After the stale process exits, the systemd unit's next restart attempt will succeed:

```bash
systemctl show hermes-gateway-<profile>.service -p ActiveState -p SubState -p MainPID
# ActiveState=active SubState=running MainPID=<new_sysd_pid>
```

If the systemd unit's older restart attempts left the unit in a degraded state, restart it explicitly:

```bash
sudo systemctl restart hermes-gateway-<profile>.service
```

**NEVER signal the gateway PID that belongs to the current profile.** Per `hermes-agent` skill rules, the current agent's gateway is reachable for one-off CLI chats; signal only the stale bash-spawned one with a confirmed bash PPID.

## Verification checklist

- `systemctl is-active hermes-gateway-<profile>.service` returns `active`.
- `MainPID > 0` and the PID's `ppid == 1` (parent is systemd/init).
- `journalctl -u hermes-gateway-<profile>.service -n 5` shows `Started hermes-gateway-<profile>.service` followed by `Hermes Gateway Starting...` with no `❌ Gateway already running` line.
- `hermes --profile <profile> -z 'Reply with exactly <PROFILE>_GATEWAY_OK and nothing else.'` returns the sentinel string (proves the model route still works through the new PID).
- Telegram state.db shows a session row for the profile with `ended_at IS NULL` and `started_at` recent (proves the Telegram adapter reconnected).

## Prevention (to-do list, not shipped)

A daily no-agent watchdog that scans `ps -ef` for `hermes --profile X gateway run` processes whose parent is a bash session rather than systemd. Report any as a Triage signal in the morning digest. This skill's author knows this is missing; not yet implemented.

A simpler prevention rule: **never run `hermes --profile X gateway run --replace` from an interactive bash session.** Use `hermes gateway restart` (systemd-managed) or `hermes gateway start --system` instead. If the goal is "make the gateway use a fresh PID," those commands do exactly that without leaving a non-systemd instance bound to the state file.

## Pitfalls

- Do not signal a PID whose PPID is systemd. That is the systemd-managed gateway; killing it just restarts the loop with a fresh PID.
- Do not assume `hermes gateway restart` will fix the duplicate-check. The duplicate-check is held by the OTHER instance, not by the systemd unit. `restart` will fail until the bash-spawned instance is gone.
- Do not delete the stale PID's `/tmp/<profile>-gateway.log` before killing the process — the log is forensic for understanding the leak source (the bash command line in the log header usually identifies the leak path).
- Do not assume this is a Telegram reconnect wedge. Different failure mode, different repair.
- Do not run `hermes gateway install --replace` (regenerate systemd unit) as the fix. The unit is healthy; the conflict is at the state-file / lock layer.