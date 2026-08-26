---
name: gateway-self-restart-guard
description: "Guard against self‑issued gateway lifecycle commands. The terminal tool cannot restart, kill, stop, or otherwise change the state of the running gateway (the host process) from inside its own terminal session. It can do all build and verify steps, but the final switchover must be run from a separate shell. Load this skill when the task involves making a gateway fix permanent, rebooting the host service, or any terminal command targeting the host's own PID is refused by a guard."
tags: [gateway, lifecycle, self-kill, terminal-guard, systemd, switchover]
category: operations
triggers:
  - asked to restart, reboot, or permanently fix a long‑running gateway or supervisor daemon from inside an active terminal session
  - a terminal command targeting the host's own PID appears blocked, hangs, or is rejected
  - user reports a restart or kill command "didn't work" and the target process is the current session's host
---

# Gateway Self‑Restart Guard

## Core rule

A terminal call that the gateway process spawned **cannot** issue lifecycle commands (restart, stop, kill, daemon‑reload‑then-restart) against **that same gateway**. It may perform every build and verification step, but the final "kill the old + restart under systemd" switchover must be executed by the user from a shell **outside** the gateway.

## What you CAN do in-session

- Read, compare, install, and enable the new unit/service file.
- Run `systemd-analyze verify` and compare against sibling units.
- Write the switchover/cutover script to disk for the user to run.
- Verify build phase: unit on disk is correct, boot links exist, etc.

## What you CANNOT do in-session

- `kill` the old gateway PID.
- `systemctl restart` the gateway unit.
- Any command whose effect is "this host process stops, restarts, or changes runtime state."

The built‑in guard will refuse or silently block such commands. If you see a command fail with a permission or lifecycle error, this is why.

## Switchover script (for the user)

Provide a self‑contained bash script that:
1. Kills the old manual‑stopgap PID (the one identified during diagnosis)
2. Runs `systemctl daemon-reload`
3. Runs `systemctl restart <unit>`
The user executes it from a terminal **outside** the gateway session. After success, verify from a fresh session:
- `systemctl is-active <unit>` → active/running
- Exactly one new gateway process with PPID=1
- Old PID no longer exists
- Fresh "Starting" banner in the log with no polling conflicts after it

## Pitfalls

- **Never attempt the switchover from the agent's terminal.** It will be refused by the guard; forcing it risks killing the session and losing the user.
- **The unit on disk is not the unit in motion.** "Installed" means the file exists; the actual switchover is a separate user action. Do not report success until the user has run it.
- **Use the correct PID.** The guard identifies by PID, not unit name. If the manual instance has a different PID than expected, the script's kill line must target the right one.
- **Log location varies.** `systemctl cat <unit>` shows the real StandardOutput path; don't assume journal.
- **The session's own architecture matters.** If the new session runs under the new unit, the agent's terminal parent PID should match the new gateway PID.

## Support files

- `templates/hermes-orchestrator-gateway.service` — verified, fleet‑aligned systemd unit to use as the base for installation (includes Restart=always, memory guards, 2h cron timeout, and the 08‑19/08‑22 fixes).
- `scripts/switchover.sh` — self‑contained bash script the user runs outside the gateway session: kills old PID, installs unit, daemon‑reload + restart, waits 90 s, verifies, with manual fallback.
