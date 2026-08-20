---
name: hermes-provider-diagnostics
description: "Diagnose Hermes Agent provider/model/auth availability using live configuration, credential pools, model discovery endpoints, and compact proof packets."
triggers:
  - what model are you using
  - is model available
  - OAuth model availability
  - Hermes provider check
  - openai-codex model list
  - switch Hermes model
  - Hermes auth diagnostics
---

# Hermes Provider Diagnostics

Use this when Michael asks about the active Hermes model/provider, whether a model is available through an OAuth/API provider, or why Hermes is using a particular model.

## Operating rule

Do not answer provider/model/auth availability from memory. Verify live state first. Model availability changes by account, credential, provider, rollout cohort, and Hermes profile.

## Standard sequence

1. **Load Hermes context if available**
   - Try to load the `hermes-agent` skill when the task is about Hermes itself.
   - If the skill is unavailable or protected/not installed, continue with live CLI/docs checks instead of guessing.

2. **Check active config**

```bash
hermes config
```

Extract only non-secret fields:

- active profile/config path;
- `model.provider`;
- `model.default` / `model.model`;
- auxiliary model overrides if relevant.

3. **Check credential presence without leaking secrets**

```bash
hermes auth list
```

Report provider names, credential counts, auth type, and obvious status such as rate-limited/ready. Never paste access tokens, refresh tokens, API keys, or full auth JSON.

4. **Use provider-specific live model discovery**

For OpenAI Codex OAuth (`openai-codex`), prefer Hermes' own runtime helpers so credential-pool and refresh behavior match production use:

```bash
python - <<'PY'
from hermes_cli.auth import resolve_codex_runtime_credentials
from hermes_cli.codex_models import get_codex_model_ids
creds = resolve_codex_runtime_credentials(refresh_if_expiring=True)
models = get_codex_model_ids(creds.get('api_key'))
wanted = [m for m in models if '5.6' in m or 'gpt-5.6' in m]
print('codex_oauth_credentials=OK')
print('credential_source=' + str(creds.get('source')))
print('model_count=' + str(len(models)))
print('gpt_5_6_models=' + (', '.join(wanted) if wanted else '(none)'))
print('all_models=' + ', '.join(models))
PY
```

This queries the same Codex OAuth model discovery path Hermes uses and respects credential pools. If it returns no requested slug, say that the model is not currently offered to *this credential/account/profile*, not that the model does not exist globally.

5. **Use current docs/web only for global availability context**

When the user asks whether a model exists generally or is rolling out, consult current docs/search. Keep the distinction clear:

- **Live local/account availability** = model discovery from current credential.
- **Global/product availability** = docs/release notes/search results.

6. **Report compactly**

Use this shape:

```text
STATUS=<PASS|PARTIAL|BLOCKED>
EVIDENCE=<command + result summary>
BOUNDARY=<what is not claimed>
NEXT=<exact next action if user wants a switch/re-auth/test>
```

For a simple answer, lead with the practical result and then include a proof block.

## Codex OAuth split-brain diagnosis

When asked to repair an `openai-codex` split-brain auth bug, diagnose before clearing auth. Hermes may already contain the repair and the live global store may already be converged. See `references/codex-split-brain-auth-convergence.md` for the secret-safe fingerprint comparison, exact two-model probe recipe, and gateway-ownership boundary.

Required sequence:

1. Verify the requested JSON parser without assuming package names. If the user says `ja` but no durable evidence identifies that CLI, check whether `jq` is present and run a real `jq -e` parse test before installing anything.
2. Inspect only structural auth fields from global `/home/.../.hermes/auth.json`: provider token key presence, credential-pool count, short hashes/fingerprints, match indexes, and error-marker counts. Never print token contents.
3. Confirm installed Hermes behavior if relevant: fresh Codex auth should mirror applicable singleton tokens into `credential_pool.openai-codex`, runtime should resolve across singleton/pool stores, and independent accounts must not be overwritten.
4. Run exact provider/model probes for at least two Codex model slugs. If both pass and singleton/pool fingerprints match, do **not** clear auth or re-authenticate.
5. If the gateway is unhealthy, classify it separately from OAuth. A `Gateway already running (PID ...)` loop or a PID under another profile's cgroup is a service-ownership blocker, not evidence of Codex split-brain. Do not kill/restart the active gateway without explicit scoped authorization.

## Stuck-session route repair

A profile can show the correct `model.provider` and `model.default` while an existing Telegram session remains pinned to an older model in `<profile>/state.db`. In multi-profile incidents, treat the problem as profile config + active session state + live gateway process + direct provider inference, not as a YAML-only setting. See `references/multi-profile-gateway-route-parity.md` for the reusable parity-audit and repair checklist.

## Multi-profile primary/fallback policy changes

When Michael asks to set a primary model plus fallback across several Hermes profiles, do not treat this as a YAML-only edit. Use `references/multi-profile-model-policy-rollout.md` for the reusable sequence: inspect actual profile roots/aliases, secret-safe config readback, pre-change provider probes, atomic YAML normalization, detached/safe gateway reload, fallback-list verification, cgroup ownership proof, and capacity-boundary reporting. If post-reload default route reaches the configured fallback but the fallback provider returns quota/rate-limit, report `CONFIG/RELOAD=PASS` and `CAPACITY=DEGRADED` instead of undoing the policy or silently adding extra fallback providers.

Diagnose this before blaming YAML or silently changing providers:

1. Read only safe session route fields from the profile SQLite database: `id`, `source`, `model`, `ended_at`, and non-secret model/provider keys from `model_config`.
2. Confirm the target profile's actual service/PID ownership with `systemctl cat`, `systemctl show`, and `/proc/<pid>/cgroup`; legacy units may use a nonstandard name.
3. When Hermes blocks `systemctl stop/restart` from inside another gateway, signal only the target service `MainPID` as documented. Wait for that old PID to exit, then update the target profile before systemd's restart delay. Never signal the current agent's gateway.
4. Atomically normalize `model.provider` and `model.default`; remove malformed literal-string fallback settings rather than preserving them.
5. With the target process closed, back up `state.db` temporarily and update only active sessions pinned to the retired route. Preserve messages and all other session metadata. Remove the temporary backup after verification.
6. Verify replacement PIDs, active service state, current active-session models, and provider config. Separate old-PID shutdown logs from new-PID runtime logs.
7. Run a real one-turn provider/model inference probe for each profile. Config and model discovery alone are not sufficient proof. Confirm the expected exact response and hash the per-profile logs without exposing credentials.
8. Verify messaging bot identity through a secret-safe API call that prints only `ok`, username, and ID presence.

## Local llama.cpp / GGUF provider checks

When the provider is a local or LAN llama.cpp endpoint (a `custom_providers` entry with an `http://<ip>:<port>/v1` api), run the liveness → model-discovery → text-smoke → multimodal-proof sequence in `references/llama-cpp-local-provider-check.md`. Key boundaries: the configured port on the Hermes host is often an unrelated local service — resolve the real listener via `hostname -I` + `ss -tlnp` + `/proc/<pid>/cmdline` before blaming the model; cross-check every `custom_providers.<name>.models` ID against `/v1/models` (unserved IDs are stale config, not outages); and a multimodal claim is only real if a direct image curl to the server shows prompt-token growth and visual reasoning — a Hermes-routed `vision_analyze` success could be the fallback answering.

## Pitfalls

- In Hermes config version 30, `hermes config set <key> '[]'` and `'null'` may persist literal strings rather than an empty list/null. After changing fallback/provider structures, perform a secret-safe YAML type/readback check and run `hermes config check`. For structural list/map deletion, use an atomic YAML mutation with a temporary file, preserve unrelated values, remove any temporary backup containing retired key material after validation, and verify zero provider routes by path/name only.
- Never use broad content search on provider config when matches could print inline API keys. Parse YAML and print only provider/model names, reference paths, counts, endpoint-presence booleans, and schema status.
- Do not infer the active model from a prior assistant answer; inspect `hermes config` or the system prompt when available.
- Do not treat web search snippets as proof that the current OAuth credential has access.
- Do not print secrets from `auth.json`, `.env`, or provider token stores.
- Do not hardcode model slugs into persistent config unless Michael explicitly asks to switch and the live provider check confirms access.
- If a model is missing from current live discovery, phrase it as account/provider-scoped: "not available on this credential now."
- Do NOT infer "text-only GGUF ⇒ vision is broken" from the model name or file format. A Q4 GGUF can be genuinely multimodal. Verify a vision claim with a direct image curl to the server (prompt-token growth + visual `reasoning_content`), not from the filename. A Hermes-routed `vision_analyze` success is not proof the local model answered — the gemini fallback can answer identically.
- Reasoning-capable small models can consume the entire `max_tokens` budget in `reasoning_content`, leaving `content` empty with `finish_reason: "length"`. Give 3–6x token headroom or read `reasoning_content` before concluding the model "isn't answering."

## References

- `references/codex-oauth-model-discovery.md` — session-derived recipe for checking GPT-5.6 availability on `openai-codex` OAuth without exposing tokens.
- `references/codex-split-brain-auth-convergence.md` — secret-safe diagnosis for singleton-vs-credential-pool Codex auth divergence, exact two-model probes, and duplicate-gateway ownership boundaries.
- `references/multi-profile-gateway-route-parity.md` — reusable checklist for auditing and repairing cross-profile model/session/service drift without exposing secrets.
- `references/multi-profile-model-policy-rollout.md` — session-derived pattern for changing primary/fallback model policy across Kai/Fred/Ned-style running profiles with alias detection, safe reloads, and capacity-boundary proof.
- `references/llama-cpp-local-provider-check.md` — session-derived recipe for verifying a local/LAN llama.cpp GGUF provider: real-listener resolution, model-ID staleness cross-check, text smoke test, and direct-curl proof of a multimodal (vision) claim.
