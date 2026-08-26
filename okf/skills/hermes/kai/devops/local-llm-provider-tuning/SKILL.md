---
name: local-llm-provider-tuning
description: "Tune reasoning effort / thinking tokens and request-level knobs for local OpenAI-compatible LLM providers (llama.cpp, Ollama, LM Studio, vLLM) wired into Hermes Agent. Use when: a local model feels slow or over-thinks; user asks about 'reasoning levels/effort/thinking tokens'; you need a provider config change to actually reach the wire; or image reads (auxiliary.vision) are slow because of thinking tokens. Verified 2026-08-15 against a llama.cpp Qwen-27B server."
tags: [hermes, llama-cpp, ollama, reasoning, performance, provider-config]
category: devops
---

# Local LLM Provider Tuning (Hermes Agent)

Tune how much a local/remote OpenAI-compatible model thinks, and make sure the knob you set actually reaches the wire. Most of the pain in this class is *config paths that silently don't apply* — so this skill leads with the wire map, then the tuning procedure.

## When to use

- "Why is the local model so slow / verbose / dumb?"
- User asks about reasoning levels (low/medium/high/xhigh) on a local model.
- After switching a profile to a new local model — set sane defaults before the user complains.
- Auxiliary tasks (vision, web_extract, compression) are slow on a local model.

## The wire map (verified in Hermes 0.17.x source, 2026-08-15)

Where reasoning-effort config actually goes, by route:

| Route | What reaches the wire |
|---|---|
| OpenRouter / Nous / GitHub Models / LM Studio | `agent.reasoning_effort` (config `agent:` block or `/reasoning <level>`), translated by `_supports_reasoning_extra_body()` + `resolve_lmstudio_effort()` |
| **Custom provider (`custom:<name>` / `providers.<name>` with plain base_url, e.g. llama.cpp, Ollama)** | **ONLY the provider block's `extra_body` dict** — merged into `agent.request_overrides.extra_body` via `_merge_custom_provider_extra_body()` (agent/agent_init.py) → `api_kwargs["extra_body"]` → openai SDK flattens it into the request body top-level |
| Auxiliary tasks (vision, web_extract, compression, title_generation, …) | Each task's own `auxiliary.<task>.extra_body` (independent of main-agent settings) |

**Consequence:** for a plain llama.cpp/Ollama custom provider, `/reasoning high` and `agent.reasoning_effort` do NOTHING. Do not suggest them. The only lever is `providers.<name>.extra_body` (main agent) and `auxiliary.<task>.extra_body` (side tasks).

llama.cpp (Qwen3-style thinking GGUF) accepts top-level `reasoning_effort` with values `none | minimal | low | medium | high | xhigh` and returns thinking in `reasoning_content`.

## Procedure

1. **Identify the server and model.** `curl <base>/v1/models` (gives quant, n_ctx, multimodal) and `curl <base>/props` (llama.cpp: default_generation_settings, chat_format, reasoning_format).
2. **Probe the server live before touching config** — never assume parameter support:
   ```bash
   python3 <skill_dir>/scripts/probe_reasoning_effort.py <base_url> [model]
   ```
   Run it with no field first: that reveals the **server default** (on the 2026-08-15 Qwen-27B server the default was **xhigh** — the user thought they were at "high" but were at the max). Compare think-chars across levels with the identical hard prompt.
3. **Set the knobs in config.yaml** (use `hermes --profile X config set`, not hand edits):
   - Main agent: `providers.<name>.extra_body.reasoning_effort: medium` (or chosen level)
   - Slow aux tasks: `auxiliary.vision.extra_body.reasoning_effort: low` (same for web_extract/compression if slow)
   - `none` fully disables thinking (fastest, for aux tasks that never need it).
4. **Verify the merge path with a unit test** (config readback is NOT proof):
   ```python
   from hermes_cli.config import load_config, get_compatible_custom_providers
   from agent.agent_init import _custom_provider_extra_body_for_agent
   cps = get_compatible_custom_providers(load_config())
   eb = _custom_provider_extra_body_for_agent(provider="custom:<name>", model="<model>",
        base_url="<base>", custom_providers=cps)
   assert eb and eb["reasoning_effort"] == "medium"
   ```
   Plus `hermes --profile X config check`.
5. **Report** the before/after table (think-chars + wall time per level) and state when the change takes effect.

## Choosing a level

| Level | Think output (Qwen-27B, hard task, 2026-08-15) | Use for |
|---|---|---|
| none | 0 | Aux tasks (titles, approvals), trivial lookups |
| low (~3.6k chars, 43s) | Vision reads, web extract, fast side tasks |
| medium (~6k chars, 70s) | **Good default for main agent** — day-to-day agent work, content, CSS, SEO, bookkeeping |
| high / xhigh (~10.7k chars, ~68s; xhigh≈high on this server) | Hard debugging, multi-step refactors, auditing others' code — or keep as default if user prefers depth over speed |

Guidance for users: high when the obvious approach already failed or the work is multi-step with one-wrong-turn-ruins-everything risk; medium for everything else. Offer per-task bumping ("go high") instead of raising the default.

## Pitfalls

- **Server default ≠ "medium".** llama.cpp with a thinking GGUF defaults to xhigh when the field is absent. Always probe no-field first.
- **`agent.reasoning_effort` / `/reasoning` are dead ends for custom providers.** `_supports_reasoning_extra_body()` returns False unless the route is OpenRouter/Nous/GitHub/LM-Studio. Suggesting `/reasoning` wastes a user turn.
- **Changes take effect at agent init** — the next session (or after gateway restart), not the session in which you made them. Say so explicitly.
- **Auxiliary vision on a thinking model is the classic slow-image-read cause.** The image goes through the same local model and generates thinking tokens before the description. Fix with `auxiliary.vision.extra_body.reasoning_effort: low|none`.
- **Tiny `max_tokens` = empty content, not a broken server.** On thinking models (Qwen3.8-27B et al.) the reasoning tokens consume the entire output budget first — at `max_tokens` ≤ ~64 you get a 200 OK with `content: ""` and everything in `reasoning_content`. A smoke test that uses a small token budget will "fail" on a perfectly healthy endpoint. Always probe with a generous budget (≥ 256) and check `usage` + `reasoning_content` before concluding the server is dead (observed 2026-08-22: both local llama endpoints returned empty bodies at 24 tokens, worked at 300).
- **Unknown-key warnings are noise, not failures:** provider blocks warn about `max_tokens` (not in the known-keys set) while still working.
- **Don't hard-code one server's behavior** (e.g. "xhigh==high") as a rule — it's per-model. Re-probe when the model changes.
- **Server-side `--chat-template-kwargs` JSON escaping:** When adding `--chat-template-kwargs '{"key": true}'` to a shell script that launches `llama-server-new`, ensure the JSON string is precisely `'{"key": true}'` (single quotes around the JSON, and double quotes *within* the JSON are escaped). Incorrect escaping (e.g., `\'{\\"key\\\": true}\'` from Python's f-string or complex bash `awk` commands) will cause JSON parsing errors on the server. The safest way is to read the script, construct the exact literal line in Python (e.g., `chat_template_kwargs_flag = f"  --chat-template-kwargs \'{{\\"enable_thinking\\\": true}}\' \\\\"`), and write the whole modified script back.

## Reference

- `references/llama-cpp-reasoning-effort.md` — full 2026-08-15 evidence: /v1/models + /props findings, live test table, config diff, verification commands, source-file line references.
