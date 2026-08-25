---
name: llm-serving-benchmark
description: "Before/after performance benchmarking of local LLM serving (k3s-node-230 Qwen servers :8000 fred / :8003 ned, or any OpenAI-compatible endpoint). Use before a serving-stack or model swap (e.g. llama.cpp -> vLLM) to record the 'before', after the swap to produce the delta report, or whenever a speed claim ('should be faster') needs verification."
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
- `references/vllm-flag-ab-k2-rejected-2026-08-24.md` — the `--spec-tokens 2` A/B (rejected), full engine matrix (Fred vLLM AWQ vs Kai llama.cpp `.232:8080` — authed via `KAI_LLM_API_KEY` env — vs Ned `.230:8003`), and the verdict rule.

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
1. **A killed benchmark run leaves an orphaned generation queued.** The llama.cpp servers run `--parallel 1` (single stream); killing the HTTP client does NOT cancel server-side generation. A subsequent "clean" run queues behind the orphan. Tell-tale: TTFT inflated (observed 64s on a 1-10s case) while total tok/s stays normal (~37). Always idle-probe (step 1) before any re-run; if queueing, wait for drain or restart the offending server (systemd services `vllm-fred`/`vllm-ned` on 192.168.1.230 — see `local-llm-inference-ops`).
2. **Thinking length varies ±40% run-to-run at temp 1.0** (observed 10k-26k chars on the identical hard prompt). Compare tok/s and wall-time trends, never single think-char counts.
3. **Don't benchmark while other agents are using the endpoints.** Fred/Ned/Kai sessions share the serving nodes (current: `:8000` fred, `:8003` ned on 192.168.1.230 — direct LAN, no k3s NodePorts) — a concurrent chat degrades TTFT numbers. Coordinate the window or note it in the report.
4. **Vision is out of scope.** These benchmarks are text-only. mmproj/vision capability must be re-verified separately after any stack swap (vLLM does NOT use GGUF+mmproj — see the vLLM switch brief in `work/fred-vllm-switch-brief.md`).
5. **max_tokens must exceed expected thinking length** or the answer gets starved (observed: out=0 chars when thinking hit the cap). 6000 for the hard case.
6. **A `n_tokens=0` / `ttft=None` row on one endpoint (while the other is healthy) is a failure to diagnose — not a result to report.** 2026-08-24 baseline: Ned came back ~47 tok/s; Fred's hard cases reported 0 tokens at ~160s — but vLLM server logs for the same window showed the engine generating ~38 tok/s (1 req running, HTTP 200, no errors). The 0 was a client-side stream/parsing issue, not a server failure. Procedure: (a) pull the server log window for that case and confirm generation actually happened (vLLM: 10s `loggers.py` lines — Avg generation throughput, Running reqs; llama.cpp: slot logs), (b) reproduce with a raw SSE dump (`curl -N` + `head`) to see the ACTUAL delta field names the server emits, (c) verify the harness counts both `content` AND `reasoning_content` deltas, (d) only then re-run the failed endpoint's cases. Never open a config-optimization pass or a before/after claim on a baseline that contains a 0-token row — you'd be tuning against a bug.

## Quick A/B for a single vLLM flag (start_fred.sh on 192.168.1.230:8000)
Lighter than the full before/after harness — use it for single-knob questions ("does `--spec-tokens 2` win?").
1. Back up: `cp start_fred.sh start_fred.sh.bak-<flag>-<date>`. Patch **in-place with python** (`open(r+)`, replace, `seek(0)`, `write`, `truncate`) — never `sed -i` (inode swap; same rule as bind-mounted files).
2. `systemctl restart vllm-fred`; readiness = `/v1/models` returns a served name (warm ~150–170s). If the unit dies during warm: `journalctl -u vllm-fred -n 20`.
3. Bench the SAME two cases on both candidate and baseline: non-streaming 256-tok single + batch-4 × 128-tok concurrent, timing with `urllib` and reading `usage.completion_tokens`. Run the concurrent fan-out with python `ThreadPoolExecutor` — the terminal tool REJECTS shell `&` backgrounding in foreground commands.
4. Revert + restart + verify: single-stream must land back in the baseline band (K=1: 32.5–39.2 tok/s) before you declare either result.
5. Verdict rule: regression in BOTH single and batch tiers = reject the flag. Same-day prefix-cache state explains ±20% spread (e.g. batch-4 126.5–169.8) — compare the band, not a single run.
Full record: `references/vllm-flag-ab-k2-rejected-2026-08-24.md`.

## Baseline context
llama.cpp Q4_K_M 27B, flash-attn, full GPU offload: **~37 tok/s sustained**. If vLLM does not beat this on the hard case, the switch is a concurrency/KV-memory win, NOT a speed win — say so plainly in the report instead of calling it faster.
