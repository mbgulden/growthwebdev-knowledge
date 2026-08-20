# AGY OAuth resilient refresh pattern

Use when AGY/Antigravity OAuth jobs fail silently or Michael is asked to race a short PKCE browser-code prompt.

## Session lesson

The interactive AGY CLI auth listener can time out before a Telegram round-trip completes. The durable fix is not to keep asking Michael for new one-time codes if any valid refresh token exists elsewhere.

## Recovery sequence

1. **Inspect token paths before browser auth.**
   Check all known AGY/Hermes token locations, including:
   - native AGY home token path,
   - work-profile watchdog path,
   - real orchestrator profile HOME path.

2. **Skip bad candidates, do not stop at first file.**
   - Empty files and malformed JSON can be leftovers from timed-out PKCE attempts.
   - Continue fallback discovery instead of treating the first token path as authoritative.
   - Prefer candidates containing `refresh_token` over access-token-only files.

3. **Recover from partial/corrupt token files cautiously.**
   - If JSON parse fails, regex-recover only `refresh_token` if present.
   - Do not print token contents.

4. **Refresh non-interactively.**
   - Use the recovered refresh token to obtain a fresh access token.
   - Copy refreshed token data back to every durable token path required by AGY/Hermes cron contexts.

5. **Smoke test AGY with bounded timeout.**
   - Use the real AGY binary candidate list, not a single hard-coded path.
   - Check for a minimal `OK` style response.

6. **Run the cron and watchdog.**
   - Run the AGY OAuth cron job itself.
   - Re-run Tier-1 Silent Failure Watchdog or detector and confirm the job leaves the silent-failure bucket.

7. **Verify code changes with isolated fixtures.**
   - Create `/tmp/hermes-verify-*` via `tempfile`.
   - Assert empty/corrupt files are skipped.
   - Assert refresh-token fallback beats access-only candidates.
   - Assert regex recovery still works.
   - Assert all unusable candidates return a clean no-token tuple.
   - Assert expected durable token paths and AGY binary candidates are present.

## Pitfalls

- Do not make Michael repeatedly race a 30-second PKCE prompt when a refresh token may already exist.
- Do not reuse authorization codes; they are bound to the active CLI process/code verifier.
- Do not print token values or OAuth secrets in summaries or verification output.
- Do not call the cron fixed until the actual cron run and watchdog/detector confirm recovery.
