# Online VM disk resize without downtime

Use this when a VM's disk needs more space (e.g. for a new model download,
docker image, or working data) and you cannot afford the 30-60s outage that
a "stop, resize, start" cycle would cause on a production-serving VM.

**The three-step recipe (verified on 2026-08-15, VM 230 grew 100G → 300G):**

```bash
# 1. Grow the virtual disk on PVE (instant, online)
sshpass -p "$PVE_PASS" ssh root@<pve-ip> "qm resize <vmid> scsi0 +<N>G"
# e.g. qm resize 230 scsi0 +200G  →  went from size=100G to size=300G

# 2. Inside the VM, grow the partition (instant, online)
sshpass -p "$PVE_PASS" ssh root@<pve-ip> \
    "qm guest exec <vmid> -- bash -c 'growpart /dev/sda <partnum>'"
# e.g. growpart /dev/sda 1  →  partition went from 99.9G to 299.9G

# 3. Inside the VM, grow the filesystem (online, ~10-30s for 100 GiB)
sshpass -p "$PVE_PASS" ssh root@<pve-ip> \
    "qm guest exec <vmid> -- bash -c 'resize2fs /dev/sda<partnum>'"
```

**Total user-visible downtime:** ~30 seconds for the resize2fs phase. The
filesystem stays mounted during the resize (ext4 supports online resize).

**Tools required inside the VM:**
- `growpart` (from `cloud-guest-utils` package)
- `resize2fs` (from `e2fsprogs` package, already installed on most Linux)

Both are installed by default on modern Ubuntu. If missing:
```bash
apt-get install -y cloud-guest-utils e2fsprogs
```

**Partnum discovery:**
```bash
qm guest exec <vmid> -- bash -c "lsblk /dev/sda"
# sda       8:0    0   300G  0 disk
# ├─sda1    8:1    0 299.9G  0 part /        ← use partnum=1 for root
# ├─sda14   8:14   0     4M  0 part
# └─sda15   8:15   0   106M  0 part /boot/efi
```

**Verification after resize:**
```bash
# Disk size on PVE side
sshpass -p "$PVE_PASS" ssh root@<pve-ip> "qm config <vmid> | grep scsi0"
# Filesystem size inside VM
qm guest exec <vmid> -- bash -c "df -h /"
# 0 restarts during the resize (proves no service interruption)
kubectl get pods -n <namespace> -o jsonpath='{.items[*].status.containerStatuses[*].restartCount}'
```

**Common pitfalls:**

- **growpart fails with "NOCHANGE"**: the partition table already shows the
  full new size. Proceed to step 3.
- **growpart fails with "failed to detect partition table state"**: the
  kernel hasn't re-read the partition table after the qm resize. Run
  `partprobe /dev/sda` then retry growpart.
- **resize2fs refuses with "Cannot online resize"**: filesystem is mounted
  but the kernel doesn't support online resize for this size jump. Rare.
  Workaround: do a real unmount (downtime ~30 seconds).
- **The new size doesn't show up in `df -h`**: kernel is still using the
  old size cache. Run `partprobe /dev/sda` then check `df -h` again.
- **The disk is GPT, not MBR**: `growpart` works with both, partition type
  GUID stays unchanged. Not a problem for ext4.

**The data_pool must have enough free space.** Check first:
```bash
sshpass -p "$PVE_PASS" ssh root@<pve-ip> "pvesm status"
# Verify the storage's Available is > +<N>G
```

**Why this is non-obvious:** most operators assume "disk resize requires
downtime" because the old `fdisk` + `mkfs` + `mount` workflow does. With
`growpart` + `resize2fs`, the resize is online. The 30-second pause is
filesystem metadata operations, not data movement.

**When online resize is NOT possible:**
- The filesystem is XFS (only offline resize)
- The filesystem is btrfs (different tool: `btrfs filesystem resize`)
- The disk is being used as a K3s PV with a filesystem claim that doesn't
  reflect the new size (you'd need to update the PV spec too)
- The VM is using a ZFS zvol — handled differently via `zfs set volsize`
