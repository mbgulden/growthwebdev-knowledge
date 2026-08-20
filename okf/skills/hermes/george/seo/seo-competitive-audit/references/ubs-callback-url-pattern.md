# Ubersuggest OAuth — Callback URL Pattern (vs OOB)

## What Happens in Practice

The Ubersuggest MCP OAuth flow supports two redirect outcomes:

### 1. OOB Code Display (documented)

When using `redirect_uri=urn:ietf:wg:oauth:2.0:oob`, Google shows a plain page with the authorization code displayed in a text box. User copies the code and pastes it back.

### 2. Direct Callback Redirect (observed)

When the authorization server redirects the browser **before** the code reaches the OOB page, the user lands on:

```
https://ubersuggest-mcp.neilpatelapi.com/callback?code=<CODE>&state=<STATE>
```

The code is in the URL query string, not on a displayed page. The user can:
- Copy the full callback URL from the browser address bar
- Extract the `code=` parameter value
- Send either the code value or the full URL back

This happened in practice during the June 2026 re-auth session — the Ubersuggest server redirected directly to its own `/callback` endpoint with the code in the URL. The user sent the full URL, and the code was extracted from it.

## How to Handle

When you send the user an auth URL and they reply with what looks like a callback URL (not a bare code):

```python
# User sends: "https://ubersuggest-mcp.neilpatelapi.com/callback?code=XXXX&state=YYY"
import urllib.parse
callback_url = "https://ubersuggest-mcp.neilpatelapi.com/callback?code=XXXX&state=YYY"
parsed = urllib.parse.urlparse(callback_url)
params = urllib.parse.parse_qs(parsed.query)
code = params.get('code', [None])[0]
# code == "XXXX" — proceed with token exchange
```

## Why This Matters

- The callback URL pattern works in ALL browsers (including Safari, which blocks `urn:ietf:wg:oauth:2.0:oob`)
- No need for OOB workarounds or local callback servers
- The code is single-use — extract it immediately and exchange for a token
- Save the resulting token to `/tmp/ubs_token` (or the configured path) before confirming to the user

**Watch out:** After extracting the code, do the token exchange with the safe-write pattern in `references/ubs-token-refresh-pkce.md` — bash variable interpolation can mangle JWT dots into literal `...`, corrupting the saved token. The code is single-use, so a corrupted save wastes the user's re-auth.

## Same Code Twice = Cached Browser Session (Symptom & Fix)

**Symptom observed (June 2026):** The user sent back `code=42f8wcgLcby0imxDNom5b1gYdbEh5G3DgB4TlVUtzQtXdJHI` twice in a row, even after I generated a fresh authorization URL with a new PKCE verifier. The second exchange then failed with HTTP 400 `{"error":"invalid_request"}` because the code was already consumed by the first exchange AND it was issued for the previous (now-replaced) verifier.

**Root cause:** The user's mobile browser cached the previous OAuth session. When they tapped my new auth URL, the browser served the cached login state instead of showing a fresh login screen, so the OAuth server happily returned the same `code=` value tied to the previous PKCE challenge.

**Diagnostic check before declaring "cached session":**
```bash
# After a failed exchange, compare the verifier you used to the verifier in /tmp/ubs_pkce_verifier
USED_VERIFIER=$(echo "$USED_VERIFIER_HERE")
SAVED_VERIFIER=$(cat /tmp/ubs_pkce_verifier)
if [ "$USED_VERIFIER" != "$SAVED_VERIFIER" ]; then
    echo "MISMATCH — code was issued for a different verifier. Cached session."
fi
```

**Fixes (in order of escalation):**
1. Make sure the auth URL includes `&prompt=login` — forces a fresh login screen.
2. If the user is on a phone, ask them to open the URL in **incognito/private browsing** mode.
3. If still failing, ask them to try a different browser (Chrome → Safari or vice versa).
4. Last resort: have them clear browser cookies for `ubersuggest-mcp.neilpatelapi.com` and `neilpatel.com`.

**Note for `prompt=login`:** It forces a new login screen but does NOT force a new code in every browser implementation. If `prompt=login` is in the URL and you still get the same `code=`, the session is sticky at the OAuth server level and you need the incognito/different-browser fallback.
