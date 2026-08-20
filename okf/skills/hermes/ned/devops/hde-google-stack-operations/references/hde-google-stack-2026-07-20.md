# HDE Google Stack Session Notes — 2026-07-20

## Context
Michael asked Ned to continue the HDE Google-stack cleanup after a prior audit reported partial/missing Google registration, GTM absence, Search Console blocked by missing OAuth, and SEO/indexing gaps.

## Durable lessons

- When Michael says Google auth exists in Kai, inspect Kai/profile credential sources first before issuing a new auth link.
- Do not equate auth layers: AGY Google auth, gcloud ADC, reusable OAuth API credentials, API enablement, Search Console ownership, and GTM publish rights are separate gates.
- Do not report “Google stack fixed” from OAuth alone. Report each layer: OAuth scopes, API enablement, GSC ownership, sitemap state, GA4 property/stream, GTM container/tag, GTM version publish, site code/build/deploy verification.
- For HDE code edits, rerun `npm run build` after the final source change/commit-facing state and then run a rendered HTML coverage check. A prior build before the last touched files is not enough.

## Credential/source locations checked

- Kai profile gcloud files: `/home/ubuntu/.hermes/profiles/kai/home/.config/gcloud/`
- HDE OAuth helper script: `/home/ubuntu/work/hd-platform-GRO-3988/scripts/google-oauth-scope-flow.py`
- OAuth client secrets: `/home/ubuntu/mounts/synology-photo/Antigravity/credentials.json`
- HDE reusable token path: `/home/ubuntu/.config/hde-google-oauth/analytics-tagmanager-searchconsole.json`
- Cloudflare zone credential shape: `/home/ubuntu/cf_setup_staging.py` (`X-Auth-Email` + `X-Auth-Key`; never print key)

## OAuth scope progression

The first broad scope set allowed GTM account/container/tag edits but failed at container versioning:

```text
ACCESS_TOKEN_SCOPE_INSUFFICIENT
method=CreateContainerVersion
required scope=tagmanager.edit.containerversions
```

Publishing also requires:

```text
tagmanager.publish
```

Use the expanded scope set in SKILL.md for future full HDE Google-stack work.

## APIs enabled

Michael enabled these Google services for project `772364335560` after probes returned API-disabled 403s:

- `analyticsadmin.googleapis.com`
- `tagmanager.googleapis.com`
- `searchconsole.googleapis.com`
- `siteverification.googleapis.com`

After enablement, probes succeeded for Analytics Admin, Tag Manager, Search Console, and Site Verification.

## Search Console / Site Verification results

Before DNS verification:

```json
{"siteUrl":"https://humandesignengine.com/","permissionLevel":"siteUnverifiedUser"}
```

Ned generated a Site Verification DNS TXT token, added it to Cloudflare after Michael approved the infrastructure change, verified public DNS via `1.1.1.1` and `8.8.8.8`, then called Site Verification API.

Cloudflare record evidence:

```text
DNS_TXT_STATUS=created
record_id=7d26294a52267896b23a86e53ecd6a5b
ttl=120
google_verification_present=True
```

Google verification evidence:

```text
SITE_VERIFICATION_STATUS=OK
id=dns://humandesignengine.com
owners=["mbgulden@gmail.com"]
```

After verification:

```json
{"siteUrl":"https://humandesignengine.com/","permissionLevel":"siteOwner"}
```

## Sitemap results

Robots advertised:

```text
Sitemap: https://humandesignengine.com/sitemap.xml
```

`https://humandesignengine.com/sitemap.xml` returned `200 application/xml`. Common alternates like `/sitemap-index.xml` and `/sitemap-0.xml` returned HTML shell, so do not submit those.

Sitemap submission evidence:

```text
SITEMAP_SUBMIT_STATUS=HTTP_204
SITEMAP_LIST_COUNT=1
```

Immediate sitemap state:

```json
{
  "path": "https://humandesignengine.com/sitemap.xml",
  "lastSubmitted": "2026-07-20T23:43:02.776Z",
  "lastDownloaded": null,
  "isPending": true,
  "errors": "0",
  "warnings": "0"
}
```

## GA4 baseline

Analytics Admin listed the HDE GA4 property under Growth Web Development:

```text
account=accounts/219535370
accountDisplayName=Growth Web Development
property=properties/541395071
displayName=Human Design Engine - GA4
```

Data stream:

```text
properties/541395071/dataStreams/15058763159
Human Design Engine Web
WEB_DATA_STREAM
https://humandesignengine.com
measurementId=G-Q6TPL08VM7
```

## GTM baseline and completed setup

Existing visible GTM accounts before HDE creation:

```text
accounts/10325987 Pacific Aviation Museum -> GTM-PNWWQK
accounts/10319161 Active Oahu Tours -> GTM-P55TSP
```

The HDE repo/source referenced `GTM-M5K8WRP`, but Tag Manager lookup returned `404 Not found or permission denied`. Treat that old ID as not green.

Ned created a new HDE container under the Active Oahu Tours account:

```text
name=Human Design Engine
publicId=GTM-TLC3H7XV
path=accounts/10319161/containers/258884256
domainName=humandesignengine.com
workspace=accounts/10319161/containers/258884256/workspaces/2
```

Ned created a Google tag in the workspace:

```text
name=Google tag - HDE GA4
type=googtag
tagId=3
measurement=G-Q6TPL08VM7
firingTriggerId=2147479553  # All Pages
```

After Michael completed the second OAuth consent including version/publish scopes, Ned created and published the GTM container version:

```text
version=accounts/10319161/containers/258884256/versions/2
versionName=Initial HDE GA4 Google tag
publish_compilerError=None
```

Live version verification showed version `2` with the `Google tag - HDE GA4` tag.

## Site code/build verification

Source defaults were updated to:

```text
PUBLIC_GTM_CONTAINER_ID=GTM-TLC3H7XV
PUBLIC_GA4_MEASUREMENT_ID=G-Q6TPL08VM7
```

Integration pattern:

- `src/layouts/Layout.astro` injects GTM on Astro-rendered pages.
- `scripts/route-complete-build.mjs` injects GTM/GA4 into built static HTML so preserved legacy pages also receive coverage.
- `.env.example` documents the public IDs.

Fresh verification after the final edit:

```text
npm run build
✓ 10 page(s) built
[route-complete] preserved 228 legacy files, generated 171 sitemap routes, 529 redirects, 297 redirect pages, and synced 4 first-class aliases; normalized 248 built HTML files
```

Rendered coverage check:

```text
html_count 248
missing_gtm_count 0
missing_noscript_count 0
missing_ga4_count 0
old_gtm_count 0
```

## Commands/patterns

Use Python/urllib with the saved OAuth token and client secrets. Do not print tokens.

For GTM publish flow:

1. POST workspace create_version:
   `https://tagmanager.googleapis.com/tagmanager/v2/{workspace_path}:create_version`
2. POST version publish:
   `https://tagmanager.googleapis.com/tagmanager/v2/{container_version_path}:publish`
3. Verify live/latest version and container snippet.
4. Update HDE site source/env from old inaccessible `GTM-M5K8WRP` to `GTM-TLC3H7XV` only after the new container is published or explicitly accepted as pending.

For rendered coverage check after build, count every `dist/**/*.html` for:

- expected GTM public ID
- GTM noscript iframe
- GA4 measurement ID
- absence of old/inaccessible GTM ID

## Safety/reporting

- Adding DNS TXT records is an infrastructure change; ask for approval before creating it.
- Do not deploy production unless Michael explicitly authorizes deployment.
- Keep token/client-secret values out of docs and logs. Site-verification values become public, but redact them unless Michael needs to install manually.
