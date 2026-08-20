# Antigravity PVE Cluster — Hardware & VM Map (as of 2026-08-16)

Session-specific snapshot of the cluster's GPU distribution and VM inventory. Load when planning workload placement, when answering "which PVE has GPUs?", or when scoping a migration like moving a model off PVE1 onto an idle GPU elsewhere.

## PVE nodes & their GPUs

| PVE   | LAN IP          | GPUs                | RAM (GiB) | Tailnet status (Aug 2026) |
|-------|-----------------|---------------------|-----------|----------------------------|
| pve1  | 192.168.1.2     | **4× RTX 3090**     | 386       | Authenticated              |
| pve2  | 192.168.1.201   | **1× RTX 3090** (DELL Precision 5820, **VT-d disabled in BIOS, GPU unusable**) | 124       | `NeedsLogin` (browser auth required) |
| pve3  | 192.168.1.202   | **1× RTX 3090**     | 62        | `NeedsLogin`               |
| pve6  | 192.168.1.205   | **0 GPUs**          | 124       | Authenticated              |

**Critical reality:** Only PVE1 and PVE3 have GPUs. PVE2 and PVE6 are CPU-only. Migration plans that assume otherwise will fail at the GPU-passthrough step.

## GPU inventory by host

| Host    | GPUs (Bus IDs)                                   | Status                       |
|---------|--------------------------------------------------|------------------------------|
| pve1    | `0000:06:00`, `0000:2f:00`, `0000:86:00`, `0000:af:00` | All 4 attached to VM 230 via `hostpci0-3` |
| pve2    | `0000:65:00`                                     | Attached to VM 231 via `hostpci0` — **UNUSABLE**: PVE2 is Dell Precision 5820 (workstation), BIOS has VT-d disabled, IOMMU type is `identity` not `DMA-FQ`. See `references/gpu-passthrough-iommu-failure-mode.md`. |
| pve3    | `0000:b3:00`                                     | Attached to VM 232 via `hostpci0` |

## VMs of interest

| VMID | Name                  | Node  | RAM (GiB, post-2026-08-16 resize) | GPUs  | Role                                    |
|------|-----------------------|-------|-----------------------------------|-------|-----------------------------------------|
| 230  | k3s-node-230          | pve1  | 64                                | 0,1,2,3 | Independent K3s server, runs Fred (TP=2), Kai, Ned |
| 231  | k3s-node-231          | pve2  | 8                                 | 0 (pass-through configured but **unusable**: BIOS VT-d disabled) | CPU-only K3s agent. **Dell Precision 5820 hardware — RTX 3090 in `hostpci0` cannot be passed through.** See `references/gpu-passthrough-iommu-failure-mode.md`. |
| 232  | k3s-node-232          | pve3  | 32                                | 0     | K3s agent, **idle GPU** (1× RTX 3090 available) |
| 233  | (template / partial)  | (cluster)| -                              | -     | ERROR in cluster API — incomplete metadata |
| 234  | k3s-node-234          | (cluster)| -                              | -     | NotReady                                |
| 235  | k3s-node-235          | pve6  | 64                                | 0     | K3s agent                               |
| 236  | k3s-node-236          | (cluster)| -                              | -     | NotReady                                |
| 241  | hb-master-1           | pve2  | 8                                 | -     | **K3s control plane** (hb cluster). Was 32 GiB → reduced 2026-08-16 (only 1 GiB used) |
| 242  | hb-master-2           | (cluster)| -                              | -     | NotReady control plane                  |
| 243  | hb-master-3           | pve6  | 32                                | -     | K3s control plane (hb cluster)          |
| 800  | webtop-hermes         | pve6  | 128                               | -     | This host (orchestrator)                |
| 993  | sriov-flasher         | pve1  | 2                                 | -     | Restored from backup, stopped           |
| 994  | sriov-flasher         | pve3  | 2                                 | -     | Stopped — NIC bound to `mlx4_core` (cluster networking) |
| 9009 | K3s-GPU-Golden-V5     | pve2  | 32                                | -     | GPU golden template (running)           |
| 9010 | K3s-GPU-Golden        | pve2  | 32                                | -     | GPU golden template (stopped)           |
| 9903 | sriov-flasher-3       | pve3  | 2                                 | -     | Disk missing, no backup                 |

## K3s cluster topology (Antigravity, hb-master-1 cluster)

- **Server (control plane):** `hb-master-1` (VM 241 on pve2, `192.168.1.241`)
- **Nodes (7 total, 138 days old):**
  - Ready: hb-master-1, hb-master-3, k3s-node-232, k3s-node-235
  - NotReady: hb-master-2, k3s-node-234, k3s-node-236
- **kubeconfig:** `/etc/rancher/k3s/k3s.yaml` on hb-master-1; API server `https://192.168.1.241:6443`
- **State:** Cluster is degraded — Cilium operator in `CrashLoopBackOff` (499 restarts over 4m6s loops), many cilium-agent pods in `Unknown` state, `nvidia-device-plugin` DaemonSet present but `0/4` ready. All workloads (`vllm-server`, `open-webui`, etc.) `Pending` for 60-100+ days.
- **Practical implication:** When targeting this cluster for new GPU workloads, **do not** rely on it being healthy. Either fix Cilium first (multi-step, hours) or fall back to path-B deployment on a fresh VM (see `proxmox-k3s-gpu-cluster-ops` skill, anti-pattern "Don't pass `--runtime nvidia` to `ctr run`").

## K3s cluster topology (independent, VM 230 on PVE1)

- **Server (standalone):** VM 230 on pve1, `192.168.1.230`
- **kubeconfig:** `/etc/rancher/k3s/k3s.yaml` on VM 230; API server `https://192.168.1.230:6443`
- **State:** Healthy, single-node cluster, `nvidia-device-plugin` running with `nvidia.com/gpu: 4`. This is where Fred (TP=2 across GPUs 0+1), Kai (GPU 2), and Ned (GPU 3) live.

## VM 230 disk resize recipe (verified 2026-08-15)

Went from 100 GB → 300 GB. Online via `qm resize + growpart + resize2fs`. See `references/online-vm-disk-resize.md`.

## VM 230 to 232 GPU migration recipe (verified 2026-08-16)

For moving a single-GPU workload off PVE1's packed GPUs onto PVE3's idle GPU 0:

1. Verify VM 232 has the GPU and it's idle: `qm guest exec 232 -- nvidia-smi`
2. Generate CDI spec: `nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml`
3. Confirm `conf.d/99-nvidia.toml` exists in containerd's conf.d (k3s default location).
4. Pull or import the `llama-cuda` Docker image into VM 232's containerd.
5. Mount the model files (use `wget` from VM 230's `python3 -m http.server`).
6. Run `ctr run` with `--runtime io.containerd.runc.v2 --annotation io.containerd.cri.accelerator.runtime=nvidia` (NOT `--runtime nvidia` — see skill anti-pattern).
7. Expose a NodePort or use `--net-host` with a fixed port on VM 232's LAN IP.

This is path-B when the hb-master-1 cluster is too degraded to deploy through. VM 232 joined the hb-master-1 cluster as a worker node (already in `kubectl get nodes`), but the cluster's CNI issues make it unusable — so standalone containerd deployment is the right call.

## PVE2 RAM over-provisioning pattern (verified 2026-08-16)

hb-master-1 (241) and k3s-node-231 (231) were both 32 GiB but using 1 GiB and unknown respectively. Both shrunk to 8 GiB via `qm set <vmid> --memory 8192` (hot-plug, no reboot). Cluster state remained healthy (K3s agent reconnected within seconds). Saved 48 GiB of PVE2 RAM.

**Rule for future resize:** always check actual usage (`free -h`) before shrinking. Shrink to comfortably above the working set.

## RAM allocation findings (verified 2026-08-16)

- 4 GiB VMs exist as templates (e.g. `9000 ubuntu-22.04-cloudinit`) but actual control-plane VMs were 32 GiB — massive overprovisioning.
- k3s-node-232 on PVE3 stayed at 32 GiB (still 30 GiB free for LLM workload).
- AI-Worker-1 (103) on PVE2 is 16 GiB but stopped (no ISO mounted, blocked from start).
- The Antigravity cluster's typical RAM budget per node was 32 GiB × N — leaves headroom to bump some VMs down when migrating workloads.