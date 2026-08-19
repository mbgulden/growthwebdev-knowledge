---
type: Integration
title: Local llama.cpp Inference Server (George Profile)
description: Shared llama.cpp OpenAI-compatible server at 192.168.1.230:8002 serving the multimodal Qwen3.8-27B Q4_K_M GGUF to the George Hermes profile.
resource: okf/integrations/llama-cpp-george-local-server.md
tags: [llama-cpp, local-llm, qwen, inference, hermes, george, integration]
auth_method: static api_key in profile config (no OAuth)
token_storage: /home/ubuntu/.hermes/profiles/george/config.yaml (custom_providers.qwen27b-george-local.api_key)
timestamp: 2026-08-18T16:19:28Z
git_repo: mbgulden/growthwebdev-knowledge
git_path: okf/integrations/llama-cpp-george-local-server.md
last_verified: 2026-08-18
verified_by: george
status: current
---

# Local llama.cpp Inference Server (George Profile)

> **Verified 2026-08-18 by George** — health, model list, text completion, and a
> direct multimodal image-count test all passed against the live server.

## TL;DR

The George Hermes profile runs entirely against a **local llama.cpp
OpenAI-compatible server** at `192.168.1.230:8002`. The server serves one model:
the multimodal `Qwen3.8-27B` GGUF (Q4_K_M, 131k context). Text generation and
**real vision** both work natively on the local model — the gemini-2.5-flash
fallback chain is wired but was **not** being exercised during verification.
One stale config entry (a non-loaded INT8-MTP model ID) is documented below as a
known dead reference.

## Connection

| Field | Value |
|---|---|
| Provider name | `qwen27b-george-local` |
| Base URL | `http://192.168.1.230:8002/v1` |
| Host | `192.168.1.230` (separate LAN box — **not** this machine, `192.168.1.59`) |
| Port | `8002` |
| Auth | static API key (no OAuth / no refresh flow) |
| Config location | `/home/ubuntu/.hermes/profiles/george/config.yaml` → `custom_providers.qwen27b-george-local` |
| Request timeout | `180s` |

### Loaded model (server `/v1/models`)

| Property | Value |
|---|---|
| Model ID | `/models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf` |
| Family | Qwen3.8, 27.32B params, GGUF Q4_K (Medium) |
| On-disk size | ~17.1 GB |
| `n_ctx` | 131072 (train ctx 262144) |
| Capabilities | `completion`, `multimodal` (vision verified — see below) |
| Speculative decoding | MTP draft active (`draft_n`/`draft_n_accepted` present in timings) |

### Fallback chain (all auxiliary roles)

Every auxiliary role in the profile (compression, curator, kanban_decomposer,
mcp, monitor, profile_describer, title_generation, triage_specifier,
tts_audio_tags, vision, web_extract) is pinned to the local model with a single
fallback: `gemini-2.5-flash` via `https://generativelanguage.googleapis.com/v1beta/openai`.

## Verification (2026-08-18)

| Check | Command | Result |
|---|---|---|
| Health | `curl http://192.168.1.230:8002/health` | `{"status":"ok"}` |
| Model list | `curl .../v1/models` | returns the Q4 GGUF only |
| Text completion | `curl .../v1/chat/completions` (16 tokens) | 1.9s; ~61 tok/s prompt, ~51 tok/s decode |
| Vision (direct, bypasses fallback) | `curl .../v1/chat/completions` with `image_url` data-URL, "count red squares" | `CONTENT:'3'` correct; reasoning counts shapes visually |

Vision test card: 3 red squares + 5 green circles + text labels on navy. The
model's `reasoning_content` showed genuine visual processing
("I see a row of red squares on the left side. Let me count them: one, two,
three."), not text-reading — confirming the `multimodal` capability claim is
honest.

## Known failure modes & gotchas

1. **Dead model ID in config (stale, benign).**
   `custom_providers.qwen27b-george-local.models` also lists
   `/models/lued-Qwen3.8-27B-INT8-W8A16-MTP` (ctx 262144), but the server only
   loads/serves the Q4 GGUF. Anything selecting that ID gets a 404. The MTP
   speculative-decoding behavior is real (visible in response timings) but the
   *model name* in config does not match what's loaded. **Action:** remove or
   correct the INT8-MTP entry; no functional impact today since `default_model`
   is the Q4 GGUF.
2. **Port collision risk.** Local `:8002` on *this* host (192.168.1.59) is
   hd-platform's payment server (`work/hd-platform/payment/server.py`), **not**
   the llama.cpp box. Always address the inference server by the full
   `192.168.1.230:8002` — never bare `:8002`/localhost.
3. **Stale env var.** `HERMES_PROFILE=/home/ubuntu/.hermes/profiles/orchestrator`
   appears in the gateway env while everything else runs as `george`. Harmless
   noise from the launcher; service is `hermes-gateway-george.service`.

## Re-auth / recovery procedure

No OAuth — recovery is a config + connectivity check:

```bash
# 1. Is the box up?
curl -sS -m 8 http://192.168.1.230:8002/health
# expect: {"status":"ok"}

# 2. Is the model loaded?
curl -sS -m 8 http://192.168.1.230:8002/v1/models

# 3. Does it actually generate?
curl -sS -m 60 http://192.168.1.230:8002/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"/models/qwen3.8-27b-q4/Qwen3.8-27B-Q4_K_M.gguf",
       "messages":[{"role":"user","content":"Reply: OK"}],"max_tokens":8}'

# 4. If key was rotated: edit
#    /home/ubuntu/.hermes/profiles/george/config.yaml
#    -> custom_providers.qwen27b-george-local.api_key
#    then restart the profile gateway:
sudo systemctl restart hermes-gateway-george.service
```

If the server is down on the remote box, the profile transparently falls back to
`gemini-2.5-flash` for all auxiliary roles; the main chat provider will fail
until the box is reachable again.

## Cross-references

- [Agent profile inventory](./agent-profile-inventory.md) — the `qwenlocal` /
  `george` local-model profiles.
- [API keys & tokens registry](./api-key-locations.md) — where the static API key lives.
