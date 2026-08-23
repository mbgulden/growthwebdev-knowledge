---
name: qwen-llamacpp-reasoning-effort
description: "Set/verify/adjust thinking levels (none/low/medium/high/xhigh) on Hermes profiles backed by custom llama.cpp servers (Kai :31002, Ned :31003 on 192.168.1.230). Use when a user says 'go high/medium/low', complains about slow local-model responses, or asks to tune reasoning on these profiles."
category: devops
tags: [hermes, llama-cpp, qwen, reasoning, config]
related_skills: [hermes-agent, llm-serving-benchmark]
---

# Qwen 27B / llama.cpp Reasoning Effort

Applies to Hermes profiles whose main model is a custom OpenAI-compatible llama.cpp server. Known instances (2026-08-21, supersedes 2026-08-15 table — kai moved off the .230 NodePorts):

| Profile | Provider key | URL | Served model id |
|---|---|---|---|
| kai | `qwen27b-kai-local` | http://192.168.1.232:8080/v1 | `qwen3.8-27b` (NOT local-qwen-27b-q4-kai) |
| ned | `qwen27b-ned-local` | http://192.168.1.230:8003/v1 | verify |

Both run Qwen 3.8 27B Q4_K_M GGUF with MTP spec decoding (~50–70 tok/s single-stream).

**Context topology (measured 2026-08-21, .232:8080):** flags are `-c 131072 -np 2` = ONE 3090 (24GB, ~23.9GB used), total KV pool 131k split across 2 parallel slots of **65,536 tokens each**. Per-request cap is 65k — prompts >65k get HTTP 400 (no auto-shrink). Hermes reads this correctly via /props n_ctx=65536 and compresses at 85% (~55.7k). Needle-in-haystack recall holds through ~62k but degraded at 63.8k — treat ~55–60k as the reliable working window. "131k context" is the POOL, not per-request. Server-side `reasoning_effort` levels verified live: `xhigh/high ≈ 10.7–11k think-chars`, `medium ≈ 6k–12k`, `low ≈ 3.6–6.7k` (low and medium barely differ on hard prompts), `none = 0` (thinking fully off). **No effort in the request = server default.**

**CRITICAL — max_tokens interaction (verified 2026-08-21):** thinking tokens COUNT against `completion_tokens`/`max_tokens`. With `model.max_tokens: 4096` (the old default) and thinking on, a medium task burned the whole budget (finish_reason=`length`, answer truncated mid-sentence, or ZERO answer chars if thinking alone exceeded the cap). Kai's profile is now `model.max_tokens: 8192` — at that cap, medium completes with `finish_reason=stop`. If a profile answers get cut off mid-thought: check `finish_reason` + `reasoning_content` length first, then raise `model.max_tokens`.

**Quality trade-off measured (2026-08-21, hard multi-bug Python prompt):** medium found the real bug AND caught an incorrect expectation in the prompt itself (58.6s); `none` misdiagnosed, hallucinated test output matching the wrong expectation, and contradicted its own code (3.7s). `none` is NOT "fast but slightly dumber" — on hard tasks it is fast and wrong. Keep main=medium; use `none` only for pure formatting/transform/mechanical work.

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

## When to use which level
- **xhigh/high**: gnarly multi-hypothesis debugging, refactors where one wrong turn poisons everything, auditing another agent's code.
- **medium** (default): normal agent work, content, CSS/SEO, triage, bookkeeping.
- **low**: image reads, quick lookups, mechanical extraction.
- **none**: pure formatting/transform tasks (7s vs ~70s on the probe).

## Pitfalls
- **Pending vLLM switch (in flight as of 2026-08-16):** Fred is replacing llama.cpp with vLLM on k3s-node-230. After the switch, RE-VERIFY this dial — vLLM's effort knob is different (chat-template `thinking` toggle / `chat_template_kwargs`, not top-level `reasoning_effort`). The provider `extra_body` path still applies, but the key may need to change. Benchmark before/after via the `llm-serving-benchmark` skill.
- Change takes effect at **agent init (next session)** — no gateway restart needed.
- No per-task mid-session override exists: for a one-off "go high" job, either instruct the model in the prompt or change config (takes effect next session).
- When installing this skill into another profile (e.g. Ned), write to `~/.hermes/profiles/<p>/skills/devops/qwen-llamacpp-reasoning-effort/SKILL.md` — requires explicit user direction (cross-profile write).
- Back up `config.yaml` before edits: `cp config.yaml /tmp/<p>-config-backup-$(date +%Y%m%d).yaml`.
