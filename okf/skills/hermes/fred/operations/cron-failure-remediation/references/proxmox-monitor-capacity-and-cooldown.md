# Proxmox monitor capacity + cooldown pattern

Use this when Michael questions noisy Proxmox/resource monitor alerts such as `Load HIGH: 5.x` on a large host.

## Durable lesson

Raw Linux load average is not an alert threshold by itself. It must be normalized against CPU capacity:

```text
load_ratio = load_1m / logical_cpu_count
```

For a 64-thread host, load `5.2` is only `0.08x/core` and should be quiet. For a 4-vCPU host, load `5.6` is `1.40x/core` and can reasonably be high.

Recommended default thresholds after the noisy-alert remediation:

```text
HIGH     load_ratio >= 1.5
CRITICAL load_ratio >= 2.0
```

For high-core Proxmox nodes, absolute load values like `10.1` should stay silent when the normalized ratio is low. Route machine-health alerts through Autobot-owned Telegram credentials only, suppress connectivity-only SSH/Tailscale misses from paging, and use a long per-condition cooldown such as 6h unless Michael explicitly wants tighter paging.

## Investigation sequence

1. Check whether the alert text is from the current script or an old copy:
   - Search all profile scripts for the literal alert header and old format.
   - Check for hardlinks across profiles with `stat -c '%i %n' ...`; if files share an inode, editing one updates both.
2. Verify host capacity from the strongest available source:
   - Prefer Proxmox API `/api2/json/nodes/<node>/status` when credentials are available.
   - Use `cpuinfo.cpus` for logical CPUs and `cpuinfo.cores`/`sockets` for physical topology.
   - Use `/nodes/<node>/qemu` to find VM allocations (`cpus`, `maxmem`, `name`, `vmid`).
3. Distinguish monitor connectivity from host health:
   - SSH/Tailscale failures mean the monitor path is unavailable, not necessarily that the Proxmox node is down.
   - Proxmox API over `https://<pve>:8006` can still work when Tailscale SSH requires an auth check.
4. Fix alert behavior:
   - Include core count and normalized ratio in status/alert text.
   - Do not alert solely on unreachable nodes unless the user wants connectivity paging.
   - Add per-alert cooldown state keyed by stable condition such as `pve6:load:high`.
   - Use a clear cooldown window in the message, e.g. `Alerts (cooldown 10m)`.

## Example facts from the session

Live Proxmox API showed:

```text
pve6: 64 logical CPUs, 32 physical cores, 2 sockets, ~377Gi RAM
webtop-hermes VMID 800: 24 vCPUs, 128Gi RAM
Other running pve6 VMs: k3s-node-235 (16 vCPUs/64Gi), hb-master-3 (8 vCPUs/32Gi)
```

Thus `pve6 Load 5.2` is not high; it is approximately `5.2 / 64 = 0.08x/core`.

## Focused verification recipe

Use a `/tmp/hermes-verify-*.py` tempfile script with mocked `subprocess.run` and `urllib.request.urlopen`:

- Fixture `pve6 cores=64, load=5.6, RAM=41%` → no Telegram payload.
- Fixture `pve6 cores=4, load=5.6, RAM=41%` → one payload containing `Load HIGH`, `4 cores`, and normalized ratio.
- Run the same high fixture twice with the same temporary state file → second payload suppressed by cooldown.
- Assert `py_compile` passes for the changed monitor script.

Report as **ad hoc targeted verification**, not full suite green.
