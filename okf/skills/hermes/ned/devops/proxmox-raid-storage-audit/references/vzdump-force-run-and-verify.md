# Force-running vzdump after a cron fix — interactive cookbook

Captured from the live PVE1 2026-08-15 recovery (cron fixed → forced `vzdump --all 1` → 71.8 GB compressed archive landed on the NAS).

## Why you can't just `ssh in && vzdump`

The "fix it + run a backup" follow-up sounds one-step, but it has its own failure shape that the silent-diagnosis reference doesn't cover:

- vzdump runs **detached from your SSH session**. Your 5-minute `timeout 5 ssh` wrapper will exit before the backup finishes, and you'll think the backup died. It didn't.
- `vzdump --all 1` iterates every VM. For a 100G vdisk, expect **read ~7 min + zstd compress ~4 min** = ~12 min total. Lifetimes of "is it stuck?" anxiety.
- The `.vma.zst` lands on the **NAS via NFS**. While vzdump is actively writing, even `ls -la /mnt/pve/Synology_NAS/dump/` over the same mount **hangs** — the NFS server is busy serving the writer. Don't repeatedly poll `ls`; it'll just time out and you'll see transient "No route to host" reports.
- The right signal of life is `pgrep -af "vzdump|zstd"` — vzdump PID, then `task UPID:` child, then `zstd --threads=1` when compressing. When the vzdump PID is gone, the backup is done (or crashed).

## Step-by-step

### 1. Pre-flight (under 30 s)

```bash
# Is the cron file actually fixed? (the line we want)
ssh root@<lan-ip> 'cat /etc/pve/vzdump.cron'
# Expected: 0 2 * * * root vzdump --all 1 --mode snapshot --storage <NAME> --compress zstd --quiet 1

# Did cron actually load it? Look at the LAST cron restart in journalctl.
ssh root@<lan-ip> 'systemctl restart cron && sleep 2 && \
  journalctl -u cron --since "5 minutes ago" --no-pager | grep -iE "vzdump|error|bad"'
# Expected: NO error lines for the most recent restart. (Old reloads may show errors; that's the
# pre-fix history, not the current state.)

# Storage target is reachable + writable
ssh root@<lan-ip> 'df -h /mnt/pve/<NAME> | tail -1 && \
  touch /mnt/pve/<NAME>/.ned-write-test-$$ && echo OK && rm -f /mnt/pve/<NAME>/.ned-write-test-$$'
```

### 2. Launch vzdump as a Hermes-tracked background process

```bash
# terminal(background=true, notify_on_complete=true)
ssh root@<lan-ip> 'bash -c "exec vzdump --all 1 --mode snapshot --storage <NAME> --compress zstd --quiet 1"' 2>&1
```

Important: do **not** shell-detach with `nohup`, `setsid`, `disown`, or `&` inside the SSH command — the platform's terminal wrapper rejects shell-level background wrappers and you'll get an error. The Hermes-tracked `background=true` is the right way; vzdump will outlive any SSH `timeout` you set because the SSH exit doesn't kill the remote process.

### 3. Confirmation — what to look at, what to ignore

After launch, poll the host:

```bash
ssh root@<lan-ip> 'pgrep -af "vzdump|zstd" | head -3'
# Healthy: vzdump PID + 1-2 task children + (later) one zstd --threads=1
# Dead:    empty output → backup finished or crashed
```

If vzdump is alive but wants to know stage:

```bash
# Read the latest task log header
ssh root@<lan-ip> 'tail -5 /var/log/pve/tasks/active'
# Healthy: shows recent UPID for the vzdump task with "OK" status
```

**Don't poll `ls /mnt/pve/Synology_NAS/dump` repeatedly.** It will hang for 10–30 s while NFS serves the writer. The NAS `df` is fine; `ls` of the dump directory is not.

If you need to see the in-progress file's size, use `find` with a tight timeout:

```bash
ssh root@<lan-ip> 'timeout 5 ls -la /mnt/pve/<NAME>/dump/vzdump-qemu-230-*.vma.dat 2>&1 | tail -3'
```

### 4. Confirm completion — only via the log file

The real "backup done" signal is the per-run vzdump log file on the NAS:

```bash
ssh root@<lan-ip> 'tail -12 /mnt/pve/<NAME>/dump/vzdump-qemu-230-<NEW>.log'
# Expected last 3 lines:
#   ... INFO: archive file size: 71.83GB
#   ... INFO: prune older backups with retention: keep-last=3
#   ... INFO: Finished Backup of VM 230 (00:11:45)
```

Both must be present to call it done:
- `archive file size: <N>GB` — the vma.zst landed
- `Finished Backup of VM <id> (HH:MM:SS)` — vzdump exited cleanly

Exit code 0 alone is **not** proof (per `ad-hoc-verification-contracts`). A vzdump Python `died: Killed` mid-run with `ret = 9` and no `Finished Backup` line means the process was killed; the partial `.vma.dat` is on the NAS but no `.vma.zst`.

### 5. Optional: verify the .vma.zst is actually restorable

Don't do this on every run — it reads the full archive back → doubles the IO. Only on first run after a fix or when the box has been unreliable:

```bash
ssh root@<lan-ip> 'qemu-img check /mnt/pve/<NAME>/dump/vzdump-qemu-230-<NEW>.vma.zst 2>&1 | head -5'
# Expected: "No errors were found" or similar.
```

## What vzdump writes where (step-by-step file lifecycle)

```
1. vzdump reads VM disk → streams into a tmpdir (/data_pool/dump/vzdump-qemu-230-*.tmp/)
2. vzdump writes the .vma.dat to the target (NAS) ← this is the slow write
3. vzdump spawns zstd --threads=1 to compress the .vma.dat → .vma.zst
4. vzdump removes the .vma.dat and the tmpdir
5. vzdump writes the run log (.vma.zst.log) to the target
6. vzdump prunes older backups per keep-last/keep-daily
```

While the backup is alive, you can confirm progression via:
- `pgrep -af vzdump` → vzdump + task child (write stage)
- `pgrep -af zstd` → zstd present (compress stage)
- NAS `ls` will **hang** while the writer holds the filesystem (don't poll it)

**Time budget for a 100 GB VM disk (verified 2026-08-15):**
- Read: ~7 min (~250 MiB/s effective snapshot bandwidth)
- zstd compress: ~4 min (single-threaded; default for vzdump)
- Total: ~12 min

If you want faster compression, you can fork the vzdump invocation and pass `--bwlimit 0` + `zstd -T0`, but that's outside the standard `--all 1` shorthand.

## Host-drops-offline pattern

If `ssh root@<lan-ip>` returns `No route to host` mid-backup, **don't panic**. PVE1 (and other PVE hosts on the same Tailscale tailnet) have been observed to drop off both LAN and Tailscale for 5–10 minutes mid-session, then return. The vzdump process is detached — it keeps running on the host and the backup will finish in the background. Back off and poll:

```bash
for i in 1 2 3 4 5 6; do
  ping -c1 -W2 <lan-ip> 2>&1 | grep -oE "time=[0-9.]+ | 100% packet loss"
  sleep 15
done
# When the host returns, re-verify the cron file is still correct and the
# vzdump run finished (look at the .log file's mtime + last line).
```

If the host stays gone > 15 min, the box is genuinely down and needs a physical/ILO/IPMI check — at that point escalate (this is real infra, not a Tailscale blip).

## Verifying the fix is durable

After the cron reload + first manual run, the nightly job will fire at 02:00 host-local on the next scheduled day. To confirm the schedule auto-fired:

```bash
ssh root@<lan-ip> 'ls -lt /mnt/pve/<NAME>/dump/vzdump-qemu-*.log | head -3'
# Look for: a log file with mtime ~02:00 of the expected date, with "Finished Backup" in its tail.
```

A failed auto-fire will leave **no log file** from that date (the file would not exist). The cron error would only appear in `journalctl -u cron --since "today"` at the next cron restart, not at the missed fire time — same pattern as the silent-diagnosis reference.

## Caveats

- **The 6-field `0 2 * * * root …` form**: Proxmox reads `/etc/pve/vzdump.cron` as `/etc/cron.d/vzdump`. The format is `m h dom mon dow user command` — **6 fields + command**. A common over-eager fix is `0 2 * * * 0 root vzdump …` (7 fields, with `0` as `dow`) which cron rejects with `bad username`. The correct repair is `0 2 * * * root vzdump …` (6 fields, `root` as the user). See `vzdump-cron-silent-diagnosis.md` for the full mtime-vs-last-backup smoking gun workflow.
- **Don't run `vzdump --all 1` twice concurrently.** It will produce interleaved `.tmp` directories and one of the runs will fail with `lockfile /var/lock/pve-vzdump.lock held by PID ...`. Wait for the first run to fully complete (or kill it cleanly) before re-running.
- **NAS disk space**: the live PVE1 Synology is 27T / 82% used. A single 100G VM backup adds ~7 GB. The `keep-last=3` retention on Proxmox defaults will keep ~15 GB per active VM. Plenty of headroom on this box, but on smaller targets, check `df` before kicking off.
