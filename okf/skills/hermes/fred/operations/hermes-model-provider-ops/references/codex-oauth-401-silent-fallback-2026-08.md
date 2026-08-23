# Codex OAuth 401 — silent fallback after "successful" reset (2026-08-22)

## Scenario

Cron check: Codex OAuth had been 429-rate-limited; a token reset ran ~04:51 UTC. Task: verify recovery 1h+ later. This is the canonical example of **every surface signal reading "recovered" while the provider is still down.**

## The trap — four signals that all lied

| # | Signal | Result | Naive verdict |
|---|---|---|---|
| 1 | `hermes auth status openai-codex` | `logged in` | fine |
| 2 | `hermes auth list` | primary cred `←` `dashboard device_code oauth` | fine |
| 3 | `auth.json` → `credential_pool.openai-codex[0].access_token` | populated | fine |
| 4 | `hermes chat -q "respond with the word PONG" --provider openai-codex --model gpt-5.5` | `PONG` in 14s, exit 0 | fine |

**All four were wrong.** The real signal sat one level deeper in `auth.json`:

```
.providers.openai-codex.last_auth_error.code    = 'refresh_token_reused'
.providers.openai-codex.last_auth_error.reason  = 'credential_pool_refresh_failure'
.providers.openai-codex.last_auth_error.relogin_required = True
.providers.openai-codex.last_auth_error.message = 'Codex refresh token was already consumed...'
.providers.openai-codex.last_auth_error.at      = 2026-08-22T11:56:02Z
```

**The failure lives on the provider entry, not the credential entry.** `credential_pool.openai-codex[0].last_error_code` was `None` — a probe that only reads the credential level reports clean.

## The proof — agent.log shows the fallback

```
11:57:00,124 WARNING agent.conversation_loop: API call failed (attempt 1/3)
  error_type=AuthenticationError provider=openai-codex model=gpt-5.5
  summary=HTTP 401: Could not parse your authentication token. Please try signing in again.
11:57:00,430 INFO agent.chat_completion_helpers: Fallback activated: gpt-5.5 → gemini-2.5-flash (google)
```

The PONG came from `gemini-2.5-flash`. The codex call never succeeded. Prior sessions (2026-08-20 11:56, 2026-08-22 04:08) showed the same 401.

## 401 message taxonomy (critical distinction)

- `HTTP 401: Provided authentication token is expired.` → normal expiry; Hermes refreshes and retries successfully. RECOVERED.
- `HTTP 401: Could not parse your authentication token. Please try signing in again.` → backend rejects the token itself; refresh loop fails with `refresh_token_reused`, `relogin_required=True`. NOT recovered — needs manual browser re-auth (`hermes auth reset openai-codex`), which a cron/agent context must never attempt.

## Silent-fallback consequence for cron

Cron jobs calling gpt-5.5 appear to succeed (they get answers) but actually run on the fallback model — masked failure. Watch `agent.log` / `errors.log` for `Fallback activated` lines; that is the alert signal. Also: the task-pointed log (`gateway-restart.log`) was stale (Jun 26, old Slack shutdown noise) — check mtimes and grep across all `logs/*.log`; the live logs were `agent.log` and `errors.log`.

## Verification recipe (use next time)

1. `hermes auth status openai-codex` — surface only, not proof.
2. Inspect BOTH levels of `auth.json`: credential `access_token` presence AND `providers.openai-codex.last_auth_error.*` / `relogin_required`. See the redacted snippet in SKILL.md step 1.
3. Smoke test: `hermes chat -q "respond with the word PONG" --provider openai-codex --model gpt-5.5`.
4. **The step that was missing before:** grep `agent.log` for the session id and for `Fallback activated` / `error_type=AuthenticationError`. PONG + fallback line = still down.
5. Report ≤5 lines; never attempt browser re-auth from a cron/agent context — report the `relogin_required` gap instead.
