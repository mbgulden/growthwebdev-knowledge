# Ubersuggest MCP — OAuth Token Refresh (PKCE Flow)

## Token Lifecycle

- Access token lives in `/tmp/ubs_token` (format: `ubs_oauth2_...`)
- Refresh token lives in `/tmp/ubs_refresh` (format: `ubs_oauth2_...`)
- Access token expires ~2 days after issuance (172800s on recent re-auths; was previously ~10 days / 864000s)
- **OAuth scope is the gate, NOT just the tier.** The auth server returns the **scope you requested**, not a fixed `scope: "profile"`. If you ask for `openid email profile` and get back `scope: "profile"`, that means you granted only profile scope — and **every data tool will 403 with "Insufficient scope"**. See "OAuth Scope Controls Tool Access" below for the working scope.
- Refresh token can be used once to get a new access + refresh pair
- After using a refresh token, both the new access AND new refresh tokens are returned

## OAuth Scope Controls Tool Access (verified June 2026)

**Symptom:** `auth_status` returns the right account and a paid tier (e.g. `Tier: tier1`), but `domain_overview`, `keyword_overview`, `serp_analysis`, `competitors`, `backlinks_overview`, `keyword_suggestions`, etc. all return HTTP 403 "Insufficient scope for this endpoint." `search_neilpatel_blog` and `validate_site` still work.

**Root cause:** the OAuth scope you requested was too narrow. With only `openid email profile` (or just `profile`), the token authenticates but the data tools are not authorized.

**Working scope (verified on a `Tier: tier1` lifetime account, June 2026):**

```
profile domain keywords serp backlinks site_audit content
```

**Why this works:** Each scope segment unlocks a category of MCP tools:
- `profile` → `auth_status`, `validate_site`
- `domain` → `domain_overview`, `domain_keywords`, `domain_top_pages`, `domain_top_countries`, `traffic_value`, `competitors`
- `keywords` → `keyword_overview`, `keyword_suggestions`, `keyword_metrics`, `match_keywords`, `google_suggestions`
- `serp` → `serp_analysis`, `estimate_serp_clicks`
- `backlinks` → `backlinks_overview`, `backlinks`, `anchor_texts`, `linking_domains`, `backlink_opportunity`
- `site_audit` → `site_audit`, `site_audit_status`, `site_audit_results`, `site_audit_pages`, `pagespeed_audit`
- `content` → `content_ideas`, `page_shares`, `page_overview`, `page_keywords`

**Tool-tier independence:** Scope determines **whether a tool returns data or 403**. Subscription tier (free / tier1 / tier2 / tier3) determines **how much** (rate limits, data depth, project slots). They are independent — a paid tier with the wrong scope still 403s, and a free-tier-with-right-scope still 403s because the user account has no paid subscription backing the requested scopes. Always request the full scope AND verify `auth_status` shows a paid tier.

**Distinguishing scope bugs from tier ceilings (after the 60-second diagnostic):** If `auth_status` shows tier1 AND `domain_overview` works AND the failing tool is `site_audit`, `traffic_value`, `content_ideas`, `page_shares`, `list_projects`, or `*project_*`, the 403 is **a legitimate tier ceiling, not a scope bug.** Don't re-auth — fix is upgrade ($290 → $490 Business Lifetime) or support ticket if account is misclassified. See `references/ubersuggest-tier-feature-matrix.md` for the full tier × tool grid.

**Quick diagnostic after a re-auth:**
```python
import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

TOKEN = open('/tmp/ubs_token').read().strip()
async def test():
    async with streamable_http_client("https://ubersuggest-mcp.neilpatelapi.com/mcp", headers={"Authorization": f"Bearer {TOKEN}"}) as (r, w, _):
        async with ClientSession(r, w) as session:
            await session.initialize()
            s = await session.call_tool("auth_status", {})
            print(s.content[0].text)  # Must show "Tier: tierX" (paid), not "Tier: free"
            d = await session.call_tool("domain_overview", {"domain": "activeoahutours.com"})
            text = d.content[0].text
            if text.startswith("Error"):
                print("SCOPE STILL BROKEN:", text)
            else:
                print("OK — scope is right, data tools work")
asyncio.run(test())
```

## When to Re-Auth

Run the PKCE flow when:
1. `curl -X POST "https://ubersuggest-mcp.neilpatelapi.com/mcp"` returns `"invalid_token"` with a **502** error
2. `curl -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" -d "grant_type=refresh_token"` returns `"invalid_grant"`
3. The stored token expired and the refresh token is also dead (`invalid_grant`)
4. `auth_status` returns a non-paid tier (free tier users only get `search_neilpatel_blog`)

## Checking Your Tier

After validating the token works, use `auth_status` to see what account you're on and what tier:

```python
r = await session.call_tool("auth_status", {})
print(r.content[0].text)  # e.g. "Logged in as mbgulden@gmail.com\nTier: free"
```

**Paid tier** unlocks: `domain_overview`, `domain_keywords`, `domain_top_pages`, `serp_analysis`, `competitors`, `backlinks_*`, `keyword_suggestions`, `google_suggestions`, `content_ideas`, and all site audit tools — 38 tools total.

**Free tier** only has: `search_neilpatel_blog` + `auth_status`. All other tools return HTTP 403 "Insufficient scope for this endpoint."

If the account shows `Tier: free`, the token is valid but the subscription has lapsed. A token re-auth won't fix this — the account needs a paid Ubersuggest subscription on Neil Patel's website.

**Tier hierarchy warning:** `auth_status` reports a tier label (`tier1`, `tier2`, `free`, etc.) but the label alone doesn't tell you whether data tools work. Historically, an account on `tier1` (Neil Patel's lowest paid tier) **with the wrong OAuth scope** still got HTTP 403 "Insufficient scope" on data tools. The fix is the scope (see "OAuth Scope Controls Tool Access" above), not a tier bump. If `auth_status` shows the correct tier AND you requested the full scope AND `domain_overview` still 403s, then the account genuinely needs a tier bump via support@ubersuggest.com with purchase proof.

Note: `api.ubersuggest.com` (the old REST API) no longer resolves (NXDOMAIN). All calls go through the MCP endpoint.

## The 502 Error Pattern

The token validation endpoint sometimes returns `"Token validation failed: 502"`. This is a backend error on Neil Patel's auth server — the server tried to validate the token against an upstream identity provider and got a 502 back. This can be:
- A transient Neil Patel backend issue (retry later)
- A genuinely expired/revoked token (run PKCE re-auth)

Distinguish by: if the token is <10 days old and was working recently, retry. If consistent over multiple attempts, the token is dead.

## PKCE Re-Auth Flow

### Step 1 — Generate PKCE verifier and challenge

```python
import base64, hashlib, os, urllib.parse

verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode()
challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()

# Save verifier for later code exchange
open("/tmp/ubs_pkce_verifier", "w").write(verifier)
```

### Step 2 — Build and present the authorization URL

```python
CLIENT_ID = "ubersuggest-mcp"
REDIRECT_URI = "https://ubersuggest-mcp.neilpatelapi.com/callback"
# CRITICAL: must include all data-tool scopes, not just openid/email/profile.
# Wrong scope here → 403 on every data tool. See "OAuth Scope Controls Tool Access" above.
SCOPE = "profile domain keywords serp backlinks site_audit content"

params = {
    "response_type": "code",
    "client_id": CLIENT_ID,
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    "code_challenge": challenge,
    "code_challenge_method": "S256",
    "access_type": "offline",
    # login_hint pre-fills the email field on the auth page so the user
    # doesn't have to type it on mobile — also reduces the chance of them
    # accidentally authorizing the wrong account.
    "login_hint": "USER_EMAIL_HERE",
    # prompt=login forces a fresh login screen — important if the user's
    # browser has a cached session that would reissue the same auth code
    # (see the parent skill's Pitfalls section: "OAuth cached-session
    # cache-buster (prompt=login)").
    "prompt": "login",
}

url = f"https://ubersuggest-mcp.neilpatelapi.com/authorize?{urllib.parse.urlencode(params)}"
```

The user opens this URL in their browser, logs in with their Neil Patel/Ubersuggest account, and grants access. They are redirected to a URL like:

```
https://ubersuggest-mcp.neilpatelapi.com/callback?code=xxxxx&state=yyyyy
```

### Step 3 — Exchange code for tokens

Extract the `code` parameter from the callback URL and exchange:

```bash
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=<CODE_FROM_CALLBACK>" \
  -d "client_id=ubersuggest-mcp" \
  -d "code_verifier=$(cat /tmp/ubs_pkce_verifier)" \
  -d "redirect_uri=https://ubersuggest-mcp.neilpatelapi.com/callback"
```

Response includes:
```json
{
  "access_token": "ubs_oauth2_...",
  "refresh_token": "ubs_oauth2_...",
  "expires_in": 864000,
  "token_type": "Bearer"
}
```

### Step 4 — Save tokens

```bash
echo "ubs_oauth2_ACCESS_TOKEN" > /tmp/ubs_token
echo "ubs_oauth2_REFRESH_TOKEN" > /tmp/ubs_refresh
```

## Token Refresh (Proactive, Before Expiry)

If the refresh token is still valid but the access token is near expiry:

```bash
REFRESH=$(cat /tmp/ubs_refresh)
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token" \
  -d "client_id=ubersuggest-mcp" \
  -d "refresh_token=$REFRESH"
```

This returns a new `access_token` and `refresh_token`. Save both.

## Verification

After saving new tokens, test:

```python
import asyncio, json
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

TOKEN = open('/tmp/ubs_token').read().strip()
async def test():
    async with streamable_http_client(
        "https://ubersuggest-mcp.neilpatelapi.com/mcp",
        headers={"Authorization": f"Bearer {TOKEN}"}
    ) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("domain_overview", {"domain": "activeoahutours.com"})
            data = json.loads(result.content[0].text)
            print(f"DA {data.get('domainAuthority')}, {data.get('organic')} organic keywords")

asyncio.run(test())
```

## Pitfall — JWT Token Truncation in Display (Wastes a Re-Auth)

**Symptom observed (June 2026 re-auth):** A successful `curl POST /token` returns a real JWT like `ubs_oauth2_zj3nZQrqRaeG3UHgNf84gzaSZvzsQdqzTdiMLMIbh2` — three dot-separated segments (header.payload.signature). But when that token is echoed via `echo $TOKEN` or `cat /tmp/ubs_token` inside the same shell session, the display collapses the dots and renders the token as the literal string `ubs_oa...XXXX` (with the truncated middle). If you then `echo $TOKEN > /tmp/ubs_token`, the **file ends up containing the literal `ubs_oa...XXXX`** (53 bytes including the ellipsis), not the real token. Every subsequent MCP call returns 401 invalid_token, and the user thinks they're connected.

**Root cause:** Some shell/terminal rendering layers (bash word-wrap on long tokens, certain output formatters) collapse sequences of dots or punctuation when displaying long strings, and that mangled display is what gets piped/written if the operator trusts the screen output over the actual JSON file.

**Verification:** The real tokens are 50-60 characters containing **real dots** that segment the JWT. The fake `ubs_oa...XXXX` form is 13-16 characters with a literal `...` in the middle. Always inspect the source-of-truth JSON file before declaring success.

**Safe-write pattern (use this every time, no exceptions):**

```bash
# Step 3 — capture FULL response to file FIRST, then parse with Python
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "code=$CODE" \
  --data-urlencode "client_id=ubersuggest-mcp" \
  --data-urlencode "code_verifier=$VERIFIER" \
  --data-urlencode "redirect_uri=https://ubersuggest-mcp.neilpatelapi.com/callback" \
  -o /tmp/ubs_token_response.json

# Parse with Python (NOT shell) — JSON has real dots that display layers mangle
python3 << 'EOF'
import json
with open('/tmp/ubs_token_response.json') as f:
    r = json.load(f)
if 'access_token' not in r:
    print("ERROR:", r); raise SystemExit(1)
with open('/tmp/ubs_token', 'w') as f:
    f.write(r['access_token'])
with open('/tmp/ubs_refresh', 'w') as f:
    f.write(r['refresh_token'])
# Sanity-check the saved tokens. Current Ubersuggest tokens are opaque strings
# like `ubs_oauth2_...`; older notes expected JWT dots, but dot-free opaque
# tokens are valid as long as they are long enough and not display-mangled.
for label, val in [('access', r['access_token']), ('refresh', r.get('refresh_token', ''))]:
    assert len(val) > 40, f"{label} token suspiciously short: {val!r}"
    assert '...' not in val, f"{label} token contains literal '...' — got mangled: {val!r}"
    assert val.startswith('ubs_oauth2_'), f"{label} token has unexpected prefix: {val[:12]!r}"
print("OK — tokens saved, lengths:", len(r['access_token']), len(r['refresh_token']))
EOF
```

**Verification before declaring success:**

```bash
wc -c /tmp/ubs_token /tmp/ubs_refresh    # both should be 50-60 bytes
python3 -c "
for p in ['/tmp/ubs_token', '/tmp/ubs_refresh']:
    t = open(p).read()
    assert '...' not in t, f'{p} contains literal ellipsis — mangled'
    assert '.' in t, f'{p} missing JWT dots — truncated'
print('OK')
"
```

**Apply the same safe-write pattern when refreshing, not just first-time PKCE:**

```bash
curl -s -X POST "https://ubersuggest-mcp.neilpatelapi.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=refresh_token" \
  --data-urlencode "client_id=ubersuggest-mcp" \
  --data-urlencode "refresh_token=$(cat /tmp/ubs_refresh)" \
  -o /tmp/ubs_refresh_response.json
# Then parse + assert the same way as above.
```

**Why this matters:** If the saved token file ends up with `ubs_oa...XXXX` (literal ellipsis), every subsequent MCP call returns 401/invalid_token. The user thinks they're connected, you think you're connected, and the first sweep silently fails. Always assert `len > 40`, no literal `...`, AND that real dots are present, before reporting success.
