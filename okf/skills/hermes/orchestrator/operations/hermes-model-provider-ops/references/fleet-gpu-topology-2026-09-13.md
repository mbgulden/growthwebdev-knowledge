# Fleet GPU/LLM server topology — verified 2026-09-13

Source of truth: live `curl /v1/models` against each endpoint + OKF integration docs.
Michael's box topology: pve1 (VM .230, 4× RTX 3090 PCIe-passthrough) + pve3 (VM .232, 48GB VRAM).

## Endpoint map

| Endpoint | Server type | GPU | Model (served alias) | Quant | Served ctx | Arch max | Hermes profile(s) |
|---|---|---|---|---|---|---|---|
| `192.168.1.230:8000/v1` | vLLM | pve1 GPUs 0+1 (TP2) | `local-qwen-27b-q8-fred` | Q8 | 131072 (131k) | 262144 | fred, orchestrator |
| `192.168.1.230:8003/v1` | vLLM (unit name `vllm-ned.service` is a misnomer — runs llama.cpp) | pve1 GPUs 2+3 (tensor split 1,1) | `qwen3.8-27b-ned` (file: `Qwen3.8-27B-UD-Q5_K_M.gguf`) | UD-Q5_K_M | **262144 (256k)** | 262144 | ned |
| `192.168.1.230:8002/v1` | llama.cpp | pve1 (GPU 2, pre-cutover; moved to .232 post 2026-08-22) | `qwen3.8-27b` (file: `Qwen3.8-27B-Q4_K_M.gguf`) | Q4_K_M | 131072 (131k) | 262144 | george |
| `192.168.1.232:8080/v1` | llama.cpp | pve3 (48GB VRAM) | `qwen3.8-27b` (file: `Qwen3.8-27B-UD-Q4_K_M.gguf`) | Q4_K_M | **65536 (65k)** | 262144 | kai |
| `100.78.237.7:11434/v1` | Ollama | GPU node (Tailscale) | Qwen 32B, Hermes 70B | — | varies | — | active-oahu, ai-consulting, autobot (aux) |

## Key facts

- **Ned's `:8003` serves 256k** (`max_model_len=262144`), NOT 131k. The OKF doc `okf/integrations/vllm-ned-q5-gpu23.md` predates the context bump and may say 131k — the server is the truth.
- **George and Kai are NOT on a shared pool.** George is on `.230:8002` (131k served), Kai on `.232:8080` (65k served). Different hosts, different servers.
- **Kai's `:8080` is capped at 65k** by `n_ctx=65536` (server flag), NOT by hardware. The 48GB VRAM + `n_ctx_train=262144` means it can serve up to 256k if the llama.cpp `--ctx-size` is raised.
- **The model is Qwen3.8-27B** everywhere (27.32B params). Quant varies: Q8 (fred), UD-Q5_K_M (Ned), Q4_K_M (George, Kai).
- **Fred's `:8000` also serves** `local-qwen-27b-q4-fred`, `qwen3.8-27b-int8-w8a16`, `qwen3.8-27b-awq-4bit` (multiple quants on one vLLM instance).
- **The old `vllm-george` unit** (which owned GPU 2 on pve1) was stopped 2026-08-22 and `systemctl disable`d 2026-08-23 so it cannot reclaim GPUs 2+3 from Ned on reboot.

## Auth

- `:8000` — vLLM `--api-key`, key in `VLLM_FRED_API_KEY` env (profile `.env`).
- `:8003` — vLLM `--api-key`, key in `VLLM_NED_API_KEY` env (profile `.env`).
- `:8002` — llama.cpp, static key (no OAuth), in george `config.yaml` → `custom_providers.qwen27b-george-local.api_key`.
- `:8080` — llama.cpp, key in `KAI_LLM_API_KEY` env (profile `.env`).
- `11434` — Ollama, no auth (LAN-only).

## OKF docs to keep in sync (update when topology changes)

- `okf/integrations/vllm-ned-q5-gpu23.md` — Ned's server (GPU 2+3, Q5, 256k served).
- `okf/integrations/llama-cpp-george-local-server.md` — George's server (`.230:8002`, Q4_K_M, 131k served).
- **Missing:** a Kai `:8080` server doc (pve3, Q4_K_M, 65k served).
- **Missing:** a fleet topology map (this reference file's content, as an OKF doc).

## Optimal context allocation (Michael's 2026-09-13 question)

Model arch max = 256k (262144). 48GB VRAM per GPU. Options:

**A — raise every server to 256k, one server per profile (recommended for max context):**
- Ned `:8003` → already 256k ✓
- George `:8002` → raise `--ctx-size` 131k → 256k (llama.cpp flag on pve1)
- Kai `:8080` → raise `--ctx-size` 65k → 256k (llama.cpp flag on pve3)
- Fred `:8000` → check/raise vLLM `--max-model-len` to 262144
- Then set every profile's `compression.context_length` + `auxiliary.compression.context_length` to 262144.
- Requires: server flag changes on pve1/pve3 (SSH or AGY), then profile config bumps + gateway restarts.

**B — keep servers as-is, align configs to served values:**
- Ned 256k, George 131k, Kai 65k, Fred 131k.
- No server changes; just fix the profile `context_length` values to match what's served.

**Constraint:** Hermes Agent hard floor is `context_length` ≥ 64,000. Kai's 65k is just above the floor; don't lower it. If Kai's server stays at 65k, his profile `context_length` must be ≤ 65536.
