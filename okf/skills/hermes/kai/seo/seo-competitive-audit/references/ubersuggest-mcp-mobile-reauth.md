# Ubersuggest MCP — Mobile Re-Auth Quick Reference

Condensed, mobile-first re-auth checklist. Pairs with the longer
`references/ubs-token-refresh-pkce.md` (which is the full PKCE-flow
walkthrough). Use this one when you're on Telegram with Michael and need
to re-auth fast.

## TL;DR (the 60-second version)

1. Generate verifier + challenge (Python one-liner, below).
2. Send auth URL with `scope=profile domain keywords serp backlinks site_audit content`, `login_hint=USER_EMAIL`, `prompt=login`.
3. User taps link on phone → logs in → approves → browser redirects to `/callback?code=XXXX`.
4. User pastes the **full callback URL**.
5. Extract `code`, exchange with `curl -o /tmp/ubs_token_response.json`.
6. Parse with Python (NOT shell — JWT dots get mangled into `...`), save to `/tmp/ubs_token` + `/tmp/ubs_refresh`.
7. Verify: `auth_status` shows paid tier AND `domain_overview` returns real data (not 403).

## The 3 most common failure modes (in order of frequency)

### 1. Wrong OAuth scope → 403 on every data tool

**Symptom:** `auth_status` returns `"Tier: tier1"` but `domain_overview`,
`keyword_overview`, `serp_analysis`, etc. all return `HTTP 403 Insufficient scope`.

**Fix:** Re-auth with the correct scope (see SKILL.md "Critical: OAuth scope"
section). The MCP backend gates each tool category behind a scope segment.

### 2. Cached browser session → same `code=` value sent back

**Symptom:** User sends back a callback URL with the same `code=XXXXX` value
as a previous attempt. Token exchange fails with `invalid_request`.

**Fix:** Add `&prompt=login` to the auth URL. Forces fresh login screen.
If that still fails, ask user to open in incognito.

### 3. JWT dots get truncated in shell display → file contains literal `ubs_oa...XXXX`

**Symptom:** Token file looks correct in shell echo, but every MCP call
returns 401 invalid_token. The `/tmp/ubs_token` file actually contains
`ubs_oa...9ytj` (with literal `...` and only 13-16 chars total).

**Fix:** Always write tokens via `curl -o response.json`, then parse with
Python and assert `len > 40`, no literal `...`, AND real dots are present.
Full safe-write pattern in `references/ubs-token-refresh-pkce.md`.

## Mobile-specific notes (this differs from most OAuth flows)

Unlike Google OAuth, the Ubersuggest MCP redirect target is
**server-handled** (`https://ubersuggest-mcp.neilpatelapi.com/callback`),
NOT a localhost loopback. So on Michael's phone:

- The redirect succeeds normally — no "address-bar trick" needed.
- User copies the full callback URL from address bar and sends back.
- Phone browser never needs to reach a localhost port.

This contrasts with the `google-api-setup` skill's "phone-only user cannot
accept loopback redirects" pitfall. Ubersuggest MCP is friendlier here.

## Tier-label sanity check

`auth_status` returns one of `free / tier1 / tier2 / tier3`. For lifetime
purchases, the tier label matches the plan name on Neil Patel's pricing
page:

| Tier label | Plan | Lifetime price |
|---|---|---|
| `tier1` | Individual | $290 |
| `tier2` | Business | $490 |
| `tier3` | Enterprise / Agency | $990 |

If the tier label disagrees with what was paid for, that's a real
support-ticket case. If it agrees, the label is correct — `tier1`
genuinely doesn't unlock `site_audit*`, `traffic_value`, `content_ideas`,
`page_shares`, or `*project_*` tools. Those are tier2+ features.
See `references/ubersuggest-tier-feature-matrix.md`.

## Copy-paste: PKCE verifier generator

```python
import base64, hashlib, os, urllib.parse

verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode()
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()

with open('/tmp/ubs_pkce_verifier', 'w') as f:
    f.write(verifier)

params = {
    "response_type": "code",
    "client_id": "ubersuggest-mcp",
    "redirect_uri": "https://ubersuggest-mcp.neilpatelapi.com/callback",
    "scope": "profile domain keywords serp backlinks site_audit content",
    "code_challenge": challenge,
    "code_challenge_method": "S256",
    "access_type": "offline",
    "login_hint": "USER_EMAIL_HERE",
    "prompt": "login",
}

print(f"https://ubersuggest-mcp.neilpatelapi.com/authorize?{urllib.parse.urlencode(params)}")
```

## Copy-paste: safe token capture + verify

```bash
CODE="<paste code from callback URL>"
VERIFIER=$(cat /tmp/ubs_pkce_verifier)
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=ubersuggest-mcp" \
  --data-urlencode "code_verifier=$VERIFIER" \
  --data-urlencode "redirect_uri=https://ubersuggest-mcp.neilpatelapi.com/callback" \
  -o /tmp/ubs_token_response.json

python3 << 'EOF'
import json
r = json.load(open('/tmp/ubs_token_response.json'))
if 'access_token' not in r:
    print("ERROR:", r); raise SystemExit(1)
open('/tmp/ubs_token', 'w').write(r['access_token'])
open('/tmp/ubs_refresh', 'w').write(r['refresh_token'])
# Sanity-check the saved tokens. Current Ubersuggest tokens are opaque
# `ubs_oauth2_...` strings; they may be dot-free and still valid.
for label, val in [('access', r['access_token']), ('refresh', r['refresh_token'])]:
    assert len(val) > 40, f"{label} suspiciously short: {val!r}"
    assert '...' not in val, f"{label} contains literal '...' — got mangled: {val!r}"
    assert val.startswith('ubs_oauth2_'), f"{label} unexpected prefix: {val[:12]!r}"
print(f"OK — scope: {r.get('scope')}, expires_in: {r.get('expires_in')}s")
EOF
```

## Copy-paste: verify connection works

```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

TOKEN = open('/tmp/ubs_token').read().strip()

async def main():
    async with streamablehttp_client(
        "https://ubersuggest-mcp.neilpatelapi.com/mcp",
        headers={"Authorization": f"Bearer {TOKEN}"},
    ) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()

            # Auth status
            s = await session.call_tool("auth_status", {})
            print(s.content[0].text)  # Should show paid tier

            # Domain overview smoke test
            d = await session.call_tool("domain_overview", {"domain": "activeoahutours.com"})
            text = d.content[0].text
            if text.startswith("Error") or "Insufficient" in text:
                print("FAIL — scope or tier problem:", text[:200])
            else:
                print("OK — domain_overview returned data")

asyncio.run(main())
```