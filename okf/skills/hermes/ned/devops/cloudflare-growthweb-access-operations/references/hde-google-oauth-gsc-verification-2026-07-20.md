# HDE Google OAuth + Search Console verification — 2026-07-20

## When this matters
Use this when HDE/`humandesignengine.com` Google-stack work is blocked on GA4/GTM/Search Console/Site Verification auth or ownership.

## Durable lesson
Do not equate any one Google auth surface with all Google API readiness:

- Kai/AGY Google login can work while reusable GA4/GTM/GSC OAuth is still missing.
- `gcloud` ADC can have only `webmasters` while missing Analytics Admin, Tag Manager, and Site Verification scopes.
- A correctly scoped OAuth token can still fail until the Google Cloud project has the relevant APIs enabled.
- Search Console can list a property as `siteUnverifiedUser`; sitemap reads/submits require `siteOwner`.

## Working OAuth flow
Repo/script used:

```bash
cd /home/ubuntu/work/hd-platform-GRO-3988
python3 scripts/google-oauth-scope-flow.py url
python3 scripts/google-oauth-scope-flow.py exchange --code '<returned-code-or-localhost-url>'
python3 scripts/google-oauth-scope-flow.py verify
```

Default token path:

```text
/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json
```

Required scopes verified:

```text
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/tagmanager.edit.containers
https://www.googleapis.com/auth/tagmanager.manage.accounts
https://www.googleapis.com/auth/tagmanager.readonly
https://www.googleapis.com/auth/webmasters
https://www.googleapis.com/auth/siteverification
```

## API enablement blocker
After OAuth exchange succeeded, live API probes returned API-disabled 403s for project `772364335560`. Michael enabled:

```text
analyticsadmin.googleapis.com
tagmanager.googleapis.com
searchconsole.googleapis.com
siteverification.googleapis.com
```

After enablement, probes succeeded:

- Analytics Admin: OK, existing GA4 property `Human Design Engine - GA4` / `properties/541395071` under Growth Web Development.
- Tag Manager: OK, but no HDE GTM container was present; only Pacific Aviation Museum and Active Oahu Tours accounts were listed.
- Search Console: OK.
- Site Verification: OK.

## Search Console verification path
Generated DNS TXT token via Site Verification API for:

```text
site.type=INET_DOMAIN
site.identifier=humandesignengine.com
verificationMethod=DNS_TXT
```

Then, after explicit user approval, added the root TXT record in Cloudflare using the GrowthWeb global-key API shape from `/home/ubuntu/cf_setup_staging.py`. Verify DNS without printing the token:

```bash
dig +short TXT humandesignengine.com @1.1.1.1 | sed -E 's/google-site-verification=[A-Za-z0-9_-]+/google-site-verification=[REDACTED]/g'
dig +short TXT humandesignengine.com @8.8.8.8 | sed -E 's/google-site-verification=[A-Za-z0-9_-]+/google-site-verification=[REDACTED]/g'
```

Site Verification API result became:

```text
SITE_VERIFICATION_STATUS=OK
id=dns://humandesignengine.com
owners=["mbgulden@gmail.com"]
```

Search Console `sites.list` then showed:

```json
{"siteUrl":"https://humandesignengine.com/","permissionLevel":"siteOwner"}
```

## Sitemap submission
Live `robots.txt` advertised:

```text
Sitemap: https://humandesignengine.com/sitemap.xml
```

The real sitemap URL returned `200 application/xml`; nearby guessed sitemap-index URLs returned the site HTML shell and should not be submitted.

Submit exact sitemap:

```text
PUT https://www.googleapis.com/webmasters/v3/sites/{urlencoded https://humandesignengine.com/}/sitemaps/{urlencoded https://humandesignengine.com/sitemap.xml}
```

Verified result:

```text
SITEMAP_SUBMIT_STATUS=HTTP_204
SITEMAP_LIST_COUNT=1
lastSubmitted=2026-07-20T23:43:02.776Z
isPending=true
errors=0
warnings=0
```

## Pitfalls
- If `google-oauth-scope-flow.py exchange` gets a malformed auth code from a localhost URL lacking scheme, retry with just the `code=` value.
- Do not print access tokens, refresh tokens, client secrets, or full verification tokens in chat/log summaries.
- Creating Cloudflare DNS records is an infrastructure change; ask for explicit approval before adding the TXT record.
- API-enabled and scope-valid is not enough for sitemap work; verify `permissionLevel=siteOwner` before submitting/reading sitemaps.
