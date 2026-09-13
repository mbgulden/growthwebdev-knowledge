---
type: Integration
title: Local LLM GPU Allocation & Model Topology (4-lane, .230 + .232)
description: Consolidated single-table map of every local LLM inference lane — who owns which GPUs, what runtime/model/quantization is served, context ceilings, VRAM headroom, and auth — verified live 2026-09-13. Supersedes the per-server docs as the "where does X run and is there room" reference.
resource: okf/integrations/local-llm-gpu-topology.md
tags: [local-llm, gpu-allocation, topology, vllm, llama.cpp, qwen3.8-27b, vm230, vm232, integration, consolidation]
auth_method: static api_key per lane (see local-llm-api-key.md)
token_storage: see per-lane rows + local-llm-api-key.md
timestamp: 2026-09-13T17:35:00Z
linear_issue: GRO-4929
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/local-llm-gpu-topology.md
last_verified: 2026-09-13
verified_by: fred
status: current
---

# Local LLM GPU Allocation & Model Topology

> **Verified 2026-09-13 by Fred** — live from the model hosts (root@.230 /
> root@.232): `systemctl status` on each service, the actual start scripts
> (`start_fred.sh`, `start_ned.sh`, `start_kai.sh`), `nvidia-smi` VRAM state,
> and unauthenticated `/v1/models` probes. This is the **single table of
> record** for "who owns which GPUs, what's served, is there room?"
>
> **Why this doc exists:** the topology was scattered across 5 per-server
> docs with at least one direct contradiction (Ned's runtime: vLLM vs
> llama.cpp) and one wrong capacity claim (.232 described as "spare VRAM"
> when it is in fact 97% full). This doc consolidates and corrects both.

## TL;DR

All local LLM inference runs on **two Proxmox passthrough VMs**:

- **`192.168.1.230` (k3s-node-230)** — 4× RTX 3090 (96 GB), all PCIe-passthrough.
  Hosts **two vLLM servers** (Fred + Ned), each TP2 on a GPU pair, both at
  96% memory utilization. **100% of .230's 96 GB is allocated.**
- **`192.168.1.232` (k3s-node-232)** — 1× RTX 3090 (24.5 GB).
  Hosts **one llama.cpp pool** (Kai + George shared), single GPU, 2 parallel
  slots. **~97% of its VRAM is in use; 378 MiB free.**

**There is no spare GPU capacity anywhere in the local fleet.** Adding a new
agent = add a `served-model-name` to an existing engine (zero GPU cost), or
rebalance `--gpu-memory-utilization`, or add hardware.

## The consolidated table

| Lane | Host | Service | Runtime | Model / quant | GPUs | TP | Port | Served name(s) | `max_model_len` | Auth key (env) | VRAM headroom |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Fred** | `.230` | `vllm-fred.service` | vLLM 0.27.1 | Qwen3.8-27B **AWQ-4bit** (barrydeen) | 0+1 | 2 | **8000** | `local-qwen-27b-q8-fred` + 5 aliases | **262144 (256k)** | `VLLM_FRED_API_KEY` → `/opt/vllm_bin/.api_keys_fred` | ~0 (0.96 util, 23.4 GiB/GPU) |
| **Ned** | `.230` | `vllm-ned.service` | vLLM 0.27.1 | Qwen3.8-27B **AWQ-4bit** (barrydeen) | 2+3 | 2 | **8003** | legacy GGUF path + `local-qwen-27b-q5-ned` + `qwen3.8-27b-ned` | **262144 (256k)** | `VLLM_NED_API_KEY` → `/opt/vllm_bin/.api_keys_ned` | ~0 (0.96 util, 23.4 GiB/GPU) |
| **Kai + George (pool)** | `.232` | `llama-kai.service` | llama.cpp (`llama-server-new`) | Qwen3.8-27B **UD-Q4_K_M** GGUF + `--mmproj` BF16 | 0 (single) | n/a | **8080** | `qwen3.8-27b` (1 alias) | served **65536 (65k)**; train 262144 | `KAI_LLM_API_KEY` → `/opt/llama_bin/.api_keys` | **378 MiB free / 24576** (97% used) |
| ~~George~~ | ~~`.230`~~ | `vllm-george.service` | — | **GONE** | — | — | **8002** | — | — | — | **DEAD** (server removed; unit disabled 2026-08-23) |

**Profile → lane routing** (client side, Hermes `config.yaml`):

| Hermes profile | Primary lane | Notes |
|---|---|---|
| Fred (orchestrator) | `.230:8000` (Fred vLLM) | This profile runs on `local-qwen-27b-q8-fred` |
| Ned | `.230:8003` (Ned vLLM) | Sends the legacy GGUF path as model id |
| George | `.232:8080` (Kai pool) | **Moved off the dead `.230:8002`** — now shares the Kai llama.cpp pool |
| Kai | `.232:8080` (Kai pool) | Co-tenant of the George pool |
| All 11 profiles (aux) | `.230:8000` + `:8003` | HDE guest template env-driven keying (GRO-4929) |

## Corrections to prior docs (the reconciliation)

1. **Ned's runtime is vLLM AWQ, NOT llama.cpp Q5.** The
   [`vllm-ned-q5-gpu23.md`](./vllm-ned-q5-gpu23.md) integrations doc describes
   the pre-cutover state (llama.cpp `UD-Q5_K_M`, 2-GPU tensor split, port
   8003). On **2026-08-24** that server was replaced with a copy of Fred's
   vLLM setup (AWQ-4bit, same port, TP2 on GPUs 2+3) — see
   [`vllm-ned-awq-qwen38-27b.md`](../standards/vllm-ned-awq-qwen38-27b.md)
   (PR #45). The integrations doc was not updated after the cutover and is now
   **stale on the runtime**; its 2026-09-13 capacity additions (256k, no free
   VRAM) are still correct. **Treat `vllm-ned-awq-qwen38-27b.md` as the
   authoritative runtime record for Ned**, and this table as the cross-lane map.

2. **`.232` is NOT spare capacity.** The Ned doc (09-13) suggested "use the
   `.232` llama.cpp pool (likely has spare VRAM)." Live `nvidia-smi` on 2026-09-13
   shows `.232` GPU 0 at **23880 / 24576 MiB used — 378 MiB free, 97% utilization,
   83% GPU util, 80 °C, 391 W**. The pool is effectively **full**. Do not
   route new load to `.232:8080` expecting headroom; it will thrash or OOM.

3. **`.230:8002` (George's old standalone) is dead.** Connection refused
   (verified 2026-09-13). The `vllm-george` unit was stopped 2026-08-22 and
   `systemctl disable`d 2026-08-23. George's profile now uses the `.232:8080`
   pool. Any config still pointing at `192.168.1.230:8002` is **stale and must
   be updated** (see "Hermes config updates" below).

## Capacity / "is there room for another agent?"

**No — not as a new engine.** The three live lanes are all at ~96–97% VRAM.
Options, cheapest first:

1. **Add a `served-model-name` to an existing engine** (zero GPU cost). vLLM
   serves many model IDs per engine; both .230 engines already list 3+ names.
   llama.cpp `.232` is single-model but could serve a second alias.
2. **Lower `--gpu-memory-utilization`** on a .230 engine to carve a KV slice
   for a 3rd engine — costs concurrency on the existing server.
3. **Add hardware** (another 3090 or a dedicated VM) — the only real expansion.

**Box-level:**
- `.230`: 4×3090 = 96 GB, **100% allocated** between Fred (0+1) and Ned (2+3),
  both at 0.96. Note: `nvidia-smi` on .230 throws a driver/library mismatch
  (580.178) as of 2026-09-13 — a kernel/userspace re-sync (reboot or driver
  reload) is needed; it does **not** affect the running vLLM engines (still
  serving 200 on `/v1/models`).
- `.232`: 1×3090 = 24.5 GB, **~97% allocated** to the single llama.cpp pool.

## Ops / quick recovery

```bash
# .230 — status
ssh root@192.168.1.230 "systemctl status vllm-fred vllm-ned --no-pager | head -12"

# .230 — restart one (do NOT restart during tenant peak; ~150–170 s to ready)
ssh root@192.168.1.230 "systemctl restart vllm-ned"

# .232 — status
ssh root@192.168.1.232 "systemctl status llama-kai --no-pager | head -8"

# .232 — restart
ssh root@192.168.1.232 "systemctl restart llama-kai"

# health (unauthenticated; /v1/models is ungated on llama.cpp, gated on vLLM)
curl -sS -m 8 http://192.168.1.230:8000/v1/models   # -> Unauthorized (vLLM, needs key)
curl -sS -m 8 http://192.168.1.232:8080/v1/models    # -> model list (llama.cpp, unauth)
```

## Cross-references

- [`local-llm-api-key.md`](../standards/local-llm-api-key.md) — the auth
  pattern + per-lane key file locations + Autobot watchdog.
- [`vllm-fred-awq-qwen38-27b.md`](../standards/vllm-fred-awq-qwen38-27b.md) —
  Fred lane detail, MTP A/B test, tenant guardrail, benchmarks.
- [`vllm-ned-awq-qwen38-27b.md`](../standards/vllm-ned-awq-qwen38-27b.md) —
  Ned lane detail (authoritative runtime), 2026-08-24 cutover, benchmarks.
- [`vllm-ned-q5-gpu23.md`](./vllm-ned-q5-gpu23.md) — **stale on runtime**
  (pre-cutover llama.cpp); keep for the 2-GPU tensor-split rationale + NUMA
  map. Superseded on runtime by the AWQ standard above.
- [`llama-cpp-george-local-server.md`](./llama-cpp-george-local-server.md) —
  George's **dead** `.230:8002` lane (historical); George now on `.232:8080`.
- [`agent-profile-inventory.md`](./agent-profile-inventory.md) — which Hermes
  profiles exist and their primary model routing.

## Hermes config updates (pending — see Linear)

The following profile configs are stale against this verified topology and
need updating (blocked on explicit direction + gateway-restart window):

- **George** `config.yaml` → `custom_providers.qwen27b-george-local` still
  points at `http://192.168.1.230:8002/v1` (dead). Must retarget to
  `http://192.168.1.232:8080/v1` with the `KAI_LLM_API_KEY` (or a dedicated
  George key) — or confirm George is already migrated and this is only a doc
  gap. **Verify live before changing.**
- **Ned** `config.yaml` → `default_model` may still point at the Q4 GGUF path
  (`/models/qwen3.8-27b-q4/...`) while the server serves the AWQ checkpoint
  under a legacy name — reconcile the served `/v1/models` id.
- Confirm all 11 aux profiles resolve `VLLM_FRED_API_KEY` / `VLLM_NED_API_KEY`
  (GRO-4929 env-driven keying) after any `.env` change.
