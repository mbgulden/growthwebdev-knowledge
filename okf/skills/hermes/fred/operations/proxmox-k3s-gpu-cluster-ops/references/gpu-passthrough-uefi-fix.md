# GPU Passthrough Failure Modes — VM 231 + PVE2 (Dell Precision 5820)

**Captured:** 2026-08-16, **CORRECTED:** 2026-08-16 (real root cause was VM BIOS, not host IOMMU)

**Initial misdiagnosis:** I first attributed the 98%-CPU-hang-with-GPU-passthrough to broken IOMMU (`/sys/kernel/iommu_groups/0/type = "identity"` on a Dell Precision 5820). Gemini pushed back: `identity` is normal under `iommu=pt` (passthrough mode). Real fix was at the **VM BIOS level**, not the host.

## Two distinct failure modes (both look like "GPU passthrough broken")

| Failure | Symptom | Cause | Fix |
|---|---|---|---|
| VM boot hang (98% CPU, no network) | `hostpci0` configured at boot | **SeaBIOS/i440fx cannot initialize the RTX 3090's large BAR space** (24 GB card) | `bios: ovmf` |
| Hot-plug with `BAR0 is 0M @ 0x0` | `device_add` via QMP works, GPU visible in lspci, but driver fails to probe | Same root cause: BIOS never gave the GPU a proper BAR address | Same fix — `bios: ovmf` |

**Both failure modes are caused by the same thing:** the default SeaBIOS legacy BIOS in PVE VMs doesn't have a large enough MMIO window for a 24 GB RTX 3090. The GPU's BAR0 collapses to 0M at 0x0, the kernel can't probe the device, and the OS either spins at 98% CPU (cold boot) or sees the GPU in lspci but can't drive it (hot-plug).

**Why I missed this initially:** I checked `/sys/kernel/iommu_groups/0/type` and saw `identity`, assumed broken IOMMU, attributed to BIOS VT-d. But `identity` is **normal** when `iommu=pt` is in the kernel cmdline (it tells the kernel to use 1:1 mapping for host devices). `DMA-FQ` is what you see with full translation mode. The smoking gun for **actually broken IOMMU** would be `dmar0/devices/` missing the GPU's VGA function (0000:65:00.0), not `identity` alone.

## The real fix (works without host BIOS access)

**On the PVE host, configure VM 231:**

```bash
qm set 231 --cpu host,hidden=1
qm set 231 --bios ovmf
qm set 231 --hostpci0 0000:65:00,pcie=1,x-vga=0
```

**Three changes that work together:**

1. **`bios: ovmf`** — UEFI replaces SeaBIOS. UEFI has the large MMIO window the RTX 3090 needs for BAR allocation. This is the load-bearing fix.
2. **`cpu: host,hidden=1`** — `host` exposes the actual host CPU instructions (AVX-512, AVX2) inside the VM; `hidden=1` hides the KVM CPU brand string so the guest sees a clean CPU model.
3. **`hostpci0: ...,x-vga=0`** — `x-vga=0` tells QEMU not to treat the GPU as the primary display adapter, leaving it for compute only. The VM's display comes from `vga: serial0` (or VirtIO GPU if you want a virtual display).

**No host reboot required.** `qm set` + `qm stop` + `qm start` is enough. The host kernel cmdline change (`iommu=pt` → `initcall_blacklist=sysfb_init pcie_acs_override=downstream,multifunction`) is **optional polish** from Gemini's plan but not required for the GPU to work.

## Verification (run after the fix)

```bash
# 1. Network reachable
ping -c 2 -W 2 192.168.1.231
# expect: 2/2 received, 0% packet loss

# 2. Guest agent responds
qm agent 231 ping
# expect: returns

# 3. GPU visible in lspci inside the VM
ssh ubuntu@192.168.1.231 'lspci | grep -i nvidia'
# expect: 01:00.0 VGA + 01:00.1 Audio

# 4. nvidia-smi works
ssh ubuntu@192.168.1.231 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader'
# expect: NVIDIA GeForce RTX 3090, 24576 MiB

# 5. Driver loaded (no BAR0 error)
ssh ubuntu@192.168.1.231 'dmesg | grep -i nvrm | tail -5'
# expect: NVRM messages about driver load, NOT "BAR0 is 0M @ 0x0"

# 6. OVMF warning is expected on first boot
# "WARN: no efidisk configured! Using temporary efivars disk."
# This is benign — the VM boots fine; if you want persistent EFI vars, add an efidisk:
# qm set 231 --efidisk0 data_pool:1,format=qcow2,efitype=4m,pre-enrolled-keys=1
```

## After VM is healthy: K3s + GPU setup (the rest of the chain)

Once GPU is visible inside the VM, the remaining steps for serving:

```bash
# 1. NVIDIA container toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y -qq nvidia-container-toolkit

# 2. CDI spec + K3s containerd config
sudo nvidia-ctk cdi generate --output=/etc/cdi/nvidia.yaml
sudo nvidia-ctk runtime configure --runtime=containerd --config=/var/lib/rancher/k3s/agent/etc/containerd/config.toml --set-as-default
echo "default-runtime: nvidia" | sudo tee /etc/rancher/k3s/config.yaml

# 3. Restart K3s + verify
sudo systemctl restart k3s
sleep 30
KUBECONFIG=/etc/rancher/k3s/k3s.yaml kubectl describe node | grep "nvidia.com/gpu"
# expect: Capacity: nvidia.com/gpu: 1, Allocatable: nvidia.com/gpu: 1

# 4. nvidia-device-plugin DaemonSet
kubectl apply -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/main/deployments/container/device-plugin.yaml
kubectl get pods -n kube-system | grep nvidia
# expect: 1/1 Running
```

## When the fix DOESN'T work

If after applying `bios: ovmf` + `cpu: host,hidden=1` + `hostpci0: ...x-vga=0` the GPU still fails:

1. **Check dmesg for the specific error.** `dmesg | grep -iE "nvrm|nvidia|bar"` inside the VM after boot. `BAR0 is 0M @ 0x0` means the BIOS didn't allocate BAR space (your OVMF change didn't take effect — confirm with `qm config 231 | grep bios`).
2. **Confirm the host kernel driver still sees the GPU.** `ls -la /sys/bus/pci/devices/0000:65:00.0/driver` on PVE2 — should show vfio-pci. If it shows nvidia, the GPU is not bound to vfio.
3. **Check Above 4G Decoding in the BIOS** (only matters for older systems without UEFI MMIO support). On modern systems, OVMF in the VM is sufficient.
4. **Try `pcie_aspm=off`** in the host kernel cmdline if you see link training errors.
5. **As a last resort:** enable VT-d in the host BIOS (physical access required). With `iommu=pt` already in cmdline + working DMAR tables (4 dmar0..dmar3), this should already be functional; if it's not, BIOS has it disabled.

## What this means for PVE2 specifically

PVE2 (Dell Precision 5820, Xeon W-2223) was originally diagnosed as "broken IOMMU" because of the `identity` type. **That diagnosis was wrong.** The IOMMU was working all along — `identity` is normal under `iommu=pt`. The VM BIOS was the actual fix point. PVE2's RTX 3090 in VM 231 is now fully operational without any BIOS-level changes on the host.

## Pre-existing "GPU inventory" anti-pattern (still relevant)

The 2026-08-16 scout of PVE2 initially missed the GPU because `qm list` showed k3s-node-231 as a CPU-only worker. The complete inventory recipe:

```bash
for pve in 192.168.1.2 192.168.1.201 192.168.1.202 192.168.1.205; do
    sshpass -p "$PVE_PASS" ssh -o HostKeyAlgorithms=+ssh-rsa root@$pve "
        echo '=== $pve ===';
        echo 'Physical GPUs:';
        lspci | grep -i nvidia;
        echo 'VMs with GPU passthrough:';
        for vmid in \$(qm list | awk 'NR>1 {print \$1}'); do
            if qm config \$vmid 2>/dev/null | grep -q hostpci; then
                echo \"  \$vmid: \$(qm config \$vmid | grep -E '^(name|hostpci)' | tr '\n' ' ')\";
            fi;
        done
    "
done
```

This catches both the physical inventory (lspci) AND the passthrough mapping (qm config grep). Missing either dimension produces incomplete answers.

## Files that capture this

- `/tmp/VM231-GPU-DIAGNOSTIC-REPORT.md` — superseded by this file. Original analysis was wrong.
- `references/gpu-passthrough-iommu-failure-mode.md` — the original (incorrect) diagnosis; kept for the diagnostic recipe but the root cause section is now wrong.
- `references/vm-boot-failure-taxonomy.md` — generic boot failure modes; this is now the fifth mode.