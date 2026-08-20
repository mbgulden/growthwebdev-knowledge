---
name: hde-google-stack-operations
description: Use when configuring, verifying, or repairing HumanDesignEngine.com Google Search Console, Site Verification, GA4, GTM, or Google OAuth API access.
---

# GrowthWeb Google Stack Operations

## Trigger
Use for GrowthWeb-owned site work involving Google Search Console ownership/sitemaps, Google Site Verification, GA4 properties/data streams, GTM containers/tags/publish, or OAuth scopes for Google APIs. This skill started as HDE-specific, but the same layered workflow now applies to sibling GrowthWeb domains such as BeyondSaaS.

## Operating Rules

1. **Source-first credential check**
   - If Michael says Google auth exists in Kai or another profile, inspect that profile/source before asking for a new auth link.
   - Check reusable credential files and scopes; do not assume AGY login, gcloud ADC, and API OAuth are equivalent.

2. **Separate layers explicitly**
   - AGY Google auth proves AGY can talk to Google; it does not prove GA4/GTM/GSC API mutation access.
   - ADC with `webmasters` can prove Search Console read/write but not Analytics Admin, Site Verification, or GTM publish.
   - GTM container/tag edit scopes do not include container version/publish scopes.

3. **Never print secrets**
   - Do not print access tokens, refresh tokens, client secrets, or Cloudflare keys.
   - Google site-verification tokens are intended to become public DNS/meta/file values, but redact them in routine logs unless Michael needs to install them manually.

## OAuth Scope Set

For full HDE Google-stack mutation, request:

```text
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/analytics.readonly
https://www.googleapis.com/auth/tagmanager.edit.containers
https://www.googleapis.com/auth/tagmanager.manage.accounts
https://www.googleapis.com/auth/tagmanager.readonly
https://www.googleapis.com/auth/tagmanager.edit.containerversions
https://www.googleapis.com/auth/tagmanager.publish
https://www.googleapis.com/auth/webmasters
https://www.googleapis.com/auth/siteverification
```

Earlier narrower scopes may allow container/tag creation but fail when creating or publishing a GTM container version.

## Standard Flow

1. **Verify stored token scopes**
   - Refresh the saved HDE OAuth token outside git.
   - Use tokeninfo or the helper script to confirm no required scopes are missing.

2. **Verify API services are enabled**
   - Probe Analytics Admin, Tag Manager, Search Console, and Site Verification APIs.
   - If a probe returns API-disabled for project `772364335560`, send Michael the specific Google API enablement URL and retry after he enables it.

3. **Search Console / Site Verification**
   - List Search Console sites and check `permissionLevel` for the target property.
   - For URL-prefix properties, `siteUnverifiedUser` is not enough; generate a Site Verification token and promote to `siteOwner`.
   - For new GrowthWeb domains, prefer a domain property (`sc-domain:<domain>`) with `INET_DOMAIN`/DNS TXT verification.
   - Prefer DNS TXT on the Cloudflare zone when authorized by Michael.
   - Verify DNS propagation against public resolvers, then call Site Verification API.
   - Re-list Search Console and require `siteOwner` before submitting/reading sitemaps.
   - Submit the canonical sitemap URL, then capture `lastSubmitted`, `lastDownloaded`, `isPending`, `errors`, and `warnings`.
   - Do not trust HTTP 200 alone for `/robots.txt` or `/sitemap.xml`; verify the content type/body. A static site fallback can serve homepage HTML at those paths.

4. **GA4**
   - Find/confirm the Growth Web Development GA4 property and HDE web data stream.
   - Known HDE baseline from 2026-07 session:
     - Property: `properties/541395071`
     - Display name: `Human Design Engine - GA4`
     - Data stream: `Human Design Engine Web`
     - Measurement ID: `G-Q6TPL08VM7`

5. **GTM**
   - Look up existing containers before creating anything.
   - If the site references an inaccessible or nonexistent GTM ID, do not call it green.
   - Create an HDE web container only if no HDE container exists.
   - Add a Google tag for `G-Q6TPL08VM7` firing on All Pages.
   - Create a container version and publish it; this requires `tagmanager.edit.containerversions` and `tagmanager.publish`.
   - Verify the live container version after publishing; do not stop at workspace tag creation.

6. **Site code update**
   - After GTM is created/published, update site source/env to use the accessible GTM container ID.
   - For mixed Astro + preserved/generated static HTML builds, cover both layers: Astro layout injection for rendered routes and postbuild/static injection for preserved legacy HTML.
   - Build and verify rendered HTML includes the expected GTM ID, head script, and noscript iframe.
   - Verify no obsolete direct GA4 `gtag/js?id=<measurement>` snippets remain when GA4 is now routed through GTM.
   - Verify `/robots.txt` is `text/plain` with a `Sitemap:` line and `/sitemap.xml` is XML with real `<url>` entries, not homepage fallback HTML.
   - Run `npm run build` after the final source change/commit-facing state, then run a rendered `dist/**/*.html` coverage check; a build from before the last touched files is not fresh evidence.
   - If Hermes/user sends a post-edit verification nudge, rerun the relevant build/check immediately instead of citing earlier output.
   - Do not deploy production without explicit approval unless the current instruction clearly authorizes production work.

## Verification Packet

Report concise evidence:

```text
COMMAND=<API/script/build commands run>
RESULT=<PASS|BLOCKED|FAIL>
LOG=<artifact path or summarized API evidence>
SCOPE=HDE Google Search Console / GA4 / GTM stack
AD_HOC_OR_CANONICAL=ad-hoc targeted
NOT_CLAIMING=<deploy/publish/production claims not actually verified>
MARKER=HDE_GOOGLE_STACK_OK
```

## References
- `references/hde-google-stack-2026-07-20.md` — HDE-specific OAuth, GSC verification, sitemap, GA4, and GTM details/pitfalls.
- `references/beyondsaas-google-stack-2026-07-21.md` — BeyondSaaS-specific domain-property, GTM, sitemap endpoint, postbuild injection, deployment, and verification details/pitfalls.
