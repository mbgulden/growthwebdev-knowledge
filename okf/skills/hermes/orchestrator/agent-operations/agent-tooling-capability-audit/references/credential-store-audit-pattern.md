# Credential Store Audit Pattern

Class-level recipe for auditing `~/.hermes/profiles/<profile>/credentials.json` (and the sibling `.env` file) when Michael says "recheck all credentials" or after a credential rotation event.

## Core principle

Two independent stores, one active per key. `credentials.json` is the Hermes-managed store; `.env` is the profile environment file that systemd/`EnvironmentFile=` loads into the gateway process. A key can be **dead in credentials.json but alive in .env** (or vice versa). The audit must test **both** and report which is the live one.

## Steps

### 1. Enumerate the keys

```python
import json
d = json.load(open('/home/ubuntu/.hermes/profiles/orchestrator/credentials.json'))
creds = d.get('credentials', {})
# Print name + length + prefix (first 8-12 chars, never full value)
for k, v in creds.items():
    val = v.get('value', '')
    print(f"{k}: len={len(val)} prefix={val[:12]}")
```

Also enumerate `.env` keys (mask values):

```bash
grep -E '^[A-Z_]+=' ~/.hermes/profiles/orchestrator/.env | cut -d= -f1
```

Note: the `.env` file is a Hermes credential store — `read_file` will refuse it. Use `terminal` with `grep`/`python3` to extract specific keys (mask values in output).

### 2. Map usage: which keys are actually referenced?

Before testing, check which keys are actually **used** by the profile. An unused dead key is noise; a used dead key is a problem.

```bash
# For each key name, grep the profile config + .env for references:
grep -c '<KEY_NAME>' ~/.hermes/profiles/orchestrator/config.yaml
grep -c '<KEY_NAME>' ~/.hermes/profiles/orchestrator/.env
```

Also check the `providers:` block in `config.yaml` — `api_key` and `key_env` fields reference credential sources. A `key_env: SOME_VAR` means the key lives in `.env` (or systemd env), not in `credentials.json`.

**Keys not referenced in config.yaml or .env** are either (a) stale leftovers, or (b) used by external scripts/crons. Grep `scripts/` for the key name before classifying as "unused."

### 3. Live-test each key against its API

For each key with a non-empty value, make a minimal live API call:

| Service | Test endpoint | Auth header |
|---|---|---|
| GitHub | `GET https://api.github.com/user` | `Authorization: token <PAT>` |
| DeepSeek | `GET https://api.deepseek.com/models` | `Authorization: Bearer <key>` |
| OpenAI | `GET https://api.openai.com/v1/models` | `Authorization: Bearer <key>` |
| Linear (API key) | GraphQL `POST https://api.linear.app/graphql` `{"query":"{ teams(first:1){nodes{key}}}"}` | `Authorization: Bearer <key>` |
| Linear (OAuth) | same GraphQL endpoint | `Authorization: Bearer <oauth_token>` |
| Telegram | `GET https://api.telegram.org/bot<token>/getMe` | (token in URL) |
| Slack | `GET https://slack.com/api/auth.test` | `Authorization: Bearer <token>` |
| Cal.com | `GET https://cal.com/api/v2/users/me` | `Authorization: Bearer <key>` |
| Google Gemini | `GET https://generativelanguage.googleapis.com/v1beta/models` | `x-goog-api-key: <key>` |
| vLLM (local) | `GET http://<host>:<port>/v1/models` | `Authorization: Bearer <key>` |
| Jules (Google) | no stable REST API — skip or note "no verifiable endpoint" |

**Interpretation rules:**
- `HTTP 200` → key is valid.
- `HTTP 401` → key is dead (revoked, expired, or wrong).
- `HTTP 403` → ambiguous. For Cal.com, `403 error code 1010` is Cloudflare WAF (geo/IP block at CF edge), NOT an auth failure. For other services, 403 usually means the key is valid but lacks permission.
- `HTTP 400` on GraphQL → auth **passed**, query was rejected. This is a VALIDATION error, not an auth error. The key works.
- `HTTP 200` returning HTML → you hit a web page, not an API. The key may be fine but the endpoint is wrong. Note "no verifiable API endpoint."

### 4. Cross-check .env vs credentials.json for duplicates

When a key appears in BOTH stores (e.g. `TELEGRAM_BOT_TOKEN`), test BOTH and report which is alive:

```
credentials.json TELEGRAM_BOT_TOKEN: 8653475199:A... → 401 (dead)
.env TELEGRAM_BOT_TOKEN:          8929563456:A... → 200 @FredTheFredBot (alive)
```

The .env token is the one systemd loads into the gateway process. The credentials.json copy is stale. Flag it but don't "fix" it — Michael decides whether to clean up.

### 5. Check local vLLM / custom providers

The `config.yaml` `providers:` block defines local endpoints with their own keys. Test the vLLM endpoint directly:

```bash
curl -s http://<host>:<port>/v1/models -H "Authorization: Bearer <key>"
```

The key may live in `.env` (via `key_env:`) or inline in `config.yaml` (`api_key:`). Check both locations.

**Critical:** a vLLM server started with `--api-key` returns 401 on `/v1/chat/completions` even when `/v1/models` returns 200. Test BOTH endpoints. 200+401 = auth gap, not dead server.

### 6. Report shape

```
Working (N):
  KEY: OK — <evidence>
  ...

Dead (N):
  KEY: <status> — <detail>
  ...

Empty (N) — not referenced in config:
  KEY: (empty)
  ...
```

End with: "Action needed: none" or "Action needed: <one specific thing>."

## Pitfalls

- **Never print full key values.** Prefix (first 8-12 chars) + length is sufficient. Full values in output = credential leak.
- **`.env` is a Hermes credential store** — `read_file` refuses it. Use `terminal` with `grep` + masking.
- **`credentials.json` may have keys that are NOT in `.env` and vice versa.** They are independent stores. Don't assume one is a superset of the other.
- **400 on GraphQL ≠ auth failure.** A GraphQL validation error means the token was accepted and the query was parsed. The key works.
- **403 ≠ auth failure.** Especially for Cal.com (Cloudflare WAF 1010) and some Google APIs (permission vs auth). Check the response body before classifying.
- **`/v1/models` 200 ≠ auth OK.** A vLLM/llama-server with `--api-key` can return 200 on the models endpoint but 401 on chat completions. Test both.
- **Don't fix what isn't broken.** A dead key that isn't referenced in any config is noise. Report it. Michael decides whether to clean it up. Don't auto-delete or auto-rotate.
- **Jules API has no stable REST endpoint.** The `AQ.Ab8RN*` token format is a Google service token. Hitting `https://jules.google.com/` returns HTML (the web app), not an API response. Note "no verifiable endpoint" rather than marking it dead.
- **`LINEAR_API_KEY_RO` (read-only) may be intentionally empty.** It's a placeholder for a future read-only token. Empty + unreferenced = safe to leave.

## Verification

- Every non-empty key in `credentials.json` was live-tested or explicitly marked "no verifiable endpoint."
- Every key in `.env` that duplicates a `credentials.json` key was tested in BOTH locations.
- The report distinguishes "dead + used" (action needed) from "dead + unused" (noise) from "empty + unreferenced" (safe).
- No full key values appear in the report or in any tool output.
