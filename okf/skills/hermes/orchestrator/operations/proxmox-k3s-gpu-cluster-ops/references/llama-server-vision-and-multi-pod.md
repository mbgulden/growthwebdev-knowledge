# llama-server: vision (mmproj) and multi-pod orchestration on 4× RTX 3090

Distilled from the 2026-08-15 session that wired Qwen3.8-27B as the multimodal
model for the Fred/Kai/Ned pods and from the 2026-08-15 follow-up on Fred's
2× 3090 layer-split deployment. Complements `llama-server-runtime-gotchas.md`
(which covers the runtime traps) with the **before-deploy and across-pod**
discipline.

This file is about **what to download, what to configure, and how to lay out
multiple models across multiple GPU pairs** — not about runtime flag bugs.

---

## 1. Verify the model is multimodal before serving it as text-only

**Symptom:** you deploy a "text-only" GGUF, the pod comes up fine, model loaded,
chat completions work, `/v1/chat/completions` returns 200 OK with a sensible
reply. Months later someone sends an image in a Telegram bot; the bot ignores
it. You discover the model has a vision tower you never loaded.

**Root cause:** Qwen3.8-27B (Aug 2026, Apache 2.0, `pipeline_tag: image-text-to-text`)
ships as a **single HF repo** but splits into **two GGUFs**:

- `Qwen3.8-27B-Q4_K_M.gguf` — text-language weights (~17 GB)
- `mmproj-F16.gguf` — vision encoder weights (~927 MB)

The language-only GGUF works perfectly without the mmproj — you'll never see
an error. You only notice the gap when someone sends an image and gets a
text response that pretends the image wasn't there.

**Recipe to verify before deploying any new model:**

```bash
# 1. Confirm the HF repo exists with the expected pipeline tag
curl -s "https://huggingface.co/api/models/<org>/<model>" | \
    python3 -c "import json,sys; d=json.load(sys.stdin); print('pipeline_tag:', d.get('pipeline_tag')); print('tags:', d.get('tags', [])[:5])"
# Expect: pipeline_tag: image-text-to-text, tags includes 'image-text-to-text'

# 2. List the GGUF siblings to confirm there's a vision projector file
curl -s "https://huggingface.co/api/models/<org>/<model>-GGUF" | \
    python3 -c "
import json,sys
d = json.load(sys.stdin)
for f in d.get('siblings', []):
    n = f.get('rfilename','')
    if 'mmproj' in n.lower() or 'proj' in n.lower() or 'vision' in n.lower() or 'mtmd' in n.lower():
        print('VISION:', n)
"
# Expect at least one mmproj-F16.gguf or mmproj-BF16.gguf file

# 3. Check the model's HF README for the "Type: Causal LM with Vision Encoder" line
curl -s "https://huggingface.co/<org>/<model>/raw/main/README.md" | \
    grep -iE 'vision|Causal LM with Vision|pipeline_tag|image-text-to-text' | head -5
```

If any of the above returns an empty result, you may be looking at a
text-only model. Don't assume.

**Recipe to enable vision on an existing pod:**

```bash
# 1. Download the mmproj
qm guest exec <vmid> -- bash -c "
  cd /models/qwen3.8-27b-q4
  wget -q https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/resolve/main/mmproj-F16.gguf \
       -O mmproj-F16.gguf
  ls -la mmproj-F16.gguf
"
# Expect ~927 MB file

# 2. Add the mmproj to the K8s deployment args:
#    args:
#    - --mmproj
#    - /models/qwen3.8-27b-q4/mmproj-F16.gguf

# 3. Roll the deployment. The mmproj adds ~1 GB VRAM when loaded
#    (loaded once at startup, shared across requests).
```

**Three things to verify after adding `--mmproj`:**

1. **Pod still comes up**, no `unknown architecture` error in startup logs.
   Some older llama.cpp builds (vendored by Ollama pre-April 2026) reject
   `qwen35`/`qwen35moe` architectures when a vision projector is attached.
   Upstream `ggml-org/llama.cpp` from `b5368` onwards handles it.
2. **`/slots` reports the model** — same slot count and `n_ctx` as before.
3. **An image-bearing request returns a vision-aware reply**:
   ```bash
   curl -s -X POST http://<node-ip>:<port>/v1/chat/completions \
       -H 'Content-Type: application/json' \
       -d "$(python3 -c '
   import json, base64
   img_b64 = base64.b64encode(open("/path/to/test.jpg","rb").read()).decode()
   print(json.dumps({
       "model": "<alias>",
       "messages": [{
           "role": "user",
           "content": [
               {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}},
               {"type": "text", "text": "What is in this image?"}
           ]
       }],
       "max_tokens": 100
   }))
   ')" | jq '.choices[0].message.content'
   # Expect a real caption, NOT "I cannot process images" or an empty reply.
   ```

## 2. Pair-aware model layout on 4× RTX 3090

**The hardware reality on a 4× 3090 PVE node:**

- RTX 3090 NVLink connects cards in **pairs only**: (0↔1) and (2↔3).
- Inter-pair communication goes over **PCIe**, not NVLink — bandwidth drops
  from ~100 GB/s to ~16 GB/s and tensor-parallel efficiency craters.

**Implication:** treat the cluster as **two independent GPU pairs**, not four
single GPUs.

**The recommended layout (works well for 27B-72B models):**

```
┌────────────────────────────┐    ┌────────────────────────────┐
│ Pair A (GPUs 0+1, NVLink)  │    │ Pair B (GPUs 2+3, NVLink)  │
│                            │    │                            │
│ One model, layer-split     │    │ One model, layer-split     │
│ across both cards          │    │ across both cards          │
│                            │    │                            │
│ e.g. Qwen3-VL-72B at Q4    │    │ e.g. Qwen3.8-27B-Q5_K_M    │
│ 37 GiB weights, fit at     │    │ 19 GiB weights, fit at     │
│ 262k ctx with q4_0 KV     │    │ 262k ctx with q4_0 KV     │
└────────────────────────────┘    └────────────────────────────┘
```

**The anti-pattern:** treat as 4 single GPUs and run 4 small models. Loses
the NVLink bandwidth and forces you into cheaper quantizations than the
hardware can actually deliver.

**The decision matrix:**

| Model size | Quant | Per-card budget | Card allocation | Notes |
|------------|-------|-----------------|-----------------|-------|
| ≤24B | Q4_K_M / Q5_K_M | ≤19 GiB | **1 card per model** | No layer-split needed; `--n-gpu-layers 99` with `--split-mode none` |
| 24-40B | Q4_K_M | 19-30 GiB | **2 cards layer-split** | `--split-mode layer --tensor-split 1,1` |
| 40-72B | Q4_K_M | 30-46 GiB | **2 cards layer-split** | `--tensor-split 1,1` per pair |
| 70-235B MoE | Q4 / Q3 | 40-80 GiB | **4 cards layer-split** | `--tensor-split 1,1,1,1` (efficiency drops for non-paired GPUs) |

For RTX 3090s, **layer-split per NVLink pair beats 4-way tensor-parallel
across the full node**. The pairing is the gotcha.

## 3. Multi-pod orchestration patterns

**Pattern A: One model per pair, two pods total (recommended start)**

```yaml
# Pair A — Fred (orchestrator, frontier reasoning)
spec:
  replicas: 1
  strategy: {type: Recreate}
  template:
    spec:
      containers:
      - name: llama-server
        image: llama-cuda:v2
        env:
        - {name: NVIDIA_VISIBLE_DEVICES, value: "0,1"}
        resources:
          requests: {nvidia.com/gpu: 2}
          limits:   {nvidia.com/gpu: 2}
        args:
        - --model       # Q5_K_M, full 27B
        - /models/qwen3.8-27b-q5/Qwen3.8-27B-Q5_K_M.gguf
        - --mmproj      # vision enabled
        - /models/qwen3.8-27b-q5/mmproj-F16.gguf
        - --split-mode
        - layer
        - --tensor-split
        - "1,1"
        - --ctx-size
        - "262144"      # n_ctx_train, no YARN needed
        - --cache-type-k
        - q4_0
        - --cache-type-v
        - q4_0
        - --parallel
        - "1"
        - --flash-attn
        - "on"
---
# Pair B — Two single-card pods on GPU 2 and GPU 3
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: llama-server
        env:
        - {name: NVIDIA_VISIBLE_DEVICES, value: "2"}  # Kai
        resources:
          requests: {nvidia.com/gpu: 1}
          limits:   {nvidia.com/gpu: 1}
        args:
        - --model
        - /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf
        - --mmproj
        - /models/qwen3.8-27b-q4/mmproj-F16.gguf
        - --ctx-size
        - "262144"
        - --cache-type-k
        - q4_0
        - --cache-type-v
        - q4_0
```

This is the live 2026-08-15 layout on VM 230: Fred on GPUs 0+1, Kai on GPU 2,
Ned on GPU 3, all at 262k ctx with q4_0 KV cache. Verified working.

**Pattern B: Three independent single-card pods, leaving the second pair idle**

This is the "cheap start" — your three named agents (Fred, Kai, Ned) each get
their own card. The fourth GPU sits idle as headroom for future workloads.
Good for: low-budget, when you don't actually need 4x model capacity.

**Pattern C: One frontier model on 4×, smaller fallback on 2×**

When traffic is mixed — easy tasks on the cheap model, hard ones on the
expensive — split the cluster so:
- 4× 3090: Qwen3-VL-235B-A22B at Q3 (the heavy lifter)
- 2× 3090: Qwen3.8-27B-Q5_K_M (the fallback / specialized)

K8s can run both Deployments in the same `llm-inference` namespace; the device
plugin balances across them.

## 4. Hermes wiring across multiple local llama-servers

When you have N pods on N ports, the Hermes `providers:` block needs one
provider per pod:

```yaml
providers:
  qwen27b-fred-local:        # Pair A (orchestrator)
    api: http://192.168.1.230:31001/v1
    api_key: llama-local
    context_length: 262144
    max_tokens: 4096          # Hermes-side cap (gotcha 12)
    default_model: local-qwen-27b-q5-fred
    models:
      local-qwen-27b-q5-fred:
        context_length: 262144
    name: "Qwen3 27B Q5_K_M (Fred, 2x 3090, vision)"
    request_timeout_seconds: 600

  qwen27b-kai-local:        # Pair B GPU 2
    api: http://192.168.1.230:31002/v1
    api_key: llama-local
    context_length: 262144
    max_tokens: 4096
    default_model: local-qwen-27b-q4-kai
    models:
      local-qwen-27b-q4-kai:
        context_length: 262144
    name: "Qwen3 27B Q4_K_M (Kai, GPU 2, vision)"
    request_timeout_seconds: 600

  qwen27b-ned-local:        # Pair B GPU 3
    api: http://192.168.1.230:31003/v1
    api_key: llama-local
    context_length: 262144
    max_tokens: 4096
    default_model: local-qwen-27b-q4-ned
    models:
      local-qwen-27b-q4-ned:
        context_length: 262144
    name: "Qwen3 27B Q4_K_M (Ned, GPU 3, vision)"
    request_timeout_seconds: 600
```

The `request_timeout_seconds: 600` matters — local LLM inference is slower
than the OpenRouter fallback for long contexts. Default 130s will trip on
80k+ token requests.

The `max_tokens: 4096` on every provider is **required** — see
`references/llama-server-runtime-gotchas.md` Gotcha 12.

## 5. "Should we be fully utilizing VRAM?" — the operating point

**Honest answer:** no — full utilization is a footgun, not a goal. The
operating point is **60-85% per card**, leaving 4-9 GB headroom for:

- Output buffer growth (the model allocates space for `max_tokens` more tokens)
- Long-context KV cache under sustained load (KV cache pressure scales with
  prompt + output, not just prompt)
- Concurrent admin requests (kubectl exec, /props, /metrics probes)

**Observed VRAM utilization on 2026-08-15 (4× RTX 3090, Qwen3.8-27B):**

| Pod | Model | Per-card used | Per-card free | Utilization |
|-----|-------|--------------:|--------------:|------------:|
| Fred (GPUs 0+1) | Q5_K_M, layer-split, 262k ctx, mmproj | ~14-15 GiB | ~9-10 GiB | ~60% |
| Kai (GPU 2) | Q4_K_M, 262k ctx, mmproj | 23,128 MiB | 1,130 MiB | ~94% |
| Ned (GPU 3) | Q4_K_M, 262k ctx, mmproj | 23,040 MiB | 1,218 MiB | ~94% |

Kai/Ned are intentionally higher-utilization than Fred because they're
single-card on Q4_K_M with 262k ctx + mmproj. They're at the warning line
(>90%); don't push context higher on them without changing `--cache-type-k/v`.

**When to push context higher:**
- Per-card used < 19 GiB AND free > 5 GiB → can push context ~30% higher
  before re-checking.
- Per-card used > 21 GiB AND free < 3 GiB → already at the warning line; do
  not push context without changing `--cache-type-k/v`.

**When to consider a bigger model instead:**
- Per-card used < 14 GiB AND free > 10 GiB → under-utilizing; bump from Q4_K_M
  to Q5_K_M (or larger) at the same context.

## 6. Verification recipe (the must-pass before declaring done)

```bash
# A. Both pairs of GPUs are claimed by the right pods
sshpass -p ... ssh root@<pve-ip> "qm guest exec <vmid> -- nvidia-smi --query-gpu=index,memory.used --format=csv,noheader,nounits"
# Expect: pairs of GPUs in similar ranges (0,1) and (2,3); not 0+1+2+3 all flat

# B. Each pod's /health is OK
for p in 31001 31002 31003; do
    echo "--- :$p ---"
    sshpass -p ... ssh root@<pve-ip> "qm guest exec <vmid> -- curl -s http://localhost:$p/health"
done

# C. Each pod exposes its model in /v1/models
curl -s http://<vm-lan-ip>:31001/v1/models | jq '.data[].id'   # Fred
curl -s http://<vm-lan-ip>:31002/v1/models | jq '.data[].id'   # Kai
curl -s http://<vm-lan-ip>:31003/v1/models | jq '.data[].id'   # Ned

# D. mmproj is loaded (server logs mention "loaded multimodal model")
kubectl logs -n llm-inference -l app=fred-llama | grep -i mmproj
kubectl logs -n llm-inference -l app=kai-llama | grep -i mmproj
kubectl logs -n llm-inference -l app=ned-llama | grep -i mmproj

# E. A real image request lands a vision-aware reply on at least one pod
# (see section 1.3 above for the image-b64 curl recipe)

# F. The context math holds under a real workload (>100k token chat
#    completes with finish_reason in (stop, length), not
#    exceed_context_size_error)

# G. /v1/models reports "multimodal" capability (use the legacy
#    'models' field, NOT 'data' — see verifier-predicate bug B)
curl -s http://<vm-lan-ip>:31002/v1/models \
  | python3 -c "import json,sys; d=json.load(sys.stdin); print([m.get('capabilities') for m in d.get('models', d.get('data', []))])"
```

If any of A-G fails, fix that layer first; don't move forward pretending
it works. **No "pod is Running" framing** — verify the model's actual
behavior, not its process status.
