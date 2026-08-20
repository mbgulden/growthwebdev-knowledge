# PWP GoogleClient — service-account JWT auth for GA4/GTM/GSC API calls

Captured from the 2026-07-29 `provision_site` Phase 2 work. The
`google-marketing-api-operations` skill describes OAuth setup and API
diagnostics; this document describes the operational client pattern that
was built into `prismatic-pwp-ubersuggest-auth/plugins/pwp/capabilities/provision_site/google_client.py`.

## When to use

Reach for this when the task requires:

- Creating a GA4 property + web data stream on the fly (returns
  `measurement_id` G-XXXXXX).
- Creating a GTM container + default workspace (returns `public_id`
  GTM-XXXXXXX).
- Writing a GSC verification TXT record at the apex via Cloudflare
  (no Google API call needed — see `references/2026-07-provision-site-phase-2-live-google-cloudflare.md` F7).
- Anything service-account-shaped for the Google Marketing stack.

Reach for the **parent** `google-marketing-api-operations` skill instead
for: AGY login, OAuth consent URL generation, `gcloud` ADC, scope
verification via `tokeninfo`, API enablement, or "is the project ready
yet?" diagnostics.

## Auth model

The PWP provisioner uses a single **shared service account** (the
parent skill describes why one SA per project is normal for Marketing API
work; the provisioner converges to one SA because it bootstraps N sites
under one account). Required IAM:

| Service | Required role |
|---|---|
| `analyticsadmin.googleapis.com` | `roles/analytics.admin` on the GA4 account |
| `tagmanager.googleapis.com` | `roles/Tagging Permissions Administrator` on the GTM account |
| Cloudflare API | Bearer token with `Zone:Edit` + `DNS:Edit` + `Zone:Read` (separate, see the Cloudflare skill) |

Scopes (smallest-necessary):

```text
https://www.googleapis.com/auth/analytics.edit
https://www.googleapis.com/auth/tagmanager.edit.containers
```

GSC verification is done via DNS TXT through Cloudflare's API; the
`webmasters` scope is **not** needed for the PWP flow.

## Client shape

The `GoogleClient` class is a thin `requests`-based wrapper. Three API
surface methods:

```python
gc = GoogleClient.from_env()  # reads GOOGLE_SA_JSON or GOOGLE_SA_INLINE
ga4_account = gc.ga4_account_id  # from GA4_ACCOUNT_ID env var or constructor

prop = gc.ga4_property_create(domain="example.com", site_name="Example")
# → GA4Property(name="properties/123456789", property_id="123456789",
#               measurement_id="G-ABC123DEF4", data_stream_name="properties/.../dataStreams/1")

ctr = gc.gtm_container_create(site_name="Example", domain="example.com")
# → GTMContainer(public_id="GTM-P5H2XK8", account_id="...", container_id="987654",
#                container_name="Example")
```

## JWT signing without `PyJWT`

Google service-account auth requires an RS256 JWT exchanged at
`https://oauth2.googleapis.com/token`. The full implementation fits in
~30 lines using stdlib `cryptography`. See the parent PWP file
`google_client.py` for the production-ready version; the key points:

1. Build header + claims as JSON, base64url-encode (no padding).
2. Concatenate as `header.claims` (the signing input).
3. Load the PEM private key with
   `serialization.load_pem_private_key(sa["private_key"].encode(), password=None)`.
4. Sign with `pk.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())`.
5. Append `.` + base64url(signature).
6. POST to `https://oauth2.googleapis.com/token` with
   `grant_type=urn:ietf:params:oauth:grant-type:jwt-bearer` +
   `assertion=<jwt>`.

Cache the access token per scope with a `(scope, expiry)` key; refresh
~5 min before `expires_in` expires. **Do not** mint a fresh JWT for
every API call — each JWT mint is an RSA-2048 signing op (~50ms).

## Env-var precedence pattern

Same shape as the Cloudflare token alias pattern:

```python
# GOOGLE_SA_JSON: path to a service-account JSON key file.
# GOOGLE_SA_INLINE: the JSON content itself (for secret managers that
#                   inject the value rather than mounting a file).
candidates_json_path = os.environ.get("GOOGLE_SA_JSON", "").strip()
candidates_inline = os.environ.get("GOOGLE_SA_INLINE", "").strip()
if candidates_inline:
    sa = json.loads(candidates_inline)
elif candidates_json_path:
    p = Path(candidates_json_path)
    sa = json.loads(p.read_text(encoding="utf-8"))
else:
    raise GoogleAuthError("Set GOOGLE_SA_JSON or GOOGLE_SA_INLINE ...")
# Validate: type=="service_account", required fields present.
```

Both the **file path** and **inline JSON** shapes are necessary: in some
deployments the secret manager injects env vars (inline); in others the
container mounts a Kubernetes secret as a file (path).

## API call shapes that work (2026-07-29)

### GA4 property + web stream

```python
# 1. Create the property.
prop_url = "https://analyticsadmin.googleapis.com/v1beta/properties"
prop_body = {
    "parent": f"accounts/{gc.ga4_account_id}",
    "displayName": site_name,
    "industryCategory": "TECHNOLOGY",
    "timeZone": "America/Los_Angeles",
    "currencyCode": "USD",
    "deleted": False,
}
prop_resp = gc._request("POST", prop_url, scope=gc.GA4_SCOPE, json_body=prop_body)
prop_name = prop_resp["name"]  # "properties/123456789"
property_id = prop_name.split("/", 1)[1]

# 2. Create the web data stream on the property.
stream_url = f"https://analyticsadmin.googleapis.com/v1beta/{prop_name}/dataStreams"
stream_body = {
    "type": "WEB_DATA_STREAM",
    "displayName": f"{site_name} — Web",
    "webStreamData": {"defaultUri": f"https://{domain}/"},
}
stream_resp = gc._request("POST", stream_url, scope=gc.GA4_SCOPE, json_body=stream_body)
measurement_id = stream_resp["webStreamData"]["measurementId"]  # "G-ABC123DEF4"
```

Note: `properties.create` and `dataStreams.create` are separate calls;
the measurement ID comes back in the dataStream response, not the
property response.

### GTM container

```python
url = f"https://tagmanager.googleapis.com/api/v2/accounts/{gc.gtm_account_id}/containers"
body = {
    "name": site_name,
    "domains": [domain],
    "usageContext": ["web"],
}
resp = gc._request("POST", url, scope=gc.GTM_SCOPE, json_body=body)
public_id = resp["publicId"]  # "GTM-ABC123DE"
container_id = resp["containerId"]
```

GTM `publicId` always starts with `GTM-`; if it doesn't, you have a
non-GTM response (auth failure or wrong account ID).

## Live-test status (2026-07-29)

Without credentials in this environment, only the **GSC verification
side-effect** (which uses Cloudflare, not Google) was exercised against
the live Cloudflare API. The GA4/GTM step bodies were tested with
mocked `_request` responses. See the parent
`ad-hoc-verification-contracts` skill's
`references/2026-07-provision-site-phase-2-live-google-cloudflare.md`
for the full live-test transcript.

To exercise GA4/GTM live, the deployment needs:

- A Google Cloud project with `analyticsadmin` + `tagmanager` APIs
  enabled.
- A service account with `analytics.admin` on the GA4 account and
  `Tagging Permissions Administrator` on the GTM account.
- The JSON key file at `/home/ubuntu/.hermes/profiles/ned/.env` as
  `GOOGLE_SA_JSON=/path/to/sa.json`.
- `GA4_ACCOUNT_ID` and `GTM_ACCOUNT_ID` env vars (the numeric account
  IDs from the GA4 Admin / GTM URL bars).