# Baseline: llama.cpp (recorded 2026-08-16 04:44 UTC)

The "before" for the llama.cpp -> vLLM switch, captured on a clean run (idle-probed
servers, no queueing, no concurrent users of the endpoints).

| endpoint | case | TTFT (s) | wall (s) | total tok/s | think (chars) |
|---|---|---|---|---|---|
| kai :31002 | chat | 9.94 | 13.39 | 37.1 | 402 |
| kai :31002 | hard | 0.75 | 163.9 | 36.8 | 25676 |
| ned :31003 | chat | 0.74 | 6.93 | 37.5 | 812 |
| ned :31003 | hard | 0.72 | 139.0 | 37.0 | 18939 |

Canonical artifacts: `work/benchmarks/before-llama-cpp.json` + `.report.md`.
This skill's `scripts/` hold the harness; run from `work/benchmarks/` so outputs land alongside the baseline.

## Interpretation notes
- ~37 tok/s sustained is the llama.cpp Q4_K_M 27B bar on a 3090 (flash-attn on, full GPU offload, q4 KV cache).
- First-case TTFT (kai chat 9.94s) includes KV-cache warm-up; later cases are ~0.7s.
- Think chars are NOT comparable across runs (temp 1.0, ±40% observed: 10k-26k on the same prompt).
- If the vLLM after-run lands near 37 tok/s on the hard case, the switch is a concurrency/KV-memory win, NOT a speed win.

## History / contamination incident (2026-08-16)
First capture attempt was killed at the 590s terminal cap. The orphaned generation
remained queued on the `--parallel 1` servers; the "clean" re-run queued behind it
(kai chat TTFT inflated to 64.05s, wall 67s, while tok/s stayed ~37 — the tell).
Recovered by killing the contaminated run, idle-probing (~1-3s round-trip = clean),
and re-running. The discarded `qwen-baseline-before-vllm.json` and the first
`bench_llama.py` harness (which had a buggy content-window metric reporting
357,000 tok/s) were deleted; `bench_qwen.py` replaced them.
