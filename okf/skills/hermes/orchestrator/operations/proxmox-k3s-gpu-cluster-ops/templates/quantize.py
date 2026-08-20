#!/usr/bin/env python3
"""
Production-grade W4A16 (INT4) GPTQ quantization for Qwen3.8-27B.

Optimized for vLLM serving on dual RTX 3090 (Ampere, sm_86) with:
- W4A16 GPTQ (group_size=128, symmetric, actorder=None for direct Marlin kernel mapping)
- Static FP8 (fp8_e4m3) KV-cache scaling factors baked into the checkpoint
- Sensitivity exclusions (KEEP IN BF16): lm_head, mtp (Multi-Token Prediction),
  visual tower (vision encoder), AND model.layers.*.linear_attn.* (DeltaNet)

CRITICAL DeltaNet exclusion (Qwen3.8 hybrid architecture):
  Qwen3.8 is a 3:1 hybrid of 48 Gated DeltaNet (linear attention) layers and
  16 full gated-attention layers (every 4th layer; full_attention_interval=4).
  INT4 quantization of DeltaNet linear_attn.* projections collapses long-context
  reasoning because DeltaNet maintains a recurrent state matrix that ACCUMULATES
  quantization noise across the context window. Gemini's architectural analysis
  is the source. Keeping DeltaNet in BF16 results in a ~27.8 GB output instead
  of ~15 GB but preserves long-context CoT, agentic tool calling, and reasoning
  quality. This is non-negotiable.

Usage:
    python quantize.py --model-id Qwen/Qwen3.8-27B \\
                       --output-dir ./output \\
                       --num-samples 512 \\
                       --seq-len 4096

Requires:
    - transformers >= 5.0  (for qwen3_5 / Qwen3.8 architecture support)
    - llmcompressor >= 0.13 (uses the new config_groups + QuantizationArgs API)
    - torch >= 2.10  (matches the transformers 5.x requirement)
    - For driver 535 hosts (legacy):  torch==2.5.1+cu121 + llmcompressor<0.7
    - For driver 580 hosts (current): torch>=2.13+cu130 + llmcompressor>=0.13

The llmcompressor API changed at 0.13: group_size / symmetric / desc_act are
no longer kwargs on GPTQModifier. They live inside QuantizationArgs objects
inside config_groups. See README "Recipe (llmcompressor 0.13 API)" section.
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from llmcompressor import oneshot
from llmcompressor.modifiers.gptq.base import GPTQModifier
from llmcompressor.modifiers.quantization import QuantizationModifier
from compressed_tensors.quantization.quant_scheme import QuantizationScheme
from compressed_tensors.quantization.quant_args import QuantizationArgs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("quantize")


# -----------------------------------------------------------------------------
# Recipe Definition (llmcompressor 0.13+ API)
# -----------------------------------------------------------------------------

# Layer exclusions for Qwen3.8-27B hybrid architecture
# All four patterns below stay in BF16 — quantizing them causes severe
# quality degradation per Gemini's architectural analysis (2026-08-16):
#
#   1. lm_head  — output projection; ~2-3% perplexity loss if quantized
#   2. visual   — vision encoder tower; OCR/spatial reasoning collapse
#   3. mtp      — multi-token prediction draft heads; breaks speculative decoding
#   4. linear_attn.* — Gated DeltaNet projections; recurrent state accumulates
#                      quantization noise across context, collapsing CoT and
#                      agentic tool calling on long contexts. THE most critical
#                      exclusion for Qwen3.8. KEEP IN BF16.
QWEN35_27B_IGNORE_PATTERNS = [
    "lm_head",                              # Output projection
    "visual",                               # Vision encoder tower
    "mtp",                                  # Multi-token prediction heads
    r"model\.layers\.\d+\.linear_attn\..*", # Gated DeltaNet projections
]

# W4A16 (INT4 weights, FP16/BF16 activations) — Marlin kernel-friendly
W4A16_WEIGHT_SCHEME = QuantizationArgs(
    num_bits=4,
    type="int",
    symmetric=True,
    group_size=128,
    strategy="group",
)

# FP8 KV cache (fp8_e4m3, per-tensor static scaling)
FP8_KV_CACHE_SCHEME = QuantizationArgs(
    num_bits=8,
    type="float",
    strategy="tensor",
    dynamic=False,
    symmetric=True,
)

# config_groups wraps the QuantizationScheme for all Linear targets
QUANTIZATION_CONFIG_GROUPS = {
    "group_0": QuantizationScheme(
        targets=["Linear"],
        weights=W4A16_WEIGHT_SCHEME,
        input_activations=None,
        output_activations=None,
    ),
}

# GPTQModifier (note: actorder=None replaces the old desc_act=False kwarg)
# QuantizationModifier (note: kv_cache_scheme takes a QuantizationArgs object,
# not a dict)
QUANTIZATION_RECIPE = [
    GPTQModifier(
        config_groups=QUANTIZATION_CONFIG_GROUPS,
        targets="Linear",
        ignore=QWEN35_27B_IGNORE_PATTERNS,
        actorder=None,  # None = no activation reordering (Marlin-direct)
    ),
    QuantizationModifier(
        config_groups=QUANTIZATION_CONFIG_GROUPS,
        kv_cache_scheme=FP8_KV_CACHE_SCHEME,
    ),
]


# -----------------------------------------------------------------------------
# Calibration Data — 35/35/30 mix per Gemini Tip 4
# -----------------------------------------------------------------------------
# Standard ultrachat-only calibration fails to trigger the high-magnitude
# activation spikes Qwen3.8 produces during CoT reasoning and structured
# tool-calling. Pure chat distribution clips outlier scales in upper MLP
# layers, causing loop repetitions, syntax corruption in JSON tool args,
# and truncated <think> blocks.
#
# The fix: 35/35/30 mix at 4096-token context.
#   - 35% reasoning (math/CoT/logic) — surfaces activation outliers
#   - 35% structured code (Python/Rust/JSON/AST) — surfaces structured-output
#     attention patterns
#   - 30% dialogue (multi-turn) — matches serving distribution
# Context 4096 (not 2048) is required to trigger deep-reasoning activations.
#
# Public datasets verified to work (no auth needed, 2026-08-16):
#   reasoning: microsoft/orca-math-word-problems-200k, GAIR/lima
#   code: ise-uiuc/Magicoder-Evol-Instruct-110K, sahil2801/CodeAlpaca-20k
#   dialogue: HuggingFaceH4/ultrachat_200k
#
# AVOID: gsm8k alone (won't trigger agentic activations), C4/wikitext
# (pure text, no chat distribution), MathR1 / MMLU (401 gated/private).
DEFAULT_CALIBRATION_SOURCES = {
    "reasoning": ["microsoft/orca-math-word-problems-200k", "GAIR/lima"],
    "code":      ["ise-uiuc/Magicoder-Evol-Instruct-110K", "sahil2801/CodeAlpaca-20k"],
    "dialogue":  ["HuggingFaceH4/ultrachat_200k"],
}
DEFAULT_CALIBRATION_WEIGHTS = {
    "reasoning": 0.35,
    "code":      0.35,
    "dialogue":  0.30,
}


def _load_reasoning_samples(dataset_id, n_samples, tokenizer):
    """Load math/CoT samples; dispatch by schema (gsm8k=question/answer, lima=conversation)."""
    try:
        ds = load_dataset(dataset_id, "main", split=f"train[:{n_samples}]")
    except Exception:
        ds = load_dataset(dataset_id, split=f"train[:{n_samples}]")
    cols = ds.column_names
    if "question" in cols and "answer" in cols:
        return ds.map(
            lambda x: {
                "text": tokenizer.apply_chat_template(
                    [{"role": "user", "content": x["question"]},
                     {"role": "assistant", "content": x["answer"]}],
                    tokenize=False,
                )
            },
            remove_columns=cols,
        )
    if "conversation" in cols:
        return ds.map(
            lambda x: {"text": tokenizer.apply_chat_template(x["conversation"], tokenize=False)},
            remove_columns=cols,
        )
    if "problem" in cols and "solution" in cols:
        return ds.map(
            lambda x: {
                "text": tokenizer.apply_chat_template(
                    [{"role": "user", "content": x["problem"]},
                     {"role": "assistant", "content": x["solution"]}],
                    tokenize=False,
                )
            },
            remove_columns=cols,
        )
    return ds.map(lambda x: {"text": str(dict(x))}, remove_columns=cols)


def _load_code_samples(dataset_id, n_samples, tokenizer):
    """Load code samples; common schemas have 'content'/'code'/'text'/'snippet' column."""
    ds = load_dataset(dataset_id, split=f"train[:{n_samples}]")
    cols = ds.column_names
    code_col = next((c for c in ["content", "code", "text", "snippet"] if c in cols), cols[0])
    return ds.map(
        lambda x: {
            "text": tokenizer.apply_chat_template(
                [
                    {"role": "user", "content": "Review and explain this code:"},
                    {"role": "assistant", "content": f"```\n{x[code_col]}\n```"},
                ],
                tokenize=False,
            )
        },
        remove_columns=cols,
    )


def _load_dialogue_samples(dataset_id, n_samples, tokenizer):
    """Load multi-turn dialogue (ultrachat uses 'messages' schema)."""
    if "ultrachat" in dataset_id:
        ds = load_dataset(dataset_id, split=f"train_sft[:{n_samples}]")
        return ds.map(
            lambda x: {"text": tokenizer.apply_chat_template(x["messages"], tokenize=False)},
            remove_columns=ds.column_names,
        )
    ds = load_dataset(dataset_id, split=f"train[:{n_samples}]")
    return ds.map(lambda x: {"text": str(x)}, remove_columns=ds.column_names)


def build_calibration_dataset(
    tokenizer,
    num_samples: int = 512,
    seq_len: int = 4096,
    sources: dict = DEFAULT_CALIBRATION_SOURCES,
    weights: dict = DEFAULT_CALIBRATION_WEIGHTS,
):
    """
    Build the 35/35/30 calibration mix recommended by Gemini Tip 4.
    Falls back across the source list for each category if the primary is
    unavailable (HF rate-limit, gated repo, etc.).
    """
    assert abs(sum(weights.values()) - 1.0) < 1e-6, f"weights must sum to 1.0, got {sum(weights.values())}"
    samples_per_category = {cat: int(num_samples * frac) for cat, frac in weights.items()}
    last_cat = list(samples_per_category.keys())[-1]
    samples_per_category[last_cat] += num_samples - sum(samples_per_category.values())

    cats = []
    for category, source_list in sources.items():
        n = samples_per_category[category]
        logger.info("Loading %d samples for [%s] from %s", n, category, source_list)
        loaded = None
        for sid in source_list:
            try:
                if category == "reasoning":
                    loaded = _load_reasoning_samples(sid, n, tokenizer)
                elif category == "code":
                    loaded = _load_code_samples(sid, n, tokenizer)
                elif category == "dialogue":
                    loaded = _load_dialogue_samples(sid, n, tokenizer)
                logger.info("  [%s] Loaded %d samples from %s", category, len(loaded), sid)
                break
            except Exception as e:
                logger.warning("  [%s] Failed to load %s: %s", category, sid, e)
        if loaded is None:
            raise RuntimeError(f"Could not load any samples for category '{category}'")
        cats.append(loaded)

    from datasets import concatenate_datasets, Dataset
    combined = concatenate_datasets(cats).shuffle(seed=42)

    def length_ok(example):
        return len(tokenizer.encode(example.get("text", ""), add_special_tokens=False)) <= seq_len
    combined = combined.filter(length_ok, num_proc=4)
    logger.info("Calibration dataset: %d samples after length filter", len(combined))
    return combined


# -----------------------------------------------------------------------------
# Main Pipeline
# -----------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Quantize Qwen3.8-27B to W4A16 with FP8 KV cache for vLLM"
    )
    parser.add_argument("--model-id", type=str, default="Qwen/Qwen3.8-27B",
                        help="HuggingFace model ID or local path to BF16 base model")
    parser.add_argument("--output-dir", type=str, default="./output",
                        help="Output directory for compressed checkpoint")
    parser.add_argument("--num-samples", type=int, default=512,
                        help="Number of calibration samples (default 512)")
    parser.add_argument("--seq-len", type=int, default=4096,
                        help="Max sequence length for calibration (default 4096 — "
                             "Gemini Tip 4: triggers activation outliers in deep "
                             "reasoning; 2048 is too short)")
    parser.add_argument("--batch-size", type=int, default=4,
                        help="Calibration batch size")
    parser.add_argument("--num-gpus", type=int, default=4,
                        help="Number of GPUs for tensor parallel")
    parser.add_argument("--attn-impl", type=str, default="sdpa",
                        choices=["sdpa", "flash_attention_2", "eager"],
                        help=("Attention implementation. Defaults to 'sdpa' "
                              "(PyTorch built-in). Use 'flash_attention_2' "
                              "only if you have flash-attn compiled against "
                              "your torch+CUDA combo."))
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("=" * 70)
    logger.info("Qwen3.8-27B W4A16 Quantization Pipeline (architecture-aware)")
    logger.info("=" * 70)
    logger.info("Model: %s", args.model_id)
    logger.info("Output: %s", output_dir)
    logger.info("Calibration: %d samples x %d tokens (35/35/30 mix per Gemini Tip 4)",
                args.num_samples, args.seq_len)
    logger.info("Attention impl: %s", args.attn_impl)
    logger.info("GPUs: %d", torch.cuda.device_count() if torch.cuda.is_available() else 0)
    logger.info("Ignore patterns (BF16): %s", QWEN35_27B_IGNORE_PATTERNS)
    logger.info("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Load tokenizer
    # ------------------------------------------------------------------
    logger.info("Step 1/5: Loading tokenizer")
    tokenizer = AutoTokenizer.from_pretrained(args.model_id, trust_remote_code=True)

    # ------------------------------------------------------------------
    # Step 2: Build 35/35/30 calibration dataset
    # ------------------------------------------------------------------
    logger.info("Step 2/5: Building 35/35/30 calibration dataset (Gemini Tip 4)")
    calibration = build_calibration_dataset(
        tokenizer=tokenizer,
        num_samples=args.num_samples,
        seq_len=args.seq_len,
    )

    # ------------------------------------------------------------------
    # Step 3: Load model with multi-GPU offload
    # ------------------------------------------------------------------
    logger.info("Step 3/5: Loading model with device_map='auto'")
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",  # Automatic multi-GPU offload across all 4 GPUs
        trust_remote_code=True,
        attn_implementation=args.attn_impl,
    )
    model.eval()

    if torch.cuda.is_available():
        for i in range(torch.cuda.device_count()):
            alloc = torch.cuda.memory_allocated(i) / 1024**3
            reserved = torch.cuda.memory_reserved(i) / 1024**3
            logger.info("GPU %d: %.2f GiB allocated, %.2f GiB reserved", i, alloc, reserved)

    # ------------------------------------------------------------------
    # Step 4: Apply quantization recipe
    # ------------------------------------------------------------------
    logger.info("Step 4/5: Applying W4A16 + FP8 KV-cache quantization")
    logger.info("  Excluded layers (kept in BF16): %s", QWEN35_27B_IGNORE_PATTERNS)
    logger.info("  DeltaNet (linear_attn.*) is CRITICAL — keeps recurrent state stable")
    start = time.time()

    oneshot(
        model=model,
        dataset=calibration,
        recipe=QUANTIZATION_RECIPE,
        max_seq_length=args.seq_len,
        num_calibration_samples=args.num_samples,
        batch_size=args.batch_size,
        output_dir=str(output_dir),
        save_compressed=True,
    )

    elapsed = time.time() - start
    logger.info("Quantization completed in %.1f seconds", elapsed)

    # ------------------------------------------------------------------
    # Step 5: Save tokenizer + config
    # ------------------------------------------------------------------
    logger.info("Step 5/5: Saving tokenizer and config")
    tokenizer.save_pretrained(output_dir)

    metadata = {
        "model_id": args.model_id,
        "recipe": "W4A16 + FP8 KV-cache",
        "architecture": "Qwen3.5 hybrid (48 DeltaNet + 16 full-attention + 64 MLP)",
        "excluded_layers_bf16": {
            "lm_head": "Output projection",
            "visual": "Vision encoder tower",
            "mtp": "Multi-token prediction heads",
            "linear_attn.*": "Gated DeltaNet projections (recurrent state — keep BF16)",
        },
        "calibration": {
            "mix": "35% reasoning / 35% code / 30% dialogue (Gemini Tip 4)",
            "num_samples": args.num_samples,
            "seq_len": args.seq_len,
            "datasets": DEFAULT_CALIBRATION_SOURCES,
        },
        "group_size": 128,
        "symmetric": True,
        "actorder": None,
        "kv_cache": {
            "type": "fp8_e4m3",
            "strategy": "tensor",
            "dynamic": False,
        },
        "suitable_for": "vllm>=0.27.1 + Marlin kernel + Ampere (sm_86) or newer",
        "quantization_time_seconds": elapsed,
    }
    with open(output_dir / "quantization_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    logger.info("=" * 70)
    logger.info("DONE. Output saved to: %s", output_dir)
    logger.info("Serve with vLLM:")
    logger.info("  vllm serve %s \\", output_dir)
    logger.info("    --quantization compressed-tensors \\")
    logger.info("    --kv-cache-dtype fp8_e4m3 \\")
    logger.info("    --gpu-memory-utilization 0.92 \\")
    logger.info("    --max-model-len 32768")
    logger.info("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())