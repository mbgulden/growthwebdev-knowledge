# AOT auth health checks

Use this when Michael asks whether anything needs to be re-authenticated for Active Oahu / Kai operations.

## Class-level pattern

Do a live credential-health pass and separate **interactive login state** from **API credentials that actually unblock the work**. A CLI such as `wrangler` can be logged out while Cloudflare API credentials still work for zone and Pages operations.

## Checks to run

### Google Search Console

- ADC credentials: `~/.config/gcloud/application_default_credentials.json`
- Required scope: `https://www.googleapis.com/auth/webmasters`
- For raw API calls, include `x-goog-user-project` from ADC `quota_project_id`; otherwise Google can complain that no quota project is set even when the JSON has one.
- Healthy signals:
  - token refresh succeeds
  - `GET https://www.googleapis.com/webmasters/v3/sites` returns HTTP 200
  - AOT property appears as `sc-domain:activeoahutours.com` with `siteOwner`

### GitHub

Use `gh auth status`. Healthy signal: logged in as `mbgulden` and token scopes include repo/workflow/project as needed.

### Linear

Probe GraphQL viewer with `LINEAR_API_KEY`:

```graphql
{ viewer { id name email } }
```

Healthy signal: HTTP 200 with Michael's viewer account.

### Cloudflare

Check both AOT zone and Pages project. Do not rely only on `wrangler whoami`.

- AOT zone operations can use `CLOUDFLARE_AOT_EMAIL` + `CLOUDFLARE_AOT_API_KEY` against `CLOUDFLARE_AOT_ZONE_ACTIVEOAHUTOURS`.
- AOT Pages operations can use the AOT account/API key against `CLOUDFLARE_AOT_ACCOUNT_ID` to list `active-oahu-tours-mirror.pages.dev`.
- `CLOUDFLARE_PAGES_API_TOKEN` / growthweb credentials may authenticate to a different Cloudflare account and list unrelated Pages projects; do not treat that as AOT Pages health.
- `wrangler whoami` being unauthenticated is optional unless the task specifically requires interactive Wrangler commands.

Healthy signals:

- zone fetch for `activeoahutours.com` returns HTTP 200 / `success: true`
- Pages project list under the AOT account includes `active-oahu-tours-mirror`

### Ubersuggest / competitor monitor

The competitor velocity monitor depends on `/tmp/ubs_token`.

Healthy signal:

```text
python3 /home/ubuntu/.hermes/profiles/kai/scripts/competitor_velocity.py
```

runs past token loading.

Unhealthy signal:

```text
/tmp/ubs_token missing or empty
ERROR: No Ubersuggest token found
```

Action: refresh the Ubersuggest MCP / PKCE token and restore `/tmp/ubs_token`; headless cron cannot complete the interactive PKCE flow autonomously.

## Reporting pattern

Return a compact table:

| Service | Status | Evidence |
|---|---:|---|
| Google Search Console API | ✅/❌ | HTTP status + property/sitemap evidence |
| GitHub | ✅/❌ | `gh auth status` account |
| Linear | ✅/❌ | GraphQL viewer |
| Cloudflare AOT zone | ✅/❌ | zone HTTP status / success |
| Cloudflare Pages for AOT | ✅/❌ | AOT Pages project visible |
| Wrangler CLI | optional | only blocking if command requires Wrangler login |
| Ubersuggest | ✅/❌ | `/tmp/ubs_token` + script behavior |

Be explicit about what needs action versus what is merely optional or logged out but not blocking.