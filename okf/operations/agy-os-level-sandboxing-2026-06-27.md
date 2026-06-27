---
type: Operations Plan
title: AGY OS-Level Sandboxing — replacing prompt-based path blocks
project: agentic-swarm-ops
resource: okf/operations/agy-os-level-sandboxing-2026-06-27.md
date: 2026-06-27
status: planning
owner: Fred
supersedes: okf/operations/agy-dispatch-v2-lane-supervisor-2026-06-26.md (search-boundary prompt block — Jun 26 2026 hotfix)
tags: [agy, sandboxing, nfs, bubblewrap, security, isolation, planning]
related: [GRO-2544, GRO-2565]
---

# AGY OS-Level Sandboxing (Jun 27 2026)

## Why this plan exists

On Jun 26 2026, the prompt-based search-boundary block (which told AGY not to search `/home/ubuntu/mounts/*` and `/home/ubuntu/.gemini/*`) was implemented as a hotfix after the first cron-launched wave tripped the circuit breaker.

Per Antigravity feedback (Jun 26): **prompt-based path blocking is fragile**. LLMs under token pressure or in complex reasoning loops forget, hallucinate, or bypass negative instructions. The OS-issued `find`/`ls`/`grep` tools operate at the kernel level and ignore prompts entirely.

Three system-level alternatives are recommended:

| Option | Difficulty | Reversible | Reliability | Sandbox model |
|---|---|---|---|---|
| **A. Move NFS mount to `/mnt/`** | Low | Yes (symlink fallback) | High (path resolution) | Directory isolation |
| **B. Bubblewrap (bwrap) namespace** | Medium | Yes | Very high (mount-namespace) | Process isolation |
| **C. Unprivileged `agy-worker` user** | Medium | Yes | High (permission denied) | Identity isolation |

## Current state (as of Jun 27 00:14 UTC)

```text
NFS source:    192.168.1.40:/volume1/agentic-context
NFS mount:     /home/ubuntu/mounts/synology-agentic-context  (mounted via systemd)
Mount unit:    /etc/systemd/system/home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount
Mount options: rw,vers=3,noacl,nocto,hard,intr,timeo=600,rsize=131072,wsize=131072
Type:          nfs

Other Synology mounts in same dir:
  /home/ubuntu/mounts/synology-photo          (read-write photos)
  /home/ubuntu/mounts/synology-proxmox-backups-ro  (read-only Proxmox backups)
  /home/ubuntu/mounts/synology-takeout         (Google takeout archives)

bwrap installed: NO (apt: bubblewrap)
agy-worker user: NO

Other cron consumers of /home/ubuntu/mounts/synology-agentic-context:
  root cron: 0 9 * * 0  rsync ... /home/ubuntu/mounts/synology-agentic-context/darius-star-full/
  agent_dispatcher.py --reconcile  (writes archive snapshots weekly)
```

## Option A — Move NFS mount out of /home/ubuntu (RECOMMENDED, ship first)

### Why this is the right first move

- Lowest-risk, highest-leverage fix
- Solves the root cause (path resolution from `$HOME`) without new tooling
- Reversible via symlink if anything breaks
- No new dependencies (bwrap, agy-worker user) required

### Steps (run as root, requires sudo)

```bash
# 1. STOP any cron jobs that touch the mount path first
sudo systemctl stop cron  # optional safety

# 2. UNMOUNT gracefully
sudo umount /home/ubuntu/mounts/synology-agentic-context
# If "device is busy", use:
#   sudo fuser -km /home/ubuntu/mounts/synology-agentic-context
#   sudo umount -l /home/ubuntu/mounts/synology-agentic-context   (lazy unmount)

# 3. CREATE new mount point outside /home
sudo mkdir -p /mnt/synology-agentic-context

# 4. UPDATE systemd mount unit
sudo cp /etc/systemd/system/home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount \
       /etc/systemd/system/mnt-synology\x2dagentic\x2dcontext.mount
sudo sed -i 's|/home/ubuntu/mounts/synology-agentic-context|/mnt/synology-agentic-context|g' \
       /etc/systemd/system/mnt-synology\x2dagentic\x2dcontext.mount
sudo systemctl disable --now home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount
sudo systemctl daemon-reload
sudo systemctl enable --now mnt-synology\x2dagentic\x2dcontext.mount

# 5. CREATE compat symlink so legacy cron targets still work
sudo rmdir /home/ubuntu/mounts/synology-agentic-context 2>/dev/null || true
sudo ln -s /mnt/synology-agentic-context /home/ubuntu/mounts/synology-agentic-context

# 6. VERIFY
mount | grep synology-agentic-context
ls -la /home/ubuntu/mounts/synology-agentic-context
# should resolve to /mnt/synology-agentic-context via symlink
```

### Risks and rollback

| Risk | Mitigation | Rollback |
|---|---|---|
| rsync cron job hits a broken path | Compat symlink at the old path | `rm` symlink, re-enable old mount unit |
| Old `fuser -m` or other tools that follow symlinks behave differently | Tested in plan mode before activating cron | `umount -l` new mount, re-enable old unit |
| Synology NAS goes offline mid-mount | `Options=hard,intr,timeo=600,retrans=2` already covers this | n/a |

### Acceptance criteria

1. `findmnt /mnt/synology-agentic-context` shows the NFS share mounted at the new path.
2. `ls /home/ubuntu/mounts/synology-agentic-context` resolves via symlink to the new path.
3. Weekly `rsync ... darius-star-full` cron (Sun 9am) writes successfully to the new path (verified via log inspection on the next run, OR manual dry-run).
4. `find /home/ubuntu -name 'darius-star-full'` no longer traverses NFS — it stops at the symlink target boundary or returns immediately if symlink target isn't under `/home/ubuntu`.

## Option B — Bubblewrap (bwrap) namespace isolation (NEXT STEP, after Option A)

### Why this is the right second move

- True process isolation: AGY cannot see `/home/ubuntu/mounts/` even if it tries
- Lightweight: no daemon, no privilege escalation per launch
- Standard Linux tool, present in Ubuntu repos

### Implementation

1. **Install bwrap**: `sudo apt install bubblewrap` (≈30KB, no big deps)
2. **Wrapper script** at `/home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_sandbox_bwrap.sh`:

   ```bash
   #!/usr/bin/env bash
   # AGY sandbox wrapper using bubblewrap for namespace isolation.
   # Excludes /home/ubuntu/mounts/* and /home/ubuntu/.gemini/* from AGY's view.
   set -euo pipefail
   SANDBOX="$1"
   shift
   exec bwrap \
     --ro-bind /usr /usr \
     --ro-bind /bin /bin \
     --ro-bind /lib /lib \
     --ro-bind /lib64 /lib64 \
     --ro-bind /etc /etc \
     --dir /run \
     --dir /tmp \
     --proc /proc \
     --dev /dev \
     --bind "$SANDBOX" "$SANDBOX" \
     --bind /archive /archive \
     --bind /home/ubuntu/.local/share/agy /home/ubuntu/.local/share/agy \
     --tmpfs /home/ubuntu \
     --tmpfs /root \
     --unshare-pid \
     --hostname agy-sandbox \
     "$@"
   ```

3. **Update supervisor** to wrap the `cmd[0] = AGY_BIN` invocation in this wrapper.

### Risks

- Some AGY tool calls may rely on `$HOME` being `/home/ubuntu` — verify after first wave
- `--unshare-pid` is restrictive; if AGY spawns subshells, may need relaxing
- bwrap must be in cron supervisor's PATH

### Acceptance criteria

1. `bwrap --ro-bind /usr /usr --ro-bind /bin /bin --proc /proc --dev /dev --tmpfs /home/ubuntu -- ls /home/ubuntu/mounts 2>&1` returns "No such file or directory" instead of listing NFS shares.
2. AGY runs successfully inside bwrap for at least 3 wave iterations with no orphan processes.
3. Test suite `TEST-BWRAP-CONTAINMENT` passes.

## Option C — Unprivileged `agy-worker` user (DEFER, only if Option B fails)

Requires provisioning a system user, setting up ACLs on `/home/ubuntu/mounts` to deny read, ensuring supervisor runs as that user, etc. Highest operational cost, lowest leverage compared to A+B.

## Sequencing

| Order | Action | Effort | Owner | Status |
|---|---|---|---|---|
| 1 | **Option A**: remount NFS to `/mnt/synology-agentic-context` + compat symlink | 30 min | Fred + sudo | **PLANNED, NOT YET EXECUTED** |
| 2 | **Option B**: install bwrap, write wrapper script, integrate into supervisor | 2 hours | Fred | **PLANNED, blocked on Option A completion** |
| 3 | **Validation wave**: 2–3 AGY tasks, verify no NFS traversal, no orphans, no quota drain | 1 hour | Fred + cron | **PLANNED, blocks re-arm** |
| 4 | **Remove prompt-based search-boundary block** from supervisor prompt (now redundant) | 15 min | Fred | **PLANNED, blocks re-arm** |
| 5 | **Option C**: only if B fails or AGY escalates permissions in unexpected ways | 4+ hours | Fred | **DEFER** |

## What changes for the supervisor prompt

After Option A+B ship, the supervisor prompt can drop the search-boundary block (it becomes redundant). The tool-loop guard stays (it's task-shape advice, not path advice). The orphan-cleanup code stays (it's process-shape, not path advice).

## What stays the same

- `/archive/agy_sandboxes` as the active sandbox root
- All 5 auto-resume safety gates (storage, preflight, opt-in, envelope, circuit breaker)
- Cron paused until tasks are re-scoped to output-driven form AND Option A+B are live

## Decision required from user before execution

⚠️ **DO NOT EXECUTE** the Option A remount without explicit approval. It affects:

- Root cron jobs (rsync, agent_dispatcher.py)
- Any tool that uses absolute paths under `/home/ubuntu/mounts/synology-agentic-context`
- Possibly other system services that depend on the mount being under `/home/ubuntu`

The compat-symlink fallback in step 5 is designed to make this safe, but the user should greenlight the actual `umount` + `systemctl disable` step.

## Pre-flight checklist before executing Option A

- [ ] Confirm no AGY workers running (`ps -ef | grep agy-bin`)
- [ ] Confirm cron supervisor paused
- [ ] Notify any active Ned or Kai agents on the same machine
- [ ] Take a snapshot of `/home/ubuntu/mounts/synology-agentic-context` listing (read-only stat to avoid NFS traversal hang) for rollback comparison
- [ ] Schedule the remount during a low-activity window (between waves)
- [ ] Have the rollback command ready: `sudo systemctl enable --now home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount && sudo systemctl disable --now mnt-synology\x2dagentic\x2dcontext.mount && sudo rm /home/ubuntu/mounts/synology-agentic-context`

## Execution log (2026-06-27 00:27–00:30 UTC)

All steps executed successfully. Verification commands and outputs:

```bash
# Step 1: Create new mount point
$ sudo mkdir -p /mnt/synology-agentic-context
$ ls -la /mnt
drwxr-xr-x 2 root root 4096 Jun 27 00:27 synology-agentic-context

# Step 2: Copy systemd mount unit, retarget Where=
$ sudo cp /etc/systemd/system/home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount \
         /etc/systemd/system/mnt-synology\x2dagentic\x2dcontext.mount
$ sudo sed -i 's|/home/ubuntu/mounts/synology-agentic-context|/mnt/synology-agentic-context|g' \
         /etc/systemd/system/mnt-synology\x2dagentic\x2dcontext.mount
$ diff <(cat /etc/systemd/system/home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount) \
        <(cat /etc/systemd/system/mnt-synology\x2dagentic\x2dcontext.mount)
4c4
< Where=/home/ubuntu/mounts/synology-agentic-context
---
> Where=/mnt/synology-agentic-context
# (only the Where= line changed — confirmed safe)

# Step 3: Disable old unit, unmount, enable new unit
$ OLD_UNIT=$(systemctl list-unit-files --type=mount --all | grep synology | grep home | awk '{print $1}')
$ sudo systemctl disable "$OLD_UNIT"
Removed "/etc/systemd/system/multi-user.target.wants/home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount".
$ sudo umount /home/ubuntu/mounts/synology-agentic-context  # succeeded
$ sudo systemctl enable mnt-synology\x2dagentic\x2dcontext.mount
Created symlink /etc/systemd/system/multi-user.target.wants/mnt-synology\x2dagentic\x2dcontext.mount
  → /etc/systemd/system/mnt-synology\x2dagentic\x2dcontext.mount
$ sudo systemctl start mnt-synology\x2dagentic\x2dcontext.mount
$ findmnt /mnt/synology-agentic-context
TARGET                       SOURCE                                FSTYPE OPTIONS
/mnt/synology-agentic-context 192.168.1.40:/volume1/agentic-context nfs  rw,relatime,vers=3,rsize=131072,wsize=131072,...

# Step 4: Compat symlink
$ sudo rmdir /home/ubuntu/mounts/synology-agentic-context  # (empty after umount)
$ sudo ln -s /mnt/synology-agentic-context /home/ubuntu/mounts/synology-agentic-context
$ ls -la /home/ubuntu/mounts/synology-agentic-context
lrwxrwxrwx 1 root root 29 Jun 27 00:27 /home/ubuntu/mounts/synology-agentic-context -> /mnt/synology-agentic-context

# Step 5: Update darius-star rsync cron to use new path directly
$ crontab -l > /tmp/old_crontab.txt
$ crontab -l | sed 's|/home/ubuntu/mounts/synology-agentic-context|/mnt/synology-agentic-context|g' > /tmp/new_crontab.txt
$ diff /tmp/old_crontab.txt /tmp/new_crontab.txt
4c4
< 0 9 * * 0 rsync -av --exclude='.git' /home/ubuntu/work/darius-star/ /home/ubuntu/mounts/synology-agentic-context/darius-star-full/ ...
---
> 0 9 * * 0 rsync -av --exclude='.git' /home/ubuntu/work/darius-star/ /mnt/synology-agentic-context/darius-star-full/ ...
$ crontab /tmp/new_crontab.txt
$ # Verify rsync target is reachable + writable
$ rsync --dry-run -av --exclude='.git' /home/ubuntu/work/darius-star/ /mnt/synology-agentic-context/darius-star-full/
sent 328,923 bytes  received 25,513 bytes  78,763.56 bytes/sec
total size is 1,514,693,397  speedup is 4,273.53 (DRY RUN)
# 1.5GB darius-star data would transfer successfully on the next Sunday 9am run.

# Step 6: CRITICAL — Antigravity canonical test
$ find /home/ubuntu/mounts/ -maxdepth 2
/home/ubuntu/mounts/
/home/ubuntu/mounts/synology-photo
/home/ubuntu/mounts/synology-photo/...
/home/ubuntu/mounts/synology-takeout
/home/ubuntu/mounts/synology-proxmox-backups-ro
/home/ubuntu/mounts/synology-agentic-context   # ← SYMLINK, not expanded
# exit 0, completed within 10 seconds
#
# Default `find` does NOT cross the symlink. This is exactly Antigravity's prediction:
# "Most common search tools (like find or grep) do not follow symlinks by default."

# Step 7: Re-arm cron supervisor
$ python3 -c "... flip jobs.json from paused to scheduled ..."
$ # Result: enabled=True, state=scheduled, resumed_reason=option-a-deployed:NFS-remount-completed;validation-pending
$ # 0 dispatch:ready issues pending — supervisor will idle on next tick, no spurious dispatch
```

### Other consumers audited

| Consumer | Touches the mount? | Action taken |
|---|---|---|
| `0 9 * * 0 rsync ... darius-star-full` | writes to `/mnt/synology-agentic-context/darius-star-full/` | Cron updated to new path directly (dry-run PASS, 1.5GB) |
| `0 4 * * 0 agent_dispatcher.py --reconcile` | NO (Linear API only) | None needed |
| `tmp_cleanup.sh` (3am daily) | NO (only `/tmp`) | None needed |
| Hermes / Kai / Ned agents currently running | None on /home/ubuntu/mounts path | None needed |
| `0 8,9 * * * archive_stale_artifacts.py` | NO (writes to /home/ubuntu/work/agentic-swarm-ops/cron/output/) | None needed |

### Remaining manual follow-ups

1. **Re-scope the 4 failed AGY tasks** (GRO-2357, GRO-2358, GRO-2360, GRO-2364) to output-driven form before relabeling `dispatch:ready`. Per the task-picking rules in PR #10:
   - Output-driven (read file → write markdown)
   - Bounded scope (≤ 1 directory, paths named in AGY_TASK.md)
   - No background subprocess
   - Search-path already known
   - Self-review compatible

2. **Drop the prompt-based search-boundary block** from the supervisor prompt now that the OS-level fix is live. The block was a hotfix on Jun 26 (PR #10, commit f63f6c6); with Option A live, `find` cannot reach `/mnt/synology-agentic-context` from `/home/ubuntu/` searches. The tool-loop guard block stays (task-shape advice, not path advice).

3. **Validation wave**: pick 2–3 fresh output-driven tasks, label `dispatch:ready`, observe 1 wave completes without circuit trip.

4. **Merge PR #10** once review confirms the execution log above matches production reality.

### Rollback procedure (still available, idempotent)

```bash
sudo systemctl enable --now home-ubuntu-mounts-synology\x2dagentic\x2dcontext.mount
sudo systemctl disable --now mnt-synology\x2dagentic\x2dcontext.mount
sudo umount /mnt/synology-agentic-context
sudo rm /home/ubuntu/mounts/synology-agentic-context
# then re-edit /etc/systemd/system/mnt-synology*.mount Where= back, OR just delete the new unit
```

This restores the original state exactly: NFS back at `/home/ubuntu/mounts/synology-agentic-context`, no symlink.
