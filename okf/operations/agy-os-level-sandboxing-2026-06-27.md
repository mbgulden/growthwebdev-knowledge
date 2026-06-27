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
