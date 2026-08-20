# LLM compression repos with llm-compressor + compressed-tensors

The class of work: producing a production-ready repo that takes a base LLM (BF16 safetensors), compresses it to W4A16 INT4 or W8A16 INT8 with FP8 KV cache using `llm-compressor`, and ships the compressed checkpoint as a vLLM-deployable artifact. Built from the 2026-08-15 and 2026-08-16 Qwen3.8-27B → W4A16 sessions.

## What the deliverable shape looks like

A complete LLM compression repo has six files at minimum:

1. **`README.md`** — prerequisites, setup, quantization execution, deployment, troubleshooting, comparison table vs other quants (BF16 / INT8 / W4A16 / INT4)
2. **`requirements.txt`** — clean split between quantization deps (`torch`, `transformers`, `accelerate`, `datasets`, `llmcompressor`, `compressed-tensors`, `flash-attn`) and serving deps (`vllm`)
3. **`quantize.py`** — production CLI with `--model-id`, `--output-dir`, `--num-samples`, `--seq-len`, `--batch-size`, `--num-gpus` flags. Calibration data prep using Qwen's native chat template. Combined recipe: GPTQModifier (W4A16 or W8A16) + QuantizationModifier (FP8 KV cache). Multi-GPU offload with `device_map="auto"`. Architecture-aware ignore patterns (DeltaNet + vision + MTP + lm_head).
4. **`serve_vllm.sh`** — production startup script with `--tensor-parallel-size`, `--kv-cache-dtype fp8`, `--reasoning-parser qwen3`, `--speculative-config` for MTP, `--language-model-only` toggle, `--enable-prefix-caching`, `--enable-chunked-prefill`, `--max-num-seqs`
5. **`validate.py`** — perplexity vs BF16 baseline, TTFT, inter-token latency, peak VRAM
6. **`upload_hf.py`** — auto-generates a HuggingFace model card (quantization details, VRAM math, vLLM quickstart snippets) and pushes the compressed weights via `huggingface_hub.upload_folder`

The 2026-08-15 working example is at `/tmp/qwen-quantize/` (6 files, 52 KB total). The 2026-08-16 updated version with Gemini architecture-aware recipe (DeltaNet exclusion + 35/35/30 calibration mix) is at `/tmp/qwen-quantize/quantize.py` on VM 230. Use the latter as the starting reference template.

## The W4A16 vs W8A16 vs INT4 tradeoff (the core decision)

This is the load-bearing decision in any LLM compression repo. The four viable formats for a 27B-class model on RTX 3090:

| Format | Weights | Activations | KV cache | Per-GPU VRAM | Quality loss | vLLM support | Source |
|---|---|---|---|---|---|---|---|
| BF16 | 55.6 GB | BF16 | BF16 | 27.8 GB | baseline | ✅ native | `Qwen/Qwen3.8-27B` |
| INT8 (W8A16) | 31.6 GB | BF16 | FP8 | 14.85 GB | ~0.1% | ✅ MTP preserved | `lued/Qwen3.8-27B-INT8-W8A16-MTP` |
| **W4A16 (INT4 weights, BF16 activations)** | **~15 GB** | BF16 | FP8 | **~7.5 GB** | **~0.5%** | **✅ Marlin kernel** | **DIY with `llm-compressor`** |
| W4A16 (DeltaNet in BF16) | **~27.8 GB** | BF16 | FP8 | **~13.9 GB** | **~0.3%** | **✅ Marlin kernel** | **Recommended DIY** |
| INT4 (W4A4) | ~7.5 GB | INT4 | FP8 | ~3.5 GB | ~1.5% | ⚠️ Marlin-AWQ only | (community hasn't released for Qwen3.8 yet) |

**Decision tree:**
- If 27B model on 24 GB single GPU: **W4A16 is the only viable compressed format** (BF16 doesn't fit, INT8 doesn't fit).
- If 27B model on 2× 24 GB (TP=2): INT8 fits with room to spare; W4A16 wastes compute. UNLESS you need vision + reasoning + agentic tool calling — then W4A16 with DeltaNet BF16 outperforms INT8 (the 0.3% vs 0.5% gap widens on hard reasoning tasks).
- If you need speculative decoding (MTP), preserve `mtp` in BF16 — the W4A16 recipe does this.
- If you need vision, preserve `visual` in BF16 — same.

## The non-negotiable recipe for W4A16

The recipe in `templates/quantize.py` is verified end-to-end (2026-08-15 from `/tmp/qwen-quantize/quantize.py`, then updated 2026-08-16 for the `llmcompressor` 0.13 API and the transformers 5.x + qwen3_5 architecture requirement, then updated 2026-08-16 again with Gemini's architecture-aware ignore patterns and 35/35/30 calibration mix).

### The llmcompressor 0.13+ API (current, for driver 580 hosts)

```python
from llmcompressor import oneshot
from llmcompressor.modifiers.gptq.base import GPTQModifier
from llmcompressor.modifiers.quantization import QuantizationModifier
from compressed_tensors.quantization.quant_scheme import QuantizationScheme
from compressed_tensors.quantization.quant_args import QuantizationArgs

W4A16_WEIGHT_SCHEME = QuantizationArgs(
    num_bits=4, type="int", symmetric=True,
    group_size=128, strategy="group",
)
FP8_KV_CACHE_SCHEME = QuantizationArgs(
    num_bits=8, type="float", strategy="tensor",
    dynamic=False, symmetric=True,
)
CONFIG_GROUPS = {
    "group_0": QuantizationScheme(
        targets=["Linear"],
        weights=W4A16_WEIGHT_SCHEME,
        input_activations=None, output_activations=None,
    ),
}

recipe = [
    GPTQModifier(
        config_groups=CONFIG_GROUPS,
        targets="Linear",
        # CRITICAL: keep these four in BF16
        ignore=[
            "lm_head",                                 # Output projection
            "visual",                                  # Vision encoder tower
            "mtp",                                     # Multi-token prediction heads
            r"model\.layers\.\d+\.linear_attn\..*",    # Gated DeltaNet (Qwen3.8 hybrid)
        ],
        actorder=None,                                # None = no reordering (Marlin-direct)
    ),
    QuantizationModifier(
        config_groups=CONFIG_GROUPS,
        kv_cache_scheme=FP8_KV_CACHE_SCHEME,
    ),
]
```

### Why the API changed at llmcompressor 0.13

The kwargs `group_size`, `symmetric`, `desc_act` were removed from `GPTQModifier.__init__` in 0.13. They're now part of the `QuantizationArgs` object that lives inside `config_groups[...]["weights"]`. Same for `kv_cache_scheme`: the dict-with-keys form became an `QuantizationArgs` object. `desc_act=False` was renamed `actorder=None` (with `None` meaning "no reordering"). Attempting the old kwarg form raises:

```
3 validation errors for GPTQModifier
group_size:  Extra inputs are not permitted [type=extra_forbidden]
symmetric:   Extra inputs are not permitted [type=extra_forbidden]
desc_act:    Extra inputs are not permitted [type=extra_forbidden]
```

The import path also moved: `llmcompressor.modifiers.quantization.gptq.base` → `llmcompressor.modifiers.gptq.base`.

### The llmcompressor < 0.7 API (legacy, torch 2.5 compatible)

```python
from llmcompressor.modifiers.quantization import GPTQModifier, QuantizationModifier

recipe = [
    GPTQModifier(
        targets="Linear",
        scheme="W4A16",
        group_size=128,
        symmetric=True,
        desc_act=False,
        ignore=[
            "lm_head", "visual", "mtp",
            r"model\.layers\.\d+\.linear_attn\..*",  # DeltaNet (legacy API accepts regex too)
        ],
    ),
    QuantizationModifier(
        kv_cache_scheme={
            "num_bits": 8,
            "type": "float",
            "strategy": "tensor",
            "dynamic": False,
            "symmetric": True,
        }
    ),
]
```

Only use this if you're pinned to torch 2.5.x (driver 535 hosts). See `references/host-side-quantization-pitfalls.md` for the install ordering.

### Why each parameter is non-negotiable

- **`scheme="W4A16"` / `num_bits=4`** — INT4 weights with BF16 activations. The only path to <20 GB file size with quality preserved on Ampere (no FP4/FP8 needed).
- **`group_size=128`** — Marlin kernel compatibility. Other group sizes (32, 64) break Marlin's direct mapping and force dequantization at runtime.
- **`symmetric=True`** — Simpler dequantization, no zero-point overhead. Negligible accuracy impact vs asymmetric.
- **`actorder=None` / `desc_act=False`** — No activation reordering. Marlin kernel expects weights in the original layout.
- **`ignore=["lm_head", "visual", "mtp", r"model\.layers\.\d+\.linear_attn\..*"]`** — Sensitivity exclusions. Removing any of these causes:
  - `lm_head`: 2-3% perplexity degradation (output projection is sensitive)
  - `visual`: multimodal accuracy loss (vision tower is small but critical)
  - `mtp`: speculative decoding breaks (MTP head needs full precision)
  - **`model.layers.*.linear_attn.*`** (Qwen3.8 hybrid DeltaNet): THE most critical exclusion. DeltaNet maintains a recurrent state matrix `S_t = S_{t-1} + ...` that ACCUMULATES INT4 quantization noise across long context windows. Without this exclusion, you get loop repetitions, syntax corruption in JSON tool arguments, and truncated `<think>` blocks on long contexts. The 4:1 DeltaNet:full-attention hybrid (48 DeltaNet layers + 16 full-attention + 64 MLP) means keeping linear_attn in BF16 bumps output to ~27.8 GB instead of ~15-16 GB but preserves long-context reasoning, CoT, and agentic tool calling. Source: Gemini architectural analysis, 2026-08-16. The current `templates/quantize.py` has all four exclusions.
- **`kv_cache_scheme.type="float"`** — FP8 KV cache. INT8 KV cache works but FP8 is what vLLM's `--kv-cache-dtype fp8` flag activates.

### The DeltaNet exclusion pattern (most critical, easy to miss)

Qwen3.8's hybrid architecture uses `full_attention_interval: 4` in `text_config` — every 4th layer is full gated attention, the other 3 are Gated DeltaNet. Across the 64 layers that's 48 DeltaNet + 16 full-attention. The DeltaNet layers carry the bulk of the long-context state but their `linear_attn.*` projections (`in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, `out_proj`) are uniquely sensitive to INT4 quantization because quantization noise ACCUMULATES in the recurrent state across the context window.

The verified exclusion pattern (regex):
```python
r"model\.layers\.\d+\.linear_attn\..*"
```

This matches `model.layers.0.linear_attn.in_proj_qkv.weight`, `model.layers.45.linear_attn.out_proj.bias`, etc. Without this pattern, the GPTQ pass will quantize DeltaNet projections to INT4 and the model will produce degraded output on long-context reasoning.

**Output size impact:** keeping DeltaNet in BF16 results in ~27.8 GB output instead of the typical ~15-16 GB for a uniform 27B model. The trade is intentional — accept the larger size, preserve quality. The single-GPU fit window on 24 GB cards is exactly what this preserves (the MTP head + DeltaNet BF16 totals ~3 GB; the W4A16 self-attn + MLP + KV-cache scales total ~12 GB; leaves headroom for activations).

## The hard architecture requirement: Qwen3.8 needs `transformers >= 5.0`

`AutoConfig.from_pretrained('/models/Qwen3.8-27B')` with `transformers==4.52.4` raises:

```
ValueError: The checkpoint you are trying to load has model type `qwen3_5`
but Transformers does not recognize this architecture. ... You can update
Transformers with the command `pip install --upgrade transformers`. If this
does not work, and the checkpoint is very new, then there may not be a release
version that supports this model yet.
```

Qwen3.8 (and all Qwen3.5-derived architectures, including the `Qwen3_5ForConditionalGeneration` multimodal class) is internal-labeled `qwen3_5` and lives in `transformers>=5.4` (and the corresponding `Qwen3_5Config`). `transformers==4.52.x` has no class for it. The symptom chain is:

1. `AutoTokenizer.from_pretrained()` may *succeed* (tokenizer is the same `Qwen2Tokenizer`)
2. `AutoConfig.from_pretrained()` fails with `ValueError: ... model type 'qwen3_5'`
3. `AutoModelForCausalLM.from_pretrained()` fails with `KeyError: 'qwen3_5'` from `CONFIG_MAPPING`
4. The recipe script crashes before Step 3 finishes

**Fix (the only one):** `pip install --upgrade transformers` to get `transformers>=5.4`. This breaks compatibility with `llmcompressor<0.7` (which requires `transformers<=4.52.4`), so you have to pick one of two install orders — see `references/host-side-quantization-pitfalls.md` for the full sequence. The cleanest ordering for current driver 580 hosts:

```bash
# Step 1: torch matching the driver (cu130 for driver 580+)
pip install --upgrade torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/cu130

# Step 2: transformers 5.x (required for qwen3_5)
pip install --upgrade transformers

# Step 3: llmcompressor 0.13+ + deps (compatible with transformers 5.x)
pip install --upgrade llmcompressor compressed-tensors accelerate datasets

# Step 4: jinja2 (transformers 5.x requires >= 3.1.0)
pip install --upgrade jinja2
```

## The attention-backend fallback (the `flash_attention_2` trap)

The legacy `quantize.py` template hardcoded `attn_implementation="flash_attention_2"`, but `flash-attn` is a separate package that has to be compiled against the exact torch+CUDA combo (cu121 vs cu130 produce different wheels). If flash-attn isn't installed, the load fails:

```
ImportError: FlashAttention2 has been toggled on, but it cannot be used due
to the following error: the package for FlashAttention2 doesn't seem to
be installed.
```

Fix: default to `attn_implementation="sdpa"` (PyTorch's built-in `torch.nn.functional.scaled_dot_product_attention`, which is fast-path on Ampere and zero extra deps). Pass `--attn-impl flash_attention_2` only after `pip install flash-attn` and the matching wheel is verified. The `templates/quantize.py` template now ships with this fallback in place.

**Fast path note:** Qwen3.5's hybrid architecture uses Gated DeltaNet (linear attention) on the linear-attention layers and full gated attention elsewhere. The fast-path library for the linear layers is `flash-linear-attention` (`fla-org/flash-linear-attention`), not flash-attn. If the warning "The fast path is not available because one of the required library is not installed. Falling back to torch implementation" appears during model load, install `flash-linear-attention` + `causal-conv1d` for the linear-attention fast path. The W4A16 quantization itself runs fine on the torch fallback; the warning is informational.

## The calibration data recipe — Gemini Tip 4 (35/35/30 mix)

Pure ultrachat calibration fails to trigger the high-magnitude activation spikes Qwen3.8 produces during CoT reasoning and structured tool-calling. Pure chat distribution clips outlier scales in upper MLP layers, causing loop repetitions, syntax corruption in JSON tool arguments, and truncated `<think>` blocks. The fix is a 35/35/30 mix at 4096-token context (not 2048 — the longer context is what triggers the activation outliers in deep reasoning):

```python
DEFAULT_CALIBRATION_SOURCES = {
    "reasoning": ["microsoft/orca-math-word-problems-200k", "GAIR/lima"],
    "code":      ["ise-uiuc/Magicoder-Evol-Instruct-110K", "sahil2801/CodeAlpaca-20k"],
    "dialogue":  ["HuggingFaceH4/ultrachat_200k"],
}
DEFAULT_CALIBRATION_WEIGHTS = {"reasoning": 0.35, "code": 0.35, "dialogue": 0.30}
```

The verifier: confirm all three categories loaded by checking the log lines `Loaded N samples from <source>`. If the primary source 401s or times out, the fallback list iterates. AVOID these:
- `gsm8k` (configured as `gsm8k@<hash>`, returns 404 on plain `gsm8k`) — use `openai/gsm8k` or stick with orca-math
- `openai-r1/MathR1` (401 gated/private)
- `cais/mmlu` (gated)
- `openai/MMLU` (401 gated)
- Pure `c4` / `wikitext` (no chat distribution → wrong activation shape)

The `templates/quantize.py` ships with this mix + schema-dispatch `_load_reasoning_samples`/`_load_code_samples`/`_load_dialogue_samples` helpers. The `--seq-len 4096` default is required; 2048 is too short for the deep-reasoning activations.

**Why the mix and not just one source:**
- 35% reasoning (math/CoT) — surfaces activation outliers from long chain-of-thought
- 35% structured code — surfaces structured-output attention patterns (Python, JSON, ASTs)
- 30% dialogue — matches serving-time distribution (you don't serve base completions)
- 4096 ctx (not 2048) — required for deep reasoning activations to develop

## Memory math (the four-layer constraint)

W4A16 quantization needs to fit in 48 GiB during quantization (when running with `device_map="auto"` for multi-GPU offload). Math (DeltaNet-included model):

- BF16 model load: 55.6 GB
- W4A16 GPTQ activations: ~20 GB peak (during scale calibration)
- Calibration data: ~2 GB (cached tokenization)
- Working space: ~5 GB

**Total peak: ~83 GB** — doesn't fit on a single 24 GB GPU, needs at least 4× 24 GB for the quantization pass. That's why user said "we will need to utilize all 4 GPUs for this LLM compression."

The K8s deployment pattern for the quantization pod:
- `nvidia.com/gpu: 4` (uses all 4 GPUs for offload)
- `--batch-size 4` (one sample per GPU during scale computation)
- `--seq-len 4096` (per-sample sequence length)

## The serving manifest

The `serve_vllm.sh` recipe (verified 2026-08-15, recommended post-2026-08-16 quantization):

```bash
vllm serve Qwen/Qwen3.8-27B-W4A16 \
    --tensor-parallel-size 2 \
    --gpu-memory-utilization 0.95 \
    --max-model-len 262144 \
    --kv-cache-dtype fp8 \
    --enable-prefix-caching \
    --enable-chunked-prefill \
    --max-num-seqs 8 \
    --reasoning-parser qwen3 \
    --speculative-config '{"method": "qwen3_mtp", "num_speculative_tokens": 3}' \
    --trust-remote-code
```

Flags explained:
- `--tensor-parallel-size 2` — split 27.8 GB weights across 2 GPUs (each gets 13.9 GB; if uniform 15 GB quant, each gets 7.5 GB)
- `--kv-cache-dtype fp8` — activates the FP8 KV cache scales baked into the checkpoint
- `--reasoning-parser qwen3` — extracts `<think>...</think>` blocks from responses
- `--speculative-config` — enables MTP speculative decoding (3 draft tokens, ~85% acceptance rate)
- `--max-num-seqs 8` — 8 concurrent users per pod (each gets ~1/8 throughput, aggregate 8× higher)

For 1M context extension:
```bash
    --max-model-len 1010000
```

vLLM handles the 262k → 1M extension natively via Qwen3.8's pre-baked RoPE scaling — no source patches needed.

## The verification recipe

`validate.py` measures four things, all against the BF16 baseline:

1. **Perplexity** on wikitext-2-raw-v1 test split (100 samples)
2. **TTFT** (time-to-first-token) on 10 prompts
3. **Inter-token latency** on the same 10 prompts
4. **Peak VRAM** during a 512-token generation

**The perplexity degradation gate:** if W4A16 degrades > 1% vs BF16, the recipe is wrong. Most likely causes:
- `lm_head` accidentally quantized → check `ignore=["lm_head"]` is present
- `linear_attn.*` accidentally quantized → check the regex exclusion is in `ignore`
- Group size too large (256, 512) → reduce to 128
- Calibration set too small (<256 samples) → bump to 512
- Calibration set is pure chat (no reasoning) → use the 35/35/30 mix

## The HF upload recipe

`upload_hf.py` auto-generates a comprehensive model card and pushes via `huggingface_hub.upload_folder`. Key fields to include in the model card:

- **Quantization method** (W4A16 GPTQ, group_size=128, symmetric, actorder=None)
- **Architecture exclusions** (lm_head, visual, mtp, AND `model.layers.*.linear_attn.*` kept in BF16 for Qwen3.8 hybrid)
- **KV cache format** (fp8_e4m3, per-tensor static)
- **Calibration data** (35/35/30 mix at 4096 ctx: orca-math + Magicoder + ultrachat)
- **VRAM requirements** (per-GPU 13.9 GB at TP=2, ~14 GB at TP=1 with DeltaNet BF16; or 7.5/13.9 with uniform W4A16)
- **vLLM quickstart** (the exact serve command above)
- **License** (Apache 2.0 inherited from base model)

The model card is rendered as a Jinja-style template in `MODEL_CARD_TEMPLATE` (constant in upload_hf.py).

## The 5 things that bit during the 2026-08-15 first attempt

1. **Disk space underestimate.** BF16 model is 55.6 GB, intermediate activations are ~20 GB, output is ~15 GB. Total ~95 GB working set. Need ~150 GB free for safety. Resize the VM disk first (`qm resize +100G` + `growpart + resize2fs`).
2. **HF rate-limit false positives** — see `references/huggingface-research-patterns.md`. The `r=2999/t=300` headers look like blocks but are normal HEAD-on-resolve behavior. Use `-L` for actual downloads.
3. **No `pip install huggingface_hub` on the VM** — install before trying `snapshot_download`. The `huggingface-cli` command comes from a separate package (`huggingface_hub[cli]`).
4. **The 1M context extension is NOT this recipe's concern.** vLLM handles `--max-model-len 1010000` natively with the base Qwen3.8 model. The llama.cpp patch required for 1M (see `references/llama-server-context-progression.md`) is a separate concern.
5. **MTP speculative decoding requires the base MTP head.** If you W4-quantize the `mtp` head by accident, `--speculative-config` will fail at runtime. The `ignore=["mtp"]` line is the protection.

## The 6 things that bit during the 2026-08-16 retry (architecture + recipe)

1. **`transformers==4.52.4` doesn't recognize `qwen3_5` architecture.** The Qwen3.5/Qwen3.8 multimodal class (`Qwen3_5ForConditionalGeneration`) needs `transformers>=5.4`. Required upgrading transformers and `jinja2` (>= 3.1.0) before anything else.
2. **`llmcompressor` 0.13 broke `GPTQModifier` kwargs.** `group_size`/`symmetric`/`desc_act` removed from `__init__`; live in `config_groups["group_0"]["weights"]` as `QuantizationArgs` fields. `desc_act` was renamed to `actorder` (None = no reordering). Live verification: `python3 -c "from llmcompressor.modifiers.gptq.base import GPTQModifier; GPTQModifier(...)"` must succeed before running the full script.
3. **`flash_attention_2` not installed by default.** The script's `attn_implementation="flash_attention_2"` hardcoded the dependency. Fix: switch to `sdpa` (PyTorch built-in, zero deps, fast on Ampere). Pass `--attn-impl flash_attention_2` only after installing `flash-attn` for the matching torch+CUDA combo.
4. **Driver upgrade from 535 → 580 (via unattended-upgrade).** The kernel module got rebuilt under 580.173.02, but the pinned torch 2.5.1+cu121 was from the 535 era and reported `cuda.is_available() == False`. Re-pinned torch to `2.13.0+cu130` (matching the new driver) and re-verified with a real matrix multiply on each GPU.
5. **`pynvml` deprecation warning from torch 2.13.** Cosmetic only — torch 2.13.0+cu130 imports `pynvml` which is deprecated in favor of `nvidia-ml-py`. Both work. Don't try to "fix" this with `pip install nvidia-ml-py --upgrade` since `pynvml` is the dependency torch uses internally.
6. **NO `linear_attn.*` exclusion in the original W4A16 recipe.** Qwen3.8 is a 3:1 DeltaNet:full-attention hybrid (48 DeltaNet + 16 full-attention + 64 MLP, `full_attention_interval: 4`). Gemini's architectural analysis: DeltaNet recurrent state ACCUMULATES INT4 quantization noise across the context window → collapses CoT, JSON tool arguments, and `<think>` blocks. The fix is a regex exclusion `r"model\.layers\.\d+\.linear_attn\..*"` added to `ignore=`. Output size grows from ~15 GB to ~27.8 GB but quality is preserved. The current `templates/quantize.py` has all four exclusions (lm_head, visual, mtp, linear_attn.*).

## When this skill applies

- The user asks to compress a HuggingFace LLM (typically 27B-class or larger)
- The user mentions `llm-compressor`, `compressed-tensors`, GPTQ, W4A16, W8A16, INT4, INT8
- The user wants a quantization recipe for vLLM (NOT for llama.cpp, which uses GGUF not safetensors)
- The user mentions Marlin kernel or FP8 KV cache
- The user asks for a "production-ready quantization pipeline"
- The user names a hybrid architecture (Qwen3.5/Qwen3.8, RecurrentGemma, etc.) — needs DeltaNet-style exclusion

## When NOT to use this skill

- The user wants GGUF quantization → use `llama.cpp` quantization tools, not `llm-compressor`
- The user wants AWQ-int4 (different scheme, separate quantization tool) — see `references/vllm-via-lued-int8.md` for the AWQ-vs-W4A16 distinction
- The user wants quantization for ONNX, TFLite, or other runtimes → wrong toolchain
- The user wants to quantize a vision-only or audio model → this recipe assumes a text-first multimodal LLM with vision tower
- The user wants to quantize a base-only text LLM (no multimodal, no DeltaNet) → the simpler `ignore=["lm_head"]` is sufficient; no DeltaNet exclusion needed

## Companion skills

- `references/vllm-via-lued-int8.md` — the verified vLLM deployment recipe for the output of this quantization pipeline
- `references/llama-server-runtime-gotchas.md` — the gotchas that bite when serving the quantized model via llama.cpp (if you go that route instead of vLLM)
- `references/llama-server-gpu-vs-cpu-verification.md` — the GPU-vs-CPU verification recipe, must run before claiming "GPU compute confirmed"
- `references/huggingface-research-patterns.md` — HF download recipes for getting the BF16 base model
- `references/online-vm-disk-resize.md` — disk resize recipe for fitting the BF16 + intermediate + output
- `references/host-side-quantization-pitfalls.md` — the runtime/install pitfalls (driver 535 vs 580, flash-attn vs SDPA, K3s pods reclaiming VRAM, unattended-upgrade trap)