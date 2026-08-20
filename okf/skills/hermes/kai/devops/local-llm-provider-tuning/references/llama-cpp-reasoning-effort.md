# Reference: llama.cpp Qwen-27B reasoning-effort tuning (2026-08-15)

Session evidence for `local-llm-provider-tuning`. Kai profile, model `local-qwen-27b-q4-kai` (Qwen 3.8 27B Q4_K_M, GGUF, llama.cpp server at 192.168.1.230:31002, GPU 2 on PVE1-VM230).

## Server facts (from live probes)

- `GET /v1/models` → single model `local-qwen-27b-q4-kai`, capabilities `["completion","multimodal"]`, n_ctx 262144, n_params ~27.3B, quant Q4_K, size ~17GB.
- `GET /props` → default_generation_settings: temperature 1.0, top_k 20, top_p 0.95, min_p 0.05, chat_format "Content-only", reasoning_format "none" (prop name is misleading — the model still thinks; it emits `reasoning_content` in the API response).
- Responses include `reasoning_content` (thinking text) separately from `content`. `usage.completion_tokens` includes thinking tokens.
- **Server default effort = xhigh** (no-field request produced ~10.9k thinking chars on a hard task). The user had been running at xhigh without knowing it.

## Live test table (identical hard prompt: Python dedupe-dicts bug analysis, max_tokens 2500)

| Request body field | Wall time | Think chars |
|---|---|---|
| (none) | 69s | 10,921 |
| `reasoning_effort: low` (top-level) | 43s | 3,612 |
| `reasoning_effort: high` | 68s | 10,812 |
| `reasoning_effort: medium` | 70s | 6,017 |
| `reasoning_effort: xhigh` | 68s | 10,668 |
| `reasoning_effort: none` | 7s | 0 (no thinking; answer still correct) |
| `reasoning: {effort: low}` (OpenRouter-style) | 3.7s* | 206 (*easy prompt, different task) |

Notes: on this server `high ≈ xhigh` (both cap ~10.7k). The OpenRouter-style nested `reasoning` object was NOT verified to work — only the top-level `reasoning_effort` string is proven.

## Hermes source trace (pipx venv, Hermes 0.17.x, 2026-08-15)

- `hermes_constants.py:551` — `VALID_REASONING_EFFORTS = ("minimal","low","medium","high","xhigh")`; `parse_reasoning_effort()` also accepts `"none"` → `{"enabled": False}`.
- `gateway/run.py:4049 _load_reasoning_config()` — reads `agent.reasoning_effort` from config.yaml, default medium.
- `run_agent.py:4867 _supports_reasoning_extra_body()` — **returns False for a custom provider** (only True for nousresearch.com, GitHub models/copilot, lmstudio provider, and OpenRouter allowlisted model families). So the `agent.reasoning_effort`/`/reasoning` path never reaches a plain llama.cpp route.
- `agent/agent_init.py:102 _custom_provider_extra_body_for_agent()` + `:147 _merge_custom_provider_extra_body()` — matches `custom:<name>` provider + base_url against `get_compatible_custom_providers(config)` (which merges both `providers:` dict entries and legacy `custom_providers:` list via `providers_dict_to_custom_providers()`), then merges the entry's `extra_body` into `agent.request_overrides["extra_body"]`.
- `agent/transports/chat_completions.py:450` — `api_kwargs.update(overrides)` after extra_body assembly → the provider `extra_body` lands in the request body top-level (openai SDK flattens `extra_body`).
- Auxiliary path: each `auxiliary.<task>.extra_body` is forwarded verbatim (documented in `hermes_cli/config.py` ~1405).
- `hermes_cli/config.py:4228` — provider known-keys include `extra_body` (so `config set providers.<name>.extra_body.reasoning_effort <lvl>` is supported). `max_tokens` in a provider block is an unknown key (warning only, harmless).

## Config change applied (Kai profile)

```yaml
providers:
  qwen27b-kai-local:
    # ... existing ...
    extra_body:
      reasoning_effort: medium     # main agent
auxiliary:
  vision:
    extra_body:
      reasoning_effort: low        # image reads
```

Commands used:
```bash
hermes --profile kai config set "providers.qwen27b-kai-local.extra_body.reasoning_effort" medium
hermes --profile kai config set "auxiliary.vision.extra_body.reasoning_effort" low
```

## Verification performed (config readback is NOT proof — do all of these)

1. `hermes --profile kai config check` — clean.
2. Raw YAML grep — both `extra_body` blocks present at expected nesting.
3. Unit test of the exact merge path (must PASS before claiming done):
```python
import sys
sys.path.insert(0, "/home/ubuntu/.local/share/pipx/venvs/hermes-agent/lib/python3.12/site-packages")
from hermes_cli.config import load_config, get_compatible_custom_providers
from agent.agent_init import _custom_provider_extra_body_for_agent
cps = get_compatible_custom_providers(load_config())
eb = _custom_provider_extra_body_for_agent(
    provider="custom:qwen27b-kai-local", model="local-qwen-27b-q4-kai",
    base_url="http://192.168.1.230:31002/v1", custom_providers=cps)
assert eb and eb.get("reasoning_effort") == "medium"
# → merged extra_body for main agent: {'reasoning_effort': 'medium'}
```
4. Live server probes (table above) proving the wire values work.

## Change propagation

- Takes effect at **agent init** (next session / gateway restart). Mid-conversation config edits do not hot-apply to the running session's agent.
- A config backup was taken to /tmp before the change (standard practice).
