# AOT Google Search Console API auth notes

Use this when Michael says Search Console access exists for `mbgulden@gmail.com` but Kai still cannot query sitemap state.

## Durable pattern

Search Console UI ownership and Search Console API access are separate layers:

1. The Google account must own or have access to the Search Console property.
2. The local shell/browser must have a fresh OAuth token with Search Console/Webmasters scopes.
3. The OAuth client/quota project must have `searchconsole.googleapis.com` enabled, or API calls can fail even when the account owns the property.

## Practical connection flow

Start an ADC OAuth flow with Search Console scopes:

```bash
gcloud auth application-default login --no-launch-browser \
  --scopes=https://www.googleapis.com/auth/webmasters,https://www.googleapis.com/auth/webmasters.readonly,https://www.googleapis.com/auth/cloud-platform
```

Send Michael the generated Google OAuth URL and have him complete it while signed in as `mbgulden@gmail.com`. Enter the returned code into the waiting process.

After the code is accepted, credentials should save to:

```text
~/.config/gcloud/application_default_credentials.json
```

## API probe

Use OAuth/ADC, not only an API key. Search Console rejects API-key-only calls.

```python
import json, urllib.request, google.auth, google.auth.transport.requests
creds, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/webmasters'])
creds.refresh(google.auth.transport.requests.Request())
headers = {'Authorization': 'Bearer ' + creds.token}
# Raw urllib calls do not always propagate the ADC quota project automatically.
# If application_default_credentials.json has quota_project_id, send it explicitly.
quota = getattr(creds, 'quota_project_id', None)
if quota:
    headers['x-goog-user-project'] = quota
req = urllib.request.Request(
    'https://www.googleapis.com/webmasters/v3/sites',
    headers=headers,
)
with urllib.request.urlopen(req, timeout=30) as r:
    print(json.load(r))
```

If Google complains that ADC needs a quota project, set one:

```bash
gcloud auth application-default set-quota-project PROJECT_ID_OR_NUMBER
```

If Search Console API is disabled for the quota project, calls may return:

```text
HTTP 403
Google Search Console API has not been used in project PROJECT before or it is disabled.
```

Then Michael must enable:

```text
https://console.developers.google.com/apis/api/searchconsole.googleapis.com/overview?project=PROJECT
```

If Service Usage API itself is disabled, enabling via API/CLI may also fail; use the console link.

## Property/sitemap checks once API works

Try common property variants because the property can be domain-level or URL-prefix:

```text
sc-domain:activeoahutours.com
https://activeoahutours.com/
http://activeoahutours.com/
https://www.activeoahutours.com/
```

For each property, call:

```text
GET https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/sitemaps
```

If needed, submit:

```text
PUT https://www.googleapis.com/webmasters/v3/sites/{siteUrl}/sitemaps/https%3A%2F%2Factiveoahutours.com%2Fsitemap.xml
```

Then document exact `lastSubmitted`, `lastDownloaded`, `errors`, `warnings`, and keep/close [GRO-327](https://prismatic.growthwebdev.com/tab/tasks?issue=GRO-327) based on verified API output.

## Validating a pasted-back GCP credential / doing the "rotate it" request (2026-08-19)

When Michael asks "rotate the GCP OAuth or do it automatically":

1. **Check automation first, honestly.** `which gcloud && gcloud auth list` — if "No credentialed accounts", you CANNOT rotate automatically: auth needs a browser login only Michael can complete, and resetting an API key/OAuth client secret is a Console action, not a `gcloud` operation. Say so plainly and give the link: `https://console.cloud.google.com/apis/credentials`.
2. **Distinguish credential shapes before probing.** `AIzaSy...` (39 chars) = **API key** (lives under *API keys*). `GOCSPX-...` or `1038....apps.googleusercontent.com` = **OAuth client**. The rotation UI differs; the old AOT SEO credential was mislabeled "OAuth client secret" in docs but the pasted replacement was an API key — verify the shape, don't assume the docs are right.
3. **Validate a pasted API key with a key-accepting endpoint** — do NOT use `oauth2.googleapis.com/tokeninfo` (that's for access tokens; it returns `invalid_token` for every API key, misleading). Use:
   ```bash
   curl -s "https://www.googleapis.com/books/v1/volumes?q=x&maxResults=1&key=AIza..."
   # 400 "API key not valid" = bad key (compare against a deliberate garbage key to learn the exact signature)
   # 200 with JSON = live key
   # 403 "API has not been used in project" = key is VALID but that API isn't enabled — still a pass for validity
   ```
   A bad and a valid key return DIFFERENT errors; a garbage-key control run makes the diagnosis unambiguous.
4. **Find the consumer before wiring the key in.** `grep -rn "AIzaSy" <workdir>` across env/config/py files. If the old key existed only in redacted docs (post-scrub), there is no live pipeline reading it — nothing to wire; just confirm the replacement is live and close the loop.
5. **If Michael sends a key that fails validation:** say so with the live evidence (the 400 + the garbage-key control), ask for the correct key from the Credentials → API keys page, and do NOT write an invalid key into any config on the off chance it "might work".
6. **Close the loop after rotation:** update any pointer note that says "rotate in GCP" to "rotated <date>" (e.g. the retired repo's `okf/README.md`), so the standing follow-up doesn't linger.

## Pitfalls

- Google browser login can show “This browser or app may not be secure”; prefer the no-launch-browser ADC code flow.
- API key alone is insufficient for Search Console API.
- `tokeninfo` endpoint is a dead-end for validating API keys (see recipe above) — it makes a valid key look invalid.
- Never assume the doc's label for a credential matches its actual format; check the key shape first.
- A refreshed OAuth token can still fail with `ACCESS_TOKEN_SCOPE_INSUFFICIENT` if the existing credential lacks Webmasters scopes; rerun ADC login with explicit scopes.
- Search Console ownership does not imply the Google Cloud quota project has the Search Console API enabled.
- Do not mark GSC-related Linear work Done until API/UI evidence confirms sitemap submission/status.
