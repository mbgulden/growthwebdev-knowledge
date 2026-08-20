# gdrive MCP reauth session transcript — 2026-08-05 (second pass)

This is the second session exercising the `local-mcp-token-reauth` recipe in a
single day. The first reauth (~1 hour earlier) followed the recipe as written.
This second pass surfaced one pitfall the SKILL.md already covers in step 10,
but the failure mode was subtle enough to deserve a transcript.

## What was different this session

About 1 hour after the first reauth, I attempted to upload 6 markdown reports
to Drive via direct `urllib` calls (not via the MCP tools). All 6 returned
HTTP 401 with `Invalid Credentials`. The MCP tools (`mcp_gdrive_drive_about`)
still worked — they returned my account info cleanly.

## Why the asymmetry

The MCP server has an `OAuth2` client with an `on('tokens', ...)` event
handler that auto-refreshes the access token transparently when any MCP tool
call fires. The `mcp_gdrive_drive_about` call triggered that refresh under
the hood, so the MCP layer was working with a fresh access_token.

My direct `urllib` calls read the **on-disk** `access_token` from
`~/.config/mcp-gdrive/.gdrive-server-credentials.json`. That file was last
written during the first reauth (~1 hour ago), so its `expiry_date` had
passed. Direct API calls fail because the file is not auto-refreshed.

## The fix (verbatim from SKILL.md step 10)

Refresh the access_token directly using the on-disk refresh_token:

```python
import json, urllib.request, urllib.parse, time

tok = json.loads(open('/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json').read())
keys = json.loads(open('/home/ubuntu/.config/mcp-gdrive/gcp-oauth.keys.json').read())
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
json.dump(tok, open('/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json', 'w'), indent=2)
```

After refresh, all 6 uploads succeeded. The MCP tools also benefit (the next
MCP call would have refreshed anyway, but now the on-disk file is consistent
with whatever the MCP layer is using).

## When to use step 10

- **Always**, if more than ~50 minutes have passed since the last reauth and
  you intend to make direct API calls (uploads, multipart, anything that
  bypasses the MCP).
- **Always**, in batch operations where >1 hour may elapse across the batch.
  Refresh once before the batch, not per item.
- **Not needed** if you only use MCP tool calls (`mcp_gdrive_*`) — those
  trigger auto-refresh on every call.

## Why this isn't caught in step 1–9

The reauth flow (steps 1–9) is about *getting a working token back*. The
direct-API-call refresh (step 10) is about *keeping the on-disk token in
sync with what the MCP layer uses*. They're different lifecycles:
- Step 8: token reauth → write a fresh access_token (1-hour lifetime)
- Step 10: token refresh → bump the access_token within that 1-hour window
  using the long-lived refresh_token

A single reauth is enough to get unstuck from `invalid_grant`, but batch
direct-API work across more than ~1 hour requires step 10 between batches.

## Diagnostic check before any direct-API batch

```python
import json, time
t = json.loads(open('/home/ubuntu/.config/mcp-gdrive/.gdrive-server-credentials.json').read())
now = int(time.time() * 1000)
exp = t.get('expiry_date', 0)
remaining_min = (exp - now) / 1000 / 60
print(f'access_token expires in {remaining_min:.1f} min')
print(f'{"OK to use directly" if remaining_min > 5 else "REFRESH FIRST (step 10)"}')
```

If `remaining_min < 5`, refresh before the batch. If you skip this and the
batch fails partway through, you'll waste the API calls you've already made
on the failures.