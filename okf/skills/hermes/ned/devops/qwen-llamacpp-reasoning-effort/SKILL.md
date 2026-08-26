---
name: qwen-llamacpp-reasoning-effort
description: "Set/verify/adjust thinking levels (none/low/medium/high/xhigh) on Hermes profiles backed by custom llama.cpp servers (Kai :31002, Ned :31003 on 192.168.1.230). Use when a user says 'go high/medium/low', complains about slow local-model responses, or asks to tune reasoning on these profiles."
category: devops
tags: [hermes, llama-cpp, qwen, reasoning, config]
related_skills: [hermes-agent]
---

# Qwen 27B / llama.cpp Reasoning Effort

Applies to Hermes profiles whose main model is a custom OpenAI-compatible llama.cpp server. Known instances (2026-08-15):

| Profile | Provider key | URL | Model |
|---|---|---|---|
| kai | `qwen27b-kai-local` | http://192.168.1.230:31002/v1 | local-qwen-27b-q4-kai |
| ned | `qwen27b-ned-local` | http://192.168.1.230:8003/v1 | /models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf |

Both run Qwen 3.8 27B Q4_K_M GGUF. **Port/model drifts with every server swap** — Ned's was `:31003` + `local-qwen-27b-q4-ned` as of 2026-08-15, now `:8003` + full GGUF path (verified 2026-08-18). Don't trust this table; live-verify first: `grep -A8 '<provider-key>:' ~/.hermes/profiles/<p>/config.yaml` and `curl -s <base>/v1/models`. Server-side `reasoning_effort` levels verified live: `xhigh/high ≈ 10.7–11k think-chars`, `medium ≈ 6k`, `low ≈ 3.6–4.6k`, `none = 0` (thinking fully off). **Server default is xhigh-class** — a Hermes agent with no effort set is running at max thinking.

## The one rule
**Never use `agent.reasoning_effort` or the `/reasoning` command for these routes.** Hermes's `run_agent._supports_reasoning_extra_body()` returns False for non-OpenRouter/Nous/GitHub/LM-Studio custom providers, so the effort never leaves the process. The **only** path that works is the provider block's `extra_body` (and the aux task's `extra_body`).

## Set levels
```bash
# Main model
hermes --profile <p> config set "providers.<provider-key>.extra_body.reasoning_effort" <none|low|medium|high|xhigh>
# Image reads
hermes --profile <p> config set "auxiliary.vision.extra_body.reasoning_effort" <level>
```
Defaults we use: **main = medium, vision = low**. For other aux tasks (compression, web_extract, ...) add the same `extra_body` key under that task only when its latency matters — web_extract on Ned already carries `thinking: disabled` (a different, older mechanism); don't delete it, add alongside.

## Verify (all three layers — config readback alone is not proof)
1. `hermes --profile <p> config check` — expect clean (a `max_tokens: unknown config key` warning is pre-existing/harmless).
2. Unit-test the actual merge path Hermes uses. **Pitfall: `load_config()` loads the *active* profile — the HERMES_PROFILE env var does not switch it. For a non-active profile, yaml-load the file directly:**
```python
import sys, yaml
sys.path.insert(0, "/home/ubuntu/.local/share/pipx/venvs/hermes-agent/lib/python3.12/site-packages")
from hermes_cli.config import get_compatible_custom_providers
from agent.agent_init import _custom_provider_extra_body_for_agent
cfg = yaml.safe_load(open("~/.hermes/profiles/<p>/config.yaml".expanduser()))
eb = _custom_provider_extra_body_for_agent(
    provider="custom:<provider-key>", model="<model>",
    base_url="http://192.168.1.230:<port>/v1",
    custom_providers=get_compatible_custom_providers(cfg))
assert eb and eb["reasoning_effort"] == "<expected>", "effort not wired"
```
3. Live probe the server (any task; think-chars in `reasoning_content` is the dial's fingerprint):
```bash
curl -s -X POST http://192.168.1.230:<port>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"<hard prompt>"}],"max_tokens":2500,"stream":false,"reasoning_effort":"<level>"}'
```
Use a genuinely hard prompt (e.g. a multi-bug Python function fix) — trivial prompts don't differentiate levels.

## Profile health check ("anything wrong with the setup?")
Deterministic recipe, ~30s, no gateway restart:
1. Read the provider block live: `grep -A12 '<provider-key>:' ~/.hermes/profiles/<p>/config.yaml` — get real `api:` URL + `models:` list. (Never assume the table above.)
2. `curl -s -m 10 <api>/v1/models` — confirms server up, model loaded, ctx size (`meta.n_ctx`).
3. Minimal completion probe: `curl -s -m 30 -X POST <api>/v1/chat/completions -d '{"model":"<model>","messages":[{"role":"user","content":"Reply OK"}],"max_tokens":10}'` — proves the full path end-to-end; `timings` in the response shows prompt tok/s.
4. `systemctl is-active hermes-gateway-<p>` + `journalctl -u hermes-gateway-<p> --since "1 hour ago" | grep -iE "error|fail"` — a single exit-code line at a config-restart timestamp is a benign reload, not an outage.

**Pitfalls:**
- `ps aux | grep llama` on the Hermes host will be empty — the llama.cpp server lives on the remote box (192.168.1.230), not locally. Don't report the model as down based on local process checks; only the HTTP probe is authoritative.
- Provider `models:` map can carry dead entries from prior model swaps (e.g. a full INT8 path nobody loaded anymore). Dormant — flag to the user for cleanup, don't silently delete.
- `auth.json` `active_provider` + `last_auth_error` (e.g. `refresh_token_reused`) can reference an unrelated dead provider. Harmless while the `model:` section pins a working custom provider; only matters if a fallback chain actually routes there.
- `hermes --profile <p> config check` may warn on the systemd unit's `TimeoutStopSec` vs drain timeout; compare against the actual unit file before calling it stale — the unit may already have been regenerated.

## When to use which level
- **xhigh/high**: gnarly multi-hypothesis debugging, refactors where one wrong turn poisons everything, auditing another agent's code.
- **medium** (default): normal agent work, content, CSS/SEO, triage, bookkeeping.
- **low**: image reads, quick lookups, mechanical extraction.
- **none**: pure formatting/transform tasks (7s vs ~70s on the probe).

## Pitfalls
- Change takes effect at **agent init (next session)** — no gateway restart needed.
- **Empty-response probe false alarm**: a completion probe with a tiny `max_tokens` (10–20) against a model that opens with newline/preamble tokens can return `content: None` / `finish_reason: length` — the budget was eaten by the preamble, the model is *not* dead. Re-probe with a realistic budget (50–300) on **both** `/v1/completions` and `/v1/chat/completions` before declaring the model broken. A gateway log showing `Empty response (no content or reasoning) — retry N/3` for a model that answers fine on a bigger direct probe is the same budget/preamble artifact, not an outage.
- **`/health` (and `/v1/models`) returning 200 is NOT proof of serving.** A llama.cpp/vLLM server can answer liveness + model-list requests while the worker queue is hung: verified 2026-08-20, `192.168.1.230:8002` returned 200 on `/health` while `/v1/completions` hung past a 20s curl timeout, and vLLM `:8000` returned 200 on `/v1/models` but took 11.25s for a 3-token completion. Gate "model is up" on a real completion probe WITH timing, then compare wall-clock against the consumer's actual timeout budget (e.g. the HDE tenant router's 45s per chat turn — full-context prompts on a 11s/3-token server blow it). A consumer timing out while `/health` is green is a queue/worker problem, not a down server — don't chase process/restart fixes first, measure completion latency.
- A **vLLM** server can host the same 27B weights as a different quant on a different port (e.g. `192.168.1.230:8000` serving `local-qwen-27b-q8-fred` INT8 + `local-qwen-27b-q4-fred` Q4 for Fred) alongside the llama.cpp instances above. The `reasoning_effort`/`extra_body` wiring still applies per provider block, but live-verify which engine (`vLLM` vs `llama.cpp`) and which model ID each profile's provider points at — the port/model table above is llama.cpp-only.
- No per-task mid-session override exists: for a one-off "go high" job, either instruct the model in the prompt or change config (takes effect next session).
- **Per-slot context overflow masquerades as "image timeouts" (2026-08-21, VM232 .232:8080):** server ran `-c 131072 -np 4` = **32,768 per slot**, but Kai's provider block claimed `context_length: 65536`. Hermes trusted its own config, so nothing compressed until ~55k; every >32k request died `HTTP 400 exceed_context_size_error (n_ctx 32768)` → 3 retries → aux compression (a 120s local-model call in itself) → "Context compression failed after 3 attempts" → "Auto-resetting session after compression exhaustion" → user sees a **3–6 min hang + a 65-char generic reply**, not a timeout. Image messages trigger it most: vision pre-analysis injects ~1–2k tokens into an already-long session. **Rule: `--parallel N` must satisfy `total_ctx/N >= provider context_length`, or align the two. Verify per-slot via `/slots` n_ctx (or `/v1/models` meta.n_ctx), never the launch flag.** Also note: vision pre-analysis itself is generation-bound (~65s for a 3.3k-char description at ~48 tok/s with MTP) — that's normal latency, not a fault.
- When installing this skill into another profile (e.g. Ned), write to `~/.hermes/profiles/<p>/skills/devops/qwen-llamacpp-reasoning-effort/SKILL.md` — requires explicit user direction (cross-profile write).
- Back up `config.yaml` before edits: `cp config.yaml /tmp/<p>-config-backup-$(date +%Y%m%d).yaml`.
