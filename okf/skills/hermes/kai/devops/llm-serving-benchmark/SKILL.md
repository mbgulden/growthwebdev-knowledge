---
name: llm-serving-benchmark
description: "Before/after performance benchmarking of local LLM serving (k3s-node-230 Qwen servers :31002 kai / :31003 ned, or any OpenAI-compatible endpoint). Use before a serving-stack or model swap (e.g. llama.cpp -> vLLM) to record the 'before', after the swap to produce the delta report, or whenever a speed claim ('should be faster') needs verification."
category: devops
tags: [benchmark, llama-cpp, vllm, qwen, performance, k3s-node-230]
related_skills: [qwen-llamacpp-reasoning-effort, tailscale-lan-access]
---

# LLM Serving Benchmark (before/after)

## When to use
- **Before** a serving-stack or model swap: record the "before" while the old stack is still live (e.g. the Aug-2026 llama.cpp -> vLLM switch).
- **After** the swap: produce the shareable delta report.
- Any time "should theoretically be faster" is said — never accept a speed claim on faith.

## Assets (this skill ships them)
- `scripts/bench_qwen.py` — streaming harness: TTFT, wall, total tok/s. Run: `python3 bench_qwen.py --label <label> --stack <stack>` (edit the ENDPOINTS dict at top if targets change).
- `scripts/compare.py` — `python3 compare.py before-<stack> after-<stack>` reads `<label>.json` files from the same dir and writes `comparison.md` with delta + verdict columns.
- `references/baseline-llama-cpp-2026-08-16.md` — the recorded llama.cpp "before" numbers + where the canonical artifacts live (`work/benchmarks/`).

## Procedure
1. **Idle probe FIRST (mandatory).** For each endpoint, fire a tiny non-streaming request and measure round-trip latency (~1-3s = idle). If it's tens of seconds, the server is queueing behind a previous generation — do NOT start a benchmark (see Pitfall 1).
2. **Run in the background.** A full run is ~8-12 min (warmup + chat + 2x hard, 2 endpoints). Foreground terminal caps at 590s and a killed run contaminates the server (Pitfall 1). Use `terminal background=true notify_on_complete=true` with output redirected to `/tmp/bench-<label>.log`.
3. **Verify the saved JSON**: all cases present, no ERROR lines, tok/s in a sane band (llama.cpp baseline ~37 tok/s; wildly different = investigate before trusting).
4. **After the swap**: `python3 compare.py before-llama-cpp after-vllm` (run from the dir containing both JSONs). The report is the shareable artifact.

## Metrics (what to trust)
- **total tok/s** = (thinking + content tokens) / generation time. The STABLE, comparable metric. On llama.cpp Q4_K_M 27B on a 3090 it is ~37 tok/s regardless of thinking length.
- **TTFT** — prefill + first token. First case in a run includes KV warm-up; later cases are the honest number.
- **wall** — end-to-end; useful for user-perceived latency on the hard case.
- **Do NOT compute "content speed after thinking ended."** When content starts late in a long think, that window denominator is ~0 and the metric explodes (bug observed: 357,000 tok/s reported for a 37 tok/s model).
- **think chars are NOT comparable across runs** at temp 1.0 (Pitfall 2).

## Pitfalls
1. **A killed benchmark run leaves an orphaned generation queued.** The llama.cpp servers run `--parallel 1` (single stream); killing the HTTP client does NOT cancel server-side generation. A subsequent "clean" run queues behind the orphan. Tell-tale: TTFT inflated (observed 64s on a 1-10s case) while total tok/s stays normal (~37). Always idle-probe (step 1) before any re-run; if queueing, wait for drain or restart the offending server (Fred owns the k8s workloads in ns `llm-inference`).
2. **Thinking length varies ±40% run-to-run at temp 1.0** (observed 10k-26k chars on the identical hard prompt). Compare tok/s and wall-time trends, never single think-char counts.
3. **Don't benchmark while other agents are using the endpoints.** Fred/Ned/Kai sessions share :31001/:31002/:31003 — a concurrent chat degrades TTFT numbers. Coordinate the window or note it in the report.
4. **Vision is out of scope.** These benchmarks are text-only. mmproj/vision capability must be re-verified separately after any stack swap (vLLM does NOT use GGUF+mmproj — see the vLLM switch brief in `work/fred-vllm-switch-brief.md`).
5. **max_tokens must exceed expected thinking length** or the answer gets starved (observed: out=0 chars when thinking hit the cap). 6000 for the hard case.

## Baseline context
llama.cpp Q4_K_M 27B, flash-attn, full GPU offload: **~37 tok/s sustained**. If vLLM does not beat this on the hard case, the switch is a concurrency/KV-memory win, NOT a speed win — say so plainly in the report instead of calling it faster.
