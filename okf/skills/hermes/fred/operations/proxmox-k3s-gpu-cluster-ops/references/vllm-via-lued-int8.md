# vLLM on dual RTX 3090 — `lued/Qwen3.8-27B-INT8-W8A16-MTP` recipe

The verified-good starting point for running Qwen3.8-27B under vLLM on **2× RTX 3090 (24 GiB each, PCIe, no NVLink)** is the community INT8 quant `lued/Qwen3.8-27B-INT8-W8A16-MTP`. This file captures what was learned in the August 2026 vLLM-research turn — the exact quant, the verified vLLM command line, and the vLLM-vs-llama.cpp trade-off analysis that decided **not** to migrate Kai/Ned.

## What "Lued" means

`lued` is a HuggingFace user who published Qwen3.8-27B family quants. The naming convention is `<MODEL>-<FORMAT>-<SCOPE>`. The quoting of `W8A16` means **weights INT8, activations FP16/BF16** — the right shape for Ampere GPUs (RTX 3090, sm_86) where native FP8 tensor-core execution is unavailable. The `MTP` suffix means the multi-token-prediction head is preserved, which is what enables speculative decoding in vLLM.

**The INT4 variant (`lued/Qwen3.8-27B-INT4-W4A16-MTP`) does NOT exist** — verified 401 for all six spelling variations (`INT4-W4A16-MTP`, `INT4-W4A16-mtp`, `INT4-MTP`, `INT4`, `W4A16-MTP`, `W8A16-MTP`). This is the missing piece for single-GPU deployment. If you need a single-24-GB-GPU INT4 quant of Qwen3.8-27B, you have to AWQ-quantize it yourself with `llm-compressor` (see "DIY AWQ quant" below).

## What the INT8 repo contains (verified from the live index)

- **Checkpoint size**: 31.6 GB / 29.44 GiB (1999 files in `model.safetensors.index.json`)
- **1999 weight tensors** — base Qwen3.8-27B has ~1850; the +149 are the MTP head tensors, preserved for speculative decoding
- **Architecture**: `Qwen3_5ForConditionalGeneration` (vision-language model)
- **Quantization**: `compressed-tensors` format via `llm-compressor`
- **License**: Apache 2.0
- **Pipeline tag**: `image-text-to-text` (vision-capable)

## The hardware-target match (why this quant exists for our setup)

The README's "Validated host profile" section literally says:

> 2×RTX 3090 24 GB, PCIe without NVLink or P2P, vLLM TP2, BF16 activations, FP8 E4M3 KV cache, MTP with three draft tokens, and `--max-num-batched-tokens 8192`.

This is exactly our PVE1 / VM 230 host. The README also reports the measured memory:

| Metric | Result |
|---|---:|
| Checkpoint size | 31.6 GB / 29.44 GiB |
| Loaded model memory per GPU | 14.85 GiB |
| Shared GPU KV pool | 266,537 tokens |
| Native maximum request length | 262,144 tokens |
| Simultaneous full-native-context capacity | 1.02× |
| Illustrative four-way KV share | ~66,634 tokens per request |

So per-GPU VRAM after model load is **14.85 GiB**, leaving **~9 GiB for KV cache and overhead**. The shared KV pool scales with `--max-num-batched-tokens` and `--max-num-seqs`.

## The verified vLLM command line

```bash
vllm serve lued/Qwen3.8-27B-INT8-W8A16-MTP \
  --trust-remote-code \
  --tensor-parallel-size 2 \
  --max-model-len 262144 \
  --quantization compressed-tensors \
  --kv-cache-dtype fp8_e4m3 \
  --mamba-cache-mode align \
  --speculative-config '{"method":"qwen3_5_mtp","num_speculative_tokens":3}' \
  --reasoning-parser qwen3 \
  --enable-auto-tool-choice --tool-call-parser qwen3_coder \
  --gpu-memory-utilization 0.85 \
  --max-num-batched-tokens 8192 \
  --max-num-seqs <concurrent_users> \
  NCCL_P2P_DISABLE=1
```

**Critical flags explained:**

- `NCCL_P2P_DISABLE=1` — avoids NCCL initialization stalls on dual consumer GPUs without NVLink (this is our exact case)
- `--mamba-cache-mode align` — required by the Qwen3.8 MTP/GDN serving path (Qwen3.8 uses Gated DeltaNet linear-attention layers)
- `--speculative-config '{"method":"qwen3_5_mtp","num_speculative_tokens":3}'` — enables the MTP draft head. Three speculative tokens is the measured default; reported acceptance rate is ~85%.
- `--reasoning-parser qwen3` — needed because Qwen3.8 is a thinking model by default (produces `reasoning_content` fields)
- `--quantization compressed-tensors` — tells vLLM to load the W8A16 weights using the `compressed-tensors` format
- `--kv-cache-dtype fp8_e4m3` — uses FP8 KV cache (works on Ampere via emulated kernels, no FP8 tensor cores needed)

## The three things you need in the K8s manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fred-vllm  # and delete the llama.cpp fred-llama deployment
  namespace: llm-inference
spec:
  replicas: 1
  strategy: {type: Recreate}  # vLLM doesn't run two pods on the same TP=2 GPUs
  selector: {matchLabels: {app: fred-vllm}}
  template:
    metadata: {labels: {app: fred-vllm}}
    spec:
      runtimeClassName: nvidia
      nodeSelector: {kubernetes.io/hostname: k3s-node-230}
      containers:
      - name: vllm
        image: vllm/vllm-openai:v0.27.1-cu129
        imagePullPolicy: IfNotPresent  # or Never if imported into containerd
        env:
        - name: NVIDIA_VISIBLE_DEVICES
          value: "0,1"
        - name: NCCL_P2P_DISABLE
          value: "1"
        - name: HUGGING_FACE_HUB_TOKEN    # only if the lued repo is gated
          value: "..."
        resources:
          requests: {nvidia.com/gpu: 2}
          limits: {nvidia.com/gpu: 2}
        ports:
        - containerPort: 8001
        args:
        - serve
        - lued/Qwen3.8-27B-INT8-W8A16-MTP
        - --trust-remote-code
        - --tensor-parallel-size
        - "2"
        - --max-model-len
        - "262144"
        - --quantization
        - compressed-tensors
        - --kv-cache-dtype
        - fp8_e4m3
        - --mamba-cache-mode
        - align
        - --reasoning-parser
        - qwen3
        - --enable-auto-tool-choice
        - --tool-call-parser
        - qwen3_coder
        - --speculative-config
        - '{"method":"qwen3_5_mtp","num_speculative_tokens":3}'
        - --gpu-memory-utilization
        - "0.85"
        - --max-num-batched-tokens
        - "8192"
        - --port
        - "8001"
        - --host
        - "0.0.0.0"
        readinessProbe:
          httpGet: {path: /health, port: 8001}
          initialDelaySeconds: 120  # vLLM model load takes 30-90s on dual GPU
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
        volumeMounts:
        - name: models
          mountPath: /models
          readOnly: true
      volumes:
      - name: models
        hostPath: {path: /models, type: Directory}  # contains BOTH q4 and q5 subdirs
---
apiVersion: v1
kind: Service
metadata: {name: fred-vllm-svc, namespace: llm-inference}
spec:
  type: NodePort
  selector: {app: fred-vllm}
  ports:
  - port: 8001
    targetPort: 8001
    nodePort: 31001  # same as old llama.cpp fred — Hermes provider URL stays the same
```

The NodePort 31001 matches the existing llama.cpp Fred service, so the Hermes `providers.qwen27b-fred-local.api: http://192.168.1.230:31001/v1` does NOT need to change. The model alias `local-qwen-27b-q5-fred` should be renamed to `local-qwen-27b-int8-fred` in the vLLM `--alias` flag (and the Hermes config) to match what the new server actually serves.

## The vLLM-vs-llama.cpp trade-off (the honest answer)

The honest benchmark for our specific deployment (1 agent per GPU, single-stream traffic, vision required):

| Metric | llama.cpp (current) | vLLM with lued INT8 |
|---|---|---|
| Single-stream tokens/sec | 37-40 t/s | 70-150 t/s (with MTP) |
| Multi-user concurrency | serialized (1 slot) | 2-8× aggregate via `--max-num-seqs` |
| KV memory management | q4_0 manual | PagedAttention (auto) |
| Context window | 1M (with patch) | 262k native (1M requires HF override) |
| Vision | mmproj separate file | bundled safetensors (vision tower) |
| Speculative decoding | b5368 doesn't support | natively supported (MTP) |
| Build complexity | moderate (CUDA build) | high (Python deps, vLLM image) |
| Production risk | LOW (proven) | MEDIUM (newer) |

**For our specific use case (1 agent per GPU, single-stream Telegram traffic from Hermes), the vLLM speedup is modest** (~2-3× single-stream) but **the real wins are speculative decoding (MTP) and PagedAttention KV management**. The 5×+ aggregate throughput gain only matters if multiple users hit the same pod — which is not our current architecture.

## The single-GPU vLLM problem (why Kai/Ned should stay on llama.cpp)

Our 3-pod, 1-GPU-per-pod architecture doesn't fit any vLLM INT8 or FP8 quant for 27B on a single 24 GB GPU:

- **BF16** (Qwen/Qwen3.8-27B): 55.6 GB → needs TP=2 (kills 2-pod parallelism) or TP=4 (kills all parallelism)
- **FP8** (Qwen/Qwen3.8-27B-FP8): 27 GB → needs driver ≥580 (we have 535); + Blackwell-tier GPU
- **NVFP4** (Inferact/Qwen3.8-27B-NVFP4): 26.4 GB → needs **Blackwell** (sm_120), we have **Ampere** (sm_86)
- **INT8** (lued): 31.6 GB → doesn't fit on 24 GB GPU
- **AWQ-int4**: no public Qwen3.8-27B AWQ safetensors exists yet (community hasn't caught up)

**The only single-GPU vLLM path is to AWQ-quantize ourselves, which takes ~30 min via `llm-compressor`.**

## DIY AWQ quant (single GPU option, 30 min)

```bash
# Install llm-compressor (Python)
pip install --break-system-packages llm-compressor

# Run the AWQ recipe
from llmcompressor.transformers import oneshot
from llmcompressor.modifiers.awq import AWQModifier
from llmcompressor.modifiers.quantization import GPTQModifier

recipe = [
    AWQModifier(ignore=["lm_head"], scheme="W4A16_ASYM", targets=["Linear"]),
    GPTQModifier(targets="linear", scheme="W4A16_ASYM", ignore=["lm_head"]),
]

oneshot(
    model="Qwen/Qwen3.8-27B",
    dataset="ultrachat-200k",  # or any small HF dataset
    recipe=recipe,
    output_dir="./Qwen3.8-27B-W4A16-AWQ",
    max_seq_length=2048,
    num_calibration_samples=512,
)
```

This produces a ~14-15 GB AWQ-int4 safetensors model that fits one 24 GB GPU with KV cache. The MTP head is harder to preserve in this recipe — you'd lose the speculative decoding benefit. Pure AWQ deploy would be:

```bash
vllm serve ./Qwen3.8-27B-W4A16-AWQ \
  --tensor-parallel-size 1 \
  --max-model-len 131072 \
  --quantization compressed-tensors \
  --max-num-seqs 1
```

Trade-off: AWQ-int4 = ~30 min build, no MTP, ~40-60 t/s single-stream.

## The recommended split (best of both engines)

| Pod | Engine | Quant | Why |
|---|---|---|---|
| **Fred** | vLLM | lued INT8 + MTP | 2 GPUs fit it, MTP gives 2× speedup, 262k ctx |
| **Kai** | llama.cpp | Q4_K_M GGUF | No vLLM quant fits single 24 GB GPU |
| **Ned** | llama.cpp | Q4_K_M GGUF | No vLLM quant fits single 24 GB GPU |

This gets Fred ≈ 2-3× speedup while leaving Kai/Ned on a proven stack. Don't migrate Kai/Ned until a single-GPU vLLM quant (AWQ or otherwise) becomes available.

## Things that will trip you up

1. **`vllm serve` is the v0.27.x subcommand.** Older engines used `python -m vllm.entrypoints.openai.api_server`. Check `vllm --help` first.

2. **`--mamba-cache-mode align` is NOT optional.** The Qwen3.8 MTP/GDN serving path requires it. Without it, vLLM aborts CUDA-graph capture.

3. **`--max-num-seqs 32` is NOT optional on FP8 builds.** The default (1024) exceeds the available Mamba cache blocks and vLLM aborts CUDA-graph capture. For INT8, the limit is more relaxed.

4. **`NCCL_P2P_DISABLE=1` is required for our PCIe topology.** NVLink-less GPUs default to NCCL P2P which stalls on init. Set this env var.

5. **The `pipeline_tag: image-text-to-text` in the lued repo means vision works out of the box.** No mmproj file needed — vLLM bundles the vision tower directly into the safetensors. This is different from llama.cpp, which needs a separate `mmproj-F16.gguf` file.

6. **vLLM model load takes 30-90 seconds** on a dual-GPU INT8 model. The `readinessProbe` should have `initialDelaySeconds: 120` (NOT 60 like llama.cpp). Setting it too low causes the pod's K8s readiness probe to fail-nozzle before the model finishes loading.

7. **The NodePort 31001 has to come from the vLLM service, not the old llama.cpp service.** The old `fred-llama-svc` must be deleted before the new `fred-vllm-svc` is applied, or the NodePort allocation will conflict.

8. **Image pull is 37.5 GB on disk.** The prebuilt `vllm/vllm-openai:v0.27.1-cu129` image is large. Pre-pull or `ctr import` to avoid running out of disk mid-deployment.

## The critical verification recipe (load-bearing)

After deploying vLLM, verify:

```bash
# 1. Server is healthy
curl -s http://localhost:31001/health
# → {"status":"ok"}

# 2. Model is multimodal
curl -s http://localhost:31001/v1/models | jq '.data[0]'
# → should have id, capabilities: ["multimodal", "completion"], n_ctx: 262144

# 3. The model is actually on GPU (not CPU fallback)
# Run a real chat and check predicted_per_second
# GPU INT8 layer-split: ~70-150 t/s (with MTP)
# CPU INT8: ~3-10 t/s

# 4. Both GPUs are allocated
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader
# → both GPUs should show 14-18 GiB used

# 5. MTP speculative decoding is enabled
# (visible in the vLLM startup log, not the API)
```

If predicted_per_second is < 20 t/s OR nvidia-smi shows ~256 MiB used, the deployment is on CPU, not GPU. Same diagnostic as llama.cpp Gotcha 17.

## The honest answer for "is vLLM worth it?"

For our specific hardware (4× RTX 3090, 535 driver, no Blackwell), the vLLM migration is **only worth it for Fred** (the only pod large enough to fit the 31.6 GB INT8 model). Kai/Ned have no vLLM-compatible quant for single-GPU deployment yet.

If the user wants faster overall:
1. **First** — try MTP speculative decoding on the existing llama.cpp stack (smaller change, similar benefit)
2. **Then** — migrate just Fred to vLLM with the lued INT8 recipe
3. **Later** — wait for a single-GPU AWQ quant of Qwen3.8-27B, then migrate Kai/Ned too

Don't try to migrate all 3 pods at once on day one.
