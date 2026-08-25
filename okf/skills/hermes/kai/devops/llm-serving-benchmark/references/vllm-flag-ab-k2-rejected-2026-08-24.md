# vLLM flag A/B — `--spec-tokens 2` REJECTED (2026-08-24) + engine matrix

## The A/B test (Fred, 192.168.1.230:8000)

Method: in-place python patch of `/opt/vllm_bin/start_fred.sh` (`--spec-tokens 1` → `2`, backup `start_fred.sh.bak-k1-<date>`), `systemctl restart vllm-fred` (~170s to ready), identical 2-case bench, revert + restart + verify.

| Metric | K=1 (live/final) | K=2 | Δ |
|---|---|---|---|
| Single-stream, 256-tok story prompt | 32.5–39.2 tok/s | 27.0 tok/s | −17…−31% |
| Batch-4 aggregate, 4×128-tok concurrent | 126.5–169.8 tok/s | 85.2 tok/s | −33…−50% |

**Verdict: REJECTED.** Extra draft token costs more PCIe-TP2 decode bandwidth than MTP acceptance recovers at 27B-4bit. Prior dynamic K scheduling (K=1 for batch≤3, off for batch≥4) also regressed (111.6 → 95.5 batch-4, same day). **Static MTP K=1 is final on this hardware.** Do not re-open speculative tuning without a memory-bandwidth headroom change (bigger card / smaller model).

Post-revert verification: single-stream 37.1 tok/s — back in band, production config confirmed.

## Engine matrix (measured 2026-08-24, identical prompts)

| Engine | Single-stream | Batch-4 aggregate | Notes |
|---|---|---|---|
| Fred · vLLM AWQ-4bit (TP2, MTP K=1, fp8 KV, prefix cache) | 32.5–39.2 | 126.5–169.8 | production, `local-qwen-27b-q8-fred` + 5 inert aliases |
| Kai · llama.cpp `192.168.1.232:8080` (UD-Q4_K_M, 2 slots) | 34.0 | 51.3 | **auth required**: `KAI_LLM_API_KEY` env var (Bearer) |
| Ned · llama.cpp `192.168.1.230:8003` (UD-Q5_K_M, GPU 2+3) | 6.7 | 22.7 | legacy lane; vLLM port is a candidate if his lane asks |
| INT8 W8A16 baseline (pre-AWQ) | 41.3 | — | AWQ traded ~7% single-stream for 2× KV pool |

Read: single-stream is parity-class (34 vs 32–39) — the win is entirely the concurrency tier (2.5–3.3× Kai under 4 concurrent, real ceiling 64 seqs vs 2 slots).

## Bench snippet (works from any box; authed endpoints get Bearer from env)

```python
import json, os, time, urllib.request
from concurrent.futures import ThreadPoolExecutor

def req(base, model, prompt, n, key=""):
    body = json.dumps({"model": model,
                       "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": n, "temperature": 0}).encode()
    h = {"Content-Type": "application/json"}
    if key: h["Authorization"] = f"Bearer {key}"
    r = urllib.request.Request(base + "/v1/chat/completions", data=body, headers=h)
    t0 = time.time()
    with urllib.request.urlopen(r, timeout=180) as f: d = json.load(f)
    return time.time() - t0, d["usage"]["completion_tokens"]

# single: req("http://192.168.1.230:8000", "local-qwen-27b-q8-fred", PROMPT, 256)
# Kai:    req("http://192.168.1.232:8080", "qwen3.8-27b", PROMPT, 256,
#            key=os.environ.get("KAI_LLM_API_KEY", ""))
# batch-4: ThreadPoolExecutor(4).map(lambda i: req(base, model, PROMPT2, 128, key), range(4))
```

## Operational notes
- Restart cost 150–170s to ready; don't restart during tenant peak.
- Fred KV pool: 383,479 tokens (fp8, 256 blocks × 1584 tok/block); `kv_cache_max_concurrency ≈ 1.46` at 256K ceiling → HD tenants capped at 64K (`vm_orchestrator.py` template + 12 `guest_hermes_bot_*/config.yaml`, done 2026-08-24).
- Same-day spread of ±20% in batch numbers = prefix-cache state, not config drift — compare bands.
- Canonical doc: OKF `okf/standards/vllm-fred-awq-qwen38-27b.md` (PR #44 on growthwebdev-knowledge).
