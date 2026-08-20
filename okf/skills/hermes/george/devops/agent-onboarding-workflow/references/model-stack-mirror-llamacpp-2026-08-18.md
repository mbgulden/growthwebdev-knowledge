# Model-stack mirror: Ned + George → Kai (2026-08-18)

Task: "Can you get Ned and George's profiles to mirror yours?" — both helpers run local llama.cpp Qwen 3.8 27B Q4 on 192.168.1.230 (Ned :8003, George :8002); Kai runs his own instance on 192.168.1.232:8080.

## Findings (before)

| Item | Kai (reference) | Ned | George |
|---|---|---|---|
| model.default | real GGUF path | `local-qwen-27b-q4-ned` (fake alias — worked by luck) | `local-qwen-27b-q4-george` (fake alias) |
| provider | `qwen27b-kai-local` → .232:8080 | `qwen27b-ned-local` → .230:8003 | `qwen27b-george-local` → .230:8002 |
| aux slots | 14 slots, all real GGUF + inline... no, `api_key_env: GOOGLE_API_KEY` fb | 14 slots, fake alias, `custom:` provider prefix, `base_url` duplicated per slot | 16 slots incl. `background_review`/`moa_aggregator`/`moa_reference` → `gpt-5.5/openai-codex` (exhausted shared OAuth) |
| fallback_providers | google/gemini-2.5-flash via `api_key_env: GOOGLE_API_KEY` | same (env var **absent** from gateway process env — verified via /proc/PID/environ) | same |
| model_catalog | absent | absent | `enabled: true, providers: {}` (breaks resolution) |
| moa | absent | absent | dead preset → gpt-5.5/openai-codex + openrouter |
| context_length | 131072 (true for .232) | 262144 (false — server hard limit 32768) | 262144 (false — 32768) |

## Key techniques that mattered

1. **Fake alias discovery**: `/v1/chat/completions` with the alias name still succeeds (server substitutes the loaded model), so config looked fine. Check `config.yaml` model names against `/v1/models` output — the real name is the GGUF path.
2. **Hard context limit discovery**: no SSH to .230 (`Permission denied (publickey,password)`). The limit surfaced as a real 400 in George's old PID's journal during shutdown: `request (35103 tokens) exceeds the available context size (32768 tokens)`. Don't trust `context_length` in configs of llama.cpp endpoints; probe or observe.
3. **Hermes 64K minimum**: setting truthful `context_length: 32768` makes `hermes -z` refuse to start: "below the minimum 64,000 required by Hermes Agent. Choose a model with at least 64K context, or set model.context_length in config.yaml to override." Fix: keep provider truth (32768) + `model.context_length: 64000` override.
4. **Vision probe**: first 1×1-PNG test with `max_tokens: 20` returned empty content on all three servers — thinking budget consumed the output. Retry with `max_tokens: 400` → all answered "Red". Small max_tokens + reasoning model = false negative.
5. **GOOGLE_API_KEY absence**: `env | grep -c GOOGLE_API_KEY` = 1 in my shell, but `/proc/<gateway-pid>/environ` = 0 for kai/ned/george gateways, and no unit-file Environment= entry. So `api_key_env: GOOGLE_API_KEY` fallbacks are unreliable in gateway context → inline the literal key (already plaintext in each config's `google` provider block).
6. **Edit method**: no comments in target config files (verified with grep), so YAML round-trip via `yaml.safe_dump(sort_keys=True)` was safe. Backups: `config.yaml.bak-mirror-<ts>`.
7. **Restart**: `os.kill(MainPID, SIGTERM)` from Python; `Restart=always` + `KillMode=mixed` replaced both services. Never touched the running kai gateway.

## Result

- Both profiles: real GGUF path as default + all 14 aux slots, own per-agent provider endpoint, inline google fallback, kai-parity timeouts, `compression` mirrored, `model_catalog`/`moa` removed from George, Ned's duplicate `gemini` provider removed.
- Smoke: `NED_OK3` / `GEORGE_OK3` via `hermes --profile <p> -z`.
- New PIDs: ned 2961382, george 2961383, both `active/running`.
- Outstanding caveat: .230 servers run 32k ctx (Kai's .232 runs 131k). Fix requires restarting those llama.cpp servers with `-c 131072` — needs .230 access (no SSH key).
