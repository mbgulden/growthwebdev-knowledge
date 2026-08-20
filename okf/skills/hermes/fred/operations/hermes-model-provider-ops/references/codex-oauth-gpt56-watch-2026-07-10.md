# Codex OAuth-only GPT-5.6 availability watch — 2026-07-10

## Context

Michael asked for a new GPT-5.6 availability cron that targets **only** the OpenAI OAuth/Codex provider — the same authenticated route currently running `gpt-5.5` — after a broader watch fired on OpenRouter Sol/Terra/Luna catalog hits.

Key distinction:

- `openai-codex` = ChatGPT/Codex OAuth-backed provider Michael uses for GPT-5.5.
- `openrouter` = separate catalog; Sol/Terra/Luna hits there are **not** evidence that Codex OAuth has GPT-5.6.
- `openai-api`, `copilot`, and others are also separate provider surfaces.

## Durable pattern

When Michael asks for an OAuth/Codex-specific watch:

1. Keep or pause any broad model watch separately; do **not** reuse OpenRouter hits.
2. Create a profile-local no-agent script under `~/.hermes/profiles/orchestrator/scripts/`.
3. Refresh the authenticated provider cache through Hermes internals.
4. Filter hits to `TARGET_PROVIDER = 'openai-codex'` before any target matching.
5. Stay silent when absent; write state under `~/.hermes/profiles/orchestrator/state/`.
6. Alert only when GPT-5.6 variants appear in the `openai-codex` model list.
7. In the alert, explicitly say OpenRouter/OpenAI API/Copilot are excluded so the user can trust the scope.

## Reference implementation shape

```python
TARGET_PROVIDER = 'openai-codex'
TARGETS = {
    'gpt-5.6',
    'gpt-5.6-codex',
    'codex-gpt-5.6',
    'codexgpt-5.6',
    'codexgpt-5-6',
}

def find_hits(provider_models):
    hits = []
    for model in provider_models.get(TARGET_PROVIDER, []) or []:
        normalized = normalize_model_id(model)
        matched = sorted(TARGETS & normalized)
        if matched or any('gpt-5.6' in bit for bit in normalized):
            hits.append({
                'provider': TARGET_PROVIDER,
                'model': model,
                'matched': ','.join(matched) if matched else 'gpt-5.6-codex-variation',
            })
    return hits
```

## Verification checklist

Use `/tmp/hermes-verify-*` via `tempfile.mkstemp`, then clean it up.

Required assertions:

- script exists and `py_compile` passes;
- `TARGET_PROVIDER == 'openai-codex'`;
- state file name is Codex-specific;
- normalization covers `GPT 5 6`, `codex GPT 5 6`, and `codexGPT-5-6`;
- OpenRouter/OpenAI API/Copilot GPT-5.6 fixtures produce **no** hits;
- `openai-codex` GPT-5.6/codexGPT-5.6 fixtures do produce hits;
- alert copy names OpenAI OAuth Codex and explicitly excludes OpenRouter/OpenAI API/Copilot;
- live state records `target_provider: openai-codex` and current GPT-5.5 Codex model list when absent.

## User-experience pitfall

If a user is interacting over Telegram, do not create tight manual auth/code races when the CLI has a short listener. Prefer durable refresh-token recovery/fallback patterns when possible, and only ask for an interactive code when no refresh token exists anywhere.
