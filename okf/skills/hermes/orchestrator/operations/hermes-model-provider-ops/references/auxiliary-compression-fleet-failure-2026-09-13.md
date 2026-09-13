# Auxiliary compression fleet failure — worked case 2026-09-13

Class: "compression broken on all profiles" + "Ned's compression number is too low."
Root cause: a FLEET of dead/mis-sized auxiliary compression models, not one bug. The Prismatic Engine was exonerated (no PE code touches Hermes session context/compression — verified by grep across `prismatic/`).

## The three failure classes (all observed in one report)

| Profile | Log signature | Root class | Fix |
|---|---|---|---|
| orchestrator, fred | `Failed to generate context summary: Error code: 429 - You exceeded your current quota` | (a) paid aux quota dead | route aux → local vLLM |
| george | `Failed to generate context summary: Error code: 401 - Invalid API Key` | (b) aux key rotated/stale | route aux → local vLLM (key via key_env) |
| ned, next-step | `Auxiliary compression model <m> has N token context, below the main model's compression threshold of M tokens — auto-lowered session threshold to N` | (c) aux context_length too small | raise aux context_length to real served ctx |
| kai | `Context length exceeded: 151,891 tokens. Cannot compress further.` + `Auto-resetting session … after compression exhaustion` | consequence of (c) + 65k window | raise window + fix aux |

All four profiles share the terminal symptom `Context compression made no progress for 0.0s (total wait 600.0s, ceiling 600.0s); continuing without compression` — that line is the GIVE-UP, not the cause. Grep for the *cause* signatures above, not this one.

## Config layout that matters

Each profile's `config.yaml` has, in order:
- `model:` block — `provider`, `default`, `context_window`, `compression_threshold`, `compression_headroom` (the MAIN model's compression intent).
- `auxiliary.compression:` block — `provider`, `model`, `base_url`, `api_key`/`api_key_env`/`key_env`, `context_length`, `fallback_chain`, `timeout`. INDEPENDENT of `model.`.
- `providers:` block — the `custom:NAME` endpoint definitions (`api`, `base_url`, `key_env`, `models`).
- top-level `compression:` block — `threshold_tokens`, `context_window`, `headroom_tokens`, `target_ratio`, `protect_first_n`, `protect_last_n`. This is the session-compressor's operating envelope.

The bug pattern: `auxiliary.compression.context_length` (the aux's window) < main intent, so the feasibility check auto-lowers the whole session threshold to the aux's window. AND a top-level `compression:` block can carry a stale small `context_window`/`threshold_tokens` (e.g. `65536`/`49152`) that doesn't match the 256k/1M the user "set" on the main model. Read ALL three blocks before concluding what the effective threshold is.

## Effective-threshold derivation (from the installed fork)

`agent/context_compressor.py`:
- `threshold_tokens = max(int(context_length * threshold_percent), <floor>)`
- `context_length = get_model_context_length(..., config_context_length=...)`
- `target_tokens = int(threshold_tokens * summary_target_ratio)`
- `check_compression_model_feasibility(agent)` (in `conversation_compression.py`): if `aux_context < threshold` → sets `agent.context_compressor.threshold_tokens = aux_context` and re-derives `threshold_percent = new_threshold / main_ctx`. So the aux is the binding constraint when it's the smallest window in the chain.

## The fix that landed (verified config edits, then user-run gateway restart)

Ned (`/home/ubuntu/.hermes/profiles/ned/config.yaml`) → Fred's vLLM endpoint:
```yaml
auxiliary:
  compression:
    api_key: vllm-fred-...            # or key_env: VLLM_FRED_API_KEY (preferred when the var exists)
    base_url: http://192.168.1.230:8000/v1
    context_length: 262144            # was 131072 (the "too low" number)
    model: local-qwen-27b-q8-fred
    provider: custom:qwen27b-fred-local
    fallback_chain:                    # keep the paid escape hatch
    - base_url: https://generativelanguage.googleapis.com/v1beta/openai
      model: gemini-2.5-flash
      provider: google
      api_key: AQ...
```
George → Kai's llama.cpp endpoint (already pointed there; only the ctx was stale):
```yaml
auxiliary:
  compression:
    provider: qwen27b-kai-local       # http://192.168.1.232:8080/v1, model qwen3.8-27b
    model: qwen3.8-27b
    context_length: 131072            # was 65536 — the real "too low" culprit for George
```
Fred + orchestrator: already `custom:qwen27b-fred-local` for compression — the 429 was a STALE-log/fallback artifact, no change needed. (Lesson: a 429 in the log does not mean the current aux is paid; read the live `auxiliary.compression` block before "fixing" it.)

## Verification (post-edit, pre-restart + post-restart)

1. `curl -s http://192.168.1.230:8000/v1/models` → 401 without key (auth-gated, expected) / lists model with key. `curl -s http://192.168.1.232:8080/v1/models` → 200 `['qwen3.8-27b']` (unauthenticated).
2. `python3 -c "import yaml; a=yaml.safe_load(open('<cfg>'))['auxiliary']['compression']; print(a['provider'], a['model'], a['context_length'])"` readback on each edited profile.
3. Confirm the key env var is present in the profile `.env` (`grep VLLM_FRED_API_KEY <profile>/.env`) and that the gateway process env carries it (systemd `EnvironmentFile=` loads the profile `.env`).
4. **User runs** `hermes --profile ned gateway restart` + `hermes --profile george gateway restart` (in-gateway guard blocks Fred from doing it himself). Post-restart: a real Telegram message through each bot should compress without the `made no progress` / `auto-lowered` warnings.

## What was NOT the cause (so it isn't re-investigated)

- Prismatic Engine → Hermes connection: no PE code touches session context/compression; the failures are inside Hermes' own `conversation_compression.py` + the aux model. PE was exonerated by grep, not assumed.
- Gateway respawn storm (`Another gateway instance is already running`, `restarted N times in 120s — backing off`): a double-spawn watchdog issue on the orchestrator, adds noise/CPU but does not cause compression failures. Separate fix: single-instance `pgrep` guard in the spawner.
