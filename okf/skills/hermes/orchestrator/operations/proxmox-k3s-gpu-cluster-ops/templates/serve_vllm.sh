#!/usr/bin/env bash
#
# Production vLLM startup script for Qwen3.8-27B W4A16 (INT4) with FP8 KV cache.
#
# Optimized for:
#   - Dual RTX 3090 (24 GB each, sm_86, Ampere)
#   - Native Marlin kernel execution for compressed-tensors W4A16 weights
#   - FlashAttention backend
#   - FP8 KV-cache (per-tensor static scaling)
#   - Qwen3.8 reasoning parser (extracting  ̑think... ̑/think ̑ blocks)
#   - Multimodal support (vision tower preserved in BF16)
#

set -euo pipefail

###############################################################################
# Configuration
###############################################################################

# Model path (HuggingFace ID or local path)
MODEL_PATH="${MODEL_PATH:-Qwen/Qwen3.8-27B-W4A16-MTP}"

# Server configuration
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"

# GPU configuration
TENSOR_PARALLEL_SIZE="${TENSOR_PARALLEL_SIZE:-2}"
GPU_MEMORY_UTILIZATION="${GPU_MEMORY_UTILIZATION:-0.95}"
MAX_MODEL_LEN="${MAX_MODEL_LEN:-262144}"

# Quantization-aware flags
KV_CACHE_DTYPE="${KV_CACHE_DTYPE:-fp8}"

# Performance flags
ENABLE_PREFIX_CACHING="${ENABLE_PREFIX_CACHING:-true}"
ENABLE_CHUNKED_PREFILL="${ENABLE_CHUNKED_PREFILL:-true}"
MAX_NUM_SEQS="${MAX_NUM_SEQS:-8}"

# Speculative decoding (Qwen3.8 ships with MTP heads)
ENABLE_MTP_SPEC="${ENABLE_MTP_SPEC:-true}"
MTP_NUM_TOKENS="${MTP_NUM_TOKENS:-3}"

# Reasoning
REASONING_PARSER="${REASONING_PARSER:-qwen3}"

# Multimodal (vision tower preserved in BF16)
LANGUAGE_MODEL_ONLY="${LANGUAGE_MODEL_ONLY:-false}"

# Logging
LOG_LEVEL="${LOG_LEVEL:-INFO}"

###############################################################################
# vLLM startup
###############################################################################

echo "=========================================="
echo "Qwen3.8-27B W4A16 vLLM Server"
echo "=========================================="
echo "Model:               ${MODEL_PATH}"
echo "Tensor parallel:     ${TENSOR_PARALLEL_SIZE} GPUs"
echo "Max model length:    ${MAX_MODEL_LEN} tokens"
echo "KV cache dtype:      ${KV_CACHE_DTYPE}"
echo "Max sequences:       ${MAX_NUM_SEQS}"
echo "Prefix caching:      ${ENABLE_PREFIX_CACHING}"
echo "MTP speculative:     ${ENABLE_MTP_SPEC} (${MTP_NUM_TOKENS} tokens)"
echo "Reasoning parser:    ${REASONING_PARSER}"
echo "Multimodal:          $([ "${LANGUAGE_MODEL_ONLY}" = "true" ] && echo "disabled" || echo "enabled")"
echo "=========================================="

# Build vLLM command
VLLM_ARGS=(
    --model "${MODEL_PATH}"
    --host "${HOST}"
    --port "${PORT}"
    --tensor-parallel-size "${TENSOR_PARALLEL_SIZE}"
    --gpu-memory-utilization "${GPU_MEMORY_UTILIZATION}"
    --max-model-len "${MAX_MODEL_LEN}"
    --kv-cache-dtype "${KV_CACHE_DTYPE}"
    --max-num-seqs "${MAX_NUM_SEQS}"
    --reasoning-parser "${REASONING_PARSER}"
    --trust-remote-code
)

# Toggle prefix caching
if [ "${ENABLE_PREFIX_CACHING}" = "true" ]; then
    VLLM_ARGS+=(--enable-prefix-caching)
fi

# Toggle chunked prefill
if [ "${ENABLE_CHUNKED_PREFILL}" = "true" ]; then
    VLLM_ARGS+=(--enable-chunked-prefill)
fi

# Toggle MTP speculative decoding
if [ "${ENABLE_MTP_SPEC}" = "true" ]; then
    VLLM_ARGS+=(
        --speculative-config '{"method": "qwen3_mtp", "num_speculative_tokens": '"${MTP_NUM_TOKENS}"'}'
    )
fi

# Text-only mode (disable vision)
if [ "${LANGUAGE_MODEL_ONLY}" = "true" ]; then
    VLLM_ARGS+=(--language-model-only)
fi

# Adjust max-num-batched-tokens for better throughput
VLLM_ARGS+=(--max-num-batched-tokens 8192)

# Run vLLM
exec vllm serve "${VLLM_ARGS[@]}"
