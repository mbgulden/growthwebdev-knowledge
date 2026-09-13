# Multi-profile capacity planning for a shared local LLM engine

Class: Michael asks "how many Hermes profiles can I have working on <local model>?"
when he plans to put "everyone to work." The profile side is NOT the constraint —
the inference engine is. (Verified 2026-08-26 for Qwen3.8-27B on .230.)

## Core insight

- Hermes profiles are effectively unbounded: a profile = config dir + gateway
  process (~0.5–1 GiB RAM each on the Hermes VM). Dozens of gateways is cheap.
- The real limits all sit in the one vLLM/llama.cpp engine they share:

  | Lever | Where | Meaning |
  |---|---|---|
  | `--max-num-seqs` | vLLM launch flag | hard cap on concurrently generating requests; beyond it, requests queue |
  | KV cache (fp8) | vLLM | shared pool; long-ctx (200K+) sessions are the pressure point and can get preempted |
  | Throughput | engine | per-profile tok/s drops as more profiles go active; batch-4 is the measured sweet spot |
  | Hermes gateways | orchestrator host | ~0.5–1 GiB each — never the bottleneck |

- Idle profiles cost zero GPU. Cron jobs draw from the same pool when they fire.

## Audit recipe (the only right way to answer)

1. `ls ~/.hermes/profiles/` — enumerate profiles.
2. Per profile config: `grep -oE 'api: http://[0-9.]+:[0-9]+/v1' config.yaml`
   plus the `default:` model line → build the consumer map. Count cron jobs per
   profile from `profiles/<p>/cron/jobs.json`.
3. `curl -s <base>/v1/models -H 'Authorization: Bearer <key>'` → confirm served
   model IDs and `max_model_len` (the real per-request ctx cap).
4. `ssh root@<gpu-box> 'nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv'`
   on EVERY box (`.230` AND `.232`) → allocation + headroom.
5. Read the engine launch flags from the systemd unit / start script
   (`max-num-seqs`, `max-model-len`, `gpu-memory-utilization`) — those are the
   actual limits, not the docs.

## Sizing heuristics (27B-class, one 2×3090 vLLM instance, 256K ctx)

- **Comfort: 4–6 active interactive profiles** (≈ the measured batch-4 point:
  ~30 tok/s at low concurrency, ~120 tok/s aggregate at batch 4).
- **Workable: 10–12** — expect queuing and slower turns when everyone fires at
  once; 200K+ ctx sessions can get preempted under KV pressure.
- If the question is "how many can I CREATE," the answer is "unbounded — they
  cost nothing until active." Size for ACTIVE concurrency, not profile count.

## Expansion ladder (cheapest first)

1. New profile → same endpoint, own provider block (zero GPU cost until active).
   Copy the consumer profile's provider block; `model:` must match a served ID.
2. KV/seqs tuning: drop `max-model-len` (256K is overkill for most profiles) or
   bump `max-num-seqs`. This is a config-semantics change, not a perf tweak —
   gateways may assume the long ctx, so check with Michael first.
3. Second engine: `.232` runs one 3090 (Kai's llama-server). The AWQ-4bit 27B
   safetensors (~15–18 GB) fit a single 24 GB 3090 at ~128K ctx → that trade-up
   is the cheapest expansion (recipe class: `vllm-via-lued-int8.md`).

## Pitfalls

- **Don't answer a capacity question from config files alone.** Profile configs
  tell you who is connected; engine flags + live nvidia-smi tell you the limits.
  Both halves required.
- **`/v1/models` `max_model_len` is per-request, not per-profile** — every
  consumer shares one pool.
- **vLLM `/metrics` may be empty** — engine health lives in the log file
  (`/var/log/vllm-*.log`, 10s throughput lines; grep out `loggers.py`), not
  Prometheus.
- **The consumer map is the most-drifted piece** — always re-grep profile
  configs instead of trusting the snapshot below.

## State snapshot 2026-08-26 (verify before reuse)

- `.230:8003` (Ned; vLLM barrydeen AWQ-4bit, GPU 2+3, 256K ctx, max-num-seqs 64)
  → ONLY the `ned` profile.
- `.230:8000` (Fred; vLLM INT8-MTP, GPU 0+1, 262K ctx) → `orchestrator`,
  `hdengine`, `next-step`, `fred`. NOTE: `next-step`'s base URL reads
  `100.858.237.7` while everyone else reads `100.78.237.7` — suspected typo,
  unverified.
- `.232:8080` (Kai; llama-server Q4, single 3090, ~23.9/24 GiB used at rest) →
  `kai`, `george`.
- ~15 profiles exist; the rest point at ollama-11434 (deepseek-v4-flash) or cloud.
