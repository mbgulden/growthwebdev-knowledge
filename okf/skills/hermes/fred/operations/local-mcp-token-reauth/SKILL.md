---
name: local-mcp-token-reauth
description: Refresh expired OAuth tokens for local-subprocess MCP servers (gdrive, gmail, etc.) running as Hermes-attached Node or Python processes, where hermes mcp login reports no URL not an OAuth-capable server. Covers locating the token-storage path, inspecting how the running server reads the token, finding and launching the OAuth callback listener that already lives in the MCP server own directory, reconstructing the auth URL from the OAuth client JSON, handing the user one click, and re-probing when the redirect exchanges. Use when an mcp service tool call returns invalid_grant or 401 Unauthorized and the MCP is configured with a command and args transport (not a URL).
category: operations
triggers:
  - mcp_<service>_* tool returns invalid_grant or 401 Unauthorized
  - user asks to reauth gdrive or reauth gmail or refresh the MCP token
  - hermes mcp login <name> fails with no URL not an OAuth-capable server
  - token file at ~/.config/<service>/ or ~/.config/mcp-<service>/ exists but expiry_date is past and refresh grant is revoked
---

# Local-Subprocess MCP Token Reauth

## Core principle

Local-subprocess MCP servers (Node `server.js` or Python `mcp_server.py` started by Hermes with a `command` + `args` transport) are not flowable by `hermes mcp login` because that command requires an HTTP/SSE URL transport. The OAuth refresh path is fully scriptable; only the browser click needs the user. The recipe is: find the token file, inspect how the running server loads it, find the OAuth callback listener that already lives in the MCP's own directory, launch it in the background, reconstruct the auth URL from the OAuth client JSON, hand the user one click, re-probe on the redirect.

## When to use

- Any `mcp_<service>_*` tool returns `invalid_grant`, `401 Unauthorized`, or "Token has been expired or revoked".
- `hermes mcp login <service>` prints `no URL not an OAuth-capable server`.
- The token file exists at the expected path (`~/.config/<service>/` or `~/.config/mcp-<service>/`) but `expiry_date` is in the past.
- The user asks to refresh MCP credentials.

## Do NOT use when

- The MCP is configured with an HTTP/SSE URL transport (`hermes mcp login <name>` works directly).
- The token uses a different auth scheme (API key, AWS sigv4). A service-account JWT is NOT a foreign scheme — it is this skill's escalation target; see "Service account migration" below.
- The fix requires something the user cannot do in one click (e.g. creating a new OAuth client in Google Cloud Console). That is a setup change, not a reauth.

## The recipe (10 steps)

### 1. List MCP servers and find the one to reauth

```bash
hermes mcp list
```

Output shows columns: Name / Transport / Tools / Status. Local-subprocess MCPs are listed with their `command`/`args` path, not a URL. Note the `name` exactly as printed (e.g. `gdrive`).

### 2. Confirm hermes mcp login does not apply

```bash
hermes mcp login <name>
```

Expected response: `no URL not an OAuth-capable server`. If you get a different error, stop — the situation is not what this skill covers.

### 3. Locate the MCP server's source directory

```bash
ps auxf | grep -i <name> | grep -v grep
```

Look for the `node server.js` or `python mcp_server.py` line and read its argv. The first non-flag arg is the server's source path (e.g. `/home/ubuntu/work/local-gdrive-mcp/server.js`). That directory is where token-handling scripts typically live.

### 4. Find the token file and OAuth client JSON

The server's source usually reads two files (constants at the top of `server.js`):

- `OAUTH_KEYS_PATH` — the OAuth client JSON (e.g. `~/.config/mcp-<name>/gcp-oauth.keys.json`)
- `TOKEN_PATH` — the access/refresh token (e.g. `~/.config/mcp-<name>/.<name>-server-credentials.json`)

Inspect both:

```bash
ls -la ~/.config/mcp-<name>/
cat ~/.config/mcp-<name>/gcp-oauth.keys.json | head -40
cat ~/.config/mcp-<name>/.<name>-server-credentials.json
```

The token JSON will have `access_token`, `refresh_token`, `expiry_date` (milliseconds since epoch). If `expiry_date` is past and you got `invalid_grant` instead of a clean refresh, the refresh grant is also revoked — you need a full re-consent flow (`prompt: 'consent'`).

### 5. Find the OAuth callback listener script in the MCP's own directory

Most local-subprocess MCPs ship a `auth_callback.js`, `auth_callback_fixed.js`, or equivalent. Look for any file matching `*auth*callback*` or `*exchange*code*` in the MCP's source directory. Read it briefly — it should print an auth URL, listen on a localhost port (typically `:8085` or `:8765`), and write the new token to `TOKEN_PATH` on the redirect.

If a script exists, use it. If only an `exchange_gdrive_code_fixed.js`-style half-script exists (exchanges a manually-pasted code without a listener), you will need to run the listener variant. If no auth script exists at all, stop — this is no longer a reauth; it is a setup task and belongs to a different skill.

### 6. Launch the callback listener in the background

```bash
cd /path/to/mcp-server-dir && node auth_callback_fixed.js &
```

Verify the listener is bound:

```bash
ss -tlnp | grep :<port> || netstat -tlnp | grep :<port>
curl -sS http://localhost:<port>/  # expect HTTP 400 Missing code parameter
```

The HTTP 400 confirms the listener is live and the auth callback path is reachable.

### 7. Reconstruct the auth URL (do not depend on Node stdout buffering)

Node/Python servers print the auth URL at startup, but pipe buffering means it may not appear in captured stdout. Reconstruct it from the OAuth client JSON plus the script's hardcoded `redirect_uri`:

```python
import json, urllib.parse
keys = json.loads(open('~/.config/mcp-<name>/gcp-oauth.keys.json').read())
cfg = keys['installed'] or keys['web']
client_id = cfg['client_id']
redirect_uri = '<port from script>'  # e.g. http://localhost:8085
scope = ' '.join([
    '<scope1>', '<scope2>',
    # match the verified scope set used previously
])
params = {
    'client_id': client_id,
    'redirect_uri': redirect_uri,
    'response_type': 'code',
    'scope': scope,
    'access_type': 'offline',
    'prompt': 'consent',
    'include_granted_scopes': 'true',
}
print('https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params))
```

Hand the URL to the user. Tell them: open this URL, log in, click Allow. The redirect to `localhost:<port>` will auto-exchange and write the new token. I will see the redirect land.

### 8. Re-probe when the redirect exchanges

The listener prints `DONE` and exits after writing the new token. Watch the background process; once it exits, re-probe the failing tool:

```bash
# confirm token file was rewritten (mtime should be <30s old)
ls -la ~/.config/mcp-<name>/.<name>-server-credentials.json
# re-probe the original failing tool
```

The MCP server reads the token at request time (most local-subprocess MCPs do), so a restart is usually not needed.

### 9. Manual exchange when the user pastes the redirect URL in chat

Sometimes the user is on a remote machine or in a sandboxed browser that cannot reach `localhost:<port>`. They paste the full redirect URL into chat and you exchange it from the agent side.

**The most common pre-existing script in the MCP directory (`exchange_*_fixed.js`) uses a different `redirect_uri` than the listener** (typically no port). Do not reuse that script — Google's `redirect_uri_mismatch` error will reject the code. Instead, write a one-shot exchanger that matches the listener's redirect_uri, and **save it inside the MCP server directory** so `node_modules/googleapis` resolves correctly:

```bash
# Path inside the MCP server's own directory (where node_modules/ lives).
cat > /home/ubuntu/work/local-gdrive-mcp/exchange_now_8085.mjs << 'EOF'
import { google } from 'googleapis';
import fs from 'node:fs/promises';

const OAUTH_KEYS_PATH='/home/...json';
const TOKEN_PATH='/home/...json';
const REDIRECT_URI    = 'http://localhost:8085'; // MUST match the auth URL

const input = process.argv[2];
const u = new URL(input);
const code = u.searchParams.get('code');
if (!code) { console.error('No ?code= in input'); process.exit(1); }

const keys = JSON.parse(await fs.readFile(OAUTH_KEYS_PATH, 'utf8'));
const cfg = keys.installed || keys.web;
const client = new google.auth.OAuth2(cfg.client_id, cfg.client_secret, REDIRECT_URI);

const { tokens } = await client.getToken(code);
await fs.writeFile(TOKEN_PATH, JSON.stringify(tokens, null, 2), 'utf8');
console.log(JSON.stringify({ status: 'ok', has_refresh_token: !!tokens.refresh_token, expiry: tokens.expiry_date }, null, 2));
EOF

cd /home/ubuntu/work/local-gdrive-mcp && node exchange_now_8085.mjs "<full-redirect-URL>"
```

Two failure modes to know about:

- **`ERR_MODULE_NOT_FOUND: 'googleapis'`** when running from `/tmp/`. Node resolves `node_modules/` relative to the script path, not `cwd`. Save the script inside the MCP directory.
- **`Aborted (core dumped)` after the JSON output is benign.** Node's HTTP client cleanup path surfaces as SIGABRT. The JSON printed before the abort is the real result. Verify by reading the token file's mtime and contents.

### 10. Auto-refresh the token before any direct Drive API calls

The MCP server's own `OAuth2` client has an `on('tokens', ...)` handler that refreshes the access token transparently when the MCP makes a tool call. **Direct API calls from the agent** (e.g., `urllib` to `https://www.googleapis.com/upload/drive/v3/files`) read the on-disk `access_token` instead — and that file is not auto-refreshed. If more than ~1 hour has passed since the last reauth, the agent's direct call will fail with HTTP 401 even though the MCP tools still work.

Fix: refresh the `access_token` directly before the batch of uploads:

```python
import json, urllib.request, urllib.parse, time

tok = json.loads(open('/home/ubuntu/.config/mcp-<name>/.<name>-server-credentials.json').read())
keys = json.loads(open('/home/ubuntu/.config/mcp-<name>/gcp-oauth.keys.json').read())
cfg = keys['installed'] or keys['web']

data = urllib.parse.urlencode({
    'client_id': cfg['client_id'],
    'client_secret': cfg['client_secret'],
    'refresh_token': tok['refresh_token'],
    'grant_type': 'refresh_token',
}).encode()
resp = urllib.request.urlopen(urllib.request.Request(
    'https://oauth2.googleapis.com/token', data=data, method='POST'))
new = json.loads(resp.read())
tok['access_token'] = new['access_token']
tok['expires_in'] = new['expires_in']
tok['expiry_date'] = int(time.time() * 1000) + int(new['expires_in']) * 1000
json.dump(tok, open('/home/ubuntu/.config/mcp-<name>/.<name>-server-credentials.json', 'w'), indent=2)
```

Then use `tok['access_token']` in the `Authorization: Bearer ***` header. The MCP tools will pick up the refreshed file on the next request.

## The no-listener flow (verified 2026-08-18, gdrive)

Steps 5-8 (launch a localhost listener, watch the redirect land) are the classic path, but no listener is needed when the user is remote (their own laptop) and the auth URL's redirect_uri is a plain registered URI with no port. The gdrive MCP's two half-scripts cover the entire flow:

1. `cd /home/ubuntu/work/local-gdrive-mcp && node get_auth_url_fixed.js` → prints the full auth URL (`access_type=offline`, `prompt=consent`, scope = the exact previously-working set, redirect_uri=`http://localhost`).
2. Hand the URL to the user as a markdown link. Script the expectation: "Approve, then the browser will try http://localhost and show 'can't reach this page' — **that is success**, not an error. Copy the full URL from the address bar (it contains `&code=...`) and paste it here."
3. When the URL arrives: `node exchange_gdrive_code_fixed.js "<full-pasted-URL>"` in the MCP directory. Its `extractCode()` accepts a full redirect URL **or** a bare code and writes the new token to TOKEN_PATH. This works directly **only** because both scripts agree on redirect_uri `http://localhost` (no port). If your scripts disagree, use the step-9 one-shot exchanger instead.
4. Re-probe the originally-failing tool immediately. The server reads the token per request — `drive_about` was live within the same turn, no Hermes restart.

Observed pasted-URL shape (Google appends extra params; the exchanger ignores them): `http://localhost/?iss=https://accounts.google.com&code=4/...&scope=email profile ...&authuser=1&prompt=consent`.

## Why the refresh token dies every 7 days — and the escalation decision (2026-08-18)

If a Google reauth becomes a recurring weekly chore, the root cause is almost always: **the OAuth consent screen is in "Testing" publishing status**. Google's documented policy: an external app in Testing is issued refresh tokens that expire in **exactly 7 days** (observed: `refresh_token_expires_in: 604799`), regardless of use. No automation can extend them; once dead, a human re-consent is required by design.

**Token-file field semantics (easy to misread):**
- `expiry_date` — **absolute milliseconds** since epoch (access-token expiry, ~1h out).
- `refresh_token_expires_in` — **relative seconds** from issuance (refresh-token lifetime). Issuance time ≈ token file mtime (the exchange script writes it immediately). Do NOT parse it as a ms epoch — that yields `1970-01-01` (observed mistake, 2026-08-18).

**Escalation decision tree** — present to the user on the SECOND recurrence; don't just hand out another 7-day cycle:

| Option | Outcome | Cost |
|---|---|---|
| Service account | Self-signed JWT, no refresh token, zero-touch forever | ~30 min one-time — **agent-executable end-to-end via gcloud when gcloud is already authenticated** (only the Drive folder-sharing needs the user); folder-scoped — no whole-Drive search. Full implementation: next section |
| Testing app + watchdog | Full access as today | silent-when-healthy daily no-agent cron (3-day alert window) + ~2 min reauth every 7 days |
| Production + verification | Infinite refresh tokens | `drive.readonly` is a **restricted** scope → CASA security assessment (weeks, possibly paid); `drive.file` is non-sensitive but an unverified production app still shows a full-page "Google hasn't verified this app" warning — not worth it for personal tooling |

**Watchdog pattern (floor option, implemented 2026-08-18):** `~/.hermes/profiles/orchestrator/scripts/gdrive_token_watchdog.py`, daily no-agent cron, silent (empty stdout) while the refresh token has >3 days left; otherwise prints a reauth message with a freshly generated auth URL (calls `node get_auth_url_fixed.js`). Verified 5/5 behavior cases via `/tmp/hermes-verify-gdrive-watchdog-suite.py` (healthy→silent, near-expiry→alert+URL, expired→alert, no-expiry-field→silent, missing-file→graceful warning).

## Service account migration — implemented 2026-08-18 (gdrive, zero-touch forever)

When the 7-day Testing-policy section above applies and the user picks the SA path, the GCP side is agent-executable (no browser) if `gcloud` is already signed in — check `gcloud auth list` first; if empty, this degrades to a user checklist.

```bash
# 1. Find the project owning the OAuth client: the OAuth client_id IS the project NUMBER.
for p in $(gcloud projects list --format "value(projectId)"); do
  [ "$(gcloud projects describe "$p" --format value(projectNumber) 2>/dev/null)" = "<client_id>" ] && echo "MATCH: $p"
done
# 2. Create SA + key (chmod 600 the key), enable the APIs the MCP actually uses:
gcloud iam service-accounts create <name> --project=<proj> --display-name="..."
gcloud iam service-accounts keys create <key.json> --iam-account=<name>@<proj>.iam.gserviceaccount.com --project=<proj>
gcloud services enable drive.googleapis.com sheets.googleapis.com --project=<proj>
```

**Pre-sharing proof signature (expected before the user shares anything):** JWT token mint → 200; `drive.about.get` → SA identity + `storageQuota.limit: "0"`; `files.list` → empty. The 0-byte quota is the SA's own storage, NOT broken auth — don't chase it.

**googleapis 172 / google-auth-library 10.6 — three auth constructions, only one works (all observed live):**
- `new google.auth.JWT(email, privateKey, scope)` positional → silently fails to bind the key → 401 CREDENTIALS_MISSING or "No key or keyFile set".
- `google.auth.fromJSON(key, { scopes: [...] })` → `400 invalid_scope` at the token endpoint, even though a hand-rolled RS256 assertion with the *identical* scope claim mints fine (verify with a manual-JWT probe before doubting the key).
- **Working:** `const auth = google.auth.fromJSON(key); auth.scopes = [...];` — set `.scopes` on the client AFTER construction.

**Server patch pattern:** env-switch (`process.env.GDRIVE_SA_KEY` path constant; empty → original OAuth branch untouched). Never delete the OAuth branch — rollback is unset the env var, plus keep a timestamped `.bak` of server.js. Then verify BOTH directions with the MCP-stdio e2e harness (`scripts/mcp-stdio-e2e.mjs`): SA mode must return the SA identity; OAuth mode (env explicitly unset) must return the human account. The OAuth-fallback regression is the check people skip and the one that matters.

**API status disambiguation:** `403 Method doesn't allow unregistered callers` = the API is not enabled for the project (fix: `gcloud services enable`). `404` on a bogus spreadsheetId = auth is fine, resource just missing. These read alike in a stack trace; the status code is the signal.

## Pitfalls

- Do not try hermes mcp login for local-subprocess MCPs. It is gated on URL transport and will fail. This skill is the alternative path.
- Do not depend on stdout from the listener to get the auth URL. Node buffers stdout when not attached to a TTY. Always reconstruct from gcp-oauth.keys.json plus the script's hardcoded redirect_uri.
- Do not use empty prompt or skip consent. If the refresh grant is revoked (which is the common case when invalid_grant is returned), you must force the consent screen to get a new refresh_token. Forgetting this means the new token has no refresh capability and expires in 1 hour.
- Match the script redirect_uri exactly in the reconstructed URL. If auth_callback_fixed.js listens on :8085 with redirect_uri http://localhost:8085, do not reconstruct the URL with http://localhost or http://localhost:8765. Google rejects mismatched redirect URIs.
- Do not include scopes the OAuth client is not registered for. invalid_scope is the failure mode. Check the previously-working token scope field and copy that exact set.
- The MCP server may need a restart if it caches the OAuth client object. Most local-subprocess MCPs re-read the token at request time, but a few cache OAuth2 instances at startup. If re-probing still fails after the token file is rewritten, the user restarts Hermes (outbound action gate).
- Do not write the new token to a different path than TOKEN_PATH reads from. Some setups have GDRIVE_TOKEN_PATH env vars overriding the default. Check the server source for process.env.*TOKEN_PATH and confirm where it actually reads.
- Do not skip step 3 (ps auxf). There are often two server processes running (e.g. one started in July, one started in August). You want to find the currently serving process's source directory, which may differ from hermes mcp list reported command.
- Do not reuse `exchange_*_fixed.js` if it uses a different `redirect_uri` than the listener. Write a one-shot exchanger that matches the listener exactly. See step 9 for the recipe.
- Do not save the one-shot exchanger to `/tmp/`. Node resolves `node_modules/` from the script's directory, not from `cwd`. `ERR_MODULE_NOT_FOUND: 'googleapis'` is the symptom. Save inside the MCP server directory.
- Do not treat `Aborted (core dumped)` after the JSON output as a failure. Node's HTTP cleanup surfaces as SIGABRT. The JSON is the real result; verify by reading the token file.
- Do not use the on-disk `access_token` for direct API calls without refreshing it first. The MCP server's OAuth client auto-refreshes transparently; the on-disk file does not. Step 10 shows how to refresh it manually.
- Do not trust the positional `google.auth.JWT(email, key, scope)` constructor in googleapis ≥170 — it may silently not bind the key. And do not pass `{scopes}` into `fromJSON()` — it yields `invalid_scope`. Set `auth.scopes` after construction (see Service account migration).
- After patching an MCP server for a new auth mode, re-verify the OLD mode still works (env unset). A green new-mode test proves nothing about the fallback the rest of the fleet may still be using.

## What this skill does NOT do

- It does not handle first-time setup of an MCP server (creating the OAuth client in Google Cloud, registering the redirect URI, writing gcp-oauth.keys.json). That is a setup task, not a reauth.
- It does not handle non-OAuth MCP auth (API keys, service accounts, basic auth). Look for the auth scheme in the server source first.
- It does not restart Hermes. The user does that. See outbound-action-gate.
- It does not cover URL-transport MCPs. Use hermes mcp login <name> directly for those.

## Reference

- Canonical worked example: /home/ubuntu/work/local-gdrive-mcp/ (gdrive MCP), with server.js (token loader), auth_callback_fixed.js (listener on :8085), and exchange_gdrive_code_fixed.js (manual-code exchange). Token JSON at /home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json.
- Reusable e2e harness: scripts/mcp-stdio-e2e.mjs — env-parameterized MCP stdio handshake + drive_about identity check; run it after any server.js auth patch, in both modes.
- Companion discipline: proactive-execution-discipline — "Don't punt when you have the tools" pitfall. This skill is the recipe that pitfall points at.
- Companion skill: hermes-agent (bundled, protected) for general MCP plumbing.
- Session-specific transcripts:
  - references/gdrive-mcp-reauth-2026-08-05.md — listener path, scopes, URL reconstruction, observed pitfalls (first session of this skill).
  - references/gdrive-mcp-reauth-2026-08-05b.md — manual exchange path + direct-API-call auto-refresh pitfall (second session).
  - references/gdrive-7day-testing-policy-2026-08-18.md — 7-day Testing-policy root cause, token-file field semantics, service-account vs watchdog escalation research, rclone-claim correction.
  - references/gdrive-service-account-impl-2026-08-18.md — executed SA migration for the gdrive MCP: exact gcloud commands, all three auth-construction attempts (2 failed, 1 worked), server.js dual-mode patch, dual-direction e2e evidence, 32-folder share list.
  - references/sandbox-strips-secrets-workflow.md — when `execute_code`/`terminal` sandboxes strip env vars (e.g., `LINEAR_OAUTH_TOKEN`); disk-via-disk helper pattern.