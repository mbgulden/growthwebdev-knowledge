# Codex OAuth token storage location

Discovered July 10, 2026 — Codex OAuth tokens do NOT live in:

- `~/.hermes/profiles/<profile>/credentials.json` (this file holds lane-scoped API keys like DEEPSEEK_API_KEY, LINEAR_API_KEY, etc.)
- `~/.hermes/credentials/` (may not exist)

They live in:

- `~/.hermes/profiles/<profile>/auth.json`

## auth.json structure

```json
{
  "version": 1,
  "providers": {
    "openai-codex": {
      "tokens": {},
      "last_refresh": "...",
      "auth_mode": "chatgpt",
      "last_auth_error": { ... }
    }
  },
  "credential_pool": {
    "openai-codex": [
      {
        "id": "64332f",
        "label": "dashboard device_code",
        "auth_type": "oauth",
        "access_token": "eyJhbG...",
        "refresh_token": "rt_-XF...",
        "last_error_code": null,
        "last_error_reason": null,
        "base_url": "https://chatgpt.com/backend-api/codex"
      }
    ]
  }
}
```

Key fields to check:
- `credential_pool.openai-codex[].access_token` — is it populated (`eyJ...`) or empty?
- `credential_pool.openai-codex[].last_error_code` — `refresh_token_reused` means the refresh token was consumed by another client (Codex CLI, VS Code). Requires re-auth.
- `providers.openai-codex.last_auth_error.relogin_required` — boolean flag.

## Quick introspection command

```bash
cat ~/.hermes/profiles/orchestrator/auth.json | python3 -c "
import json,sys
d=json.load(sys.stdin)
pool=d.get('credential_pool',{}).get('openai-codex',[])
for c in pool:
    tok = 'HAS_TOKEN' if c.get('access_token') else 'NO_TOKEN'
    err = c.get('last_error_code') or 'none'
    print(f\"  {c['label']:30s} access_token={tok} last_error={err}\")
"
```
