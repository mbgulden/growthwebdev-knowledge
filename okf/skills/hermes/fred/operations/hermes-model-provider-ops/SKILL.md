---
name: hermes-model-provider-ops
description: Check and manage Hermes Agent model/provider availability, especially OAuth-backed providers such as openai-codex/ChatGPT OAuth, OpenAI API, OpenRouter, Copilot, and provider model caches.
category: operations
---

# Hermes Model Provider Ops

Use this skill when Michael asks whether a model is available, whether an OAuth-backed provider has a new model, or whether Hermes should switch/default to a newer model.

## Principles

- Verify availability from Hermes' live provider/model discovery or refreshed cache, not from memory.
- Public release/news claims are secondary; the actionable answer is whether the model appears for the authenticated Hermes provider/account.
- Do not print API keys, OAuth tokens, Authorization headers, or credential file contents. Redact secrets as `[REDACTED]`.
- For ChatGPT OAuth / Codex access, distinguish:
  - `openai-codex` = ChatGPT/Codex OAuth-backed provider.
  - `openai-api` = OpenAI API key provider.
  - `openrouter`/`copilot` = separate catalogs and access gates.

## Model availability check

1. Load this skill first for Hermes model/provider work.
2. Check auth status without exposing secrets:

```bash
hermes auth status openai-codex
hermes auth list | sed -E 's/(token|secret|key|password)[^[:space:]]*/[REDACTED]/Ig'
```

3. Refresh provider models. `hermes model --refresh` is interactive and may fail from non-TTY sessions, so use Hermes' Python environment when needed:

```bash
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python - <<'PY'
import pathlib, yaml
from hermes_cli.model_switch import list_authenticated_providers
from hermes_cli.models import clear_provider_models_cache

cfg_path = pathlib.Path('/home/ubuntu/.hermes/profiles/orchestrator/config.yaml')
cfg = yaml.safe_load(cfg_path.read_text())
model_cfg = cfg.get('model', {})
clear_provider_models_cache()
rows = list_authenticated_providers(
    current_provider=model_cfg.get('provider', ''),
    current_base_url=model_cfg.get('base_url', ''),
    current_model=model_cfg.get('default') or model_cfg.get('model', ''),
    refresh=True,
)
for row in rows:
    slug = row.get('slug')
    if slug in ('openai-codex', 'openai-api', 'openrouter', 'copilot'):
        print('\nROW', slug, row.get('name'), 'current=' + str(row.get('is_current')), 'total=' + str(row.get('total_models')))
        for model in row.get('models') or []:
            if 'gpt' in str(model).lower():
                print(' ', model)
PY
```

4. Read the refreshed cache for timestamped proof:

```bash
python3 - <<'PY'
import datetime, json, pathlib
p = pathlib.Path('/home/ubuntu/.hermes/profiles/orchestrator/provider_models_cache.json')
data = json.loads(p.read_text())
for provider in ['openai-codex', 'openai-api', 'openrouter', 'copilot']:
    entry = data.get(provider, {})
    models = entry.get('models', [])
    at = datetime.datetime.fromtimestamp(entry.get('at', 0), datetime.timezone.utc).isoformat()
    print(provider, 'cache_at_utc=' + at, 'has_target=' + str(any('5.6' in m for m in models)))
    print(', '.join([m for m in models if 'gpt' in m.lower()]))
PY
```

5. Cross-check public docs/news with web search when the user asks about a release. Treat public search snippets as context, not as evidence that Michael's authenticated provider has access.

## Scheduled availability watches

Use this pattern when Michael expects a model to land soon and wants Hermes to notify him the moment it appears in authenticated provider catalogs.

1. Create a no-agent Hermes cron under the active profile's `scripts/` directory; profile-local scripts avoid scheduler path restrictions.
2. Refresh/read Hermes provider model cache on each tick and check exact target IDs plus normalized variants:
   - provider prefixes: `openai/gpt-5.6-sol` → `gpt-5.6-sol`
   - separators/case: `GPT 5.6 Sol`, `gpt_5_6_sol`, `gpt-5-6-sol`
3. If the user asks for a **provider-specific** watch, filter by provider *before* target matching. Example: a Codex OAuth watch must only inspect `openai-codex`; OpenRouter/OpenAI API/Copilot GPT-5.6 hits must be ignored and the alert copy should explicitly say they are excluded.
4. Stay silent when absent. For no-agent cron jobs, empty stdout means no user-facing message.
5. Emit a concise alert only when a target appears. If Michael asked for escalation/celebration, store small state under the profile `state/` directory and increase intensity per hit.
6. Verify with an ad hoc `/tmp/hermes-verify-*.py` script that covers compile, normalization, absent silence, provider isolation, present detection, message assertions, live smoke run, cron enabled/schedule, and cleanup.

## Frontier model landing → Prismatic integration

When a watch fires and Michael says the model should become part of Prismatic Engine, switch from “discovery” mode to “governed integration” mode:

1. Pause/remove the availability-watch escalation once Michael replies after the hit.
2. State the evidence precisely as provider/catalog availability, not production readiness.
3. Treat OpenRouter catalog hits as requiring low-token smoke tests before any autonomous routing; free-tier/credit behavior may differ from catalog visibility.
4. Add an OKF operations note with found model slugs, discovery cron id, paused watch state, staged rollout, fallback mapping, and an explicit “do not change global defaults yet” guardrail.
5. Create a capability lane/feature flag (for example `frontier-orchestrator`) rather than flipping Hermes or Prismatic global defaults.
6. Benchmark exactly one safe slice before routing production or revenue-critical work.

See `references/frontier-model-prismatic-integration.md` for the post-hit pattern and verification shape.

## Recovery verification (post-rate-limit / post-auth-reset)

Use this workflow when Michael reports a provider was rate-limited (429) or OAuth-dropped, and asks you to verify recovery after the reset window. The pattern: **confirm tokens → test chat → verify no silent fallback → check logs**.

1. Check if credentials have actual tokens, not just device_code stubs:

```bash
hermes auth list | grep -A5 "openai-codex"
```

The primary credential (marked `←`) should show a label like `dashboard device_code oauth` or similar. Secondary/exhausted credentials showing "device_code exhausted (Xm left)" are normal — they are the retry-cooldown stubs, not the active token. If the primary credential has the `←` marker and `hermes auth status openai-codex` says "logged in", the token is present.

If you need deeper inspection, check the auth store directly (redacted):

```bash
# Check for access_token presence without dumping values:
python3 -c "
import json, pathlib
for p in [pathlib.Path.home() / '.hermes' / 'profiles' / 'orchestrator' / 'auth.json',
          pathlib.Path.home() / '.hermes' / 'auth.json',
          pathlib.Path.home() / '.config' / 'hermes' / 'auth.json']:
    if p.exists():
        d = json.loads(p.read_text())
        pool = d.get('credential_pool', d)
        codex = pool.get('openai-codex', []) if isinstance(pool, dict) else []
        for c in codex if isinstance(codex, list) else [codex]:
            label = c.get('label','?')
            tok = 'YES' if c.get('access_token') else 'NO'
            err = c.get('last_error_code') or c.get('error') or 'none'
            # Real failure signals live on the PROVIDER entry, not the credential:
            # providers.openai-codex.last_auth_error.{code,relogin_required,message}
            prov = d.get('providers', {}).get('openai-codex', {})
            lae = prov.get('last_auth_error') or {}
            relogin = lae.get('relogin_required', prov.get('relogin_required', '?'))
            auth_err = lae.get('code') or 'none'
            print(f'{label:30s} access_token={tok} cred_err={err} relogin_required={relogin} auth_err={auth_err}')
```

**Read the provider-level `last_auth_error` block, not just credential `last_error_code`.** Real case 2026-08-22: credential `last_error_code` was `None` (looked clean) while `providers.openai-codex.last_auth_error.code = 'refresh_token_reused'` and `relogin_required = True` — the token was actually dead. A populated `access_token` + `relogin_required=True` means the token is present but the backend rejects it.
```

2. Run a minimal smoke test — the simplest possible query, not a conversation:

```bash
hermes chat -q "respond with the word PONG" --provider openai-codex --model gpt-5.5
```

Expect: returns "PONG" within seconds. If it hangs/errors, provider is still degraded.

**CRITICAL: a "PONG" response does NOT prove the target provider served it.** When a fallback chain is configured, a failed codex call silently falls back to the backup provider and the user still sees "PONG". Real case 2026-08-22: `--provider openai-codex --model gpt-5.5` returned PONG in 14s, but `agent.log` showed `HTTP 401: Could not parse your authentication token` followed by `Fallback activated: gpt-5.5 → gemini-2.5-flash (google)`. **Always pair the smoke test with a log check that the session actually used the intended provider** — grep `agent.log` for the session id and for `Fallback activated` / `error_type=AuthenticationError`. Answer + fallback line = provider still down, and cron jobs calling that model are silently running on the fallback. See `references/codex-oauth-401-silent-fallback-2026-08.md`.

**Important: a stale availability watch file does NOT prove the token is dead.** The OAuth availability watch (`state/gpt56_codex_oauth_availability_watch.json`) and the actual token credential store are independent subsystems. The watch may still report `"last_result": "absent"` even after the token refreshes correctly, because the watch runs on its own clock. A successful live inference test overrides a stale "absent" watch result.

3. Check gateway/error logs for the retry-success pattern (401 → retry → success):

```bash
# Check errors.log for the retry-success handshake:
tail -20 /home/ubuntu/.hermes/profiles/orchestrator/logs/errors.log 2>/dev/null | grep -E "openai-codex|AuthenticationError|codex"
# If you see a 401 "token expired" followed by a successful run, that's normal recovery
# — Hermes retries auth automatically after a token refresh.

# Check agent.log for codex success confirmation on retry:
tail -20 /home/ubuntu/.hermes/profiles/orchestrator/logs/agent.log 2>/dev/null | grep -E "openai-codex|PONG"
```

The characteristic recovery pattern in errors.log:
```
AuthenticationError ... HTTP 401: Provided authentication token is expired.  ← first attempt
(no further errors)                                                          ← retry got fresh token
```

**401 messages are NOT all equal — distinguish "expired" from "unparseable":**
- `HTTP 401: Provided authentication token is expired.` → normal expiry; Hermes refreshes and retries successfully. RECOVERED.
- `HTTP 401: Could not parse your authentication token. Please try signing in again.` → backend rejects the token itself; the refresh loop fails with `refresh_token_reused` and `relogin_required=True`. NOT recovered — requires manual browser re-auth (`hermes auth reset openai-codex`). A populated `access_token` in the pool does not clear this; the token is present but invalid at the backend, and every request silently falls back.

4. Check cron/watchdog logs for residual fallback signals. Focus on the most recent log files, not stale ones:

```bash
# Check actively rotating logs (most recent entries):
for f in /home/ubuntu/.hermes/profiles/orchestrator/logs/*.log; do
  [ "$(stat -c%Y "$f" 2>/dev/null)" -ge "$(date -d '7 days ago' +%s 2>/dev/null)" ] && \
    tail -5 "$f" 2>/dev/null | grep -E "Codex auth|fallback|codex" && echo "   ^ in $(basename $f)"
done
# Avoid stale files — a gateway-restart.log from June has no bearing on today's recovery.
```

5. Report findings in ≤5 lines. If the test passed, say so clearly. If tokens are still empty, do NOT attempt browser-based re-auth (requires user interaction) — just report the gap.

## Profile model change + gateway load verification

When changing a live Hermes bot/profile model, verify the runtime gateway actually loaded the supported model; config readback alone is insufficient. If a requested Codex/ChatGPT model is not in the authenticated `openai-codex` catalog or gateway logs reject it, switch to the highest supported model in the same provider family, restart the target gateway, inspect `gateway_state.json`/systemd/journal logs, run a live smoke on the final route, clean one-shot helper scripts, and label verification as ad hoc targeted. See `references/profile-model-gateway-restart-verification.md`.

## Reporting format

Return a compact table:

| Provider | Target present? | Available GPT-ish models |
|---|---:|---|

Then state the active current route, e.g.:

```text
provider: openai-codex
model: gpt-5.5
```

- If the model is absent from the picker/catalog, say “not available in our authenticated provider list yet,” not “not released.”
- For GPT-5.6 on the OAuth-backed Codex route, verify the exact slugs directly, not only the picker/catalog. `gpt-5.6-sol`, `gpt-5.6-terra`, and `gpt-5.6-luna` may work via explicit `-m`/Hermes smoke even when `list_authenticated_providers()` omits them. Prefer `gpt-5.6-sol` for a live bot default; avoid assuming bare `gpt-5.6` is the safest persisted default unless gateway logs confirm it.
- Do not confuse the Hermes `openai-codex` *provider* (a Hermes-side model catalog used by `hermes --provider openai-codex -m …`) with the **standalone Codex CLI** at `/usr/bin/codex`. They have separate auth (`hermes auth status openai-codex` vs `codex login`), separate state (`auth.json` pool vs `~/.codex/`), and separate session stores. PE lanes dispatch to the **CLI**, not the provider, and not a Hermes `codex-*` profile. See `references/codex-cli-lane-integration-2026-07.md` for the canonical invocation, model slugs, failure-mode map, and the 2026-07-26 decision to wipe retired `codex-*` / `agy` Hermes profiles from history.

## Direct MiniMax vs OpenRouter MiniMax

When Michael says to use **our MiniMax API** or **direct MiniMax**, do not route MiniMax through OpenRouter even if OpenRouter exposes `minimax/...` IDs and the smoke test passes. Use Hermes' first-class MiniMax provider instead:

```yaml
model:
  provider: minimax
  default: MiniMax-M3
```

For guest/deconditioning bot containers, also verify the runtime exports `MINIMAX_API_KEY` and does not export `OPENROUTER_API_KEY` for that route. Direct MiniMax uses Hermes' Anthropic-compatible provider path, so guest images may need `anthropic>=0.39.0` installed. See `references/hde-guest-minimax-direct-provider.md` for the HDE guest-container wiring and ad-hoc verification pattern.

## Local custom providers (llama-server / vLLM / Ollama — OpenAI-compatible)

When Michael says "use the local GPU model" or "hook up the local llama-server to [profile]", the pattern is **`provider: custom:NAME`** plus a `providers:` block in `~/.hermes/profiles/<profile>/config.yaml`. Hermes treats `custom:NAME` as a reference to a named provider; the `providers:` block defines where it points. This works for any OpenAI-compatible endpoint — llama-server, vLLM, Ollama with `--api` mode, LM Studio, etc.

### Minimal config for a local llama-server

```yaml
model:
  default: local-qwen-27b-q4-kai
  provider: custom:qwen27b-kai-local
providers:
  qwen27b-kai-local:
    name: Qwen 27B Q4_K_M on VM 230 (GPU 2)
    api: http://192.168.1.230:31002/v1
    api_key: local                 # llama-server doesn't require a key, but the field is required
    default_model: local-qwen-27b-q4-kai
    models:
      local-qwen-27b-q4-kai:
        context_length: 32768
    context_length: 32768
    request_timeout_seconds: 600
fallback_providers:
- provider: openai-codex          # keep the previous model as fallback
  model: gpt-5.6-terra
```

### Wiring rules

- The provider `api` URL must end in `/v1` (Hermes appends `/chat/completions` itself).
- `api_key` is required by the schema; pass any non-empty string when the upstream is unauthenticated. `local` is a conventional choice.
- The `default_model` field must match a key under `models:`. The `models:` block is what Hermes uses to populate the picker.
- `context_length` should match the upstream's actual context window (don't exceed the server's `--ctx-size`).
- **Hermes Agent hard floor: `context_length` must be ≥ 64,000 tokens.** A session start on a provider with `context_length: 32768` raises `ValueError: Model has a context window of N, which is below the minimum 64,000 required by Hermes Agent` before any request is made. If the local llama-server can do 65k, set `context_length: 65536` on both the provider and the model entry; if the upstream caps below 64k, the local endpoint cannot be used for a real Hermes Agent session until the upstream ctx is bumped. This is independent of the runtime `--ctx-size` flag on the server — both must be ≥ 64,000. See `proxmox-k3s-gpu-cluster-ops/references/llama-server-runtime-gotchas.md` for the full diagnostic and the `--ctx-size` × `--parallel` per-slot interaction that bites when you try to push context past 32k.
- `default_model` value in `providers:` must equal `model.default` if you want a single model route; if you list multiple models you can switch with `hermes chat -m <key>`.
- Keep the previous remote provider in `fallback_providers:` so the gateway rolls over when the local endpoint is unreachable.

### Per-profile isolation

Each profile is independent — to route Kai and Ned to different GPUs/endpoints, edit each profile's `config.yaml` separately. The Telegram bot / gateway inside each profile uses the local `model.default` for that profile, so the chat experience changes per profile without code changes.

### Auxiliary vision is NOT routed by `model.default`

Hermes has separate config blocks for each auxiliary task:

- `model.default` / `model.provider` — chat routing
- `auxiliary.vision.provider` / `model` / `base_url` — Telegram image attachments, screenshots
- `auxiliary.web_extract.provider` — URL/document text extraction
- `auxiliary.compression.provider` — context compression
- `auxiliary.session_search.provider`, `auxiliary.title_generation.provider`, etc.

Each is independent. Wiring `model.default` to a local multimodal server does NOT route Telegram image attachments to it — you must patch `auxiliary.vision` separately. The agent then reports "vision API failed" the moment cloud auth drifts (rate limits, OAuth expiry, prompt drift). This is the single most common silent failure when migrating a Hermes profile from a cloud model to a local multimodal endpoint. See `references/local-custom-provider-wiring-2026-08.md` section 3 for the full `auxiliary.vision` block shape.

Verification: read back both blocks after every patch and confirm they point at the same custom provider:

```bash
python3 -c "
import yaml
cfg = yaml.safe_load(open('/home/ubuntu/.hermes/profiles/kai/config.yaml'))
print('main:', cfg['model']['provider'], cfg['model']['default'])
print('vision:', cfg['auxiliary']['vision']['provider'], cfg['auxiliary']['vision']['model'])
"
# Both rows should reference the same custom provider.
```

### Verification (mandatory before declaring "hooked up")

1. Live endpoint reachable from the orchestrator host: `curl -s http://<host>:<port>/v1/models | jq '.data[].id'` — must list the alias.
2. Live chat from the orchestrator: `curl -s -X POST http://<host>:<port>/v1/chat/completions -H 'Content-Type: application/json' -d '{"model":"<alias>","messages":[{"role":"user","content":"Respond with only OK"}],"max_tokens":10,"temperature":0}' | jq -r '.choices[0].message.content'`.
3. Per-profile config readback: `python3 -c "import yaml; print(yaml.safe_load(open('/home/ubuntu/.hermes/profiles/<profile>/config.yaml'))['model'])"`
4. **Then** restart the gateway for that profile (the gateway caches the model at startup; a config change is not picked up until restart). After restart, send a real message through the Telegram bot and verify the response went via the local endpoint (response time should match the local LLM speed, not the upstream API).
5. Write a `/tmp/hermes-verify-local-provider.py` script that runs steps 1–4 and exit-codes.
6. **Confirm `context_length` ≥ 64,000 tokens at both provider and model level.** Hermes Agent's hard floor rejects lower values with a `ValueError` at session start. Run a real chat through the Telegram bot to confirm the gateway loads the model — config readback alone doesn't prove the gateway passed the 64k check.

### Common pitfalls

- **404 on `model.default`**: the value doesn't match any key under `providers.<NAME>.models`. Run `curl /v1/models` and use the exact `id` it returns.
- **Mistaking gateway timeout for provider error**: the local server doesn't choke on OAuth, but `request_timeout_seconds` defaults too low; bump to 600+ for long-running chat.
- **Container hostname vs LAN IP**: if the gateway runs in a container, "localhost" points at the container; use the LAN IP of the GPU host.
- **CDI / device-plugin not loaded**: the endpoint processes requests but every response is gibberish or empty when the GPU isn't actually visible to the container. Verify with `nvidia-smi` from inside the serving pod.
- **Build-host vs target-host CPU mismatch**: a llama.cpp binary built on a host with AVX-512 crashes with `Illegal instruction` on a KVM VM running default `kvm64` CPU. Fix the VM (`qm set <vmid> --cpu host`) before blaming the model. See `proxmox-k3s-gpu-cluster-ops` for the diagnostic.
- **Auxiliary vision NOT routed by `model.default`**: see "Auxiliary vision" subsection above. Wiring the main model to local does not route Telegram image attachments to local; `auxiliary.vision.provider/base_url/model` must be patched separately, otherwise images keep flowing to GPT/OpenRouter and the agent reports "vision API failed" the moment cloud auth drifts.
- **Slot monopolization from missing `provider.max_tokens`**: even when the local llama-server has `--n-predict 4096` set, a Hermes request without `max_tokens` may still cause unbounded generation if `provider.max_tokens` is unset. Always set both server-side and Hermes-side caps. See `proxmox-k3s-gpu-cluster-ops/references/llama-server-runtime-gotchas.md` Gotchas 11-12 for the layered cap pattern.
- **Versioning `/tmp/hermes-verify-*.py` filenames**: when a verifier script gets cleaned up before the next verification needs it, the system asks for fresh evidence and you waste time rewriting it from scratch. Version the suffix (`-v2`, `-v3`) so successive runs leave an audit trail instead of a churn loop. If the check will be re-run, write it once and reference its results, then write a follow-up version when the schema changes — never delete the only copy of a known-good verifier.
- **"It's text-only" assumption**: a model labeled `Qwen3-27B` may be the language-only weights of a multimodal model (Qwen3-27B comes in `-27B`, `-VL-30B-A3B`, etc.). Verify by reading the Hugging Face `pipeline_tag` and `library_name` before declaring a model text-only. Qwen3.8-27B from `unsloth/Qwen3.8-27B-GGUF` reports `pipeline_tag: image-text-to-text` and ships an `mmproj-F16.gguf` to enable vision — a single file download plus `--mmproj` CLI flag added vision capability to an existing text-only deployment.

See `references/local-custom-provider-wiring-2026-08.md` for the full Kai/Ned-on-VM-230 worked example including the YAML diff and the chat-completion verification.

## Reverse lookup: which profile uses a model / VM / endpoint

When Michael asks "what profile is using the model from VM 232" (or generally "who points at this endpoint"), resolve server-side first, then sweep configs client-side.

1. **Verify what is actually serving, from the server side — do not trust the alias.** The Hermes-side model name (session banner, `model.default`) does not guarantee the quant or even the host actually loaded. Real case 2026-08-21: banner read `local-qwen-27b-q8-fred` while VM 232 was actually serving `Qwen3.8-27B-Q4_K_M` under a lookalike alias — the Q8 lived on a different VM (230). Truth is the process's `-m /models/...` argument or `/v1/models`:
   ```bash
   qm guest exec <vmid> -- bash -c 'ps aux | grep -Ei "vllm|llama|sglang|tgi|ollama" | grep -v grep'
   # or from the orchestrator:
   curl -s http://<vm-ip>:<port>/v1/models | jq '.data[].id'
   ```
2. **Sweep every profile config by the endpoint IP, not by model name.** Aliases collide across machines (same family, different quant, different box). Grep the raw IP:
   ```bash
   grep -rln "192.168.1.232" /home/ubuntu/.hermes/config.yaml /home/ubuntu/.hermes/profiles/*/config.yaml
   ```
   **Use absolute paths.** From the orchestrator profile, `~/.hermes/profiles/` resolves to a shadow tree (`/home/ubuntu/.hermes/profiles/orchestrator/home/.hermes/`) that holds only a partial profile set — a `~`-relative sweep silently misses the real fleet and returns nothing.
3. **Read the `model:` block AND the `providers:` block of every hit** (`model.provider: custom:NAME` is the live route; `providers.NAME.api` is the endpoint). **Also check `auxiliary.*` blocks** — vision, compression, curator, mcp, kanban_decomposer etc. can each independently route to the local provider, so a profile can hit in many places and the "who uses it" answer includes the fallback chain.
4. Report as a table: profile → provider name → endpoint → model on disk. Explicitly flag any alias-vs-actual-quant mismatch found in step 1.

## Pitfalls

- Do not claim availability from a release article alone.
- When Michael says “our MiniMax API,” route through Hermes' direct `minimax` provider and model IDs such as `MiniMax-M3`; do not substitute OpenRouter slugs like `minimax/minimax-m3` unless he explicitly asks for OpenRouter.
- For containerized guest bots using direct MiniMax, verify `MINIMAX_API_KEY` is present inside the container, `OPENROUTER_API_KEY` is not required for that route, and the image has the Anthropic SDK if Hermes' MiniMax provider uses the Anthropic-compatible path.
- Do not run broad credential dumps; inspect only redacted status/model lists.
- `hermes model --refresh` requires an interactive terminal; use the Python model-switch path in headless sessions.
- Copilot may show unrelated token warnings from `GITHUB_TOKEN`; report the model list separately and avoid treating that as a global Hermes failure.
- Do not create a narrow one-release skill for every frontier model landing. Capture model-family landing lessons in this umbrella skill and put session-specific details under `references/`.
- For local custom providers, the same "re-run the verifier script" rule as everywhere else applies: a config edit plus a successful /v1/models curl is not "hooked up" until the profile's gateway restart + Telegram-path smoke also passes.
- **Auxiliary vision routing is independent of `model.default`.** Patching `model.provider` to local does not route image attachments to local. Always patch `auxiliary.vision` separately and verify with the readback in `references/local-custom-provider-wiring-2026-08.md`.
- **A modal-capable model and a routed vision workflow are two different things.** The local server can advertise `multimodal` capability while Hermes still routes image requests to GPT. The fix is in `~/.hermes/profiles/<profile>/config.yaml`, not in the server.
- **Don't delete the only known-good verifier.** When the system asks for fresh verification, rewrite from the last working copy with a `-v2` suffix — don't clean it up the first time. Versioned verifier scripts are audit trail.
- **Don't accept "the agent says the API is broken" without verification.** Three things share the same symptom (slot monopolization, cloud provider auth drift, actual model fault). The verification recipe in `proxmox-k3s-gpu-cluster-ops/references/llama-server-runtime-gotchas.md` walks through layer-by-layer diagnosis.

## Support Files

- `references/gpt56-availability-watch-2026-07-09.md` — worked pattern for a silent no-agent cron that watches authenticated provider catalogs for imminent model variants and escalates only when found.
- `references/codex-oauth-gpt56-watch-2026-07-10.md` — provider-isolated watch pattern for GPT-5.6 in `openai-codex` only, including fixture checks that OpenRouter/OpenAI API/Copilot GPT-5.6 hits are ignored.
- `references/codex-cli-lane-integration-2026-07.md` — Codex CLI as a standalone lane target: disambiguation from Hermes `openai-codex` provider and retired `codex-*` profiles, canonical `codex exec` invocation, model slugs, failure-mode map, concurrency model, and the 2026-07-26 decision to wipe retired Hermes profiles.
- `references/codex-gpt56-explicit-slugs-and-gateway-load.md` — live-profile pattern for GPT-5.6 Codex slugs (`gpt-5.6-sol`/`terra`/`luna`), picker/catalog mismatch, gateway restart proof, and post-switch slowness diagnosis.
- `references/frontier-model-prismatic-integration.md` — pattern for turning a fired availability watch into a governed Prismatic capability lane: pause discovery escalation, record OKF evidence, smoke OpenRouter/free-tier behavior, and feature-flag rollout without changing global defaults.
- `references/codex-auth-json-structure.md` — Codex OAuth token storage layout in `auth.json` (not `credentials.json`) and quick-introspection command for checking token presence and error codes.
- `references/codex-oauth-401-silent-fallback-2026-08.md` — worked example: OAuth reset populated an access_token but the backend still 401'd ("Could not parse your authentication token"); the smoke test returned PONG via silent fallback to gemini. Full evidence chain for "logged in + token present + PONG ≠ recovered", including the provider-level `last_auth_error` / `relogin_required` signal and the 401 message taxonomy.
- `references/direct-minimax-guest-bot-2026-07.md` — direct MiniMax API wiring for containerized Hermes guest bots: `provider: minimax`, `MiniMax-M3`, `MINIMAX_API_KEY`, Anthropic SDK dependency, and explicit/routed smoke tests.
