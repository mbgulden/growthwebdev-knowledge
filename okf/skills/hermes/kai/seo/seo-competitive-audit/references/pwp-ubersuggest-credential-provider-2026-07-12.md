# PWP Ubersuggest credential provider — 2026-07-12

## Why this exists

Ubersuggest MCP access tokens currently expire quickly (~172800s / ~2 days on current refreshes). The durable pattern is **not** a Kai-only profile script and not repeated browser PKCE: PWP owns provider credential rotation as a real tool/API surface.

Merged implementation in `prismatic-engine` PR #220:

- `plugins/pwp/oauth_credentials.py`
- `plugins/pwp/plugin.py`
- `plugins/pwp/tests/test_oauth_credentials.py`
- `plugins/pwp/docs/credential-providers.md`
- `scripts/pwp`
- `plugins/__init__.py`

## Canonical commands

From the `prismatic-engine` repo:

```bash
python3 scripts/pwp credentials status ubersuggest
python3 scripts/pwp credentials status ubersuggest --verify
python3 scripts/pwp credentials refresh ubersuggest
python3 scripts/pwp credentials refresh ubersuggest --verbose
```

The CLI must never print raw token material. It returns only lengths, scope, expiry, and verification summary.

## Provider contract

The provider registry declares:

- `client_id`: `ubersuggest-mcp`
- token endpoint: `https://ubersuggest-mcp.neilpatelapi.com/token`
- required scope: `profile domain keywords serp backlinks site_audit content`
- token prefix: `ubs_oauth2_`
- minimum token length: > 40

Default files:

```text
/tmp/ubs_token
/tmp/ubs_refresh
/tmp/ubs_refresh_response.json
```

Env overrides:

```bash
UBERSUGGEST_ACCESS_TOKEN_FILE=/path/to/access
UBERSUGGEST_REFRESH_TOKEN_FILE=/path/to/refresh
UBERSUGGEST_REFRESH_RESPONSE_FILE=/path/to/response.json
```

## Safety rules
UBERSUGGEST_REFRESH_RESPONSE_FILE=/path/to/response.json
```

## Safety rules

The refresh path must reject:

- missing/empty refresh token
- suspiciously short tokens
- literal `...` inside a token (display/truncation corruption)
- wrong provider prefix
- token endpoint response that lacks a replacement refresh token
- non-JSON token endpoint response
- HTTP errors from the token endpoint
- live verification failure when verification is enabled

Tokens are written atomically with `0600` permissions.

## Live verification

`--verify` checks Ubersuggest MCP with:

- `auth_status` — should show Michael's account and paid tier, e.g. `tier1`
- `domain_overview` for `activeoahutours.com` — should return real DA/organic keyword data

## Cron integration

Kai cron `4356ea55909b` (`Active Oahu — Ubersuggest Token Auto-Refresh`) runs daily at `0 3 * * *` as a no-agent script. The cron script is only a thin bridge:

```text
/home/ubuntu/.hermes/profiles/kai/scripts/pwp_ubersuggest_refresh.py
```

It delegates to the shipped PWP CLI and must stay silent on success. It prints an actionable error only when refresh/verification fails.

Recommended schedule order for AOT:

1. `03:00 UTC` — PWP Ubersuggest credential refresh
2. `04:00 UTC Monday` — AOT weekly rankings report
3. `06:00 UTC Sunday` — AOT competitor content velocity

## Important implementation pitfall

Hermes' scheduler Python had an unrelated installed top-level `plugins` package. The repo-local CLI must force `plugins.pwp` to resolve to the checked-out repo:

- add `plugins/__init__.py`
- put `REPO_ROOT` at the front of `sys.path`
- evict any preloaded external `plugins` module if its `__file__` is not under the repo

This is a durable import-pattern pitfall for repo-local plugin CLIs run under agent virtualenvs.

## Human re-auth boundary

This eliminates routine re-auth only while `/tmp/ubs_refresh` remains valid. Human/browser PKCE is still required if:

- `/tmp/ubs_refresh` is missing
- token endpoint returns `invalid_grant`
- provider revokes the refresh token
- login/2FA/CAPTCHA/consent is required again

Once a fresh refresh token is saved, PWP resumes automatic rotation.

## Verification pattern

Focused verification should include:

```bash
python3 -m pytest plugins/pwp/tests/test_oauth_credentials.py -q
python3 -m pytest plugins/pwp/tests tests/test_pwp_hooks.py tests/test_plugin_loader_capability_validation.py tests/test_plugin_loader_pipeline.py -q
python3 scripts/pwp credentials status ubersuggest --verify
/home/ubuntu/.local/share/pipx/venvs/hermes-agent/bin/python scripts/pwp credentials status ubersuggest --verify
python3 /home/ubuntu/.hermes/profiles/kai/scripts/pwp_ubersuggest_refresh.py
```

Expect the cron bridge to exit 0 with no stdout/stderr on success.
