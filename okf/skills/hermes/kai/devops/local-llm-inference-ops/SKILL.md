---
name: local-llm-inference-ops
description: "Operate, scale, migrate, or benchmark the local LLM inference stack (llama.cpp / vLLM) on PVE1's k3s GPU node that backs Hermes profiles (kai/ned/fred). Use when: switching inference backends, adding a new per-profile model instance, debugging model endpoints :31001/:31002/:31003, benchmarking generation speed before/after a change, or when a model capability (e.g. vision) is about to change."
category: devops
tags: [vllm, llama-cpp, k3s, proxmox, gpu, inference]
related_skills: [qwen-llamacpp-reasoning-effort, tailscale-lan-access]
---

# Local LLM Inference Ops (PVE1 GPU cluster)

Class of work: deploying, operating, migrating, and benchmarking the local model servers behind the Hermes profiles. They run as **k3s workloads** (not bare processes) on `k3s-node-230` (Proxmox VM 230 on pve1). Access: `ssh root@192.168.1.230` (LAN) or `root@100.78.237.7` (tailscale) — see `tailscale-lan-access`.

## Topology (verified 2026-08-18 — supersedes 2026-08-15 table)

| systemd service on .230 | port | GPU | served model | consumer |
|---|---|---|---|---|
| `vllm-george.service` (script `/opt/vllm_bin/start_george.sh`) | **8002** | 2 | Qwen3.8-27B Q4 (`-np 1 -c 131072 --mmproj --spec-type draft-mtp`) | George profile |
| `vllm-ned.service` (script `/opt/vllm_bin/start_ned_vm230.sh`) | **8003** | 3 | same | Ned profile |
| `llama-fred.service` (llama.cpp :8000, GPU 0) | — | — | — | **REMOVED 2026-08-18** (unit+start script moved to `*.removed-20260818-161552`; Fred uses vLLM via `vllm-fred.service`) |
| VLLM::Worker_TP0/TP1 (pids ~56608/56609) | :8000 via python3 | 0+1 (TP2, ~23.5GB each) | ? | unknown/legacy |

- Profile configs hit `http://192.168.1.230:8002/v1` and `:8003/v1` directly — the old k3s NodePort 31001/2/3 table is STALE; nothing listens on those.
- 2026-08-18 change: both .230 llama servers were `-np 2 -c 65536` → 32768 ctx PER SLOT (the "hard 32k" that broke long sessions). Now `-np 1 -c 131072` (single 3090 holds 17GB Q4 weights + 131k q4 KV fine — verified: loads in ~90s, 2.5GB headroom). Backups: `/opt/vllm_bin/*.sh.bak-ctx-*`.
- Pitfall: `-np N` splits total context across N slots — when debugging "context smaller than -c", check `/slots` (`n_ctx` per slot), not the launch flag.
- Vision LIVE on both: 1×1 red PNG → "Red" via `/v1/chat/completions` base64 data URL (tested 2026-08-18, both old and new configs).
- GPU0/1 VLLM workers = `vllm-fred.service` (Fred's INT8 27B, TP2, :8000, model id `local-qwen-27b-q8-fred`, max_model_len 262144) — live and in use, do not touch.

## Topology (2026-08-15, superseded above)

| k3s service (ns `llm-inference`) | container port | NodePort | served model name | consumer |
|---|---|---|---|---|
| `kai` | 8002 | **31002** | `local-qwen-27b-q4-kai` | Kai profile |
| `ned` | 8003 | **31003** | `local-qwen-27b-q4-ned` | Ned profile |
| `newfred-llama-svc` | 8001 | **31001** | `local-qwen-27b-q5-fred` (Q5) | Fred profile |

- Hardware: 4× RTX 3090 24GB (typically ~23/24GB in normal use), 62GB RAM, **~31GB free on `/`**, HuggingFace reachable from the VM (HTTP 200).
- Model files: `/models/qwen3.8-27b-q4/{Qwen3.8-27B-Q4_K_M.gguf, mmproj-F16.gguf}`, `/models/qwen3.8-27b-q5/Qwen3.8-27B-Q5_K_M.gguf`. **GGUF only — no safetensors on disk.**
- The served model name (llama.cpp `--alias` or vLLM's `/v1/models` id) **must match** the `model:` field in the Hermes profile config — profiles hit `http://192.168.1.230:<NodePort>/v1` and select by name. Renaming the served model breaks the profile unless config follows.

## 2026-08-18 state update (Kai endpoint)

Kai's server is a **direct `llama-server` process on 192.168.1.232:8080**, not a k3s NodePort: `llama-server-new -m /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf --mmproj /models/qwen3.8-27b-q4/mmproj-F16.gguf --spec-type draft-mtp --spec-draft-n-max 4 -ngl 99 -c 131072 -fa on --reasoning-effort medium --port 8080`. Access: `ssh root@192.168.1.232` (shared key, see `tailscale-lan-access`).

**Vision is LIVE and verified**: sent a 2×2 red/blue PNG through `/v1/chat/completions` (base64 data URL) — model answered "red blue" with correct spatial reasoning. Recipe for any future mmproj doubt: the `--mmproj` flag in `/proc/<pid>/cmdline` is necessary but NOT sufficient proof; a live image round-trip is. The server's self-reported "multimodal" capability flag in API metadata is also not proof.

## Backend switch procedure (llama.cpp → vLLM)
1. **Vision check first.** llama.cpp `--mmproj mmproj-F16.gguf` is what gives the model vision; **vLLM does not consume GGUF+mmproj.** Preserving vision requires native safetensors VL weights + a vLLM build supporting that VL arch. Losing it is a capability regression (Kai falls back to tesseract OCR) — get the owner's explicit decision (keep-vision vs text-only) before pulling weights.
2. **Sizing.** BF16 27B (~54GB) does NOT fit the 31GB free. Use AWQ or GPTQ-Int4 safetensors (~15–18GB) so one 24GB 3090 holds weights + KV cache.
3. **Endpoint preservation.** Replace the k3s workload, keep the same Service name + NodePort (31001/2/3) → Hermes profile configs need zero changes. vLLM serves OpenAI-compatible `/v1` by default.
4. **GPU placement.** One 3090 per instance via the k8s nvidia device plugin; tensor-parallel 2 only if KV headroom is tight.
5. **Never run both backends concurrently** — VRAM contention (GPUs already ~23/24GB).
6. **Verify with real traffic:** `curl http://192.168.1.230:<NodePort>/v1/models` + one actual chat-completion round-trip. "Pod is green" is not done.

## Before/after benchmark (never claim "faster" on faith)
- Same hard prompt (multi-bug Python fix), non-streaming, same `max_tokens`, hit old and new endpoints.
- Record: wall time, **think-chars = len(reasoning_content)**, final-answer quality.
- Known Qwen-27B think-chars fingerprints: xhigh/high ≈ 10.7–11k, medium ≈ 6k, low ≈ 3.6–4.6k, none = 0 (effort-dial mechanics live in `qwen-llamacpp-reasoning-effort`).
- Set expectations honestly: llama.cpp with `flash-attn on + cont-batching + n-gpu-layers 99 + q4 KV` is near the single-stream ceiling. vLLM's real wins are concurrency/throughput (PagedAttention) — a single-stream comparison may show only a modest gain.
- **After any backend switch, re-probe the reasoning dial on the new backend** — accepted `extra_body` fields differ per backend (curl the endpoint with `reasoning_effort` variants and compare think-chars; don't assume the old mechanism still works).

## Pitfalls
- **vLLM :8000 (Fred, INT8 27B) intermittent empty completions (observed 2026-08-18 19:20-19:22):** Hermes logs show `Empty response (no content or reasoning) — retry N/3 (model=local-qwen-27b-q8-fred)` → 3 retries → fallback to gemini-2.5-flash. The endpoint itself was healthy (live completion round-trip ~1s the same evening). This is the Qwen3.8 "reasoning-only" failure mode on vLLM — the model burns output budget on the `reasoning` field and returns null content. Self-heals via Hermes retry/fallback; if frequency climbs, check vLLM `max_tokens`/stop-config on the server and whether MTP spec decoding (`--spec-type draft-mtp`) is implicated. Watch `profiles/<x>/logs/errors.log` (note: for fred, that's a symlink into the orchestrator profile — see `hermes-profile-audit` step 0).
- NodePorts are k3s (kube-proxy chain in iptables: `llm-inference/kai:http` → 31002 etc.) — change the workload, never the NodePort, or you break every profile pointed at it.
- `qm guest exec` does not forward stdin pipes — use the base64 trick (`tailscale-lan-access`).
- Hermes `load_config()` loads the *active* profile and ignores the `HERMES_PROFILE` env var — yaml-load the target profile's `config.yaml` directly when unit-testing wiring.
- When staging work for another agent (e.g. Fred doing the switch), hand over a brief with the verified recon (ps flags, df, port map, /models listing) so it doesn't re-probe — see `references/vllm-switch-2026-08-15.md` for the pattern + that specific recon.

## Session detail
- `references/vllm-switch-2026-08-15.md` — full recon of the 2026-08-15 vLLM switch, constraints, and the brief staged for Fred.
