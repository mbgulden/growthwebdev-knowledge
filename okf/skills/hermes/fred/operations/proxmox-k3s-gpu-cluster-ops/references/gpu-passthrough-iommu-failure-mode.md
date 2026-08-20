# GPU Passthrough IOMMU Failure Mode — Dell Precision 5820

**Captured:** 2026-08-16
**Symptom:** VM with `hostpci0` GPU configured boots but hangs at 98% CPU, no network response. Hot-plug works (GPU visible in lspci) but nvidia-smi fails with `BAR0 is 0M @ 0x0`.

## Diagnosis recipe (run on the PVE host, not inside the VM)

```bash
# 1. Confirm the GPU is bound to vfio-pci
ls -la /sys/bus/pci/devices/<bus:dev.fn>/driver
# expect: lrwxrwxrwx .../drivers/vfio-pci

# 2. Check the IOMMU group type — THE smoking gun
cat /sys/kernel/iommu_groups/0/type
# WORKING: DMA-FQ (or any "DMA-*" type)
# BROKEN:  identity ← BIOS VT-d is disabled

# 3. Check whether the GPU is in any DMAR device list
ls /sys/devices/virtual/iommu/dmar*/devices/
# WORKING: both VGA and Audio functions appear (e.g., 0000:65:00.0 + 0000:65:00.1)
# BROKEN:  only Audio function appears; VGA function missing → DMAR table incomplete

# 4. Confirm kernel cmdline (must have intel_iommu=on for Intel CPUs)
cat /proc/cmdline | tr ' ' '\n' | grep -iE 'iommu|vfio'
# expect: intel_iommu=on iommu=pt

# 5. Identify the hardware (Dell workstations often have VT-d disabled by default)
dmidecode -s system-product-name
dmidecode -s bios-version
cat /proc/cpuinfo | grep "model name" | head -1
```

## What "broken IOMMU" looks like

`/sys/kernel/iommu_groups/0/type = identity` is the canonical smoking gun. It means the kernel loaded with `intel_iommu=on iommu=pt` but the BIOS/firmware isn't actually enabling DMA translation. VFIO claims the device (driver binds correctly) but DMA from the GPU bypasses the IOMMU entirely.

**Two failure modes on the GPU side:**

| Failure | Symptom | Cause |
|---|---|---|
| VM boot hang (98% CPU, no network) | `hostpci0` configured at boot | DMA corruption in the guest OS — kernel spin trying to handle failed DMA |
| Hot-plug with `BAR0 is 0M @ 0x0` | `device_add` via QMP works, GPU visible in lspci, but driver fails to probe | GPU's BAR addresses not mapped; OS sees the device but can't talk to it |

## Workarounds (in order of preference)

### 1. Enable VT-d in BIOS (only real fix)
Dell workstations (Precision 5820, 7920, T-series) ship with VT-d **disabled by default**. The setting is usually under:
- **Security → Virtualization → Intel Virtualization Technology for Directed I/O (VT-d)**

Or in some BIOS revisions:
- **Advanced → CPU Configuration → VT-d**

Requires physical/IPMI access. Reboot required. After enabling, the IOMMU type flips from `identity` to `DMA-FQ` and the DMAR device list includes the VGA function.

### 2. Use a different PVE node (when BIOS access unavailable)
PVE1 and PVE3 in the Antigravity cluster have working GPU passthrough (Lenovo ThinkSystem + Dell server, respectively). PVE2's hardware (Dell Precision 5820 workstation) has the disabled-VT-d problem. Move workloads to PVE1 or PVE3 instead.

### 3. Use mdev (mediated devices) — won't work for NVIDIA consumer GPUs
NVIDIA consumer GPUs (RTX 3090 included) don't officially support vGPU/mdev. Skip this option unless you have a Tesla/A100/H100.

### 4. Software passthrough with `enable_unsafe_noiommu=1` (don't do this)
The kernel has an escape hatch `vfio.enable_unsafe_noiommu=1` that allows VFIO without IOMMU. The kernel warns it's a security risk (DMA bypasses IOMMU protection, can read/write host memory). Will make the GPU work in the guest but with no isolation. Don't use for any workload that matters.

## Verification after the fix

Once VT-d is enabled in BIOS and the host reboots:

```bash
cat /sys/kernel/iommu_groups/0/type
# expect: DMA-FQ (NOT identity)

ls /sys/devices/virtual/iommu/dmar*/devices/ | grep <gpu-bus-id>
# expect: both .0 (VGA) and .1 (Audio) functions

# Boot a test VM with the GPU
qm set <vmid> --hostpci0 <bus:dev,pcie=1>
qm start <vmid>
# wait 60s for boot, then:
qm guest exec <vmid> -- nvidia-smi
# expect: GPU appears with VRAM, no BAR0 error
```

## Why Dell workstations ship with VT-d disabled

Dell has a long history of disabling VT-d by default on workstation-class hardware. The reasoning (per Dell support) is that consumer GPUs (GeForce line, including RTX 3090) are not validated for production virtualization, so Dell keeps the setting off to prevent accidental unsupported configurations.

Enterprise GPUs (Tesla, Quadro RTX, A-series) are validated for virtualization, so on those platforms VT-d is usually enabled by default.

The current workaround for the Antigravity cluster is to use PVE1 (Lenovo ThinkSystem server) or PVE3 (Dell server with proper BIOS defaults) for any GPU passthrough workload. PVE2's RTX 3090 in VM 231 is effectively stranded until someone physically accesses the box and enables VT-d in BIOS.

## Files that capture this failure mode

- `/tmp/VM231-GPU-DIAGNOSTIC-REPORT.md` — full session-specific diagnostic transcript (8 KB, shareable with Gemini)
- `references/vm-boot-failure-taxonomy.md` — generic boot failure modes (this is a fifth, GPU-specific mode worth adding)