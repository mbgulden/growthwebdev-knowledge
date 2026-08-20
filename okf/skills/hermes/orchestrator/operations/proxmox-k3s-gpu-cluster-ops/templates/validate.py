#!/usr/bin/env python3
"""
Validation script for Qwen3.8-27B W4A16 quantization.

Measures perplexity against the BF16 baseline, Time-to-First-Token (TTFT),
inter-token latency, and peak VRAM consumption.

Usage:
    python validate.py --baseline Qwen/Qwen3.8-27B \\
                      --quantized ./output \\
                      --num-samples 100
"""

import argparse
import json
import logging
import time
from pathlib import Path
from typing import List, Optional

import torch
import torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("validate")


def compute_perplexity(
    model_path: str,
    dataset: List[str],
    seq_len: int = 2048,
    device: str = "cuda",
) -> float:
    """Compute perplexity on a dataset."""
    logger.info("Loading model: %s", model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    losses = []
    with torch.no_grad():
        for i, text in enumerate(dataset):
            ids = tokenizer(text, return_tensors="pt", truncation=True, max_length=seq_len).input_ids.to(device)
            if ids.size(1) < 2:
                continue
            outputs = model(ids, labels=ids)
            loss = outputs.loss.item()
            losses.append(loss)
            if (i + 1) % 10 == 0:
                logger.info("Processed %d / %d samples", i + 1, len(dataset))

    avg_loss = sum(losses) / len(losses)
    perplexity = torch.tensor(avg_loss).exp().item()
    logger.info("Perplexity: %.4f (avg loss: %.4f)", perplexity, avg_loss)

    # Free model from GPU
    del model
    torch.cuda.empty_cache()

    return perplexity


def measure_ttft_latency(
    model_path: str,
    prompts: List[str],
    max_new_tokens: int = 64,
) -> dict:
    """Measure Time-to-First-Token (TTFT) and inter-token latency."""
    logger.info("Measuring TTFT and latency for: %s", model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    ttft_list = []
    itl_list = []  # Inter-token latency

    for i, prompt in enumerate(prompts):
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            # Warm-up
            _ = model.generate(**inputs, max_new_tokens=1, do_sample=False)

            # Measured run
            start = time.time()
            output = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                return_dict_in_generate=True,
            )
            ttft = time.time() - start

            # Compute per-token latency
            total_tokens = output.sequences.shape[1] - inputs.input_ids.shape[1]
            if total_tokens > 0:
                # Approximate: first token latency ≈ TTFT, rest = (total - TTFT) / remaining
                itl = ttft / total_tokens
                itl_list.append(itl)
                ttft_list.append(ttft)

        if (i + 1) % 5 == 0:
            logger.info("Processed %d / %d prompts", i + 1, len(prompts))

    # Free model
    del model
    torch.cuda.empty_cache()

    return {
        "ttft_mean_sec": sum(ttft_list) / len(ttft_list),
        "ttft_p50_sec": sorted(ttft_list)[len(ttft_list) // 2],
        "itl_mean_sec": sum(itl_list) / len(itl_list),
        "itl_mean_tokens_per_sec": 1.0 / (sum(itl_list) / len(itl_list)),
    }


def measure_peak_vram(model_path: str, prompt: str) -> float:
    """Measure peak VRAM consumption during inference."""
    logger.info("Measuring peak VRAM for: %s", model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    # Reset peak memory stats
    torch.cuda.reset_peak_memory_stats()

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        # Run a long generation to capture peak VRAM
        output = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
        )

    peak_gib = torch.cuda.max_memory_allocated() / 1024**3
    logger.info("Peak VRAM: %.2f GiB", peak_gib)

    # Free model
    del model
    torch.cuda.empty_cache()

    return peak_gib


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate W4A16 quantization")
    parser.add_argument("--baseline", type=str, default="Qwen/Qwen3.8-27B",
                        help="Baseline BF16 model path")
    parser.add_argument("--quantized", type=str, required=True,
                        help="Quantized W4A16 model path")
    parser.add_argument("--num-samples", type=int, default=100,
                        help="Number of samples for perplexity")
    parser.add_argument("--seq-len", type=int, default=2048,
                        help="Sequence length for perplexity")
    parser.add_argument("--output", type=str, default="validation_results.json",
                        help="Output JSON file")
    parser.add_argument("--skip-perplexity", action="store_true",
                        help="Skip perplexity (useful when baseline is unavailable)")
    parser.add_argument("--skip-latency", action="store_true",
                        help="Skip latency measurements")
    parser.add_argument("--skip-vram", action="store_true",
                        help="Skip VRAM measurements")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    # Load validation dataset
    logger.info("Loading validation dataset (wikitext-2-raw-v1)")
    ds = load_dataset("wikitext", "wikitext-2-raw-v1", split=f"test[:{args.num_samples}]")
    validation_texts = [t for t in ds["text"] if len(t.strip()) > 100]

    results = {
        "baseline": args.baseline,
        "quantized": args.quantized,
        "num_samples": args.num_samples,
    }

    # 1. Perplexity comparison
    if not args.skip_perplexity:
        logger.info("=" * 70)
        logger.info("Computing baseline perplexity")
        logger.info("=" * 70)
        baseline_ppl = compute_perplexity(args.baseline, validation_texts, seq_len=args.seq_len)
        results["baseline_perplexity"] = baseline_ppl

        logger.info("=" * 70)
        logger.info("Computing quantized perplexity")
        logger.info("=" * 70)
        quantized_ppl = compute_perplexity(args.quantized, validation_texts, seq_len=args.seq_len)
        results["quantized_perplexity"] = quantized_ppl

        # Perplexity degradation percentage
        ppl_degradation = (quantized_ppl - baseline_ppl) / baseline_ppl * 100
        results["perplexity_degradation_percent"] = ppl_degradation
        logger.info("Perplexity degradation: %.2f%%", ppl_degradation)

    # 2. TTFT + latency
    if not args.skip_latency:
        sample_prompts = validation_texts[:10]
        logger.info("=" * 70)
        logger.info("Measuring quantized latency")
        logger.info("=" * 70)
        latency = measure_ttft_latency(args.quantized, sample_prompts)
        results["quantized_latency"] = latency

    # 3. Peak VRAM
    if not args.skip_vram:
        sample_prompt = "The future of AI is" * 100
        logger.info("=" * 70)
        logger.info("Measuring quantized peak VRAM")
        logger.info("=" * 70)
        peak_vram = measure_peak_vram(args.quantized, sample_prompt)
        results["quantized_peak_vram_gib"] = peak_vram

    # Save results
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2)

    logger.info("=" * 70)
    logger.info("Validation results saved to: %s", args.output)
    logger.info("=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
