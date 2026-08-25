---
name: local-llm-inference-ops
description: "Operate, scale, migrate, or benchmark the local LLM inference stack (llama.cpp / vLLM) on PVE1's k3s GPU node that backs Hermes profiles (kai/ned/fred). Use when: switching inference backends, adding a new per-profile model instance, debugging model endpoints :31001/:31002/:31003, benchmarking generation speed before/after a change, or when a model capability (e.g. vision) is about to change."
category: devops
tags: [vllm, llama-cpp, k3s, proxmox, gpu, inference]
related_skills: [qwen-llamacpp-reasoning-effort, tailscale-lan-access]
---

# Local LLM Inference Ops (PVE1 GPU cluster)

Class of work: deploying, operating, migrating, and benchmarking the local model servers behind the Hermes profiles. They run as **k3s workloads** (not bare processes) on `k3s-node-230` (Proxmox VM 230 on pve1). Access: `ssh root@192.168.1.230` (LAN) or `root@100.78.237.7` (tailscale) — see `tailscale-lan-access`.

## Topology (verified 2026-08-18 — supersedes 2026-08-15 table)

| systemd service on .230 | port | GPU | served model | consumer |
|---|---|---|---|---|
| `vllm-george.service` (script `/opt/vllm_bin/start_george.sh`) | **8002** | 2 | Qwen3.8-27B Q4 (`-np 1 -c 131072 --mmproj --spec-type draft-mtp`) — **stopped 2026-08-22, unit still `enabled` (reboot-conflict risk, see Q5 cutover note)** | George profile |
| `vllm-ned.service` (script `/opt/vllm_bin/start_ned.sh`) | **8003** | 2+3 (TP2) | **vLLM copy of Fred's config, 2026-08-24 cutover**: `/models/barrydeen-Qwen3.8-27B-AWQ-4bit`, MTP K=1, fp8 KV, 256K ctx; served names incl. legacy GGUF path → zero consumer changes. llama.cpp artifacts kept as rollback | Ned profile |
| `llama-fred.service` (llama.cpp :8000, GPU 0) | — | — | — | **REMOVED 2026-08-18** (unit+start script moved to `*.removed-20260818-161552`; Fred uses vLLM via `vllm-fred.service`) |
| `vllm-fred.service` (script `/opt/vllm_bin/start_fred.sh`; logs `/var/log/vllm-fred.log`) | **8000** | 0+1 (TP2) | `/models/lued-Qwen3.8-27B-INT8-W8A16-MTP` (served as `local-qwen-27b-q8-fred`) — see "vLLM Fred ops notes" | Fred profile |

- Profile configs hit `http://192.168.1.230:8002/v1` and `:8003/v1` directly — the old k3s NodePort 31001/2/3 table is STALE; nothing listens on those.
- 2026-08-18 change: both .230 llama servers were `-np 2 -c 65536` → 32768 ctx PER SLOT (the "hard 32k" that broke long sessions). Now `-np 1 -c 131072` (single 3090 holds 17GB Q4 weights + 131k q4 KV fine — verified: loads in ~90s, 2.5GB headroom). Backups: `/opt/vllm_bin/*.sh.bak-ctx-*`.
- Pitfall: `-np N` splits total context across N slots — when debugging "context smaller than -c", check `/slots` (`n_ctx` per slot), not the launch flag.
- Vision LIVE on both: 1×1 red PNG → "Red" via `/v1/chat/completions` base64 data URL (tested 2026-08-18, both old and new configs).
- GPU0/1 VLLM workers = `vllm-fred.service` (Fred's INT8 27B, TP2, :8000, model id `local-qwen-27b-q8-fred`, max_model_len 262144) — live and in use, do not touch.

**pve1 GPU/NUMA map (verified 2026-08-22, host side):** pve1 = 2× Xeon Gold 6230 (80 cores, NUMA0=0-19,40-59; NUMA1=20-39,60-79). All four 3090s are PCIe-passthrough (q35, `pcie=1`) into VM 230. Host PCI BDF → NUMA: `06:00.0`→0, `2f:00.0`→0, `86:00.0`→1, `af:00.0`→1. So guest GPU0/1 sit on host NUMA 0, guest GPU2/3 on host NUMA 1. **Fred's vLLM (guest GPUs 0+1, TP2) is same-NUMA — no cross-CPU barrier; placement is correct.** Caveat: guest sees `numa_node=-1` on every GPU (passthrough doesn't expose affinity), so inside the VM you cannot tell GPUs apart by NUMA — only by this host-side BDF map. Ned(GPU3)+George(GPU2) share host NUMA 1 — a 2-GPU Ned on 2+3 would also be single-NUMA.

**Consumer topology drift (verified 2026-08-22; updated 2026-08-24):** `vllm-george` on .230 is ORPHANED (unit stopped 2026-08-22, `enabled` + `inactive` = reboot-conflict risk on GPUs 2+3 — recommend `systemctl disable`, pending Michael). The george profile points at `192.168.1.232:8080` (model `qwen3.8-27b`), kai also `.232:8080`. **As of the 2026-08-24 cutover the `vllm-*` misnomer is half-fixed:** `vllm-ned` is now actually vLLM (see cutover section below); only the george unit still runs llama.cpp-style bits if restarted at all. .232:8080 runs `llama-server-new --alias qwen3.8-27b --parallel 2 --ctx 131072`.

## 2026-08-22 Ned Q5 cutover (verified live)

Ned's `.230` endpoint (`:8003`) moved **Q4_K_M on single GPU3 → UD-Q5_K_M on guest GPUs 2+3 (tensor split `1,1`, single host NUMA 1)**:

- Weights: `/models/qwen3.8-27b-q5/{Qwen3.8-27B-UD-Q5_K_M.gguf, mmproj-F16.gguf}`. 19.77GB does NOT fit a single 24.5GB 3090 — that's why the 2-GPU split. Vision verified via live image round-trip with thinking disabled (clean `content`).
- Active script: `/opt/vllm_bin/start_ned_vm230.sh` (Q5, GPU 2+3, `--mmproj`); pre-cutover backup: `/opt/vllm_bin/start_ned_vm230.sh.bak-q4-20260822`.
- Bench delta (harness `/tmp/bench_ned230.py`, `--endpoints ned230`, identical hard prompt, non-streaming): chat **47.5 → 55.0 tok/s (+7.5 / +15.8%)**, hard **44.8 → 48.4 tok/s (+3.6 / +8.0%)**. New "no change" anchor for future .230/Ned comparisons; artifacts in `/home/ubuntu/work/benchmarks/` (`before-q4-ned-gpu3.*` / `after-q5-ned-gpu23.*`).
- **`vllm-george` is `enabled` + `inactive`** (stopped 2026-08-22): on reboot it auto-starts and would contend for GPUs 2+3 with Ned's tensor split. Recommended `systemctl disable vllm-george` — pending Michael's call, not yet executed.
- Q5 thinking-model caveat: with thinking enabled, `content` can come back empty (tokens land in the `reasoning` field). Disable thinking for clean verification; bench tok/s counts all generated tokens regardless of field.
- Fred unscathed: `vllm-fred` on `:8000`, guest GPUs 0+1 (host NUMA 0, TP2, 262k ctx) — healthy through the cutover.
- Harness fix worth reusing: the bench report's `model` line is derived dynamically from the stack string (`model_desc`) so the header renders the actual quant (e.g. `UD-Q5_K_M`) instead of a hardcoded label — a mislabeled model line in bench artifacts is a silent-trust failure, same class as the branch-divergence-count pitfall.

## 2026-08-24 Ned vLLM cutover (llama.cpp → copy of Fred's vLLM)

Ned's `:8003` llama.cpp (Q5_K_M, GPU 2+3 split) was replaced in-place with a **byte-for-byte copy of Fred's vLLM config** on the same GPUs, same port (Michael directive: "a copy of Fred's vLLM setup"). Verified live:

- **Zero-config cutover trick (reusable):** the first `--served-model-name` in `start_ned.sh` is the **legacy GGUF path** (`/models/qwen3.8-27b-q5/Qwen3.8-27B-UD-Q5_K_M.gguf`) — Ned's profile provider block sends that exact string as the `model:` field. Keeping it as a vLLM alias means NO profile/cron/aux config edits anywhere. Friendly names follow (`local-qwen-27b-q5-ned`, `qwen3.8-27b-ned`). This is the key step for any llama→vLLM cutover where consumers use path-style model ids.
- **Vision is NOT lost on this cutover:** the barrydeen AWQ checkpoint is a full VL checkpoint — verified 333 `model.visual.*` tensors in `model.safetensors.index.json` BEFORE loading. Arch is `Qwen3_5ForConditionalGeneration`. So the old "vLLM doesn't do GGUF+mmproj, vision dies" concern did not apply — the checkpoint itself carries the vision tower. Always check the safetensors index for `visual`/`vision` keys before promising vision survives a vLLM switch.
- Live numbers (vs replaced llama.cpp 6.7 single / 22.7 batch-4): **30.0 tok/s single, 120.9 tok/s batch-4** (4.5× / 5.3×). Engine ready ~155s after start. GPUs 2/3 at 23,418 MiB each; Fred on 0/1 untouched.
- Tool calls verified: `qwen3_xml` parser returned `get_weather {"location": "Honolulu"}`. Vision verified: real 64×64 PNG round-trip — answer came in the **`reasoning` field with `content: null`** (Qwen thinking + `reasoning-parser qwen3`); that is a PASS, not an empty response. Don't "fix" it by disabling the parser — consumers read `reasoning_content` via Hermes' normal merge.
- Unit surgery: same unit file name (`vllm-ned.service`), backup `*.bak-llama-20260824`, in-place Python edit of ExecStart/Description/log path (no sed -i). Old start script `start_ned_vm230.sh` and GGUFs left on disk = rollback path. Service is `enabled` — survives reboot.
- Cutover record + reusable procedure: `okf/standards/vllm-ned-awq-qwen38-27b.md` (PR #45).

## vLLM Fred ops notes (verified 2026-08-24)

- **Live launch flags** (`/opt/vllm_bin/start_fred.sh`, vLLM 0.27.1): `--tensor-parallel-size 2 --disable-custom-all-reduce --spec-method mtp --spec-tokens 1 --kv-cache-dtype fp8 --max-model-len 262144 --max-num-seqs 64 --gpu-memory-utilization 0.96 --enable-prefix-caching --enable-auto-tool-choice --tool-call-parser qwen3_xml --reasoning-parser qwen3 --host 0.0.0.0 --port 8000`.
- **Logs:** `StandardOutput=append:/var/log/vllm-fred.log` — `journalctl -u vllm-fred` shows **nothing** ("No entries"); always read the file. Grep trap: `grep -i "kv cache"` matches EVERY 10s `loggers.py` throughput line ("GPU KV cache usage") — filter those out (`grep -v loggers.py`) or you get no signal.
- **Engine health cross-check:** every 10s the log emits `Avg generation throughput: N tokens/s, Running: K reqs` + `SpecDecoding metrics` (drafted/accepted tok/s, acceptance rate). Use these to cross-verify what a client benchmark actually saw — e.g. a 0-token client row with `Running: 1` + ~38 tok/s in the same window means the stream was generated but never reached the client (harness bug), not a server failure.
- **MTP cap:** the INT8-MTP checkpoint carries exactly 1 MTP layer (separate module file) — `--spec-tokens 1` is the model maximum; do not try to raise it.
- **Optimization candidates confirmed valid for 0.27.1:** `--max-num-batched-tokens 8192` (engine warned `max_num_scheduled_tokens=2048 … consider increasing max_num_batched_tokens`) and `--gpu-memory-utilization 0.98`; removing `--disable-custom-all-reduce` was under evaluation. Keep `--max-model-len 262144` — Fred's gateway assumes 262K context; shrinking it to free KV is a config-semantics change, not a perf tweak.

## Topology (2026-08-15, superseded above)

| k3s service (ns `llm-inference`) | container port | NodePort | served model name | consumer |
|---|---|---|---|---|
| `kai` | 8002 | **31002** | `local-qwen-27b-q4-kai` | Kai profile |
| `ned` | 8003 | **31003** | `local-qwen-27b-q4-ned` | Ned profile |
| `newfred-llama-svc` | 8001 | **31001** | `local-qwen-27b-q5-fred` (Q5) | Fred profile |

- Hardware: 4× RTX 3090 24GB (typically ~23/24GB in normal use), 62GB RAM, **~31GB free on `/`**, HuggingFace reachable from the VM (HTTP 200).
- Model files: `/models/qwen3.8-27b-q4/{Qwen3.8-27B-Q4_K_M.gguf, mmproj-F16.gguf}`, As of 2026-08-22 the Q5 dir is BACK: `/models/qwen3.8-27b-q5/{Qwen3.8-27B-UD-Q5_K_M.gguf, mmproj-F16.gguf}` (UD-Q5_K_M = 19.77GB, serving Ned — see Q5 cutover note below); `lued-...INT8-W8A16-MTP` + `qwen3.8-27b-q4` also present. Unsloth deleted the plain Q5_K variants — only **UD-Q5_K_M / UD-Q5_K_S / UD-Q5_K_XL** remain in `unsloth/Qwen3.8-27B-GGUF` (measured: UD-Q5_K_M = 19.77GB, UD-Q5_K_XL = 20.88GB). **GGUF only — no safetensors on disk.**
- The served model name (llama.cpp `--alias` or vLLM's `/v1/models` id) **must match** the `model:` field in the Hermes profile config — profiles hit `http://192.168.1.230:<NodePort>/v1` and select by name. Renaming the served model breaks the profile unless config follows.

## 2026-08-18 state update (Kai endpoint)

Kai's server is a **direct `llama-server` process on 192.168.1.232:8080**, not a k3s NodePort: `llama-server-new -m /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf --mmproj /models/qwen3.8-27b-q4/mmproj-F16.gguf --spec-type draft-mtp --spec-draft-n-max 4 -ngl 99 -c 131072 -fa on --reasoning-effort medium --port 8080`. Access: `ssh root@192.168.1.232` (shared key, see `tailscale-lan-access`).

**Vision is LIVE and verified**: sent a 2×2 red/blue PNG through `/v1/chat/completions` (base64 data URL) — model answered "red blue" with correct spatial reasoning. Recipe for any future mmproj doubt: the `--mmproj` flag in `/proc/<pid>/cmdline` is necessary but NOT sufficient proof; a live image round-trip is. The server's self-reported "multimodal" capability flag in API metadata is also not proof.

## Backend switch procedure (llama.cpp → vLLM)
1. **Vision check first.** llama.cpp `--mmproj mmproj-F16.gguf` is what gives the model vision; **vLLM does not consume GGUF+mmproj.** Preserving vision requires a safetensors checkpoint that *itself* carries the vision tower — check `model.safetensors.index.json` for `model.visual.*` / `vision` keys BEFORE loading (the barrydeen AWQ 4-bit Qwen3.8-27B does: 333 `model.visual.*` tensors, arch `Qwen3_5ForConditionalGeneration` — vision survived the 2026-08-24 Ned cutover intact). If the checkpoint is text-only, losing vision is a capability regression (Kai falls back to tesseract OCR) — get the owner's explicit decision before pulling weights.
2. **Sizing.** BF16 27B (~54GB) does NOT fit the 31GB free. Use AWQ or GPTQ-Int4 safetensors (~15–18GB) so one 24GB 3090 holds weights + KV cache.
3. **Endpoint + model-id preservation (zero-config cutover).** Keep the same service name + port so base URLs don't change. Then make the **legacy model id (often a full GGUF path string in profile configs) the FIRST `--served-model-name`** in the vLLM launch, with friendly aliases after it. Consumers need zero config edits. vLLM serves OpenAI-compatible `/v1` by default.
4. **GPU placement.** One 3090 per instance via the k8s nvidia device plugin; tensor-parallel 2 only if KV headroom is tight. On .230 use explicit `CUDA_VISIBLE_DEVICES` in the start script — Fred=0,1; Ned=2,3.
5. **Never run both backends concurrently** — VRAM contention (GPUs already ~23/24GB).
6. **Verify with real traffic:** `curl http://192.168.1.230:<port>/v1/models` (confirm the legacy name appears) + a single-stream + batch-N chat-completion round-trip + a vision round-trip (expect the answer in `reasoning` with `content: null` on thinking models with `--reasoning-parser qwen3`) + one OpenAI `tools` call. "Service is green" is not done.

## Before/after benchmark (never claim "faster" on faith)
- Reusable live probe: `scripts/bench_tok_s.py <base_url> <model> <max_tokens>` — prints wall time, token counts, think-chars, tok/s, and warns on reasoning-only (answer-less) runs.
- Reference baseline (2026-08-21, Kai endpoint 192.168.1.232:8080, 27B Q4 single 3090, MTP spec decode, reasoning medium): **~49–52 tok/s** — 2048-token sustained run = 49.4 tok/s, 300-token run = 52.3, ~6% drop under sustained load. Use this as the "no change" anchor for before/after comparisons.
- Same hard prompt (multi-bug Python fix), non-streaming, same `max_tokens`, hit old and new endpoints.
- Record: wall time, **think-chars = len(reasoning_content)**, final-answer quality.
- Known Qwen-27B think-chars fingerprints: xhigh/high ≈ 10.7–11k, medium ≈ 6k, low ≈ 3.6–4.6k, none = 0 (effort-dial mechanics live in `qwen-llamacpp-reasoning-effort`).
- Set expectations honestly: llama.cpp with `flash-attn on + cont-batching + n-gpu-layers 99 + q4 KV` is near the single-stream ceiling. vLLM's real wins are concurrency/throughput (PagedAttention) — a single-stream comparison may show only a modest gain.
- **After any backend switch, re-probe the reasoning dial on the new backend** — accepted `extra_body` fields differ per backend (curl the endpoint with `reasoning_effort` variants and compare think-chars; don't assume the old mechanism still works).

## Pitfalls
- **Small `max_tokens` + reasoning dial ON = reasoning-only response (observed 2026-08-21):** with `max_tokens: 300` and medium reasoning effort, the entire budget went to `reasoning_content` (1515 think-chars) and `content` came back **empty** — a 300-token "benchmark" that produced no answer. This is the same reasoning-only failure class as the vLLM empty-completions issue below, but triggered by output-budget size rather than server config. Rule: any speed benchmark must use `max_tokens >= 2000` AND verify `answer_chars > 0` before reporting tok/s. `scripts/bench_tok_s.py` warns on this automatically. **Measured 2026-08-21 (27B Q4, .232:8080): `max_tokens >= 2000` is NOT sufficient at `reasoning_effort=medium` — a ~300-token SEO task at medium produced 5000 think-chars (~1250 tokens) in a 2000-token budget → `finish=length`, empty content, 2/2. At 1000 tokens: 5/5 empty (2320–2980 think-chars each). The only lever that made it PASS 100% was `reasoning_effort=none` (4.8s, all required facts, finish=stop). Rule refinement: for short-output tasks, either set `effort=none`, or budget `max_tokens >= 4000` if medium is required for quality. Note: think-chars ≈ 4× completion tokens consumed (5000 chars ≈ 1250 tokens).**
**Measured 2026-08-21 (continued, medium at production budget): the 1250-token estimate was an underestimate — at max_tokens=8192, medium's thinking ran 16.4k–24.4k chars (~4–6k tokens) on the same task. Plain prompt: 0/3 (2/3 finish=length with 0–302 chars content, one fully empty answer, walls 72–94s). Explicit verbatim-fact prompt: also 0/3 at 8192. At max_tokens=16384: medium + explicit prompt = 3/3 PASS (think 9k–26.4k chars, finish=stop, walls 46–123s); medium + plain prompt = still 0/3 (phone number dropped even when content fit). Conclusions: (a) medium needs ≥16384 max_tokens on this model, NOT 4000; (b) the explicit "MUST contain verbatim: <facts>" prompt line is required at medium regardless of budget; (c) medium costs 10–25× wall time vs none (46–123s vs 4.5s). Production config for fact-dense AOT copy: `effort=none` + explicit fact list + `max_tokens=8192` (5/5, ~5s) for pipeline scripts. Reserve medium for deliberation-heavy tasks with a 16k budget. **Kai profile agent defaults since 2026-08-21 (Michael directive): `model.max_tokens=18432` + `providers.qwen27b-kai-local.extra_body.reasoning_effort=medium` — 18432 ≥ 16384, so medium fits on the agent's own generations; verified via `_custom_provider_extra_body_for_agent()` merge-path check, effective at next agent init.** llama-server has no server-side max_tokens cap (no --max-tokens flag, /props default_params empty, slots unbounded) — the budget is always the caller's request field.**
- **Second pitfall (same day, budget sweep): raising `max_tokens` does NOT fix factual omission. 5-task sweep (prompts 2.7k–27k tokens, all `effort=none`) scored 1/5 at EVERY budget from 8192→15360 — all runs `finish=stop`, outputs 261–2829 ctok (never near budget). The model dropped the phone number 808-498-1894 when the prompt only said "keep every factual detail." A/B at 8192: plain prompt 0/5 pass; prompt with explicit "output MUST contain verbatim: <fact list>" line → 5/5 pass, identical wall times. Failure signature to distinguish: `finish=length` + empty/thin content = budget/reasoning problem; `finish=stop` + missing facts = prompt-explicitness problem — do NOT raise max_tokens for the second one. Also: llama-server with no `--max-tokens` flag has NO server-side cap (/props default_params empty, slot max_tokens None) — max_tokens lives entirely in the caller's request; there is no "server setting" to change.**
- **`llama-server-new` `--chat-template-kwargs` JSON parsing error (`[json.exception.parse_error.101]`):** This argument is extremely sensitive to shell escaping. The `llama-server-new` executable expects the JSON string (e.g., `{"enable_thinking": true}`) to be enclosed in single quotes, and the double quotes *within* the JSON string must **not** be escaped. For example, in a `bash` script using a heredoc, the line should appear exactly as:
  `--chat-template-kwargs '{"enable_thinking": true}'`
  Attempting to use `export LLAMA_ARG_CHAT_TEMPLATE_KWARGS='{"enable_thinking": true}'` in a shell script, even within a quoted heredoc, can lead to the shell misinterpreting the JSON string and causing parsing errors. The most reliable method is to place the correctly formatted argument directly on the `llama-server-new` command line.
- **vLLM :8000 (Fred, INT8 27B) intermittent empty completions (observed 2026-08-18 19:20-19:22):** Hermes logs show `Empty response (no content or reasoning) — retry N/3 (model=local-qwen-27b-q8-fred)` → 3 retries → fallback to gemini-2.5-flash. The endpoint itself was healthy (live completion round-trip ~1s the same evening). This is the Qwen3.8 "reasoning-only" failure mode on vLLM — the model burns output budget on the `reasoning` field and returns null content. Self-heals via Hermes retry/fallback; if frequency climbs, check vLLM `max_tokens`/stop-config on the server and whether MTP spec decoding (`--spec-type draft-mtp`) is implicated. Watch `profiles/<x>/logs/errors.log` (note: for fred, that's a symlink into the orchestrator profile — see `hermes-profile-audit` step 0).
- NodePorts are k3s (kube-proxy chain in iptables: `llm-inference/kai:http` → 31002 etc.) — change the workload, never the NodePort, or you break every profile pointed at it.
- `qm guest exec` does not forward stdin pipes — use the base64 trick (`tailscale-lan-access`).
- Hermes `load_config()` loads the *active* profile and ignores the `HERMES_PROFILE` env var — yaml-load the target profile's `config.yaml` directly when unit-testing wiring.
- When staging work for another agent (e.g. Fred doing the switch), hand over a brief with the verified recon (ps flags, df, port map, /models listing) so it doesn't re-probe — see `references/vllm-switch-2026-08-15.md` for the pattern + that specific recon.

## Session detail
- `references/vllm-switch-2026-08-15.md` — full recon of the 2026-08-15 vLLM switch, constraints, and the brief staged for Fred.
