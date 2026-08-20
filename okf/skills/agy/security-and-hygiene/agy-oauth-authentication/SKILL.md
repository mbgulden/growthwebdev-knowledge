---
name: agy-oauth-authentication
description: Diagnose and manage AGY's Google OAuth credentials and tokens.
version: 1.0.0
---

# AGY OAuth Authentication

Inspect, refresh, and maintain the CLI's Google authentication tokens.

## Trigger Conditions

Use when AGY returns authentication errors, prompts for login, or when tokens expire.

## Numbered Steps with Exact Commands

1. **Check active token files**:
   Verify OAuth files exist:
   ```bash
   ls -la $HOME/.gemini/antigravity-cli/
   ```

2. **Do not rely on `agy auth status` in headless Hermes/cron contexts**:
   ```bash
   export TERM=dumb
   /home/ubuntu/.local/bin/agy auth status 2>/dev/null || echo "auth status is not headless-safe; use smoke test below"
   ```
   As of 2026-07-20, `agy auth status` can still fail with Bubble Tea `/dev/tty` errors even when print-mode auth works. Treat it as an interactive-only diagnostic, not proof of failure.

3. **Restore/Copy token in cross-profile execution**:
   If running from a sub-profile, locate Fred's active token and reuse it:
   ```bash
   export HOME=$HERMES_PROFILE/home
   /home/ubuntu/.local/bin/agy --print "Reply exactly: AUTH_OK" --print-timeout 45s
   ```

4. **Verify connection**:
   Run a short query:
   ```bash
   /home/ubuntu/.local/bin/agy --print "Reply exactly: AUTH_OK" --print-timeout 45s
   ```

## Pitfalls

- **Headless TTY requirement**: commands like `agy auth` fail in subagents/cron jobs due to TTY requirements; `TERM=dumb` is not sufficient for current AGY. Prefer bounded `--print` smoke tests.
- **Wrong-layer false positive**: A neutral `--print AUTH_OK` only proves OAuth/model connectivity. It does not prove the Prismatic/Linear preflight pipeline is unblocked. Inspect event-router launch records, queue preflight fields, and captured AGY logs before claiming the pipeline is healthy.
- **Profile-hopping HOME override**: Ensure `$HOME` is explicitly modified before every command block if referencing another profile's auth token.

## Verification Steps

- Ensure a simple print command executes without triggering a login prompt:
  ```bash
  /home/ubuntu/.local/bin/agy --print "Reply exactly: AUTH_OK" --print-timeout 45s
  ```
