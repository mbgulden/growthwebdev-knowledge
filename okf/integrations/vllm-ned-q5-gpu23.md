---
type: Integration
title: Ned Qwen3.8-27B UD-Q5_K_M on .230 (2-GPU tensor split)
description: Ned's local llama.cpp OpenAI-compatible server at 192.168.1.230:8003 serving Qwen3.8-27B UD-Q5_K_M (19.77GB, multimodal) across guest GPUs 2+3 with a 2-way tensor split; cutover from Q4_K_M single-GPU on 2026-08-22.
resource: okf/integrations/vllm-ned-q5-gpu23.md
tags: [llama.cpp, local-llm, qwen, inference, hermes, ned, integration, tensor-split]
auth_method: static api_key in profile config (no OAuth)
token_storage: /home/ubuntu/.hermes/profiles/ned/config.yaml (custom_providers.qwen27b-ned-local.api_key)
timestamp: 2026-08-22T23:10:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/vllm-ned-q5-gpu23.md
last_verified: 2026-08-22
verified_by: kai
status: current
---

# Ned Qwen3.8-27B UD-Q5_K_M on .230 (2-GPU tensor split)

> **Verified 2026-08-22 by Kai** — live chat + multimodal image round-trip,
> tensor-split confirmation in service logs, and before/after benchmark all
> passed against `192.168.1.230:8003` post-cutover.
>
> **LANE WAIVER (PR #38 precedent):** `okf/integrations/` is Jules's lane.
> This doc lands on a `kai/...` branch under Michael's 2026-07-30 lane grant
> (full control of all Active Oahu + Hawaii tourism projects) with the
> pre-push lane hook bypassed for this commit only.

## TL;DR

Ned's Hermes profile runs against a **local llama.cpp OpenAI-compatible
server** at `192.168.1.230:8003` (VM on pve1, all 4× RTX 3090 are
PCIe-passthrough). On **2026-08-22** the server moved from `Q4_K_M` on a
single guest GPU (GPU 3) to **`UD-Q5_K_M` (19.77GB) across guest GPUs 2+3
with a 2-way tensor split (`1,1`)** plus `--mmproj` vision. Quality and
speed both improved (see Benchmarks). Fred's production vLLM on `:8000`
(guest GPUs 0+1, TP2) was untouched and stayed healthy through the cutover.

The old `vllm-george` unit (which owned guest GPU 2) was stopped
2026-08-22 and **`systemctl disable`d 2026-08-23** so it cannot reclaim
GPUs 2+3 from Ned on reboot.

## Connection

| Field | Value |
|---|---|
| Provider name | `qwen27b-ned-local` |
| Base URL | `http://192.168.1.230:8003/v1` |
| Host | `192.168.1.230` (pve1 VM; root SSH key per `tailscale-lan-access`) |
| Port | `8003` |
| Auth | static API key `llama-local` (no OAuth) |
| Config location | `/home/ubuntu/.hermes/profiles/ned/config.yaml` → `custom_providers.qwen27b-ned-local` |
| Request timeout | `180s` |
| systemd unit | `vllm-ned.service` — **name is a misnomer; it runs llama.cpp** |
| Start script | `.230:/opt/vllm_bin/start_ned_vm230.sh` (Q5, GPU 2+3, `--mmproj`) |
| Pre-cutover backup | `.230:/opt/vllm_bin/start_ned_vm230.sh.bak-q4-20260822` |

### Served model

| Property | Value |
|---|---|
| Weights | `.230:/models/qwen3.8-27b-q5/Qwen3.8-27B-UD-Q5_K_M.gguf` (19.77GB) |
| Vision projector | `.230:/models/qwen3.8-27b-q5/mmproj-F16.gguf` |
| Quant | `UD-Q5_K_M` (Unsloth dynamic Q5) — plain `Q5_K_M` no longer exists upstream; Unsloth keeps only `UD-Q5_K_M` / `UD-Q5_K_S` / `UD-Q5_K_XL` |
| GPU placement | guest GPUs **2+3**, tensor split `(1,1)` — 19.77GB does **not** fit a single 24.5GB 3090 |
| NUMA | guest 2 = host BDF `86:00.0` → NUMA 1; guest 3 = host BDF `af:00.0` → NUMA 1. **Single host NUMA** — no cross-CPU barrier |

## Why the 2-GPU split

1. **Capacity:** 19.77GB weights + KV cache for 131k ctx cannot fit one 24.5GB 3090.
2. **NUMA safety:** guest GPUs 2 and 3 both land on host NUMA 1 (verified host-side BDF map), so a 2-way split stays single-NUMA. The guest itself reports `numa_node=-1` on every GPU (passthrough doesn't expose affinity), so placement can only be validated from the pve1 host: `06:00.0`→0, `2f:00.0`→0, `86:00.0`→1, `af:00.0`→1.
3. **No Fred impact:** Fred's vLLM TP2 stays on guest 0+1 (host NUMA 0) — physically separate NUMA island.

## Benchmarks (2026-08-22, .230/Ned)

Identical hard prompt, non-streaming, harness `/tmp/bench_ned230.py`
(`--endpoints ned230`):

| Metric | Before (Q4_K_M, GPU3) | After (UD-Q5_K_M, GPU2+3) | Delta |
|---|---|---|---|
| chat | 47.5 tok/s | **55.0 tok/s** | +7.5 / **+15.8%** |
| hard | 44.8 tok/s | **48.4 tok/s** | +3.6 / **+8.0%** |

These are the new "no change" anchor for future .230/Ned comparisons.
Artifacts: `~/work/benchmarks/before-q4-ned-gpu3.{report.md,json}` and
`~/work/benchmarks/after-q5-ned-gpu23.{report.md,json}` on the Hermes VM.

## Known failure modes

- **Empty `content` on Q5:** Qwen3.8 is a thinking model. With thinking
  enabled, tokens land in the `reasoning` field and `content` can come back
  empty. Disable thinking for clean verification. (Bench tok/s counts all
  generated tokens regardless of field.)
- **Reboot conflict (RESOLVED 2026-08-23):** `vllm-george` was
  `enabled` + `inactive` after its 2026-08-22 stop; on reboot it would have
  auto-started and contended for GPU 2. Now `systemctl is-enabled` =
  `disabled`. Unit + start script remain on disk (`/etc/systemd/system/vllm-george.service`,
  `.230:/opt/vllm_bin/start_george.sh`) — `systemctl enable vllm-george`
  restores it if ever needed. George profile itself has since moved to
  `192.168.1.232:8080` (llama.cpp mirror box), so this unit is orphaned.
- **Model-name drift:** the Ned profile config's `default_model` still
  points at the Q4 path `/models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf`
  while the server now serves the Q5 GGUF — reconcile after confirming the
  served `/v1/models` id (the served name must match the profile config's
  `model:` field or the profile breaks).

## Ops / recovery procedure

```bash
# status
ssh root@192.168.1.230 "systemctl status vllm-ned --no-pager | head -5"

# restart
ssh root@192.168.1.230 "systemctl restart vllm-ned"

# quick health (expect the Q5 model id)
curl -s http://192.168.1.230:8003/v1/models -H 'Authorization: Bearer llama-local' | head -c 400

# roll back to Q4 (pre-cutover script)
ssh root@192.168.1.230 "cp /opt/vllm_bin/start_ned_vm230.sh.bak-q4-20260822 /opt/vllm_bin/start_ned_vm230.sh && systemctl restart vllm-ned"
```

## Verification evidence (2026-08-22)

- Vision: live 1×1 red PNG round-trip via `/v1/chat/completions` → "Red",
  thinking disabled (clean `content`).
- Tensor split `(1,1)` visible in `vllm-ned` service log lines.
- Chat completion clean, logs error-free.
- Fred `:8000` healthy pre/post (GPU 0+1, TP2, 262k ctx).
