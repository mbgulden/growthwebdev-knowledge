---
name: proxmox-raid-storage-audit
description: Audit drives/storage on Proxmox or any hardware-RAID host. Use when asked to "audit the drives," "check disk health/SMART," or "what's on the <T> drive" on a server where the big block device is a RAID virtual disk (LUN) behind a controller (Lenovo 930-8i / LSI MegaRAID / Broadcom SAS3508 / Dell PERC). Covers why smartctl is blind on RAID VDs, how to get per-drive SMART via the controller CLI, and how to pair drive health with pool-contents + backup-freshness checks.
tags: [devops, storage, raid, proxmox, smart, storage-audit, infra]
---

# Proxmox / RAID Storage & Drive Audit

## When to use
- Michael asks to audit / health-check the drives on a PVE host, NAS, or any server.
- The "drive" is a large block device (e.g. an 18T disk) that is actually a **RAID virtual disk behind a hardware controller**, not a bare platter.
- You need per-physical-drive SMART, and/or you must answer "is anything important on there" + "is it protected."

## Core truth: the OS block device is NOT the physical disk
On a hardware-RAID host, `/dev/sdX` for the big disk is a **virtual disk / LUN** presented by the controller.
- `smartctl -a /dev/sdX` returns `SMART support is: Unavailable - device lacks SMART capability` and `0 C` temps. **That is expected, not a fault, and not the answer.**
- `lsblk -o NAME,SIZE,MODEL` shows the big disk's MODEL as a controller name (`RAID 930-8i-2GB`, `PERC`, `MegaRAID`). `lspci | grep -iE "raid|sas|mega|adapt"` names the controller; `lsmod | grep -iE "megaraid|mpt|sas"` confirms the driver.
- Real per-drive health lives **behind the controller** — query it with the controller's CLI: `storcli64` (LSI/Broadcom), `perccli` (Dell), `ssacli` (HPE).

## Workflow
1. **Identify device + controller.** `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL`. If the big disk's MODEL is a controller, it's a VD. Confirm with `lspci` + `lsmod`.
2. **Get the controller CLI onto the host.** See `references/storcli64-acquisition-and-syntax.md` — vendor direct mirrors are often blocked; use the GitHub-hosted mirror.
3. **Enumerate topology.** `storcli64 /c0 show` and `/c0 show all` → VDs (RAID level, Optimal/Degraded/Consistent) and the PD LIST with `EID:Slot` per physical drive.
4. **Per-drive SMART.** For each slot: `prescan` (refresh) then `show all` / `show smart` via `/c0/e<EID>/s<slot>`. Read Media Error Count, Other Error Count, Predictive Failure Count, SMART alert flag, Drive Temperature. Decode POH from the ATA raw field (reference).
5. **Pair with contents + protection** (this is what makes it an audit, not a SMART dump):
   - `du -sh <pool>/*` + `find <pool> -type f -exec du -sh {} \\;` → what's actually there.
   - Proxmox: `qm list` + `qm config`; diff pool `images/<id>/` dirs against `qm list` to find **orphaned VM disks**.
   - **Backup freshness:** `cat /etc/pve/vzdump.cron`, `systemctl is-active cron`, `find <backup_target> -name '*.log' -newermt <cutoff> | wc -l`, `tail` the newest vzdump log. A healthy drive set with a stale backup is the real risk.
   - **Root-cause the stale backup** before reporting. `cron` being `active` + clean syslog does NOT mean the schedule is healthy — a malformed `/etc/pve/vzdump.cron` (read as `/etc/cron.d/vzdump`) is dropped by cron with `bad day-of-month … this crontab file will be ignored`, and that error only appears in **journalctl at boot/reload**, not in per-fire syslog. The file **mtime matching the last-good-backup date** is the smoking gun (see `references/vzdump-cron-silent-diagnosis.md`). Report the exact corrupted line + a proposed fix and wait for approval before touching the schedule.
   - **The correct repair shape**: `/etc/cron.d/vzdump` uses 6 fields + command (`m h dom mon dow user command`). The line `0 2 * * * * root vzdump …` (7 fields, with `0` as `dow`) still fails with `bad username`. The canonical line is `0 2 * * * root vzdump --all 1 --mode snapshot --storage <NAME> --compress zstd --quiet 1`. After patching, verify the **last** cron restart in `journalctl -u cron --since "5 minutes ago"` is clean — older error lines from the pre-fix reload are noise.
6. **Report** a `.md` audit: topology → per-drive SMART table → pool usage + importance → backup status → ranked recommendations. Attach with `MEDIA:`.

## Deliverable pattern (Michael's standing rule)
- **The audit `.md` itself is a durable artifact** — it documents hardware/access/backup facts that other agents (and future Ned sessions) will need. Save it under **`/home/ubuntu/work/okf/standards/<slug>.md`** (or `okf/operations/` if date-prefixed observation). Format: `Date / Owner / Status` header → body → sections → reference commands.
- Michael's standing rule: **"infrastructure facts go to the OKF on the server, not memory."** Use the existing OKF standards files for that host's facts (e.g. `pve1-hardware-and-access-facts.md`) or create a new one if none exists. Memory gets *only* the durable cross-host facts (e.g. "PVE1 RAID LUNs need storcli64, not smartctl"). The full audit lives in the OKF.
- **Don't ship the audit via memory alone.** Memory is for cross-session pointers; the OKF is the source of truth a future agent can `read_file` without burning tokens on retrieval.
- **Verify the `.md` before reporting done.** Existing standards are mojibake-safe Telegram-style; mirror that. After writing, run a quick `/tmp/hermes-verify-*.py` artifact verifier (no canonical build applies to a docs edit). Assertions: file exists, size in range, OKF header (`Date / Owner / Status`), required sections, hard facts, no curly quotes / em-dash / nbsp / ellipsis, no credential-shaped strings. See `references/audit-report-deliverable-pattern.md` for the full verdict.

## Pitfalls
- **Don't trust `smartctl` on the big disk.** If its MODEL is a controller name, the LUN is blind. Reporting "SMART unavailable / no data" as the result is a failed audit — go through the controller.
- **storcli64 addressing is version-dependent.** The newer "SAS Customization Utility" (e.g. v007.3405) rejects the classic `e<s> p<s>` / `/c0 show physdisk` forms with `syntax error, unexpected TOKEN_OBJ_ENCLOSURE`. Working form: `/c0/e<EID>/s<slot>` (enclosure then slot). `/c0/s0` without the enclosure parses but returns "Drive not found". See reference for the exact failing forms.
- **POH is not printed as a number** in `show smart`; it's a 48-bit little-endian raw field. Decode + round (reference).
- **A clean SMART pass ≠ "no risk."** Always check backup recency and orphaned data before calling the box healthy. In practice the top finding on a healthy-drive box is stale backups, not the drives.
- **Preserve real mechanics, don't invent them.** If you cannot reach the controller or a tool, say so and give the exact blocker — never fabricate SMART numbers.
- **The over-eager repair trap.** When patching a corrupted vzdump cron, the temptation is to write `0 2 * * * * root vzdump …` (7 fields). That still fails with `bad username` because the `dow` is `*` and `*` is the user — never works. The canonical 6-field form is `0 2 * * * root vzdump …`. After patching, verify the **last** cron restart's log line in `journalctl -u cron --since "5 minutes ago"` is clean; older error lines from the broken-file reloads are noise.
- **PVE hosts can disappear mid-session.** On PVE1 (and a few siblings on the same Tailscale tailnet), the host has been observed to drop off both LAN and Tailscale for 5–10 minutes mid-session, then return. If you hit `No route to host` mid-edit, **don't panic** — the host is almost certainly coming back. Back off, poll, and re-attempt. vzdump processes stay alive on the host even while your SSH times out. Only escalate to physical/ILO/IPMI if the host stays gone > 15 min.
- **Don't query an in-flight NAS write.** When vzdump is actively writing a `.vma.dat` to the NFS-mounted NAS, `ls -la /mnt/pve/<NAME>/dump/` over the same mount **hangs** for 10–30 s. The hang is real but harmless — the writer is busy. Use `pgrep -af vzdump` as the "is it alive" signal instead, and only `ls` the destination after the writer finishes. See `references/vzdump-force-run-and-verify.md` for the full interactive cookbook.

## Reaching the PVE host
- Prefer **LAN SSH** (`root@<lan-ip>`, `-o StrictHostKeyChecking=accept-new`) when on-wire — it just works.
- **Tailscale SSH** with no provisioned keys requires a one-time web consent; the consent URL prints to the **TTY**, so `BatchMode` ssh hangs and never shows it. Surface it for the user via a **PTY** run + `grep -oiE "https://login\.tailscale\.com/a/[a-z0-9]+"`. Details in `references/vzdump-cron-silent-diagnosis.md`.

## References
- `references/storcli64-acquisition-and-syntax.md` — working download/acquisition path (vendor mirrors blocked), exact working + failing commands, POH decode method.
- `references/vzdump-cron-silent-diagnosis.md` — root-causing "backups stopped silently": malformed `/etc/cron.d/vzdump`, why syslog looks clean but journalctl has the real error, the mtime-vs-last-backup smoking gun, fix + verify, and the Tailscale-consent-URL trick.
- `references/vzdump-force-run-and-verify.md` — interactive cookbook for the "fix it + back it up" follow-up: detached process handling, NAS-write-hangs-don't-poll, zstd stage detection, the canonical 6-field cron shape, host-drops-offline pattern, durable-verify-after-02:00.
- `references/audit-report-deliverable-pattern.md` — saving the audit `.md` to the OKF (`okf/standards/` for durable facts, `okf/operations/` for date-prefixed observations), ASCII discipline, the artifact verifier skeleton, and the verifier re-trigger handling.

## Reaching the PVE host
- Prefer **LAN SSH** (`root@<lan-ip>`, `-o StrictHostKeyChecking=accept-new`) when on-wire — it just works.
- **Tailscale SSH** with no provisioned keys requires a one-time web consent; the consent URL prints to the **TTY**, so `BatchMode` ssh hangs and never shows it. Surface it for the user via a **PTY** run + `grep -oiE "https://login\.tailscale\.com/a/[a-z0-9]+"`. Details in `references/vzdump-cron-silent-diagnosis.md`.

## References
- `references/storcli64-acquisition-and-syntax.md` — working download/acquisition path (vendor mirrors blocked), exact working + failing commands, POH decode method.
- `references/vzdump-cron-silent-diagnosis.md` — root-causing "backups stopped silently": malformed `/etc/cron.d/vzdump`, why syslog looks clean but journalctl has the real error, the mtime-vs-last-backup smoking gun, fix + verify, and the Tailscale-consent-URL trick.
- `references/audit-report-deliverable-pattern.md` — saving the audit `.md` to the OKF (`okf/standards/` for durable facts, `okf/operations/` for date-prefixed observations), ASCII discipline, the artifact verifier skeleton, and the verifier re-trigger handling.
