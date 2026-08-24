---
type: Standard
title: Ned vLLM Instance — Ned vLLM (Qwen3.8-27B AWQ, GPU 2+3, :8003)
status: live
owner: kai
updated: 2026-08-24
tags: [vllm, inference, vm230, ned, qwen3.8-27b, awq]
resource: okf/standards/vllm-ned-awq-qwen38-27b.md
git_path: okf/standards/vllm-ned-awq-qwen38-27b.md
---

# Ned vLLM Instance

Cutover 2026-08-24 (Kai, on Michael's directive): Ned's llama.cpp server on
VM230 replaced with a **copy of Fred's vLLM setup** — same model checkpoint,
same proven flags — on GPUs 2/3, same port (8003), so consumers needed **zero
config changes**.

## Topology

| Field | Value |
|---|---|
| Service | `vllm-ned.service` (same unit name as the old llama.cpp unit; backup: `vllm-ned.service.bak-llama-20260824`) |
| Start script | `/opt/vllm_bin/start_ned.sh` (old: `start_ned_vm230.sh`, retained on disk) |
| Log | `/tmp/ned_vllm_service.log` |
| GPUs | **2 + 3** (`CUDA_VISIBLE_DEVICES=2,3`, TP2) — Fred owns 0/1 |
| Port | **8003** (unchanged — Ned's profile provider block `qwen27b-ned-local` points at `http://192.168.1.230:8003/v1`) |
| Model | `/models/barrydeen-Qwen3.8-27B-AWQ-4bit` (same AWQ checkpoint as Fred; verified to include the 333 `model.visual.*` tensors — multimodal) |
| Flags | Identical to Fred's final config: `--spec-method mtp --spec-tokens 1 --kv-cache-dtype fp8 --max-model-len 262144 --max-num-seqs 64 --gpu-memory-utilization 0.96 --enable-prefix-caching --enable-auto-tool-choice --tool-call-parser qwen3_xml --reasoning-parser qwen3 --disable-custom-all-reduce` |
| Served names | `/models/qwen3.8-27b-q5/Qwen3.8-27B-UD-Q5_K_M.gguf` (legacy — Ned's profile sends the GGUF path as model id; **kept for zero-config cutover**), `local-qwen-27b-q5-ned`, `qwen3.8-27b-ned` |
| Enabled | yes (survives reboot) |

## Verification (live, 2026-08-24)

| Check | Result |
|---|---|
| Engine ready after restart | ~155s, service active + enabled |
| GPU 2/3 | 23,418 MiB each (Fred on 0/1 at 23,484 — fully isolated) |
| Single-stream, legacy model name | **30.0 tok/s** (256 tok) |
| Batch-4 aggregate | **120.9 tok/s** (per-req ~30.1) |
| Vision (data-URL image) | OK — image processed, response in `reasoning` field (Qwen thinking) |
| Tool call (OpenAI tools) | OK — `get_weather {"location": "Honolulu"}` |
| Old llama.cpp process | gone (0 processes) |

**vs replaced llama.cpp (Q5_K_M, single GPU 3, MTP draft 4):** 6.7 → 30.0 tok/s
single (**4.5×**), 22.7 → 120.9 tok/s batch-4 (**5.3×**). Quant effectively the
same class (AWQ 4-bit vs Q5_K_M GGUF); the win is the runtime.

## Cutover procedure (reusable)

1. `cp /etc/systemd/system/vllm-ned.service vllm-ned.service.bak-llama-<date>`
2. Write `start_ned.sh` as a copy of `start_fred.sh` with `CUDA_VISIBLE_DEVICES=2,3`,
   port 8003, and the **legacy GGUF path as first served-model-name**.
3. In-place Python edit of the unit (ExecStart, Description, log path) — no
   `sed -i` on bind-mounted/shared files.
4. `daemon-reload`, `stop` (gap begins), `start`, poll `/v1/models` for the
   legacy name (~3 min), then benchmark + vision + tool-call smoke tests.

## Notes

- Quantization note: the legacy served name says Q5 but the weights are AWQ 4-bit
  — intentional, keeps every existing consumer (Ned's profile, cron jobs, aux
  blocks) working unmodified. If anyone queries `max_model_len`, expect 262144.
- Old llama.cpp artifacts left in place (`/opt/llama_bin/`, GGUFs in
  `/models/qwen3.8-27b-q5/`) — no deletion without approval; they are the
  rollback path along with the unit backup.
- Full fleet benchmark matrix incl. Kai's llama.cpp: `okf/standards/vllm-fred-awq-qwen38-27b.md` (PR #44).
