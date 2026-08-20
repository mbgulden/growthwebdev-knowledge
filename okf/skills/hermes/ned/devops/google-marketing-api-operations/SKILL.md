---
name: google-marketing-api-operations
description: Use when diagnosing or setting up Google Analytics Admin, Google Tag Manager, Search Console, or Site Verification API access for HDE/SEO/marketing-stack work. Distinguishes Google account/UI ownership, AGY Google auth, gcloud ADC, reusable OAuth tokens, granted scopes, quota/API enablement, and live API probes.
---

# Google Marketing API Operations

## When to use

Use this skill when work depends on any of these Google services:

- Google Analytics / GA4 Admin API
- Google Tag Manager API
- Google Search Console / Webmasters API
- Google Site Verification API
- SEO/indexing audits where Search Console or sitemap submission is needed
- HDE or site-wide Google stack registration work

## Core rule

Do not collapse all “Google auth” into one green/red state. These layers are separate:

| Layer | What it proves | What it does **not** prove |
|---|---|---|
| AGY/Antigravity Google login | AGY can talk to Google/Gemini as a user | GA4/GTM/GSC/Site Verification API mutation scopes |
| `gcloud auth list` | CLI user account exists | Application Default Credentials or required scopes |
| ADC token | Google API client can refresh a token | Required marketing scopes or API enablement |
| Reusable authorized-user token | Scriptable refresh token exists | The Google Cloud project APIs are enabled |
| `tokeninfo` scopes | OAuth consent granted required scopes | Account has property/container ownership |
| Live API probes | Real API is usable | That the desired site/property/container has already been configured |

## Required scopes for full GA4/GTM/GSC/Site Verification work

```text
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/tagmanager.edit.containers
https://www.googleapis.com/auth/tagmanager.manage.accounts
https://www.googleapis.com/auth/tagmanager.readonly
https://www.googleapis.com/auth/webmasters
https://www.googleapis.com/auth/siteverification
```

For a narrower Search Console-only task, `webmasters` / `webmasters.readonly` may be enough. Do not claim the full Google stack is ready from Search Console-only scopes.

## Standard workflow

1. **Find existing credentials without printing secrets**
   - Check metadata/paths only: file existence, permissions, type, scope summaries.
   - Never print access tokens, refresh tokens, client secrets, API keys, or full credential JSON.

2. **Check which auth layer exists**
   - AGY smoke tests are useful but only prove AGY auth.
   - Check ADC location(s), profile-specific home directories, and any project-specific reusable token path.
   - Verify scopes with token refresh + `tokeninfo`; report only email, scopes present/missing, quota project, and credential path.

3. **If scopes are missing, generate a consent URL**
   - Prefer a repeatable project script when present.
   - Include the **full raw URL in a text/code block**, not only a Markdown link; mobile clients may truncate or hide query parameters.
   - Instruct Michael to return the failed `localhost/?code=...` redirect or just the `code=` value.

4. **Exchange and verify the code immediately**
   - Exchange the code into a non-git token path.
   - Ensure token file permissions are private, e.g. `0600`.
   - Run a verify command that refreshes the token and confirms no required scopes are missing.

5. **Probe APIs, not just OAuth**
   - Probe Analytics Admin, Tag Manager, Search Console, and Site Verification endpoints with the new token.
   - If probes return API-disabled 403s, OAuth is good but the Google Cloud project needs services enabled.
   - Provide exact Google Console API enablement links for the project ID.

6. **Only then continue site registration/configuration**
   - Do not claim GA/GTM/GSC/Site Verification registration is complete until live API calls succeed and the target property/container/site IDs are verified.

## Reporting pattern

```md
🟡 Google auth partially ready

**Good**
- OAuth token saved at `<path>` with `0600` permissions.
- Required scopes present: `<scope summary>`

**Blocked**
- `<API>` returned HTTP 403 API disabled for project `<project>`.

**Needed**
- Enable: `<full console URL>`

**Next Step**
- After APIs are enabled, rerun live probes and register/verify the site-wide Google stack.
```

## Pitfalls

- Do not say “Google auth is all there” just because AGY can authenticate as the account.
- Do not say “Search Console is blocked by OAuth” when the token has the right scope but the quota/client project API is disabled.
- Do not use API keys for Search Console/Analytics Admin/Tag Manager mutation; these APIs require OAuth.
- Do not hide a consent URL behind only Markdown link formatting when Michael asks for an auth link; provide the complete raw URL.
- Do not print tokens or full credential JSON into chat or logs.
- If the user gives a `localhost/?code=...` redirect and the exchange script rejects it as malformed, retry with only the extracted `code` value before declaring failure.
- **Two Google credential kinds, not one.** A Google credentials JSON file may be either `service_account` (private-key JWT assertion grant) or `authorized_user` (refresh_token grant). The PWP `GoogleClient` handles both: it sets `_creds_kind` based on `type` and branches at `_access_token()` time. Service-account needs `client_email` + `private_key`; authorized_user needs `client_id` + `client_secret` + `refresh_token`. If you see a credentials JSON with `type: "authorized_user"`, that is the gcloud ADC shape (`application_default_credentials.json`) and it works through the OAuth `grant_type=refresh_token` flow, NOT the JWT-bearer flow.
- **OAuth refresh_token `invalid_grant` is a known failure mode.** The gcloud ADC file may carry a refresh_token whose underlying grant has been revoked (rotated client secret, expired scope consent, etc.). Symptom: HTTP 400 from `https://oauth2.googleapis.com/token` with `{"error":"invalid_grant", "error_description":"Bad Request"}`. The fix is `gcloud auth application-default login --scopes=<full-scope-list>` to mint a fresh grant. Do not try to debug this further without re-running the login flow first; the refresh_token itself is opaque.
- **`GoogleClient._load_service_account()` returning `None` vs raising.** When no `GOOGLE_SA_JSON` / `GOOGLE_SA_INLINE` env vars are set, the loader returns `None` rather than raising. Callers (`from_env`) must check and fall back to `auth_loader.get_secret("google_adc")` for the gcloud ADC. If a `GoogleAuthError` from this fallback path says "No Google credentials found", that means auth_loader also returned nothing — usually because the active Hermes profile has no `home/.config/gcloud/application_default_credentials.json` and no project-level `.env` set `GOOGLE_APPLICATION_CREDENTIALS`.

## References

- `references/2026-07-hde-google-oauth-ga4-gtm-gsc.md` — HDE session pattern: Kai AGY auth vs reusable Google marketing OAuth, full-scope consent URL, code exchange, token verification, and API-disabled project blocker.
- `references/2026-07-pwp-google-client-service-account.md` — Operational client pattern from the 2026-07-29 PWP `provision_site` Phase 2 work: ~30 lines of stdlib `cryptography` for service-account JWT signing, token caching, `GOOGLE_SA_JSON` / `GOOGLE_SA_INLINE` env-var precedence, GA4 property + web-stream API call shapes, GTM container API call shape, and what live-test credentials would be needed to exercise GA4/GTM end-to-end.
