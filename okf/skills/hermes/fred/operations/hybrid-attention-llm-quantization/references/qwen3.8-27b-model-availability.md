# Qwen3.8 27B Quantized Models — HuggingFace Availability Reference

Snapshot of HuggingFace Hub availability as of 2026-08-16. Use this to short-circuit the "which quantized model should we use?" question without re-doing the search.

## The user-suggested format

Michael asked the agent to quantize the BF16 base model `Qwen/Qwen3.8-27B` (55.6 GB) down to W4A16 (INT4) and publish under the format:

```
Mbgulden/Qwen3.8-27B-INT4-W4A16-MTP
```

The `INT4` / `W4A16` / `MTP` naming follows the `lued/Qwen3.8-27B-INT8-W8A16-MTP` precedent. The resulting model:
- Size target: ~14-18 GB on disk (vs 31.6 GB for INT8)
- Fits on a single 24 GB RTX 3090 with FP8 KV cache (~32k context)
- MTP head preserved in BF16 for vLLM speculative decoding support

## What `lued/` ships (the precedent)

| Repo | Exists? | Size | Notes |
|---|---|---|---|
| `lued/Qwen3.8-27B-INT8-W8A16-MTP` | ✅ Yes | 31.62 GB | Validated for dual RTX 3090 with vLLM TP=2; W8A16 (INT8 weights, 16-bit activations); MTP head preserved |
| `lued/Qwen3.8-27B-INT4-W4A16-MTP` | ❌ **Does not exist** | — | The INT4 companion repo was never published |

**Implication:** if you need a vLLM-ready Qwen3.8 27B model today without running the BF16→INT4 quantization pipeline yourself, the lued INT8 is the path that ships. The INT4 variant does not exist; treat any URL/claim that it does as a hallucination.

## The official Qwen model

| Repo | Exists? | Notes |
|---|---|---|
| `Qwen/Qwen3.8-27B` | ✅ Yes | 55.6 GB BF16; the base model for quantization |
| `Qwen/Qwen3.8-27B-FP8` | ⚠️ Conditional | 26.4 GB but FP8 weights; **Blackwell-only** (B100/B200/GB200). RTX 3090 (Ampere SM86) has no native FP8 Tensor Cores — running FP8 weights on Ampere forces software dequantization or fallback to a slower integer pipeline. Do NOT pick this for the 3090 fleet. |
| `Qwen/Qwen3.8-27B-NVFP4` | ❌ Same restriction | NVFP4 is a Blackwell format. |

## Other Qwen3.8 community quantizations

As of 2026-08-16 a HF Hub search for `Qwen3.8-27B` with the `quantization` filter returned no widely-used INT4-AWQ or INT4-GPTQ variants. Community quants exist for older Qwen models (2.5, 3.0) but the 3.8 hybrid-architecture model has not been broadly quantized by the community. Going from BF16 yourself is the only path.

## Recommended deployment paths (ranked)

1. **Self-quantize BF16 → W4A16** (the hybrid-attention recipe from `hybrid-attention-llm-quantization/SKILL.md`). Produces a 14-18 GB model that fits a single 24 GB GPU. ETA: 2-4 hours GPU compute after a 30-45 min BF16 download.
2. **Use `lued/Qwen3.8-27B-INT8-W8A16-MTP`** with vLLM TP=2 on 2 GPUs. 31.6 GB but works today without quantization. ETA: 20 min download + 2 min deploy.
3. **Run BF16 with vLLM TP=2** (the GGUF Q4_K_M is 17 GB and fits on one 24 GB GPU with FP8 KV-cache, but BF16 needs 2 GPUs). 55.6 GB model. ETA: 45 min download + deploy.
4. **Use the Q4_K_M GGUF** with llama.cpp on 1 GPU (the existing Kai/Ned deployment). 17.1 GB, 262k context. ETA: already deployed.

Path #1 is the long-term right answer (per Gemini's architecture matrix). Path #2 is the working answer for "right now."

## Naming-convention reminder

The `INT4` / `W4A16` / `MTP` triplet encodes:
- **INT4** = W4A16 (4-bit weights, 16-bit activations) — the quantization level
- **W4A16** = the weight-activation precision tuple
- **MTP** = Multi-Token Prediction (speculative decoding) head preserved

For Qwen3.8 27B specifically, "W4A16-MTP" means:
- W4A16 weights and activations (Marin GEMM compatible, group_size=128, symmetric)
- MTP head kept in BF16 (so vLLM can use it for speculative decoding)

If anyone asks for "INT8-W8A16-MTP" they mean the lued variant (31.6 GB, dual-GPU only). If they ask for "W4A16-MTP" they mean a single-GPU INT4 quant that needs to be self-produced.

## Reference

- HF Hub: `https://huggingface.co/Qwen/Qwen3.8-27B` (base model, 55.6 GB BF16)
- HF Hub: `https://huggingface.co/lued/Qwen3.8-27B-INT8-W8A16-MTP` (the only community vLLM-ready variant)
- HF Hub: `https://huggingface.co/Mbgulden/Qwen3.8-27B-INT4-W4A16-MTP` (target publication after our quantization completes)
- The pipeline that produces the Mbgulden variant: `/tmp/qwen-quantize/quantize.py` and `/tmp/qwen-quantize/serve_vllm.sh` from the 2026-08-16 session.