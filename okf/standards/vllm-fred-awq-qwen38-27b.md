---
type: Integration
title: Fred vLLM Qwen3.8-27B AWQ-4bit on .230 (TP2, MTP static K=1)
description: Fred's vLLM server at 192.168.1.230:8000 serving Qwen3.8-27B AWQ-4bit (barrydeen) across GPUs 0+1 with TP2, MTP speculative decode (static K=1, tested-final), fp8 KV cache (383,479-token pool), prefix caching, 64-seq cap. Benchmark vs Kai llama.cpp and vs Ned llama.cpp, plus the 2026-08-24 K=2 A/B test that rejected spec-tokens 2.
resource: okf/standards/vllm-fred-awq-qwen38-27b.md
tags: [vllm, local-llm, qwen, inference, hermes, fred, awq, mtp, speculative-decoding, benchmark, integration]
auth_method: unauthenticated LAN endpoint (deliberate; no key migration)
token_storage: n/a
timestamp: 2026-08-24T23:30:00Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/standards/vllm-fred-awq-qwen38-27b.md
last_verified: 2026-08-24
verified_by: kai
status: current
---

# Fred vLLM — Qwen3.8-27B AWQ-4bit (192.168.1.230:8000)

## Topology (final, 2026-08-24)

| Item | Value |
|---|---|
| Model | `/models/barrydeen/Qwen3.8-27B-AWQ-4bit/` (~26 GB, 13 files) |
| Service | `vllm-fred.service` — `/opt/vllm_bin/start_fred.sh` |
| GPUs | 0+1, TP2 (`--tensor-parallel-size 2 --disable-custom-all-reduce`), ~23.4 GiB each |
| Key flags | `--spec-method mtp --spec-tokens 1 --kv-cache-dtype fp8 --max-model-len 262144 --max-num-seqs 64 --gpu-memory-utilization 0.96 --enable-prefix-caching --enable-auto-tool-choice --tool-call-parser qwen3_xml --reasoning-parser qwen3` |
| Served names | `local-qwen-27b-q8-fred` + 5 aliases (same engine; aliases route nothing) |
| KV pool | 383,479 tokens (fp8, 256 blocks × 1584 tok/block), `kv_cache_max_concurrency ≈ 1.46` at 256K ceiling |
| Auth | **Unauthenticated** on LAN by decision; consumer keys in profiles are inert |
| Untouched | Ned llama.cpp `vllm-ned.service` on GPUs 2/3 (port 8003) |

## Benchmarks (measured 2026-08-24, identical 256-tok story prompt / 4×128-tok batch)

| Engine | Single-stream | Batch-4 aggregate | Notes |
|---|---|---|---|
| **Fred vLLM AWQ, MTP K=1** (post-revert verify) | 37.1 tok/s | ~170 tok/s (warm, prefix-cache hit) | production config |
| Fred vLLM AWQ, MTP K=1 (earlier same-day) | 39.2 / 32.5 tok/s | 126.5–169.8 tok/s | variance = prefix-cache state |
| Fred vLLM AWQ, MTP **K=2 (rejected)** | 27.0 tok/s | 85.2 tok/s | −27% single, −50% batch |
| **Kai llama.cpp .232:8080** (UD-Q4_K_M, 2 slots) | 34.0 tok/s | 51.3 tok/s | 34 vs 37 single = parity class; 3.3× behind Fred on concurrency |
| Ned llama.cpp .230:8003 (UD-Q5_K_M, GPU 2+3) | 6.7 tok/s | 22.7 tok/s | legacy lane; migration candidate |
| INT8 W8A16 baseline (pre-AWQ) | 41.3 tok/s | — | AWQ traded ~7% single for 2× KV pool |

**Read:** AWQ single-stream sits within noise of Kai's llama.cpp (34 vs 32–39). The win is entirely in the **concurrency tier**: 126–170 tok/s aggregate under 4 concurrent vs Kai's 51 and Ned's 23. MTP adds ~1.5–2× speculative length with 55.7–100% acceptance.

## A/B test: `--spec-tokens 2` — REJECTED (2026-08-24)

Method: in-place patch of `start_fred.sh` (1→2), service restart (~170s warm), identical prompts, revert + restart + verify.

| Metric | K=1 (live) | K=2 | Δ |
|---|---|---|---|
| Single 256 tok | 32.5–39.2 tok/s | 27.0 tok/s | −17…−31% |
| Batch-4 aggregate | 126.5–169.8 tok/s | 85.2 tok/s | −33…−50% |

Both tiers regressed → **static MTP K=1 is final** for this hardware. Prior dynamic K scheduling (K=1≤3, off ≥4) already regressed batch-4 111.6→95.5 (rejected same day). Do not re-open speculative tuning without a bigger memory-bandwidth headroom change.

## Tenant guardrail (2026-08-24, completed)

HD guest tenants (10 containers, 12 host config files) were all set `context_length: 262144` → ~6 full-length conversations would exhaust the 383K-token pool and preempt Fred. Fixed at the source layer:

- 12 × `/home/ubuntu/guest_hermes_bot_*/config.yaml` → **65536** (in-place write, same inode — `sed -i` breaks the read-only bind mount; tenant 43 additionally needed `docker restart` for a stale inode)
- `vm_orchestrator.py` tenant template → 65536 (both sites) + guardrail comment; `hde_orchestrator` restarted
- Result: pool fits **~6 concurrent 64K tenant conversations**; realistic worst case no longer preempts Fred
- Guest agents run one-shot `hermes -z` per message → cap effective on next message, no further restarts

## Load-balancing reality

No multi-server, no DP, no router. One engine, one continuous-batching scheduler: packs ≤64 sequences per decode step, admits mid-batch, queues on KV exhaustion (`num_requests_waiting`), preempts only when queueing isn't enough. Cross-server "routing" is static and client-side per Hermes profile. Monitoring target: `vllm:num_requests_waiting_by_reason="capacity"` — stays 0 → done tuning; non-zero → first lever is `--max-num-seqs 64 → 32`, nothing else remains on this hardware.

## Operational notes

- Backups: `start_fred.sh.bak-int8-20260824`, `.bak-static-mtp`, `.bak-k1-<date>` (pre K=2 test)
- Restart cost: ~150–170s to ready; do not restart during tenant peak
- `--kv-cache-dtype auto` is a no-op here (RTX 3090 CC 8.6 → fp8)
- Next hardware change to consider: nothing on .230 GPUs 0/1; the jump is smaller model or faster card
