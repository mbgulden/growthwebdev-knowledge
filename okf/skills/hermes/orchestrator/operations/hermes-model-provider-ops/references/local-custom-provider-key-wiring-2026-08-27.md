# Local custom provider key wiring — `key_env` for an auth-gated local server (2026-08-27)

Session: 2026-08-27. Symptom: Kai's bot kept emitting `⚠️ Model fallback: qwen3.8-27b via custom unavailable (authentication failed); using gemini-2.5-flash via google`. Root cause: the local OpenAI-compatible server **enforces an API key** but Kai's provider block had no key wired in.

## Topology

```
orchestrator (this session, runs INSIDE a gateway)
  └─ Hermes profile: kai ────► http://192.168.1.232:8080/v1   (qwen3.8-27b, llama.cpp, key-gated)
  └─ (compare)  fred  ─────► http://192.168.1.230:8000/v1     (works: sends api_key inline)
```

The `1.232:8080` server was started with an `--api-key`; the key already lives in Kai's profile `.env` as `KAI_LLM_API_KEY` (a `kai-…` bearer, 58 chars). Fred's config worked because it sends `api_key: llama-local` inline; Kai's slots had `api_key: ''`.

## Diagnosis (do this before editing anything)

1. **Server is healthy but auth-gated** — the two calls disagree:
   ```bash
   curl -s http://192.168.1.232:8080/v1/models            # 200 + {"data":[{"id":"qwen3.8-27b",...}]}
   curl -s -X POST http://192.168.1.232:8080/v1/chat/completions \
     -H 'Content-Type: application/json' \
     -d '{"model":"qwen3.8-27b","messages":[{"role":"user","content":"ping"}],"max_tokens":5}'
   # 401 {"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}
   ```
   200 on `/v1/models` + 401 on `/v1/chat/completions` = **config auth gap, not a dead server**.

2. **Find the key** — grep the profile `.env` for a plausible var:
   ```bash
   grep -oE '^[A-Z0-9_]+_API_KEY' /home/ubuntu/.hermes/profiles/kai/.env   # → KAI_LLM_API_KEY
   ```

3. **Test the key LIVE before touching config** (redact the value — never print it):
   ```bash
   KEY=$(grep -oP '^KAI_LLM_API_KEY=\K.*' /home/ubuntu/.hermes/profiles/kai/.env)
   curl -s -o /dev/null -w '%{http_code}\n' -X POST http://192.168.1.232:8080/v1/chat/completions \
     -H 'Content-Type: application/json' -H "Authorization: Bearer $KEY" \
     -d '{"model":"qwen3.8-27b","messages":[{"role":"user","content":"say pong"}],"max_tokens":5}'
   # 200 = correct key + Bearer. (Raw `key: $KEY` header → 401; Bearer is what llama.cpp wants.)
   ```

4. **Confirm the var is in the GATEWAY process env** (the var being in `.env` isn't enough unless systemd loads it in):
   ```bash
   pid=$(systemctl show -p MainPID --value hermes-gateway-kai)
   tr '\0' '\n' < /proc/$pid/environ | grep -q '^KAI_LLM_API_KEY=' && echo "in process env" || echo "NOT in process env"
   ```
   The unit has `EnvironmentFile=/home/ubuntu/.hermes/profiles/kai/.env`, so it is loaded. (Note: `GOOGLE_API_KEY` was NOT in the process env in this session — the gemini fallback must have resolved its key from another path; don't assume the fallback env is present.)

## The fix (one line)

Add `key_env` to the provider entry in `~/.hermes/profiles/kai/config.yaml`:

```yaml
providers:
  qwen27b-kai-local:
    name: qwen27b-kai-local
    api: http://192.168.1.232:8080/v1
    base_url: http://192.168.1.232:8080/v1
    key_env: KAI_LLM_API_KEY        # ← resolves to the bearer from the gateway env
```

- `key_env` (also accepted as `api_key_env`) is read by `hermes_cli/providers.py` `resolve_custom_provider` (`entry.get("key_env")`) → becomes `api_key_env_vars` → hermes pulls the value from the process env at request time and sends it as `Authorization: Bearer <value>`.
- Prefer `key_env` over an inline `api_key: <literal>` when the secret already lives in an env var — no plaintext key in config, rotates in one place, and the profile `.env` is the canonical secret store.
- Back up first: `cp config.yaml config.yaml.bak-$(date +%Y%m%d-%H%M%S)`.

## Apply + verify (the in-gateway constraint)

- This session ran INSIDE a gateway (orchestrator), so **the gateway-restart step is guarded** and must be handed to the user. The in-gateway terminal guard also **false-positives on probe-script text**: a Python diagnostic that imports `hermes_cli.providers` to resolve the provider (no restart intent) can still be blocked because the guard regexes scan the whole command/file string. Keep lifecycle literals out of any probe; the on-disk config readback + the live `curl` key test are sufficient pre-restart evidence.
- Hand the user a one-shot script (run from outside the gateway) that: restarts the unit, waits ≤90s for `active`, verifies exactly one `gateway run` process (PPID 1) whose `/proc/<pid>/environ` has `KAI_LLM_API_KEY`, then instructs a real Telegram test message. Expected result: the `⚠️ Model fallback … gemini` warning is gone and responses come from `qwen3.8-27b`.

## Why the fallback mask is the trap

The `fallback_chain` to `gemini-2.5-flash` (via `GOOGLE_API_KEY`) is a *recovery* path, not the route. When the primary custom provider 401s, Hermes **silently rolls over** and the user still gets a plausible answer — so "the bot answers" is NOT evidence the local model is being used. The only reliable signal is the absence of the `⚠️ Model fallback … authentication failed` line in the bot's reply / the profile `agent.log`.

## Cross-references

- `hermes-model-provider-ops` — parent skill; "Local custom providers" section + the `401 Invalid API Key` pitfall (this reference is the worked example).
- `hermes-gateway-lifecycle-ops` — the in-gateway guard behavior and the pre-stage-and-handoff pattern for the restart.
- `local-custom-provider-wiring-2026-08.md` — the unauthenticated local-provider wiring (inline `api_key: local`); this reference is the auth-gated variant.
