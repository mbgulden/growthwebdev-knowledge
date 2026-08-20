# Codex OAuth model discovery — GPT-5.6 availability check

Session signal: Michael asked whether GPT-5.6 was available on the current OpenAI Codex OAuth route. The reliable answer came from live Hermes/Codex model discovery, not from general web results.

## Durable recipe

Use Hermes' installed helper modules so credential-pool resolution and token refresh match the runtime path:

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

## Example proof from this session

```text
codex_oauth_credentials=OK
credential_source=credential_pool
model_count=5
gpt_5_6_models=(none)
all_models=gpt-5.5, gpt-5.4-mini, gpt-5.4, gpt-5.3-codex, gpt-5.3-codex-spark
```

## Reporting language

Good:

> GPT-5.6 is not currently available on this OpenAI Codex OAuth credential. Live discovery returned no `gpt-5.6-*` models. This does not prove GPT-5.6 is unavailable globally or on other accounts.

Avoid:

> GPT-5.6 does not exist.
> GPT-5.6 is available because search results say it launched.
> The OAuth is broken.

## Safety notes

- Do not read/paste raw `auth.json` or token values.
- `hermes auth list` is safe for high-level credential status, but still inspect output before finalizing.
- Web/docs can explain rollout context, but the current credential's model list is the authority for "can George use it now?".
