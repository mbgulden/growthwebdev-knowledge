---
name: hybrid-attention-llm-quantization
description: Class-level recipe for quantizing hybrid-attention LLMs (DeltaNet + Full Attention) to W4A16 / INT4 with Marlin GEMM and FP8 KV-cache, optimized for Ampere SM86 (RTX 3090). Covers the 7 BF16 exclusion patterns (linear_attn, in_proj, visual, merger, mtp, embed_tokens, lm_head), the 40/30/30 calibration protocol for reasoning/code/dialogue, Hessian dampening (dampening_frac=0.05, offload_hessians=True), Marlin W4A16 constraints (group_size=128, symmetric), and the kill-and-rebuild pattern when the running recipe is wrong. Trigger when the user asks to quantize a hybrid model (Qwen 3.x+, DeepSeek-V3, Mamba, RWKV, Jamba), or when an existing quantization is suspected of clipping sensitive layers. Distinct from proxmox-k3s-gpu-cluster-ops (which deploys the quantized model, not the quantization recipe).
category: operations
triggers:
  - user says "quantize Qwen 3.8 / 3.5 / DeepSeek / Jamba / Mamba / RWKV" or any hybrid-attention LLM
  - user pastes a hybrid-attention quantization prompt with explicit exclusion list (DeltaNet, MTP, vision)
  - running GPTQ / AWQ / llm-compressor quantization recipe is suspected of clipping DeltaNet or recurrent-state layers
  - recipe needs static FP8 KV-cache scales for Ampere (no native FP8 hardware)
  - Marlin SM86 deployment on RTX 3090 / 4090 / A5000 / A100
  - killing a long-running quantization to rebuild with corrected recipe (architecture-aware)
  - user asks "what quantized Qwen3.8 models exist on Hugging Face?" or wants to deploy vLLM with an existing quant (load references/qwen3.8-27b-model-availability.md)
references:
  - references/qm-guest-exec-verifier-helpers.md
  - references/qwen3.8-27b-model-availability.md
---

# Hybrid-Attention LLM Quantization (W4A16 + FP8 KV-cache on Ampere)

## Core principle

Hybrid-attention LLMs (Qwen 3.5+, DeepSeek-V3, Mamba, Jamba, RWKV) have a **uniform quantization failure mode**: the linear/recurrent projection layers (DeltaNet, Mamba SSM, RWKV time-mix, Jamba Mamba) accumulate quantization noise across their recurrent state. Quantizing these to INT4 produces a model that loads fine but **collapses on long-context reasoning** because errors compound over token steps.

The recipe must **explicitly exclude** the recurrent projections, keep them in BF16, and only quantize the standard-attention + MLP layers. This produces a hybrid-precision model: ~17-18 GB on disk for a 27B model (vs ~15 GB for a uniform INT4) but with reasoning + long-context quality preserved.

## The 7 BF16 exclusion patterns (mandatory)

For Qwen 3.5/3.8 27B specifically, every recipe MUST include these in `ignore=`:

```python
RECIPE_IGNORE_PATTERNS = [
    "re:visual\\..*",                            # Vision encoder tower
    "re:merger\\..*",                            # Vision merger (cross-modal)
    "re:model\\.layers\\.\\d+\\.linear_attn\\..*",   # Gated DeltaNet projections
    "re:.*in_proj.*",                           # DeltaNet sub-projections (in_proj_qkv/z/b/a, out_proj)
    "re:.*mtp.*",                               # Multi-Token Prediction heads
    "re:.*embed_tokens.*",                      # Input embeddings
    "lm_head",                                    # Output projection (exact match)
]
```

### ⚠️ CRITICAL: The `re:` prefix is mandatory in llm-compressor ≥ 0.13.0

The `ignore=` parameter is dispatched through `compressed_tensors.utils.match.match_name`,
which has two modes:

```python
def match_name(name: str, target: str, fused: FusedMappping | None = None) -> bool:
    if target.startswith("re:"):
        return re.match(target.removeprefix("re:"), name) is not None
    else:
        return target == name   # ← exact-string match, no regex!
```

Without the `"re:"` prefix, the recipe silently treats the pattern as a literal name and
**compares against the module path as an exact string match.** A recipe like
`r"model\.layers\.\d+\.linear_attn\..*"` is never going to equal any module name — so the
pattern matches NOTHING, and DeltaNet gets quantized to INT4 anyway. The recipe appears to
load correctly, the GPTQ pass appears to apply the ignore list, but every DeltaNet layer is
processed. A structural test (model loads + 1-token generation) passes. The user's actual
workload (long-context reasoning) collapses silently.

**Symptom:** recipe runs to completion, output looks fine, but the `compress_module_list.
Quantizing ...` log lines show every DeltaNet layer being quantized. The `Recipe applied
config_groups to N/256` count looks normal. Only the per-module "Quantizing model.layers.
N.linear_attn.in_proj_qkv" log entries reveal the bug.

**Fix:** prepend `"re:"` to every pattern that should be regex. Patterns that should remain
exact (module name == exact match) stay as-is: `"lm_head"`.

This bug cost ~52 minutes of GPTQ pass on the first run of this recipe. The corrected recipe
runs `(N/65): Calibrating` (where N is much less than the full Linear layer count of ~768),
confirming DeltaNet was correctly excluded.

The Python-side regex tests pass with or without the prefix (because Python `re.search`
is called on `name` regardless), so this bug doesn't show up in unit tests that test
`ignore` patterns against module paths in isolation — only in the live integration test
inside the GPTQ loop.

The 7 patterns correspond to 7 distinct failure modes:

| Pattern | Failure mode if quantized to INT4 |
|---|---|
| `linear_attn.*` | Recurrent state noise accumulates across token steps; long-context reasoning collapses |
| `in_proj.*` | Sub-projections (qkv fused projection in DeltaNet) — same recurrent-state noise |
| `visual.*` | Vision encoder — OCR hallucination, spatial reasoning loss |
| `merger.*` | Vision merger (cross-modal projector) — same multimodal degradation |
| `mtp.*` | Multi-Token Prediction draft heads — speculative decoding rejection rates spike |
| `embed_tokens.*` | Input semantic separation blurs; vocabulary distributions shift |
| `lm_head` | Output vocabulary logits shift; perplexity degrades on all tokens |

**Pattern coverage vs specific naming:** the patterns above are regexes that match the module
path under `model.layers.N.*`. They are not specific to Qwen 3.x; the same shape applies
to any DeltaNet / Mamba / RWKV hybrid model. For Mamba-only models, replace `linear_attn.*`
with `mixer.*` (Mamba's mixer module name).

**Reciprocal check:** if any of these patterns is missing from the recipe, the resulting
model will pass naive structural tests (load + 1-token generation works) but fail on the
user's actual use case (reasoning, long context, multi-modal, speculative decoding).
Always grep the recipe source for all 7 patterns before launching.

## W4A16 Marlin scheme (Ampere SM86 constraint)

```python
W4A16_WEIGHT_SCHEME = QuantizationArgs(
    num_bits=4,
    type="int",
    symmetric=True,        # Marlin requirement
    group_size=128,        # Marlin requirement (group_size=32/64 triggers slow Triton fallback)
    strategy="group",
)
```

**Three hard requirements for Marlin on SM86:**

1. **`group_size=128`** (or `-1` for per-channel). Non-standard sizes (32, 64) trigger the
   generic CUDA/Triton dequant path that is 2-3x slower.
2. **`symmetric=True`**. Asymmetric INT4 needs an extra zero-point that Marlin does not support.
3. **`desc_act=False`** → in `llm-compressor` v0.13.0 API this is `actorder=None` (the
   activation-ordering parameter was renamed). Setting `actorder=None` produces weights in
   standard layout that Marlin can dequantize directly inside Tensor Core registers.

If any of these is wrong, the model still loads and runs, but the **kernel auto-falls back
to generic CUDA** and throughput drops 2-3x with no error message. The verifier must grep
for all three.

## FP8 KV-cache (Ampere has no native FP8)

Ampere (SM80/SM86, RTX 3090 / A100) lacks FP8 Tensor Cores. The `fp8_e4m3` KV-cache scheme
doesn't run as native FP8 — it's stored as static per-tensor scale factors baked into the
checkpoint. vLLM applies the scales at runtime and stores the KV-cache in BF16.

```python
FP8_KV_CACHE_SCHEME = QuantizationArgs(
    num_bits=8,
    type="float",
    strategy="tensor",
    dynamic=False,        # static scales (computed during quantization, baked in)
    symmetric=True,
)
```

**Why bother:** even with static scales, vLLM's KV-cache allocator reads the static scales
and packs 2 BF16 values per FP8-byte (effectively 4-bit cache). On a 24GB RTX 3090 with
~17.5 GB model + ~1.5 GB runtime, the remaining ~5 GB KV pool fits **~32,768 context tokens**
(16 full-attention layers × hidden_dim × q/k heads × 2 (k+v) × fp8-byte) before eviction.
Without FP8 KV-cache, the same pool fits ~16k context.

## Calibration protocol (40/30/30 mix @ 4096 ctx)

The calibration dataset must trigger the activation outliers that arise during deep
chain-of-thought reasoning. Vanilla chat datasets (UltraChat alone) miss this.

**40 / 30 / 30 mix:**

| % | Source | Why |
|---|---|---|
| 40% | `bespokelabs/Bespoke-Stratos-17k` (primary) / `microsoft/orca-math-word-problems-200k` / `GAIR/lima` | Deep CoT, `<think>` token sequences, multi-step math. Triggers the activation spikes that vanilla chat misses. |
| 30% | `iamtarun/python_code_instructions_18k_alpaca` / `bigcode/the-stack-smol` / `ise-uiuc/Magicoder-Evol-Instruct-110K` | Indentation, JSON schema, brackets. Activates the MLP output-channel outliers that code generation produces. |
| 30% | `HuggingFaceH4/ultrachat_200k` / `gorilla-llm/Berkeley-Function-Calling-Leaderboard` | Multi-turn chat + tool-calling. Matches serving-time distribution. |

**Context length:** 4096 tokens (was 2048 in older recipes). The 4096 length triggers the
longer-trace outliers that pure 2k calibration misses. Use `seq_len=4096` as the default;
do not regress to 2048 unless constrained by memory.

**Hessian dampening (mandatory):**

```python
GPTQModifier(
    config_groups=...,
    ignore=RECIPE_IGNORE_PATTERNS,
    actorder=None,            # desc_act=False for Marlin
    dampening_frac=0.05,      # prevents outlier clipping during math/code bursts
    offload_hessians=True,    # moves Hessians to CPU for memory safety
)
```

- `dampening_frac=0.05-0.1`: adds a small damping term to the GPTQ Hessian diagonal,
  preventing the inverse computation from blowing up on extreme activation outliers.
  **Without this, perplexity spikes by 1-2 points on math-heavy prompts.**
- `offload_hessians=True`: GPTQ accumulates a Hessian matrix per linear layer; for a 27B
  model the peak memory can hit ~12 GB. Offloading to CPU makes the recipe fit on 24GB cards.

Both parameters must be set. The recipe that produces a clean static INT4 model is one
with both flags.

## The kill-and-rebuild pattern for long-running tasks with the wrong recipe

When the running quantization is suspected of clipping sensitive layers (DeltaNet, vision,
MTP), the disciplined move is **kill and restart with the corrected recipe**, NOT to let
the run complete and "fix it later."

**Why:** A quantization that processes DeltaNet layers to INT4 produces a model that:
- Passes load + 1-token generation (the structural tests look fine)
- Fails on the user's actual workload (long-context reasoning collapses)
- Cannot be "un-quantized" — the damage is baked into the weights
- Cost: 14 minutes of model loading + ~10 min of GPTQ already done (vs 2-4 hours total)

The 14-minute waste is the **right** trade-off. Saving 1.5 hours of GPTQ compute by letting
the wrong recipe finish produces a broken artifact that costs more (re-quantize from
scratch + confusion about which model is the "real" one).

**The recipe check before re-launch:** grep the log for `compress_module_list.*Quantizing` lines.
If any line contains `linear_attn.in_proj_*` or `linear_attn.out_proj`, the recipe is wrong.
The expected pattern for a working recipe is `(N/M): Calibrating ... mlp.gate_proj /
up_proj / down_proj` and `self_attn.q_proj / k_proj / v_proj / o_proj`. Only 65 modules
in total (vs the full Linear layer count of ~768 for Qwen3.5-27B).

**Recipe for the kill-and-rebuild:**

1. Confirm the recipe is wrong (grep the running log for missing exclusion patterns).
2. `qm guest exec 230 -- bash -c 'pkill -9 -f "python3.*quantize"; sleep 3; nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -4'` — verify GPUs are free (1 MiB each).
3. Fix the recipe (`patch` or `write_file` the corrected section).
4. Transfer the fixed file to the VM via `wget` from a local HTTP server (`http://<webtop>:8766/file.py`).
5. Verify it compiles (`python3 -c "import py_compile; py_compile.compile(...); print('OK')"`).
6. Re-launch (`nohup bash /tmp/run_quant.sh > /tmp/quantize_main.log 2>&1 < /dev/null & disown`).
7. Confirm the new process is alive and at Step 1 (calibration data building).
8. Within 60-90s, check for `(1/65): Calibrating` in the log — confirming only the
   non-DeltaNet modules are being processed.

The kill-and-rebuild is correct **even when the run is hours deep**. The blast radius of a
wrong recipe is the entire artifact; the cost of re-running is one wall-clock day, not
the artifact's lifetime.

## Verifier for the recipe (before launching the GPTQ pass)

```python
# verifier structure (ad-hoc, /tmp/hermes-verify-quant-recipe-rerun.py)
checks = [
    ("7 BF16 exclusions present with 're:' prefix", [
        "re:visual", "re:merger", "re:linear_attn",
        "re:in_proj", "re:mtp", "re:embed_tokens", "lm_head",
    ]),
    ("Marlin W4A16 constraints", [
        "group_size=128", "symmetric=True", "num_bits=4",
    ]),
    ("Hessian dampening", ["dampening_frac=0.05", "offload_hessians=True"]),
    ("40/30/30 calibration weights", []),  # verified via live import
    ("FP8 KV-cache", ["fp8_e4m3", "FP8_KV_CACHE_SCHEME"]),
    ("Reasoning dataset primary", ["Bespoke-Stratos"]),
    ("Context 4096 (not 2048)", []),  # process args check
    ("Live process state", []),       # ps + grep
    ("GPU distribution", []),          # nvidia-smi check
    ("vLLM launch flags", [
        "compressed-tensors", "fp8_e4m3", "enable-prefix-caching",
        "qwen3_mtp", "trust-remote-code", "tensor-parallel-size",
    ]),
    ("Module count check (post-launch)", []),  # '(N/65): Calibrating' in log
]
```

**Always expect 1-2 rounds of fix-and-re-verify.** The first verifier run almost always
trips on SSH `qm guest exec` JSON-wrapper parsing (inner quotes get stripped, Python
SyntaxError, regex returns 0 instead of the actual count). Fix the verifier (not the
recipe), re-run, expect PASS.

**See `references/qm-guest-exec-verifier-helpers.md` for the helper functions that survive
the SSH/qm shell-escape hell.** Naive `text.find('{"')` parsing fails because the JSON
wrapper has the brace on its own line — use `text.find('{')` + `text.rfind('}')` instead.

## Serving the quantized model (vLLM launch)

```bash
vllm serve Qwen/Qwen3.8-27B-W4A16-MTP \
    --quantization compressed-tensors \  # Marlin W4A16
    --kv-cache-dtype fp8_e4m3 \          # static FP8 cache scales
    --gpu-memory-utilization 0.92 \      # reserve headroom for recurrent state
    --max-model-len 32768 \              # 32k context in ~5 GB KV pool (1 GPU)
    --enable-prefix-caching \            # reuse KV across repeated prompts
    --enable-chunked-prefill \           # long-input prefill stability
    --reasoning-parser qwen3 \           # extract <think> blocks
    --trust-remote-code                  # Qwen3.5/3.8 needs custom code
```

**Tuning for parallelism:**
- 1 GPU (24GB): `--max-model-len 32768`
- 2 GPU (48GB): `--max-model-len 131072`
- 4 GPU (96GB): `--max-model-len 262144`

The Marlin W4A16 weights are ~14-17 GB; the rest is KV-cache pool. The static FP8 scales
make the cache 50% smaller than BF16 cache, freeing more room for context.

## VRAM budget (single RTX 3090)

```
24.0 GB Total VRAM
├── Loaded W4A16 Model Weights (hybrid exclusions): ~17.5 GB
├── CUDA Context & PyTorch Runtime Workspace:        ~1.5 GB
└── Usable KV Cache Memory Pool:                     ~4.5 - 5.0 GB
    └── FP8 KV Cache (fp8_e4m3): Supports ~32,768 context tokens
```

If the model loads but OOMs at inference, the most likely cause is **not the model weight**
but the **KV-cache pool** — drop `--max-model-len` from 32768 to 16384 and try again.

## Pitfalls

- **The `re:` prefix is the single biggest pitfall.** Recipes that look right but ship with
  `r"model\.layers\.\d+\.linear_attn\..*"` instead of `"re:model\.layers\.\d+\.linear_attn\..*"`
  silently quantize DeltaNet. The Python regex unit test passes because `re.search(pattern,
  name)` works on the local string. The integration test catches it only by reading the
  GPTQ log for `Quantizing model.layers.N.linear_attn.*` lines. Always verify the
  `compress_module_list` log after launching.
- **The 7-pattern list is not exhaustive.** Different hybrid models use different naming
  conventions. For DeepSeek-V3, replace `linear_attn.*` with `model.layers.N.mlp.shared_experts.*`
  (their MoE shared experts have the same recurrent-state noise issue). For Mamba-only,
  replace with `mixer.*`. The principle is the same: **find the recurrent-state projection,
  exclude it**. Use `print(list(model.named_modules()))` to enumerate the module tree
  before writing the recipe.
- **`in_proj.*` vs `linear_attn.*` overlap.** The DeltaNet `linear_attn` module CONTAINS
  `in_proj_qkv`, `in_proj_z`, `in_proj_b`, `in_proj_a`, and `out_proj` as sub-modules.
  Listing both patterns in `ignore=` is intentional redundancy: `linear_attn.*` catches
  the parent module path (which GPTQ might traverse via the `Linear` target),
  `in_proj.*` catches the sub-projection names. Either one alone may leave gaps depending
  on how `targets="Linear"` traverses the module tree. List both.
- **`dampening_frac=0.05` is below the range llm-compressor may default to.** Some recipes
  silently set `dampening_frac=0.01` (the GPTQ default), which produces subtle quality loss
  that only shows up on math-heavy prompts. Always explicitly set `dampening_frac=0.05`.
- **`offload_hessians=True` makes the run 2-3x slower** (CPU offload + disk I/O if swap is
  involved). On a 96GB-multi-GPU setup the memory headroom is enough that this flag can be
  omitted — but on a 24GB single GPU it's mandatory or the run will OOM during Hessian
  accumulation. The flag is per-environment, not per-recipe: decide based on the GPU's
  available memory, not the recipe.
- **The FP8 KV-cache scales are baked at quantization time.** Re-running the model with
  `--kv-cache-dtype fp8_e4m3` after quantization with a different `kv_cache_scheme` produces
  a working model but with stale scales that don't match the activations. The quantization
  step is the only place to set the scheme; serving time just reads it.
- **Marlin auto-fallback is silent.** If the `group_size` or `symmetric` parameters are
  wrong, the model still serves — but throughput drops to generic-CUDA speed. The only way
  to catch this is a throughput benchmark (target: 30+ tok/s/user on 27B for SM86);
  structural tests will pass.
- **The `lued/` Qwen3.8 model line is real but only the INT8 variant ships.** As of
  2026-08-16, `lued/Qwen3.8-27B-INT4-W4A16-MTP` does not exist on Hugging Face. The
  companion repo `lued/Qwen3.8-27B-INT8-W8A16-MTP` (31.62 GB, W8A16 with preserved
  MTP head) does, and is validated for dual-RTX-3090 vLLM TP=2. If you need a vLLM-
  ready model today and don't have time to quantize from BF16, the lued INT8 is the
  working path. The mismatch in name format (`W8A16-MTP` not `W4A16-MTP`) is the
  giveaway that lued only ships the INT8 variant. Verified via HuggingFace model
  lookup; do not assume the INT4 path exists before checking.
- **Driver upgrades during a session can break the running quantization.** On
  2026-08-16 an unattended-upgrade on VM 230 silently pulled `nvidia-dkms-580`
  while the quantization was running. After reboot the kernel driver was 580.173
  but the user-space `libnvidia-ml.so.1` symlink was missing (the 580 packages
  were installed but the `libnvidia-ml.so.580` files were not). Symptom:
  `torch.cuda.is_available() == False` even though `nvidia-smi` showed all 4 GPUs.
  Recovery: install the matching user-space libs (`apt-get install
  libnvidia-compute-580-server`), reboot, verify with
  `nvidia-smi -q | grep "Driver Version"`. The fix may also be done by running
  `nvidia-smi` once after the apt install — it rebuilds the device nodes. Pattern:
  **always re-verify `torch.cuda.is_available()` after any nvidia package change
  and before re-launching a long-running quantization.**
- **The 580 vs 535 driver determines the torch pin.** After the unattended-upgrade
  to 580 on 2026-08-16, the working pin became `torch==2.13.0+cu130`. With 535
  (the prior state) the working pin was `torch==2.5.1+cu121`. `nvidia-smi
  --query-gpu=driver_version --format=csv,noheader` tells you which pin to use
  before installing torch. Installing the wrong pin produces a torch that
  imports but fails `cuda.is_available()` with `forward compatibility was
  attempted on non supported HW` (CUDA 13 torch on 535 driver) or vice-versa.
- **Mamba / RWKV models need different quant scheme.** Pure-Mamba models (no full attention
  layers) can be uniformly quantized — there's no recurrent-vs-attention asymmetry to
  exploit. The recipe collapses to "W4A16 with no exclusions" and the size benefit is the
  full 4x. The verifier checks should be relaxed for these (no `linear_attn` exclusion
  required).
- **DeepSeek-V3 MoE is its own beast.** The `shared_experts.*` Linear modules are
  recurrent-state-like (they receive the full token stream, unlike routed experts). Excluding
  them is necessary but not sufficient — the routed experts need per-expert calibration
  that the standard GPTQ recipe doesn't handle. Use a MoE-aware recipe from
  `neuralmagic/llm-compressor` examples if DeepSeek-V3 is the target.
- **The verification recipe must re-import, not just grep.** A recipe that sets
  `actorder=None` (desc_act=False) checks PASSES with `actorder=False` in the grep — both
  string-match "False" — but they're different parameters in the API. The reliable check is
  `python3 -c "from quantize import get_recipe; r = get_recipe('default'); g = r[0]; print(g.actorder)"`
  and assert the result is `None`, not `False`. The string-grep approach silently accepts a
  wrong recipe.
- **The number-of-modules counter is the integration test.** After launching the corrected
  recipe, grep for `(N/M): Calibrating` in the log. M should be ~65 for Qwen3.5-27B (the
  non-DeltaNet, non-ignored count). If M is anywhere close to 768 (full Linear layer count),
  the ignore patterns are silently failing — kill and rebuild.

## What this skill does NOT do

- It does not deploy the quantized model to a serving platform. That's
  `proxmox-k3s-gpu-cluster-ops/`. This skill stops at the recipe + verifier + the launch
  command for the user to run.
- It does not cover uniform-quantization recipes (AWQ/GPTQ on a standard transformer). For
  those, follow the `neuralmagic/llm-compressor` examples. The hybrid-attention failure
  mode is the new addition; the uniform recipe is the boring baseline.
- It does not cover MTP head preservation for non-Qwen3.5/3.8 models. The `.*mtp.*` pattern
  works for Qwen; other models with speculative decoding heads may name them differently
  (`draft_heads.*`, `medusa_heads.*`). Always `print(model.state_dict().keys())` to confirm.

## Reference

- `references/qm-guest-exec-verifier-helpers.md`: the SSH/qm shell-escape workarounds and the
  `direct_qm_grep` / `direct_qm_command` helpers. Required reading before writing any
  recipe verifier.
- Gemini's Architecture & Quantization Matrix for Qwen 3.8 27B: full 6-tip breakdown that
  this skill codifies (DeltaNet collapse, vision/MTP leakage, Ampere SM86 kernel constraints,
  calibration skew, KV cache sizing, GGUF tensor overrides). The GGUF tip (Tip 6) does not
  apply to vLLM serving — only llama.cpp — so it's intentionally omitted from this skill.
- `neuralmagic/llm-compressor` v0.13.0 API: `GPTQModifier(config_groups=..., targets=...,
  ignore=..., actorder=None, dampening_frac=0.05, offload_hessians=True)` — note the
  parameter rename from `desc_act` to `actorder`. And the `re:` prefix requirement on
  regex `ignore` patterns (this was the silent-failure bug from this session).
- **llm-compressor 0.13.0 import path changed** — `GPTQModifier` moved from
  `llmcompressor.modifiers.quantization.gptq.base` (the path in older recipes and
  most documentation) to `llmcompressor.modifiers.gptq.base`. Recipes copied from
  older examples will fail with `ImportError: cannot import name 'GPTQModifier' from
  'llmcompressor.modifiers.quantization'`. Verified in this session by reading
  `llmcompressor.modifiers.gptq.__path__` directly. `QuantizationModifier` import
  path is unchanged. `oneshot`, `recipe`, `dataset` parameter shapes also changed
  between v0.6 and v0.13 — dump `GPTQModifier.model_json_schema()` to get the
  canonical v0.13 shape before patching a recipe.
- **Dependency ordering matters at install time.** Flash-attn will fail to build
  without `torch` already installed, and the newest `llm-compressor` requires
  `torch>=2.10` (so `torch==2.5.1+cu121` won't work with `llm-compressor>=0.7`).
  For 535-driver hosts (CUDA 12.x), the working pin was
  `torch==2.5.1+cu121 torchvision==0.20.1+cu121 llmcompressor==0.6.0.1
  compressed-tensors==0.10.2`. For 580-driver hosts (CUDA 13.x), the working pin
  was `torch==2.13.0+cu130 torchvision==0.28.0+cu130 llmcompressor==0.13.0`. The
  driver version dictates which torch pin to use; `nvidia-smi --query-gpu=driver_version`
  before installing torch.
- The verifier structure (`/tmp/hermes-verify-quant-recipe-rerun.py`) is an ad-hoc targeted
  check, not a hermes suite green. Plan for 1-2 rounds of fix-and-re-verify.
- The 7-pattern ignore list with `re:` prefix is the load-bearing bit. If the recipe ships
  with fewer than 7 patterns or without the `re:` prefix, the resulting model will fail on
  the user's workload.
- This skill ships in the `operations/` category alongside the deploy infrastructure skills
  (`proxmox-k3s-gpu-cluster-ops`) but is **not** deployed under that umbrella — quantization
  recipe is its own class.