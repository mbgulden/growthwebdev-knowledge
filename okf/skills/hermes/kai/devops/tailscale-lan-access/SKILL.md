---
name: tailscale-lan-access
description: "Verified access map for the local network (192.168.1.0/24) + tailnet, including which SSH keys work where and how to extend key auth to new VMs. Use before SSHing to pve1/k3s-node-230 or when 'permission denied (publickey)' appears against a local server."
category: devops
tags: [tailscale, ssh, proxmox, networking]
related_skills: [hermes-agent]
---

# Tailscale + LAN Access Map (verified 2026-08-15)

All Hermes profiles on this host share one key: `/home/ubuntu/.ssh/id_ed25519` (ed25519, comment `mbgulden@LightBringer`, fingerprint `SHA256:89+z3DAzYC/Suo+j1iaoNubounfupjdW8SUHuSGNalg`). No per-profile keys exist.

## Access matrix (live-tested)

| Host | Tailscale IP | LAN IP | Key auth |
|---|---|---|---|
| webtop-hermes (this box) | 100.83.32.92 | — | local |
| pve1 | 100.114.18.91 | 192.168.1.2 | ✅ root via tailscale IP |
| k3s-node-230 (VM 230; runs Qwen llama.cpp :31001 Fred, :31002 Kai, :31003 Ned — k3s `llm-inference` ns) | 100.78.237.7 | 192.168.1.230 | ✅ root via BOTH tailscale + LAN |
| llm-inference host (runs Kai Qwen-27B `llama-server` :8080 with `--mmproj`; models in `/models/qwen3.8-27b-q4/`) | 100.118.250.83 | 192.168.1.232 | ✅ root via shared key (verified 2026-08-18) |
| pve2/pve3/pve5/pve6 | 100.119.225.27 / 100.115.231.48 / 100.65.32.83 / 100.90.63.4 | — | ⚠️ tailscale offline as of 2026-08-15; no key test |
| bigboy (windows) | 100.98.80.41 | — | offline |

Notes:
- `ubuntu@` does not exist on pve1 (Tailscale SSH: "failed to look up local user") and NOT on k3s-node-230 (key is registered for root only). Use `root@`. `Permission denied (publickey,password)` against a LAN IP on .230 almost always = you typed `ubuntu@`; retry `root@`.
- k3s-node-230 = Proxmox VM 230 on pve1 (`qm config 230` on pve1). Two Qwen 27B llama.cpp servers live there as systemd `vllm-ned.service` (:8003, GPU3) + `vllm-george.service` (:8002, GPU2), start scripts `/opt/vllm_bin/start_{george,ned_vm230}.sh`. As of 2026-08-18 both run `-np 1 -c 131072 --mmproj` (mirroring Kai on .232); older `-np 2 -c 65536` gave 32k per slot. GPU0/1 run VLLM workers.
- `ss -tln`/`netstat` may be absent in the VM; probe llama.cpp via `curl http://192.168.1.230:31002/health`.

## Extend key auth to a new VM (no password needed, via pve1)
Pipe-into-`qm guest exec` does NOT forward stdin — use base64:
```bash
KEY_B64=$(base64 -w0 ~/.ssh/id_ed25519.pub)
ssh root@100.114.18.91 "qm guest exec <VMID> -- bash -c 'echo $KEY_B64 | base64 -d >> /root/.ssh/authorized_keys && chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys && wc -l < /root/.ssh/authorized_keys'"
```
Then verify with a real `ssh root@<lan-or-ts-ip> 'hostname'` — do not trust the exec's exit output alone (`qm guest exec` returns JSON with `exited: 1` even on success paths; read `out-data`).

## Pitfalls
- `Permission denied (publickey,password)` against a LAN IP = key not registered there (or wrong user). Check the matrix, then extend per above.
- `tailscale status` shows relay/direct state — "idle" (k3s-node-230) is fine, the connection dials on demand.
- Fred's `proxmox-orchestrator-remote-ops` skill has PVE1 deployment history + credentials notes; this skill is the access map, that one is the ops playbook.
- PVE API port 8006 is NOT reachable from this box over tailscale (no 8006 on any tailnet node) — use SSH to pve1 for Proxmox work.
