# Linear Credential Surface: API, OAuth Token, OAuth Client, Webhook

Use this reference when a Linear alert or failure mentions OAuth/API/webhook access. Do not collapse the surfaces into “Linear is broken.” Verify which layer failed.

## Credential surfaces

| Surface | Typical variable/path | Purpose | Failure means |
|---|---|---|---|
| Linear API key | `LINEAR_API_KEY` | Direct GraphQL API access as the user/API actor. Useful for administrative GraphQL reads/writes. | API-key GraphQL path is unavailable, rate-limited, or missing. It does **not** prove OAuth/webhooks are broken. |
| Linear OAuth token | `LINEAR_OAUTH_TOKEN` or `credentials.json` entry | App/agent actor GraphQL access used by Prismatic/agent activity paths. | Current OAuth app actor token is missing/expired/revoked. It does **not** necessarily mean the API key or webhook secret is missing. |
| OAuth client credentials | `LINEAR_OAUTH_CLIENT_ID` + `LINEAR_OAUTH_CLIENT_SECRET` | Mint/rotate a fresh OAuth app token via `https://api.linear.app/oauth/token`. | Rotation cannot mint a new token. Existing OAuth token/API key/webhook may still work. |
| Webhook secret | `PRISMATIC_LINEAR_WEBHOOK_SECRET` | Verify incoming Linear webhooks at the gateway. | Incoming webhook signature verification can fail. It does **not** imply GraphQL access is broken. |

## Triage pattern

1. Identify the exact failing contract from logs/alerts.
   - `Cannot find Linear OAuth client credentials` = missing OAuth client id/secret for rotation, not proof that API, OAuth token, or webhook paths are down.
   - `invalid_grant` or token format errors = OAuth token mint/refresh problem.
   - GraphQL 401/403/429 = API/OAuth token access problem depending on which token was used.
   - Webhook signature mismatch = webhook secret/gateway env problem.
2. Check current cron state before trusting a stale Telegram alert. The alert may have fired before credentials were restored.
3. Verify surfaces separately:
   - API key GraphQL: `viewer`/`organization` query with `LINEAR_API_KEY`.
   - Stored OAuth token GraphQL: read from profile `credentials.json`, then query `viewer`/`organization`.
   - Rotation contract: run the refresh wrapper; if token is fresh, “skip + gateway env refreshed” is healthy.
   - Gateway env: assert `LINEAR_OAUTH_TOKEN` and `PRISMATIC_LINEAR_WEBHOOK_SECRET` entries exist without printing values.
4. Report in separate rows: API key, OAuth token, OAuth client credentials, webhook secret.
5. If only OAuth client credentials are missing, say exactly that; do not say Linear access is down.

## Reporting language

Use wording like:

```text
This is not “Linear is down.” API key, OAuth token, webhook secret, and OAuth client credentials are separate surfaces. The failing contract is <surface>. Current live checks: <results>.
```

## Safety

- Never print raw tokens/secrets.
- When documenting state, use `set/missing` or masked prefixes only.
- Do not rotate webhook secrets casually. Linear webhook signing secret must match the gateway environment.
