# vLLM Switch — 2026-08-15 (session detail)

Michael's directive: Fred (not Kai) executes the llama.cpp → vLLM switch on k3s-node-230 because vLLM generations should theoretically be faster. Kai's role: recon + brief + post-deploy benchmark.

## Verified recon (Kai, via `ssh root@192.168.1.230`)
- 3 llama.cpp servers as **k3s workloads** in ns `llm-inference`:
  - `kai` :8002 → NodePort 31002, `--alias local-qwen-27b-q4-kai`
  - `ned` :8003 → NodePort 31003, `--alias local-qwen-27b-q4-ned`
  - `newfred-llama-svc` :8001 → NodePort 31001, `--alias local-qwen-27b-q5-fred` (Q5 variant, ctx 1048576, `--split-mode layer --tensor-split 1,1`)
  - Common flags: `--flash-attn on --cont-batching --n-gpu-layers 99 --cache-type-k q4_0 --cache-type-v q4_0 --mmproj mmproj-F16.gguf`
- iptables: k3s kube-proxy DNAT rules `llm-inference/kai:http` → 31002, etc.
- GPU: 4× RTX 3090 24GB, each ~23GB used (driver 535.288.01)
- Disk: `/` = 97G total, 66G used, **31G free** (69%)
- RAM: 62Gi total / 51Gi available
- `/models/`: qwen3.8-27b-q4 (Q4_K_M gguf + mmproj-F16), qwen3.8-27b-q5 (Q5_K_M gguf) — **no safetensors**
- HF reachable (HTTP/2 200). Python 3.10.12, pip 22.0.2 (system, likely needs a venv/container for vllm).

## Blockers surfaced to Michael
1. **Vision regression risk** — vLLM can't use GGUF+mmproj. Keep-vision ⇒ pull native safetensors VL weights (bigger, needs matching vLLM build); text-only ⇒ quantized safetensors, Kai falls back to tesseract OCR. Decision parked with Michael; Fred to ping with specific repo + size before pulling.
2. **Disk 31GB** — BF16 27B (~54GB) won't fit; AWQ/GPTQ-Int4 (~15–18GB) required.
3. **k3s, not processes** — swap the pod, keep Service + NodePort so zero Hermes config change.

## Brief staged for Fred
`/home/ubuntu/work/fred-vllm-switch-brief.md` (pattern: verified recon + hard constraints + endpoint-preservation rule + definition of done + "leave a live endpoint for Kai to benchmark — don't mark done on pod green").

## Open (at session end)
- Awaiting Michael's vision decision + Fred's deploy.
- Kai to benchmark old-vs-new (same hard prompt, wall time + think-chars) and re-probe the `reasoning_effort` dial on vLLM — the `extra_body.reasoning_effort` path is a llama.cpp behavior and is NOT guaranteed on vLLM.

## Cross-profile note
`local-llm-inference-ops` (this skill) should be installed to **Fred** (executor) and **Ned** (consumer of :31003) after the switch lands. Fred's model config also points at :31001 (`local-qwen-27b-q5-fred`) — included in the endpoint-preservation list.
