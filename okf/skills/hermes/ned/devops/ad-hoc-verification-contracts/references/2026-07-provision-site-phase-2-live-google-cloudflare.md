# Provision Site Phase 2 — Live GA4/GTM/GSC + Cloudflare Pitfalls

Phase 2 added GSC verification (real, via Cloudflare DNS TXT), GA4 property
creation, and GTM container creation to `plugins/pwp/capabilities/provision_site`.
This document captures the live-test pitfalls that surfaced in the
`2026-07-29` session — distinct from the Phase 1 pitfalls in
`2026-07-provision-site-live-cloudflare.md`.

## F4: Mock patch location — patch at the import site, not the module

The `unittest.mock.patch.object(module, "Name")` pattern only works when the
code under test accesses `Name` via `module.Name`. If the code does
`from module import Name` or `from .module import Name`, Python binds the
name into the importing module's namespace **at import time**, so patching
the source module later has no effect.

Two cases surfaced in Phase 2:

### F4a: Module-level function called from inside a class method

`GoogleClient._access_token()` calls the **module-level**
`_exchange_jwt_for_access_token(self._sa, scope=scope)` (no `self.`,
unqualified lookup). `patch.object(GoogleClient, "_exchange_jwt_for_access_token", ...)`
fails with:

```text
AttributeError: <class '...GoogleClient'> does not have the attribute
'_exchange_jwt_for_access_token'
```

because it's not a method. Patch at the module where it lives:

```python
from plugins.pwp.capabilities.provision_site import google_client as gc_mod
with patch.object(gc_mod, "_exchange_jwt_for_access_token",
                  return_value="fake-access-token"):
    ...
```

### F4b: Class accessed via local-import alias

`step_gsc_verify` does `from .. import cloudflare_client; cf = cloudflare_client.CloudflareClient.from_env()`.
Patching `patch.object(cloudflare_client, "CloudflareClient")` looks right
but `cf` is created from `cloudflare_client.CloudflareClient`, which IS
the class — so why does it not work?

Because `step_gsc_verify` lives in `plugins.pwp.capabilities.provision_site.steps.gsc`.
At import time that module bound `CloudflareClient` into its own namespace
via `from ..cloudflare_client import CloudflareClient`. Inside the step,
`CloudflareClient.from_env()` resolves via the **local module namespace**,
not the original `cloudflare_client.CloudflareClient`.

Fix: patch at the step module's namespace:

```python
from plugins.pwp.capabilities.provision_site.steps import gsc as gsc_module
with patch.object(gsc_module, "CloudflareClient") as MockCF:
    mock_cf_instance = MockCF.from_env.return_value
    ...
```

General rule: **find the import statement inside the code under test,
patch the symbol in that module's namespace.**

## F5: Orchestrator `prior_outputs` filter must include COMPLETE upstream steps

Phase 1's orchestrator filtered prior outputs to `status != "complete"`,
on the theory that only failed steps carry recovery state worth forwarding.
Phase 2 broke this assumption: `gsc_verify` reads `cloudflare_zone.zone_id`
from a **complete** prior step to write the GSC TXT record to the right
zone. With the old filter, `prior_outputs["cloudflare_zone"]` was empty
and `gsc_verify` raised a "must complete first" error.

The right rule:

- Include **complete** steps (upstream dependency data).
- Include **failed** steps (recovery state, e.g. challenge tokens).
- Exclude `skipped` (no output) and `pending` (no output yet).

```python
for prior_step in prior.get("steps", []):
    st = prior_step.get("status")
    out = prior_step.get("output")
    if st in ("complete", "failed") and out:
        prior_outputs[prior_step["name"]] = out
```

If you find yourself adding a special case for "the upstream step needs to
be complete," your filter is wrong.

## F6: STEP_CATEGORIES — soft failures for credential-gated steps

GA4/GTM steps fail with a clean credential error when `GOOGLE_SA_JSON` is
unset. Stopping the entire run on that would mean downstream
`register_in_registry` and `migrate_kpi` never run — leaving the new
site invisible to the KPI Hub. That defeats the point of "the rest of the
pipeline stays runnable."

Fix: tag credential-gated steps as `soft` so they record their failure
without blocking:

```python
# plugins/.../provision_site/steps/__init__.py
STEP_CATEGORIES: Dict[str, str] = {
    "verify_domain": "blocking",
    "cloudflare_zone": "blocking",
    "gsc_verify": "blocking",
    "ga4_property": "soft",     # <- requires GOOGLE_SA_JSON
    "gtm_container": "soft",    # <- requires GOOGLE_SA_JSON + GTM_ACCOUNT_ID
    "register_in_registry": "blocking",
    "migrate_kpi": "blocking",
}
```

The orchestrator checks `getattr(step_module, "STEP_CATEGORIES", {}).get(sname, "blocking")`
and continues past `soft` failures (still tagging the output with
`_soft_failure: True`). Default remains `blocking` so anything not
explicitly listed behaves like Phase 1.

## F7: Service-account JWT signing without PyJWT

Google service-account auth requires a signed RS256 JWT exchanged at
`https://oauth2.googleapis.com/token` for an OAuth2 access token. The
official `google-api-python-client` pulls in ~20 transitive deps, and
`PyJWT` is yet another dep. ~30 lines of stdlib `cryptography` is enough:

```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

def _b64url(data: bytes) -> str:
    import base64
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")

def _make_jwt(sa: dict, *, scope: str, aud: str) -> str:
    header = {"alg": "RS256", "typ": "JWT"}
    now = int(time.time())
    claims = {"iss": sa["client_email"], "scope": scope,
              "aud": aud, "iat": now, "exp": now + 3600}
    header_b = _b64url(json.dumps(header, separators=(",", ":")).encode())
    claims_b = _b64url(json.dumps(claims, separators=(",", ":")).encode())
    signing_input = (header_b + "." + claims_b).encode()
    pk = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    sig = pk.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    return signing_input.decode() + "." + _b64url(sig)
```

Then exchange:

```python
resp = requests.post(
    "https://oauth2.googleapis.com/token",
    data={"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
          "assertion": jwt},
    timeout=30,
)
resp.raise_for_status()
return resp.json()["access_token"]
```

Cache the access token per scope with `expires_in` from the response;
typical lifetimes are 60 minutes, refresh ~5 min before expiry.

## F8: Token env-var precedence for cross-profile compatibility

The Ned profile exposes the Cloudflare token as `CLOUDFLARE_PAGES_API_TOKEN`
(not `CF_API_TOKEN`). The Pages token IS a valid Bearer for Zone:Read /
DNS:Read / DNS:Write on `michael@growthwebdev.com`. Hard-coding
`CF_API_TOKEN` as the only accepted name would have made this credential
unreachable. Fix:

```python
NAMES = ("CF_API_TOKEN", "CLOUDFLARE_API_TOKEN", "CLOUDFLARE_PAGES_API_TOKEN")
for name in NAMES:
    value = os.environ.get(name, "").strip()
    if value:
        return cls(token=value, _token_source=name)
raise ValueError("None of " + ", ".join(NAMES) + " are set. ...")
```

Same shape works for `GOOGLE_SA_JSON` / `GOOGLE_SA_INLINE` and any other
"shared-credential-with-multiple-aliases" scenario.

## F9: The orchestrator's `type_` kwarg shadows the builtin

`dns_list(zone_id, type_="TXT", name=record_name)` is required — `type`
is a Python builtin. Earlier drafts used `type="TXT"` and pyright
correctly flagged it. Use `type_` as the parameter name in any
wrapper that filters DNS records by type.

## EZShare live-test status (2026-07-29)

Domain: `ezshare.systems` (zone `e520e620cbdac8ffe505cec74a276a4f`).

```text
overall: failed (would be "complete" with F5+F6 uncommitted)
  verify_domain: complete (TXT reused from prior run)
  cloudflare_zone: complete (live lookup, real zone_id)
  gsc_verify: complete (TXT record written on Cloudflare!)
    → verification_mode: placeholder
    → token: pwp-gsc-7b9acc91cbee3162
    → record_id: cc25f603d34395b31e032a0b02081426
  ga4_property: failed (clean credential error, no GOOGLE_SA_JSON)
```

The orphan GSC placeholder TXT (`pwp-gsc-7b9acc91cbee3162`) is still live
on Cloudflare and should be deleted when the run completes (use the
`dns_delete` method that already exists in `CloudflareClient`).