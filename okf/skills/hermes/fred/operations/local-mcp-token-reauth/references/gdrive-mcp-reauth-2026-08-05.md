# gdrive MCP reauth — 2026-08-05 session transcript

Reproducible recipe + exact observed values from the session that established this skill.

## Failure

```text
mcp_gdrive_drive_about -> {"error": "invalid_grant"}
mcp_gdrive_drive_search -> {"error": "invalid_grant"}
```

Persistent across two consecutive calls, ruling out a transient network blip.

## Root cause

`/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json`:

```json
{
  "access_token": "ya29.a...0207",
  "expires_in": 3598,
  "refresh_token": "1//06K...QiRo",
  "scope": "https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid https://www.googleapis.com/auth/drive.readonly",
  "token_type": "Bearer",
  "id_token": "eyJhbG...gJVw",
  "refresh_token_expires_in": 69128,
  "expiry_date": 1784300436682
}
```

- `expiry_date` 1784300436682 ms = 2026-07-17T14:00:36 UTC
- Today: 2026-08-05 (token ~19 days expired)
- Refresh grant also revoked (otherwise a clean token-refresh would have succeeded)
- Therefore: `prompt: 'consent'` required to get a fresh `refresh_token`

## hermes mcp login path (does not work)

```bash
$ hermes mcp list
MCP Servers:
  Name             Transport                      Tools        Status
  ──────────────── ────────────────────────────── ──────────── ──────────
  gdrive           /home/ubuntu/work/local-g...   all          ✓ enabled

$ hermes mcp login gdrive
✗ Server 'gdrive' has no URL — not an OAuth-capable server
```

`gdrive` is a local-subprocess MCP (Node `server.js`), not an HTTP/SSE URL transport. `hermes mcp login` requires the latter.

## MCP server discovery

```bash
$ ps auxf | grep -i gdrive | grep -v grep
ubuntu   1270373  0.0  0.1 11884876 154176 ?    Ssl  Aug02   0:03  |       \_ node /home/ubuntu/work/local-gdrive-mcp/server.js
ubuntu   3935152  0.0.1 1168860 130776 ?     Ssl  Jul10   0:16  \_ /usr/bin/node /home/ubuntu/work/local-gdrive-mcp/server.js
```

Two server processes — one started July 10, one August 2. The currently serving one is the August 2 instance, but both read from the same source dir. Source dir confirmed: `/home/ubuntu/work/local-gdrive-mcp/`.

## Existing auth scripts in the MCP directory

```text
/home/ubuntu/work/local-gdrive-mcp/auth_callback.js               (older, broken redirect_uri)
/home/ubuntu/work/local-gdrive-mcp/auth_callback_fixed.js        ← USE THIS
/home/ubuntu/work/local-gdrive-mcp/exchange_gdrive_code.js
/home/ubuntu/work/local-gdrive-mcp/exchange_gdrive_code_fixed.js (manual-code path, no listener)
```

`auth_callback_fixed.js` is the right one — it uses `redirect_uri: 'http://localhost:8085'` which is the registered redirect for this OAuth client.

## OAuth client config

`/home/ubuntu/.config/mcp-gdrive/gcp-oauth.keys.json`:

```json
{
  "installed": {
    "client_id": "977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com",
    "project_id": "...",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "...",
    "redirect_uris": ["http://localhost"]
  }
}
```

Note: the `redirect_uris` list in the OAuth client JSON says `["http://localhost"]`, but the working `auth_callback_fixed.js` uses `http://localhost:8085` and that has been working since the July 17 token was issued. This is suspicious but not blocking — Google accepted it. Do not "fix" the redirect URI to match the JSON literally; doing so would re-break the existing working flow.

## Verified working scope set

The previously-working token had this exact scope string (space-separated):

```
https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file https://www.googleapis.com/auth/userinfo.email https://www.googleapis.com/auth/userinfo.profile openid
```

`auth_callback_fixed.js` requests the same set. Confirmed by reading the script:

```js
scope: [
  'https://www.googleapis.com/auth/drive.readonly',
  'https://www.googleapis.com/auth/drive.file',
  'https://www.googleapis.com/auth/userinfo.email',
  'https://www.googleapis.com/auth/userinfo.profile',
  'openid',
]
```

Do not add `documents` or `spreadsheets` API scopes — those are `invalid_scope` on this client. Drive API export endpoint works under `drive.readonly` for Docs/Sheets/Slides.

## Auth URL reconstruction (handed to the user)

```python
import json, urllib.parse

keys = json.loads(open('/home/ubuntu/.config/mcp-gdrive/gcp-oauth.keys.json').read())
cfg = keys['installed'] or keys['web']
client_id = cfg['client_id']
redirect_uri = 'http://localhost:8085'  # matches auth_callback_fixed.js
scope = ' '.join([
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.file',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
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
auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)
```

Generated URL (2026-08-05):

```
https://accounts.google.com/o/oauth2/auth?client_id=977861670312-8prttldh1prmgf1h0pguld5boa3g022h.apps.googleusercontent.com&redirect_uri=http%3A%2F%2Flocalhost%3A8085&response_type=code&scope=https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.readonly+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fdrive.file+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.email+https%3A%2F%2Fwww.googleapis.com%2Fauth%2Fuserinfo.profile+openid&access_type=offline&prompt=consent&include_granted_scopes=true
```

## Listener launch + verification

```bash
$ cd /home/ubuntu/work/local-gdrive-mcp && node auth_callback_fixed.js &
[+] Server ready on http://localhost:8085

$ ss -tlnp | grep :8085
LISTEN 0  511  *:8085  *:*  users:(("node",pid=3910380,fd=21))

$ curl -sS http://localhost:8085/
Error: Missing code parameter
```

HTTP 400 from the root path confirms the listener is live and the auth callback path is reachable. The redirect will land at `http://localhost:8085/?code=...`, the script will exchange it for tokens, write `TOKEN_PATH`, print `DONE`, and exit.

## Re-probe after redirect

The listener writes `/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json` and exits. The MCP server reads it at request time, so re-probe immediately:

```bash
ls -la /home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json
# mtime should be within the last 30s

# then a fresh tool call — the first one was deferred while the user was clicking.
```

(Re-probe result was not captured in this transcript because the user had not yet clicked at the time the session ended.)

## Pitfalls observed in this session

1. **The first reply punted** with "I don't have a reauth link" and "you need to fix it." The user pushed back: "It's your job to fix it. You have all access. If you can't fix it then you aren't doing your job." The mistake was treating "OAuth needs a browser" as a hard blocker when in fact only the click needs the user; everything else is scriptable.
2. **Node stdout buffering** swallowed the printed auth URL when the process was launched via `terminal(background=true)`. Reconstructing the URL from `gcp-oauth.keys.json` + the script's hardcoded redirect_uri was the workaround.
3. **Two server processes running.** `ps auxf` showed a July 10 process and an August 2 process. Both read from the same source dir, so it didn't matter which one we reauthed against, but it would matter for any setup change that requires a restart.
4. **redirect_uris in `gcp-oauth.keys.json` says `["http://localhost"]`** but the working script uses `http://localhost:8085`. Do not "fix" this — it's been working since July 17 and altering it risks breaking the flow.

## Follow-up: see also

- `references/gdrive-mcp-reauth-2026-08-05b.md` — second session, manual exchange path + on-disk token auto-refresh pitfall + `Aborted (core dumped)` false-positive + `textwrap.dedent` execute_code pitfall.