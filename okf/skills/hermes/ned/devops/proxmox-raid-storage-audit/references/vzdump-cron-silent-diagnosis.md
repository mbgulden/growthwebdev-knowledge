# Why Proxmox vzdump "silently stopped" — diagnosing a dead backup schedule

When the audit's step-5 backup-freshness check shows **no recent backups** but `systemctl is-active cron` is `active` and `grep CRON /var/log/syslog` looks healthy (only `run-parts /etc/cron.hourly`), the usual cause is a **malformed Proxmox cron file** that cron is dropping on every reload. This is a live PVE1 finding (2026-08): drives 100% healthy, but the GPU node's last backup was ~4 months old.

## Where the schedule lives
- Proxmox's vzdump schedule is `/etc/pve/vzdump.cron`.
- cron reads it as `/etc/cron.d/vzdump` (there's a symlink `/etc/cron.d/vzdump -> /etc/pve/vzdump.cron`).
- `/etc/cron.d/` format: `min hour dom mon dow user command` — **6 fields + command, the `user` field is required.** A healthy daily-at-02:00 line:
  ```
  0 2 * * * root vzdump --all 1 --mode snapshot --storage Synology_NAS --compress zstd --quiet 1
  ```

## The symptom that looks fine but isn't
```
systemctl is-active cron                     # active
grep CRON /var/log/syslog | tail             # only "CMD (cd / && run-parts --report /etc/cron.hourly)"
find <backup_target> -name '*.log' -newermt <cutoff> | wc -l   # 0  ← backups dead
```
`grep CRON /var/log/syslog` does **not** show the failure. The error is logged by cron **only when it (re)loads the crontab file** — i.e. at boot / cron restart — not on each missed fire. So the box can run for months with a dead backup schedule while syslog looks clean.

## The actual error (journalctl, not syslog)
```
journalctl --no-pager | grep -iE "cron.*(error|bad|invalid|unpars|syntax)|bad day|bad month"
```
→
```
cron[3636]: Error: bad day-of-month; while reading /etc/cron.d/vzdump
cron[3636]: (*system*vzdump) ERROR (Syntax error, this crontab file will be ignored)
```
One occurrence per boot/reload. The phrase **"this crontab file will be ignored"** is the tell — cron parsed the file, rejected it, and never schedules anything from it.

## The smoking gun: file mtime == last-good-backup date
```
stat -c '%y  %n' /etc/pve/vzdump.cron
# 2026-04-09 07:39  /etc/pve/vzdump.cron
```
If the cron file's **mtime matches the date of the last successful backup**, the file was mangled on that exact day. Correlate with the backup logs: **manual** runs appear at odd times (e.g. 11:52 / 12:33 / 15:24), *not* the scheduled hour (02:00) — that's why the last "good" backup is a manual run and nothing has run since the corruption.

## The common corruption
A script or botched edit pastes a token (often a script name) into the **dom (field 3)** and/or **mon (field 4)** positions instead of `*`. Example of the broken line found on PVE1:
```
0 2 pve1_thermostat.py pve1_thermostat.py 0 root vzdump --all 1 --mode snapshot --storage Synology_NAS --compress zstd --quiet 1
```
Here fields 3 & 4 are `pve1_thermostat.py` (a fan-control daemon name, unrelated to backups) instead of `* *` — so `dom=pve1_thermostat.py` is an invalid day-of-month → cron rejects the whole file.

Quick validation:
```
awk '{print "NF="NF" : "$0}' /etc/pve/vzdump.cron
# fields 1-5 must be cron specs (* or digits/ranges); a bare .py filename in field 3/4 is the bug
```
Confirm the injected token is actually something else: `find / -name 'pve1_thermostat.py'` → it was `/root/pve1_thermostat.py` (ST550 fan daemon), proving it was pasted in, not intended.

## Fix (infra change — get approval first)
1. `cp /etc/pve/vzdump.cron /etc/pve/vzdump.cron.bak-<date>` (preserve the broken line as evidence).
2. Patch the line so fields 3 & 4 are `* *` (and confirm the intended schedule — don't assume `0 2`; read the original intent).
3. `systemctl reload cron` (or it self-heals at next reload/boot).
4. Force a run now to stop the data sitting on a stale restore:
   `vzdump --all 1 --mode snapshot --storage <STORAGE> --compress zstd --quiet 1`
5. **Verify** — new `.log` + `.vma.zst` under the target with fresh mtime; `tail` the newest log shows `Finished Backup of VM <id>` and `Finished Backup` (exit 0 alone is not proof).

> **Outbound/infra gate:** editing the backup schedule is an infra change. Report the exact corrupted line + proposed fix and wait for Michael's go-ahead; do not patch and run unilaterally. (On PVE1 Michael approved, then I patched + forced the backup.)

## Connection note (reaching the PVE host)
- Prefer **LAN SSH** (`root@<lan-ip>`, e.g. `192.168.1.2`, `-o StrictHostKeyChecking=accept-new`) — it just works when you're on-wire.
- **Tailscale SSH** (`root@<ts-ip>`) on a host with no provisioned keys (`~/.ssh/` empty) requires a **one-time web consent per session**. The consent URL (`https://login.tailscale.com/a/<id>`) **prints to the TTY**, so running `ssh -o BatchMode=yes ...` hangs and you never see the link. To surface it for the user: run `ssh` under a **PTY** and grep it out:
  ```
  timeout 40 ssh -o ConnectTimeout=35 -o StrictHostKeyChecking=accept-new root@<ts-ip> 'echo OK' 2>&1 | grep -oiE "https://login\.tailscale\.com/a/[a-z0-9]+" | head -1
  ```
  Hand the user that link to approve. (On PVE1 LAN SSH was used for the work; Tailscale was a redundant route.)
