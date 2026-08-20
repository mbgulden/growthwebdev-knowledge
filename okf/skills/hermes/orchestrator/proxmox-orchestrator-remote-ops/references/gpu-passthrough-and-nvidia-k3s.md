# Proxmox GPU passthrough + k3s nvidia-device-plugin — Reference

Captured 2026-08-15 while bringing up 4x RTX 3090 on VM 230 (k3s-node-230) on PVE1 of the "Antigravity" cluster. The cluster identity is from the user's environment; the **mechanics** are general to Proxmox + k3s deployments of any GPU.

## When you need this

- A Proxmox VM has `hostpci` entries pointing at NVIDIA GPUs in `qm config <vmid>`.
- `nvidia-smi` inside the VM sees the GPUs.
- BUT K8s pods can't request `nvidia.com/gpu` — `kubectl describe node` shows no nvidia resources.
- This is the canonical fix.

## Pre-flight: verify the GPU host is actually the right host

**Recipe:** before assuming the user is wrong about which PVE node holds the GPUs, enumerate every online PVE node and check `lspci`:

```bash
for ip in 192.168.1.{200..220}; do
  out=$(sshpass -p "<pw>" ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no \
    -o HostKeyAlgorithms=+ssh-rsa root@$ip "lspci | grep -i nvidia | head -2" 2>/dev/null)
  [[ -n "$out" ]] && echo "$ip: $out"
done
```

LAN IPs differ from Tailscale IPs. The user's "PVE1" might be reachable on `100.114.18.91` (Tailscale) but the SSH path is on `192.168.1.2` (LAN). Both should give the same answer about which host has the GPUs.

**The `lspci` step alone is not enough — also enumerate GPU passthrough on every RUNNING VM on every PVE node.** On the 2026-08-16 scout the agent checked `qm list` / `pvesh get /cluster/resources` which only show allocated CPU/RAM/disk, then concluded PVE2 had no GPU host. VM 231 (k3s-node-231) on PVE2 had `hostpci0: 0000:65:00` (a full RTX 3090) configured but the scout never grepped `hostpci` from `qm config`. Michael had to correct: *"PVE2/vm231 has a 3090 GPU…"*

**Always run this as part of every GPU scout, alongside the `lspci` loop:**

```bash
for ip in 192.168.1.{200..220}; do
  sshpass -p "<pw>" ssh -o ConnectTimeout=3 -o StrictHostKeyChecking=no \
    -o HostKeyAlgorithms=+ssh-rsa root@$ip \
    'for vmid in $(qm list 2>/dev/null | awk "/running/ {print \$1}"); do
       hostpci=$(qm config "$vmid" 2>/dev/null | grep -E "^hostpci[0-9]+" | head -4)
       [[ -n "$hostpci" ]] && echo "VM $vmid: $hostpci"
     done' 2>/dev/null
done
```

This surfaces every VM with GPU passthrough even if its `qm list` row looks unremarkable. Don't conclude a PVE host has "no free GPUs" until both the `lspci` AND the `hostpci` sweeps return nothing for that host.

## Layer 1: Proxmox hostpci

A Proxmox VM config that passes through 4 GPUs looks like:

```ini
hostpci0: 0000:06:00,pcie=1
hostpci1: 0000:2f:00,pcie=1
hostpci2: 0000:86:00,pcie=1
hostpci3: 0000:af:00,pcie=1
machine: q35
cpu: host
bios: ovmf
efidisk0: <storage>:vm-230-disk-1,pre-enrolled-keys=1,size=128K
```

The PCIe addresses are physical slots in the host's IOMMU groups. `pcie=1` enables PCIe passthrough (vs `pcie=0` for legacy PCI). The VM must have `machine: q35` (modern PCIe topology) and `cpu: host` for the passthrough to work cleanly.

## Layer 2: VM-level nvidia driver

Inside the VM, the nvidia driver must be loaded:

```bash
lsmod | grep nvidia
# Should show: nvidia_uvm, nvidia_drm, nvidia_modeset, nvidia

ls /dev/nvidia*
# Should show: /dev/nvidia0 /dev/nvidia1 /dev/nvidia2 /dev/nvidia3
#               /dev/nvidiactl /dev/nvidia-uvm /dev/nvidia-uvm-tools

nvidia-smi
# Should show a table with each GPU's name, memory, temperature
```

If `nvidia-smi` says "couldn't communicate with the NVIDIA driver", the driver is not loaded — install via `apt-get install -y nvidia-driver-535` (or whichever matches the kernel). The CUDA toolkit (`nvcc`) is NOT required for the driver to work — the driver only needs to expose `/dev/nvidia*`.

## Layer 3: nvidia-container-toolkit + CDI

For GPU access from inside containers, install `nvidia-container-toolkit` and generate the CDI spec:

```bash
apt-get install -y nvidia-container-toolkit
nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
nvidia-ctk runtime configure --runtime=containerd \
  --config=/var/lib/rancher/k3s/agent/etc/containerd/config.toml
systemctl restart k3s
```

The CDI spec (`/etc/cdi/nvidia.yaml`) describes the device files and library mounts that should be injected into a container that requests `nvidia.com/gpu`. The `runtime configure` step adds the `nvidia` runtime to containerd so pods with `runtimeClassName: nvidia` get the nvidia runtime.

After this, you should see `nvidia` listed in `kubectl get runtimeclass`:
```
NAME                  HANDLER
crun                  crun
nvidia                nvidia          <-- this is what we just added
nvidia-experimental   nvidia-experimental
```

## Layer 4: nvidia-device-plugin DaemonSet

The device plugin is what advertises `nvidia.com/gpu` to the kubelet. Without it, the kubelet doesn't know about GPUs. Without the device plugin on every node, pods can't request GPU resources.

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nvidia-device-plugin-daemonset
  namespace: kube-system
spec:
  selector:
    matchLabels: {name: nvidia-device-plugin-ds}
  template:
    metadata:
      labels: {name: nvidia-device-plugin-ds}
    spec:
      priorityClassName: system-node-critical
      hostNetwork: true
      runtimeClassName: nvidia            # POD LEVEL — not container level
      nodeSelector: {kubernetes.io/hostname: k3s-node-230}
      tolerations:
      - effect: NoSchedule
        key: nvidia.com/gpu
        operator: Exists
      containers:
      - name: nvidia-device-plugin-ctr
        image: nvcr.io/nvidia/k8s-device-plugin:v0.14.5
        env:
        - name: FAIL_ON_INIT_ERROR
          value: "false"
        - name: NVIDIA_VISIBLE_DEVICES
          value: "all"
        securityContext:
          allowPrivilegeEscalation: false
          capabilities: {drop: [ALL]}
        volumeMounts:
        - name: device-plugin
          mountPath: /var/lib/kubelet/device-plugins
      volumes:
      - name: device-plugin
        hostPath: {path: /var/lib/kubelet/device-plugins}
```

**Critical pitfall:** `runtimeClassName: nvidia` goes on the **pod** spec, not the container spec. Setting it on the container is rejected with:
```
strict decoding error: unknown field "spec.template.spec.containers[0].runtimeClassName"
```
at least in k3s v1.34. v1.35+ may differ.

**Useful version discovery:** the v0.17.x device-plugin images moved under `nvcr.io/nvidia/k8s-device-plugin:v0.17.0` etc., but the older v0.14.5 still works for the basic "advertise GPUs" case. If v0.17.x fails to deploy (image pull errors), fall back to v0.14.5 — same API surface for our purposes.

## Diagnosing "VM is running but unresponsive"

A VM may report `qmpstatus: running` to the PVE host while the guest OS is broken (kernel panic, network interface down, partial boot). On 2026-08-16 VM 231 (PVE2) showed:

- `qm status 231` → `status: running`, `uptime: 134786` (~37 hours)
- `qm guest exec 231` → `QEMU guest agent is not running` (immediate fail)
- `ping 192.168.1.231` → 100% packet loss
- `kubectl describe node k3s-node-231` → `nodes "k3s-node-231" not found` (not in cluster)

**Diagnostic ladder when a "running" VM doesn't respond:**

```bash
# 1. Confirm QEMU itself is alive
sshpass -p "<pw>" ssh root@<host> \
  '(echo "{\"execute\":\"qmp_capabilities\"}"; echo "{\"execute\":\"query-status\"}"; sleep 1) \
   | socat - UNIX-CONNECT:/var/run/qemu-server/<vmid>.qmp,shut-down'
# Expect: {"return": {"status": "running", "running": true}}

# 2. Check the guest agent socket exists
sshpass -p "<pw>" ssh root@<host> ls -la /var/run/qemu-server/<vmid>.qga
# If missing → agent was never started or crashed; VM needs restart to re-init

# 3. Check the VM has any networking at all from the bridge
sshpass -p "<pw>" ssh root@<host> \
  'arp -an | grep <vmid-known-mac-prefix>'
# Empty → guest never brought up its NIC; treat as half-booted
```

**Recovery paths when QEMU is alive but the guest is half-booted:**

- **Hard reset:** `qm stop <vmid> --skiplock true` then `qm start <vmid>` (loses any in-VM state)
- **Send a clean shutdown via QEMU monitor:** `socat - UNIX-CONNECT:/var/run/qemu-server/<vmid>.qmp` → `{"execute":"qmp_capabilities"}` then `{"execute":"guest-ping"}` or `{"execute":"powerdown"}` to test if the guest agent responds at all
- **Re-enable guest agent:** boot the VM with `agent: 1` (already in config) and confirm `qemu-guest-agent` is running inside the VM

A VM that's `running` to QEMU but unresponsive to the agent and network for 24+ hours is almost certainly in a kernel-level stuck state. Don't try to use the GPU from it — plan for a hard reset before deploying workloads.

## Verifying the layers

After all 4 layers are in place, the check sequence is:

```bash
# 1. Host sees GPUs
ssh <vm> nvidia-smi
# → table with N GPUs

# 2. K8s node advertises GPUs
kubectl describe node <vm-name> | grep -A30 "Capacity:" | grep nvidia
# →  nvidia.com/gpu: 4

# 3. Pod can schedule on a GPU
kubectl apply -f - <<'EOF'
apiVersion: v1
kind: Pod
metadata: {name: gpu-smoke}
spec:
  restartPolicy: Never
  runtimeClassName: nvidia
  nodeSelector: {kubernetes.io/ hostname: <vm-name>}
  containers:
  - name: smoke
    image: nvidia/cuda:12.2.0-base-ubuntu22.04
    command: ["nvidia-smi"]
    resources: {limits: {nvidia.com/gpu: 1}}
EOF
sleep 15
kubectl logs gpu-smoke
# → nvidia-smi table showing 1 GPU allocated
```

If layer 3 passes but layer 4 fails, the device-plugin logs are the diagnostic:
- `Detected non-NVML platform: could not load NVML library: libnvidia-ml.so.1: cannot open shared object file` → not using the nvidia runtime
- `Detected non-Tegra platform: /sys/devices/soc0/family file not found` → informational, fine
- `Registered device plugin for 'nvidia.com/gpu' with Kubelet` → success

## Per-GPU pod allocation pattern

Once `nvidia.com/gpu: 4` is advertised, pods can pin to specific GPUs two ways:

```yaml
# By index — pod sees GPUs 0 and 1 only
env:
- name: NVIDIA_VISIBLE_DEVICES
  value: "0,1"
resources:
  limits: {nvidia.com/gpu: 2}

# All GPUs — pod sees all of them
env:
- name: NVIDIA_VISIBLE_DEVICES
  value: "all"
resources:
  limits: {nvidia.com/gpu: 4}
```

The kubelet enforces that `nvidia.com/gpu` requests across pods on the same node sum to ≤ the node's capacity. So 4 pods requesting 1 GPU each fit; a pod requesting 2 needs the node to have ≥ 2 free at scheduling time.

For a multi-tenant setup where Kai uses GPU 2 and Ned uses GPU 3, the pattern is:
- Kai deployment: `NVIDIA_VISIBLE_DEVICES=2`, `nvidia.com/gpu: 1`
- Ned deployment: `NVIDIA_VISIBLE_DEVICES=3`, `nvidia.com/gpu: 1`
- Each pinned to a specific GPU. No scheduling contention.

## Common error: "0/1 nodes are available: 1 Insufficient nvidia.com/gpu"

This is the kubelet saying "no GPU resources available on the target node." Two causes:

1. The nvidia-device-plugin isn't running on the target node. Check `kubectl -n kube-system get pods -o wide | grep nvidia`.
2. The target node has 0 GPUs. Check `kubectl describe node <name> | grep -A30 "Capacity:" | grep nvidia`. If empty, the device plugin ran but found no GPUs (nvidia-smi inside the VM would also be empty).

## Live transcript (2026-08-15 VM 230 bring-up)

The transcript captured during the actual bring-up of VM 230 + 4x RTX 3090 + nvidia-device-plugin + first GPU pod:

- **05:39 UTC** — VM 230 restored from `vzdump-qemu-230-2026_04_09-15_22_26.vma.zst` on Synology NAS. `qmrestore` returned success after ~70 seconds.
- **05:41 UTC** — `qm start 230` → VM boot. `qm guest exec 230 -- bash -c 'hostname'` returned `k3s-node-230` after ~30 seconds.
- **05:42 UTC** — `nvidia-smi` inside VM 230 showed 4 RTX 3090s, each with 24 GB memory.
- **05:43 UTC** — Kubeconfig recovered from `qm guest exec 230 -- bash -c 'cat /etc/rancher/k3s/k3s.yaml'`. Server pointed at `https://192.168.1.230:6443`. `kubectl get nodes` showed `k3s-node-230 Ready`.
- **05:44 UTC** — `nvidia-ctk cdi generate` and `nvidia-ctk runtime configure` completed. `systemctl restart k3s` reloaded the runtime config.
- **05:45 UTC** — Default nvidia-device-plugin v0.14.5 deployed. Logs showed `Detected non-NVML platform: could not load NVML library`. Pods pending with `Insufficient nvidia.com/gpu`.
- **05:47 UTC** — DaemonSet patched to add `runtimeClassName: nvidia` at pod level. New pod started. Logs showed `Detected NVML platform: found NVML library` and `Registered device plugin for 'nvidia.com/gpu' with Kubelet`. `kubectl describe node` showed `nvidia.com/gpu: 4`.
- **05:48 UTC** — gpu-test pod completed, logs showed `nvidia-smi` table with GPU 0 in use.

End of the verified sequence. Remaining work (model deployment, llama-server pods, service exposure) was cut off at the iteration cap but the GPU plumbing was fully working.

## Reference patterns from the running deployment

The K8s manifests for Kai and Ned as llama-server pods were written to `/tmp/kai-ned-llama.yaml` during the session. The pattern was:

- `Namespace: llm-inference`
- `PersistentVolume` (hostPath, ReadOnlyMany) → `PersistentVolumeClaim` for the 17 GB GGUF
- `Deployment kai-llama`: `runtimeClassName: nvidia`, `NVIDIA_VISIBLE_DEVICES=2`, `--n-gpu-layers 99`, `--ctx-size 32768`, port 8002
- `Service kai`: NodePort 31002 → 8002
- `Deployment ned-llama`: same shape, `NVIDIA_VISIBLE_DEVICES=3`, port 8003
- `Service ned`: NodePort 31003 → 8003

Apply with `KUBECONFIG=/tmp/k3s230-clean.yaml kubectl apply -f /tmp/kai-ned-llama.yaml` and verify with `KUBECONFIG=/tmp/k3s230-clean.yaml kubectl -n llm-inference get pods -o wide`.
