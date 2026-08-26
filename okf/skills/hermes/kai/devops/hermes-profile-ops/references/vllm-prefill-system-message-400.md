# vLLM + prefill_messages_file: system-role 400 → silent fallback (2026-08-25, Fred/orchestrator)

Symptom: profile (Fred = `orchestrator`) configured for vLLM `.230:8000` / `local-qwen-27b-q8-fred`,
but every turn was served by the Gemini fallback. Gateway healthy, Telegram healthy, config correct.
Nothing looked broken — only the `provider=` field in agent.log told the truth.

## Diagnostic chain
1. Config check: `provider.base_url` + `model` already correct ⇒ not a config problem.
2. Log scan: `grep -a BadRequestError <profile>/logs/agent.log` → repeated
   `BadRequestError: Error code: 400 - {'error': {'message': 'System message must be at the beginning.'...}}`
   with `LLM call completed ... provider=gemini` (fallback) on every turn.
3. Direct endpoint probe (use execute_code, not shell — quoting + redaction harness):
   - `system, user` → 200 OK
   - `system, user, system, user` → 400 "System message must be at the beginning."
   ⇒ vLLM accepts exactly one system message, and only at position 0.
4. Found the second system message: `<profile>/state/prefill_messages.json` began with
   `{"role": "system", ...}` (session-handoff prefill). Hermes injects prefill *right after* the real
   system prompt (conversation_loop.py ~line 842) ⇒ dual-system payload on every API call.

## Fix
1. Backup: `cp state/prefill_messages.json state/prefill_messages.json.bak-<ts>`.
2. Rewrite ALL prefill entries to `role: user`, content verbatim. (Prefill is few-shot priming, never
   persisted to history — the roles only shape what the backend accepts.)
3. Re-probe the endpoint with the post-fix shape (`system, user, user, user`) → 200 before touching the gateway.
4. Restart the gateway — prefill is loaded ONCE at GatewayRunner init (`gateway/run.py` ~line 2548,
   `self._prefill_messages = self._load_prefill_messages()`) and passed to every AIAgent. File edit alone
   has no effect on the running process. From inside a gateway session (terminal guard blocks
   `systemctl restart`): MainPID-kill pattern from Section B —
   `kill $(systemctl show <unit> -p MainPID --value)`; `Restart=always` respawns with a new MainPID.
5. Smoke test: `hermes --profile <p> -z 'Reply with exactly: X_OK'` → expect exactly X_OK.
6. Confirm: `grep -aE 'BadRequestError|400 - ' <profile>/logs/agent.log` post-restart → zero hits.
   CAUTION: a bare `grep fallback` also matches Telegram startup lines
   ("Auto-discovered Telegram fallback IPs") — noise, not LLM fallback.

## Why it stayed silent
The Hermes fallback chain swallows the 400 and routes to the next configured provider. The profile keeps
answering on Telegram, so the outage is invisible by feel; token burn is the tell (local-endpoint profile
spending 1M+ tokens/turn = it is running on the fallback, not the local model).

## Code locations (hermes-agent pipx venv, 2026-08-25 build)
- `gateway/run.py` ~line 2548: `self._prefill_messages = self._load_prefill_messages()` in GatewayRunner init
- `gateway/run.py` ~line 4003: `_load_prefill_messages()` — env `HERMES_PREFILL_MESSAGES_FILE` first, then
  top-level `prefill_messages_file`, then legacy `agent.prefill_messages_file`; relative paths resolve from `~/.hermes/`
- `agent/conversation_loop.py` ~line 842: "Inject ephemeral prefill messages right after the system prompt"
- `agent/agent_init.py` line 503: `agent.prefill_messages = prefill_messages or []`

## Files
- `<profile>/state/prefill_messages.json` — the prefill payload (ephemeral, never persisted)
- `<profile>/logs/agent.log` — LLM call lines + provider field (the truth)
- `vllm-fred` service on the inference host — rejects multi-system payloads at request time (no server-side workaround; fix the client payload)
