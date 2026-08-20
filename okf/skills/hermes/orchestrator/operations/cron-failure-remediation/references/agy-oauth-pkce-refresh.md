# AGY OAuth PKCE Refresh Pattern

Use this when the Tier-1 watchdog or AGY refresh cron reports missing/expired AGY OAuth tokens and the CLI asks for browser login.

## Key lesson

AGY's OAuth login uses PKCE. The pasted `4/...` authorization code is bound to the exact live CLI process that generated the `code_challenge` link. A code from a previous link/process will fail with:

```text
oauth2: "invalid_grant" "Invalid code verifier."
```

Do not retry the old code. Start a fresh AGY auth listener, send the fresh link, and paste the code into that same still-running process.

## Working sequence

1. **First try non-interactive token recovery before asking Michael to race the 30s prompt.** Inspect the expected token paths for an existing refresh token. Empty/corrupt files can be left by failed auth attempts and may sit before a valid fallback path; the refresh helper must skip unusable token files and continue searching.

```bash
python3 - <<'PY'
import json, time
from pathlib import Path
for p in [
    Path('/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token'),
    Path('/home/ubuntu/work/.hermes/profiles/orchestrator/home/.gemini/antigravity-cli/antigravity-oauth-token'),
    Path('/home/ubuntu/.hermes/profiles/orchestrator/home/.gemini/antigravity-cli/antigravity-oauth-token'),
]:
    print(p, 'exists=', p.exists(), 'size=', p.stat().st_size if p.exists() else '-')
    if p.exists() and p.stat().st_size:
        data = json.loads(p.read_text())
        tok = data.get('token', {})
        print('  has_refresh=', bool(tok.get('refresh_token')), 'expiry=', tok.get('expiry'))
PY
```

2. If a refresh token exists in any fallback path, run the refresh script with the workspace PRISMATIC_HOME when needed. The durable refresh helper should write the resulting refreshed token to **all** runtime paths expected by AGY/Hermes, not just the source path.

```bash
PRISMATIC_HOME=/home/ubuntu/work python3 /home/ubuntu/.hermes/profiles/orchestrator/scripts/agy_oauth_refresh.py
```

A resilient helper should maintain a deduped token target set equivalent to:

```text
/home/ubuntu/.gemini/antigravity-cli/antigravity-oauth-token
/home/ubuntu/work/.hermes/profiles/orchestrator/home/.gemini/antigravity-cli/antigravity-oauth-token
/home/ubuntu/.hermes/profiles/orchestrator/home/.gemini/antigravity-cli/antigravity-oauth-token
```

It should also use a deduped AGY binary candidate list, including `/home/ubuntu/.local/bin/agy`, so smoke tests do not depend on `PRISMATIC_HOME` pointing at the same root as the binary.

3. Verify with a smoke test and the actual cron:

```bash
HOME=/home/ubuntu/.hermes/profiles/orchestrator/home /home/ubuntu/.local/bin/agy --print-timeout 60s --print 'respond OK'
# expect: OK
```

Then run `cronjob(action="run", job_id="d8660aee2fb0")` and confirm `last_status=ok`.

4. Only if no refresh token is recoverable, start AGY in a PTY with the correct profile HOME:

```bash
HOME=/home/ubuntu/.hermes/profiles/orchestrator/home /home/ubuntu/.local/bin/agy --print 'respond OK'
```

5. Keep the process running. Capture the login URL from stdout.
6. Send the fresh URL to Michael immediately and say the listener is short-lived.
7. When Michael replies with a code, submit it to the same process stdin with newline.
8. Wait for the process to exit.
9. Verify with a fresh AGY smoke test and rerun the AGY OAuth refresh cron.

## Timing and chat coordination

The listener commonly times out around 30 seconds. `--print-timeout` does **not** extend this auth prompt window; it only affects print-mode response waiting after authentication. If it times out, generate a new listener and link. The old URL/code pair is invalid for any future listener.

When Michael asks to “speed up your own processes or extend the CLI wait time,” treat that as a workflow correction: stop making him race repeated 30-second listeners. First exhaust non-interactive refresh-token recovery and make the refresh helper resilient. Only use live PKCE when every refresh-token path is truly unavailable.

For Telegram/human-in-the-loop flows:

- Do not start repeatedly spawning listeners unless Michael is actively ready to click the link and paste the code.
- If a process returns `already_exited` when you try `process.submit`, do **not** start a new listener and submit the old code. Tell Michael the code missed its matching verifier, then generate a fresh link only when he is ready.
- Background watch messages like `matched watch pattern "Or, paste the authorization code here"` are not user codes; poll the process but wait for an actual `4/...` authorization code message.
- Prefer a compact instruction: “Open this exact link, approve, paste the code immediately — no extra text.”

## Verification checklist

After changing `agy_oauth_refresh.py` or token-discovery behavior, run an ad hoc verifier under `/tmp/hermes-verify-*` that imports the script and monkeypatches `TOKEN_PATHS` against tempfile fixtures. Verify at least:

- `py_compile` passes for the changed script
- empty/corrupt first token file is skipped and a later valid refresh token is used
- refresh-token candidates are preferred over access-token-only candidates
- truncated/corrupt token text containing `"refresh_token"` is still recoverable via regex
- all-unusable candidates return `(None, None, None)` cleanly
- the durable token path list includes native AGY, work-profile watchdog, and orchestrator profile HOME token paths
- the AGY binary candidate list includes the real native binary path
- the verifier file is removed after execution

Label the result as **ad hoc targeted verification only**, not suite green. Then verify the live path with AGY `--print 'respond OK'` and the actual OAuth refresh cron when credentials are present.

## OKF documentation

If this remediation changes the durable recovery contract or closes a Tier-1 silent-failure loop, record it in OKF operations and link it from the operations index. The OKF note should include:

- trigger / watchdog symptom
- root cause
- durable fix contract
- ad hoc verification evidence and cleanup status
- actual cron run status
- any remaining PKCE caveat without storing tokens or authorization codes

## Reporting

- If the code fails with `Invalid code verifier`, say plainly that it belonged to a previous listener.
- Do not say AGY is broken; this is expected PKCE behavior.
- Do not persist or quote OAuth tokens. Authorization codes are transient and should not be stored in memory/skills beyond this generic pattern.
