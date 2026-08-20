# Stale daemon vs Hermes cron alert source

Use this when an alert keeps firing after the Hermes cron script was patched and verified.

## Durable lesson

A noisy alert can come from a second runtime path, not the cron row you just fixed. If the user says the same alert keeps arriving after a cron remediation, immediately prove the active source before doing more threshold tuning.

Common duplicate sources:

- A long-running `systemd` service running an older script copy, e.g. `/home/ubuntu/.hermes/scripts/<monitor>.py`.
- A hardlinked script copy across Hermes profiles.
- A daemon log/relay posting directly to Telegram while the Hermes cron output is silent.
- Backup or root-level `.hermes/scripts/` copies that predate profile-local scripts.

## Investigation sequence

1. Search for the exact alert title and old wording across live scripts, service units, and profile logs:
   - alert header, e.g. `Proxmox Cluster Monitor`
   - old alert phrase, e.g. `Load CRITICAL:`
   - specific host line if available, e.g. `pve6 Load CRITICAL`
2. Check active processes, not just cron state:
   - `ps -eo pid,ppid,lstart,cmd | grep -E '<script>|<service-name>'`
   - `systemctl --type=service --state=running | grep -Ei '<monitor>|cron|hermes'`
   - `systemctl cat <service>.service`
3. Compare script paths:
   - Cron may run `~/.hermes/profiles/orchestrator/scripts/<script>.py`.
   - A daemon may run `/home/ubuntu/.hermes/scripts/<script>.py`.
   - Patch or replace both if the root copy can still be invoked.
4. Stop the old source decisively:
   - `systemctl stop <service>`
   - `systemctl disable <service>`
   - If it should never restart, remove/back up the unit file and `systemctl mask <service>`.
   - Kill leftover processes after stopping if necessary.
5. Re-run the intended Hermes cron and confirm its latest output is silent/expected.

## Verification recipe

Create `/tmp/hermes-verify-*.py` with `tempfile.mkstemp`. Verify:

- Patched profile script and any root/daemon script copy both compile.
- Old alert wording is absent from every live script path.
- `systemctl is-active <service>` is `inactive` and `systemctl is-enabled <service>` is `masked` or otherwise unable to start.
- `ps` shows no stale monitor process.
- The latest Hermes cron output is silent or contains only the new expected contract.
- Mocked high-core fixture stays silent; low-core or RAM-critical fixture still alerts through the intended channel.

Report as **ad hoc targeted verification**, not suite green.
