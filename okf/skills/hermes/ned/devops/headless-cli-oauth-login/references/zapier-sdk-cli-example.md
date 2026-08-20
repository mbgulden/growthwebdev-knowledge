# zapier-sdk CLI Headless Login — Worked Example

Real transcript from authenticating `@zapier/zapier-sdk-cli` v0.70.0 on a headless Ubuntu server (Tailscale, no browser, user authorizes from a local laptop).

## Context

- Server: Ubuntu 24.04, Node v22.22.2, npm 10.9.7.
- No global `zapier-sdk` install — used `npx -y @zapier/zapier-sdk-cli` per fallback guideline.
- User was actively logged into a different provider when the flow started; agent had to wait for them to log into Zapier separately.

## Step 1 — Environment check

```bash
node -v && npm -v
# v22.22.2
# 10.9.7

which zapier-sdk && zapier-sdk --version 2>/dev/null || echo "zapier-sdk not installed globally"
# zapier-sdk not installed globally
```

Decision: skip global install (`npm install -g` would hit `EACCES` on the shared host), use `npx -y` for every invocation.

## Step 2 — Kick off headless login

First attempt (failed):

```bash
# background=true, no stdbuf wrapping
npx -y @zapier/zapier-sdk-cli login --non-interactive --headless --timeout 600 2>&1
```

Behavior observed:
- `process(action='poll')` returned `status: running, uptime_seconds: 1..60, output_preview: ""` repeatedly.
- `process(action='log')` returned `total_lines: 0`.
- Agent assumed the CLI was hung. Killed it.

**Root cause:** npx was buffering stdout. The CLI was actually fine — it just hadn't flushed.

Second attempt (worked) — same command, but with `stdbuf -oL -eL` wrapping:

```bash
stdbuf -oL -eL npx -y @zapier/zapier-sdk-cli login --non-interactive --headless --timeout 600 --name "ned-headless" 2>&1
```

Behavior observed:
- `process(action='poll')` continued to show empty output (the background process wrapper also buffers).
- `process(action='wait', timeout=30)` forced the CLI to finish — after which the full log was readable.

**Final output (exit code 0):**

```
To run a command as administrator (user "root"), use "sudo <command>".
See "man sudo_root" for details.

Open this login URL in a browser to continue:
https://zapier.com/oauth/authorize/?response_type=code&client_id=grwWZD5hUWGvb4V8ODBuOtXer3h0DBEZ2HR8aay6&redirect_uri=http%3A%2F%2Flocalhost%3A49505%2Foauth&scope=internal+credentials+offline_access&state=7c610a053682fd439a1b2b6f783cffd8dd3c2160b65af6110d98c2de&code_challenge=oqG7FEOmqbLKFNoC9MUoNAAfI33ExDKIDGIbrjUCcTg&code_challenge_method=S256
After authorizing, finish with `zapier-sdk login --callback-url <final-url>`.
```

**Key observation:** the CLI printed the URL and exited cleanly (`exit_code: 0`). It was **not** waiting for the callback. The footer line literally tells the user to run a separate `login --callback-url` invocation.

## Step 3 — Message to the user

Agent relayed:

1. The full URL.
2. The expected redirect URL shape: `http://localhost:49505/oauth?code=...&state=7c610a05...`.
3. The instruction that the browser will fail to load `localhost:49505` (it's a loopback on the server), but the URL with the `code=` param stays visible in the address bar — copy it.
4. The `state` parameter the user must see in the pasted URL: `7c610a053682fd439a1b2b6f783cffd8dd3c2160b65af6110d98c2de`. If it differs, the flow is stale.

## Step 4 — (Deferred pending user callback)

Not yet executed in this session. The resume command will be:

```bash
stdbuf -oL -eL npx -y @zapier/zapier-sdk-cli login --callback-url "<pasted-url>" 2>&1
```

## Step 5 — (Deferred) verification

```bash
stdbuf -oL -eL npx -y @zapier/zapier-sdk-cli list-connections --json 2>&1
# + scripts/check-headless-login-artifacts.sh
```

## Lessons baked into the umbrella skill

1. **Always wrap backgrounded CLI invocations with `stdbuf -oL -eL`** if stdout must be live-read.
2. **Don't trust `process(action='poll')` showing empty output** to mean "CLI is hung." Force a flush with `process(action='wait', timeout=30)`.
3. **Most headless-OAuth CLIs print URL + exit clean + resume via `--callback-url`.** Don't expect a long-lived background process.
4. **Pre-empt the localhost-redirect-looks-broken confusion** in the user message.
5. **Match-on-state.** Always tell the user the expected `state` value so they can sanity-check the callback before pasting.
